import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from playwright.async_api import async_playwright
import aiohttp
import random
import time


# ========== Прокси менеджер ==========
class ProxyManager:
    def __init__(self):
        self.proxies = []

    def add_proxy(self, proxy: str):
        """Добавить прокси"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)

    def remove_proxy(self, proxy: str):
        """Удалить прокси"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)

    def list_proxies(self):
        """Вывести список прокси"""
        return self.proxies

    async def check_proxy(self, proxy: str):
        """Проверить статус прокси"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get("https://ipinfo.io/json", proxy=f"http://{proxy}", timeout=5) as response:
                    elapsed_time = time.time() - start_time
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "proxy": proxy,
                            "status": "working",
                            "location": data.get("city", "unknown") + ", " + data.get("country", "unknown"),
                            "latency": round(elapsed_time, 2),
                        }
                    else:
                        return {"proxy": proxy, "status": "failed"}
        except Exception as e:
            return {"proxy": proxy, "status": "failed", "error": str(e)}

    def get_working_proxy(self):
        """Выбрать случайный рабочий прокси из списка"""
        if not self.proxies:
            raise HTTPException(status_code=400, detail="No proxies available")
        return random.choice(self.proxies)


proxy_manager = ProxyManager()

# ========== FastAPI приложение ==========
app = FastAPI()


# Модель для запросов
class ProxyRequest(BaseModel):
    proxy: str


class CrawlRequest(BaseModel):
    url: str
    use_internal_proxy: Optional[bool] = False  # Использовать внутренний прокси
    proxy: Optional[str] = None  # Внешний прокси
    user_agent: Optional[str] = None  # Пользовательский User-Agent (необязательно)


# ========== Эндпоинты менеджера прокси ==========
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
    return {"proxies": proxies}


@app.get("/proxy/check")
async def check_proxy(proxy: str):
    status = await proxy_manager.check_proxy(proxy)
    return status


@app.get("/proxy/check/all")
async def check_all_proxies():
    proxies = proxy_manager.list_proxies()
    tasks = [proxy_manager.check_proxy(proxy) for proxy in proxies]
    results = await asyncio.gather(*tasks)
    return {"proxies_status": results}


# ========== Эндпоинты для парсинга ==========
async def fetch_page(url: str, proxy: Optional[str] = None, user_agent: Optional[str] = None):
    async with async_playwright() as p:
        browser_args = {"headless": True}
        if proxy:
            browser_args["proxy"] = {"server": f"http://{proxy}"}

        browser = await p.chromium.launch(**browser_args)
        context_args = {}

        # Установка кастомного User-Agent (если указан)
        if user_agent:
            context_args["user_agent"] = user_agent

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            # Загрузка страницы
            await page.goto(url, timeout=60000)
            content = await page.content()
            await browser.close()
            return content
        except Exception as e:
            await browser.close()
            raise HTTPException(status_code=500, detail=f"Error fetching page: {str(e)}")


@app.post("/crawl")
async def crawl_page(request: CrawlRequest):
    # Определяем, какой прокси использовать
    proxy = request.proxy
    if request.use_internal_proxy and not proxy:
        try:
            proxy = proxy_manager.get_working_proxy()
        except HTTPException:
            proxy = None  # Продолжаем без прокси, если нет рабочих

    content = await fetch_page(request.url, proxy, request.user_agent)
    return {"url": request.url, "proxy_used": proxy, "content": content}

# Запуск сервера (если запускается как отдельный скрипт)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)