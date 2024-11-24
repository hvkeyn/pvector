import requests

# Базовый URL API
API_URL = "http://0.0.0.0:8000"
CRAWL_URL = f"{API_URL}/crawl"
MULTIPLE_CRAWL_URL = f"{API_URL}/crawl/multiple"
PROXY_URL = f"{API_URL}/proxy"

# Тестовая функция для отправки одиночного запроса
def test_single_request():
    # Данные для одиночного запроса
    payload = {
        "url": "https://anycoindirect.eu",  # Замените на нужный URL
        "proxy": None,  # Если хотите использовать прокси, укажите его здесь
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    # Отправляем POST запрос
    response = requests.post(CRAWL_URL, json=payload)

    # Проверяем результат
    if response.status_code == 200:
        print("Успешный ответ!")
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

# Тестовая функция для отправки множественных запросов
def test_multiple_requests():
    # Данные для нескольких запросов
    payload = [
        {"url": "https://anycoindirect.eu"},
        {"url": "https://httpbin.org/get", "proxy": None},
        {"url": "https://jsonplaceholder.typicode.com/posts"}
    ]

    # Отправляем POST запрос
    response = requests.post(MULTIPLE_CRAWL_URL, json=payload)

    # Проверяем результат
    if response.status_code == 200:
        print("Успешный ответ для множественных запросов!")
        for res in response.json():
            print(res)
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

# Тестовая функция для работы с прокси
def test_proxy_management():
    test_proxy = "127.0.0.1:8080"

    # Добавление прокси
    print("\n=== Добавление прокси ===")
    add_response = requests.post(f"{PROXY_URL}/add", json={"proxy": test_proxy})
    print(add_response.json())

    # Получение списка прокси
    print("\n=== Список всех прокси ===")
    list_response = requests.get(f"{PROXY_URL}/list")
    print(list_response.json())

    # Проверка статуса одного прокси
    print("\n=== Проверка статуса одного прокси ===")
    check_response = requests.get(f"{PROXY_URL}/check", params={"proxy": test_proxy})
    print(check_response.json())

    # Проверка всех прокси
    print("\n=== Проверка всех прокси ===")
    check_all_response = requests.get(f"{PROXY_URL}/check/all")
    print(check_all_response.json())

    # Удаление прокси
    print("\n=== Удаление прокси ===")
    remove_response = requests.delete(f"{PROXY_URL}/remove", json={"proxy": test_proxy})
    print(remove_response.json())

# Проверка использования внутреннего прокси
def test_internal_proxy_crawl():
    payload = {
        "url": "https://anycoindirect.eu",
        "use_internal_proxy": True,  # Использовать внутренний прокси
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    # Отправляем POST запрос
    response = requests.post(CRAWL_URL, json=payload)

    # Проверяем результат
    if response.status_code == 200:
        print("Успешный ответ при использовании внутреннего прокси!")
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

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

def modules_list():
    api_url = f"{API_URL}/routes"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            print("Ответ сервера:", response.json())
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Не удалось подключиться: {str(e)}")

if __name__ == "__main__":
    print("=== Тест Соединения ===")
    test_connection()

    print("=== Список модулей на сервере ===")
    modules_list()

    print("=== Тест одиночного запроса ===")
    test_single_request()

    print("\n=== Тест множественных запросов ===")
    test_multiple_requests()

    print("\n=== Тест работы с прокси ===")
    test_proxy_management()

    print("\n=== Тест парсинга с внутренним прокси ===")
    test_internal_proxy_crawl()