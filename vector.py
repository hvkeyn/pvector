import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from typing import Optional
from concurrent.futures import ThreadPoolExecutor


# Модель данных для запросов
class CrawlRequest(BaseModel):
    url: str
    proxy: Optional[str] = None  # Прокси (необязательно)
    user_agent: Optional[str] = None  # Пользовательский User-Agent (необязательно)


# Создаем FastAPI приложение
app = FastAPI()


# Функция для загрузки страницы
async def fetch_page(url: str, proxy: Optional[str] = None, user_agent: Optional[str] = None):
    async with async_playwright() as p:
        browser_args = {"headless": True}
        if proxy:
            browser_args["proxy"] = {"server": proxy}

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

# Асинхронный эндпоинт для выполнения задачи
@app.post("/crawl")
async def crawl_page(request: CrawlRequest):
    content = await fetch_page(request.url, request.proxy, request.user_agent)
    return {"url": request.url, "content": content}


# Устанавливаем ограничение на потоки для многозадачности
executor = ThreadPoolExecutor(max_workers=10)  # Настройка максимального числа потоков


# Асинхронный обработчик для запуска задач параллельно
@app.post("/crawl/multiple")
async def crawl_multiple(requests: list[CrawlRequest]):
    loop = asyncio.get_event_loop()

    # Запускаем задачи в потоках
    tasks = [
        loop.run_in_executor(
            executor,
            lambda req=req: asyncio.run(fetch_page(req.url, req.proxy, req.user_agent))
        )
        for req in requests
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Формируем ответы
    responses = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            responses.append({"url": requests[i].url, "error": str(result)})
        else:
            responses.append({"url": requests[i].url, "content": result})
    return responses


# Запуск сервера (если запускается как отдельный скрипт)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)