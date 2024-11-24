import asyncio
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from playwright.async_api import async_playwright
import aiohttp
import random
import time
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Прокси менеджер ==========
class ProxyManager:
    def __init__(self):
        self.proxies = []

    def add_proxy(self, proxy: str):
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            logger.info(f"Proxy added: {proxy}")

    def remove_proxy(self, proxy: str):
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            logger.info(f"Proxy removed: {proxy}")

    def list_proxies(self):
        return self.proxies

    async def check_proxy(self, proxy: str):
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get("https://ipinfo.io/json", proxy=f"http://{proxy}", timeout=5) as response:
                    elapsed_time = time.time() - start_time
                    if response.status == 200:
                        data = await response.json()
                        return {"proxy": proxy, "status": "working", "location": f"{data.get('city', 'unknown')}, {data.get('country', 'unknown')}", "latency": round(elapsed_time, 2)}
        except Exception as e:
            logger.warning(f"Proxy check failed for {proxy}: {str(e)}")
            return {"proxy": proxy, "status": "failed", "error": str(e)}

    def get_working_proxy(self):
        if not self.proxies:
            raise HTTPException(status_code=400, detail="No proxies available")
        return random.choice(self.proxies)


proxy_manager = ProxyManager()
app = FastAPI()

# Модель для запросов
class ProxyRequest(BaseModel):
    proxy: str

class CrawlRequest(BaseModel):
    url: str
    use_internal_proxy: Optional[bool] = False
    proxy: Optional[str] = None
    user_agent: Optional[str] = None

class PostRequest(CrawlRequest):
    post_data: Optional[Dict[str, Any]] = None  # Параметры для POST-запроса
    headers: Optional[Dict[str, str]] = None    # Дополнительные заголовки
    cookies: Optional[Dict[str, str]] = None    # Cookies для запроса

@app.get("/routes")
def list_routes():
    return [{"path": route.path, "methods": list(route.methods)} for route in app.routes]

@app.get("/test_connection")
def test_connection(request: Request):
    client_host = request.client.host
    return {"status": "ok", "message": "Connection successful!", "client_ip": client_host, "server_ip": request.headers.get("host", "unknown")}

@app.post("/proxy/add")
def add_proxy(request: ProxyRequest):
    proxy_manager.add_proxy(request.proxy)
    return {"message": "Proxy added successfully", "proxy": request.proxy}

@app.delete("/proxy/remove")
def remove_proxy(request: ProxyRequest):
    proxy_manager.remove_proxy(request.proxy)
    return {"message": "Proxy removed successfully", "proxy": request.proxy}

@app.get("/proxy/list")
def list_proxies():
    proxies = proxy_manager.list_proxies()
    if not proxies:
        return {"message": "No proxies available"}
    return {"proxies": proxies}

@app.get("/proxy/check")
async def check_proxy(proxy: str):
    status = await proxy_manager.check_proxy(proxy)
    return status

@app.get("/proxy/check/all")
async def check_all_proxies():
    proxies = proxy_manager.list_proxies()
    if not proxies:
        return {"message": "No proxies available"}
    tasks = [proxy_manager.check_proxy(proxy) for proxy in proxies]
    try:
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=30)
        return {"proxies_status": results}
    except asyncio.TimeoutError:
        return {"message": "Proxy checking timed out"}

async def fetch_page(url: str, proxy: Optional[str] = None, user_agent: Optional[str] = None, headers: Optional[Dict[str, str]] = None, cookies: Optional[Dict[str, str]] = None, post_data: Optional[Dict[str, Any]] = None):
    async with async_playwright() as p:
        browser_args = {"headless": True}
        if proxy:
            browser_args["proxy"] = {"server": f"http://{proxy}"}
        browser = await p.chromium.launch(**browser_args)
        context = await browser.new_context(user_agent=user_agent, extra_http_headers=headers)
        if cookies:
            for name, value in cookies.items():
                await context.add_cookies([{"name": name, "value": value, "url": url}])
        page = await context.new_page()
        try:
            if post_data:
                await page.goto(url, timeout=6000)
                response = await page.evaluate(
                    """(url, data) => fetch(url, {
                        method: 'POST',
                        body: JSON.stringify(data),
                        headers: { 'Content-Type': 'application/json' }
                    }).then(res => res.text())""",
                    url,
                    post_data,
                )
                await browser.close()
                return {"content": response, "headers": await page.evaluate("() => document.head.innerHTML"), "cookies": cookies}
            else:
                await page.goto(url, timeout=6000)
                content = await page.content()
                headers = await page.evaluate("() => document.head.innerHTML")
                await browser.close()
                return {"content": content, "headers": headers, "cookies": cookies}
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Failed to fetch page {url}: {str(e)}")

@app.post("/crawl")
async def crawl_page(request: CrawlRequest):
    proxy = request.proxy or (proxy_manager.get_working_proxy() if request.use_internal_proxy else None)
    content = await fetch_page(request.url, proxy, request.user_agent)
    return {"url": request.url, "proxy_used": proxy, "content": content}

@app.post("/post_crawl")
async def post_crawl(request: PostRequest):
    proxy = request.proxy or (proxy_manager.get_working_proxy() if request.use_internal_proxy else None)
    result = await fetch_page(
        url=request.url,
        proxy=proxy,
        user_agent=request.user_agent,
        headers=request.headers,
        cookies=request.cookies,
        post_data=request.post_data,
    )
    return {"url": request.url, "proxy_used": proxy, "result": result}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", 8000))
    uvicorn.run(app, host=host, port=port)