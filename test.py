import requests

# Базовый URL API
API_URL = "http://0.0.0.0:8000"
CRAWL_URL = f"{API_URL}/crawl"
POST_CRAWL_URL = f"{API_URL}/post_crawl"
MULTIPLE_CRAWL_URL = f"{API_URL}/crawl/multiple"
PROXY_URL = f"{API_URL}/proxy"

# Тестовая функция для одиночного GET-запроса
def test_single_request():
    payload = {
        "url": "https://google.com",
        "proxy": None,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = requests.post(CRAWL_URL, json=payload)
    if response.status_code == 200:
        print("Успешный GET-запрос!")
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

# Тестовая функция для POST-запроса с параметрами
def test_post_request():
    payload = {
        "url": "https://httpbin.org/post",
        "proxy": None,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "post_data": {"key": "value", "name": "test"},
        "headers": {"Authorization": "Bearer test-token"},
        "cookies": {"session_id": "12345"}
    }
    response = requests.post(POST_CRAWL_URL, json=payload)
    if response.status_code == 200:
        print("Успешный POST-запрос!")
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

# Тестовая функция для множественных GET-запросов
def test_multiple_requests():
    payload = [
        {"url": "https://google.com"},
        {"url": "https://httpbin.org/get", "proxy": None},
        {"url": "https://jsonplaceholder.typicode.com/posts"}
    ]
    response = requests.post(MULTIPLE_CRAWL_URL, json=payload)
    if response.status_code == 200:
        print("Успешные множественные запросы!")
        for res in response.json():
            print(res)
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

# Тестовая функция для работы с прокси
def test_proxy_management():
    test_proxy = "127.0.0.1:8080"

    print("\n=== Добавление прокси ===")
    add_response = requests.post(f"{PROXY_URL}/add", json={"proxy": test_proxy})
    print(add_response.json())

    print("\n=== Список всех прокси ===")
    list_response = requests.get(f"{PROXY_URL}/list")
    print(list_response.json())

    print("\n=== Проверка статуса одного прокси ===")
    check_response = requests.get(f"{PROXY_URL}/check", params={"proxy": test_proxy})
    print(check_response.json())

    print("\n=== Проверка всех прокси ===")
    check_all_response = requests.get(f"{PROXY_URL}/check/all")
    print(check_all_response.json())

    print("\n=== Удаление прокси ===")
    remove_response = requests.delete(f"{PROXY_URL}/remove", json={"proxy": test_proxy})
    print(remove_response.json())

# Проверка использования внутреннего прокси
def test_internal_proxy_crawl():
    payload = {
        "url": "https://google.com",
        "use_internal_proxy": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = requests.post(CRAWL_URL, json=payload)
    if response.status_code == 200:
        print("Успешный запрос с внутренним прокси!")
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

# Проверка соединения
def test_connection():
    api_url = f"{API_URL}/test_connection"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            print("Успешное соединение!")
            print("Ответ сервера:", response.json())
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Не удалось подключиться: {str(e)}")

# Проверка списка маршрутов
def modules_list():
    api_url = f"{API_URL}/routes"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            print("Маршруты сервера:", response.json())
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Не удалось подключиться: {str(e)}")

if __name__ == "__main__":
    print("=== Тест соединения ===")
    test_connection()

    print("\n=== Список маршрутов ===")
    modules_list()

    print("\n=== Тест одиночного GET-запроса ===")
    test_single_request()

    print("\n=== Тест POST-запроса с параметрами ===")
    test_post_request()

    print("\n=== Тест множественных запросов ===")
    test_multiple_requests()

    print("\n=== Тест работы с прокси ===")
    test_proxy_management()

    print("\n=== Тест парсинга с внутренним прокси ===")
    test_internal_proxy_crawl()