import requests

# URL вашего API
API_URL = "http://localhost:8000/crawl"


# Тестовая функция для отправки запроса
def test_single_request():
    # Данные для одиночного запроса
    payload = {
        "url": "https://anycoindirect.eu",  # Замените на нужный URL
        "proxy": None,  # Если хотите использовать прокси, укажите его здесь
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    # Отправляем POST запрос
    response = requests.post(API_URL, json=payload)

    # Проверяем результат
    if response.status_code == 200:
        print("Успешный ответ!")
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)


def test_multiple_requests():
    # URL для множественного эндпоинта
    API_MULTIPLE_URL = "http://localhost:8000/crawl/multiple"

    # Данные для нескольких запросов
    payload = [
        {"url": "https://ya.ru"},
        {"url": "https://httpbin.org/get", "proxy": None},
        {"url": "https://jsonplaceholder.typicode.com/posts"}
    ]

    # Отправляем POST запрос
    response = requests.post(API_MULTIPLE_URL, json=payload)

    # Проверяем результат
    if response.status_code == 200:
        print("Успешный ответ для множественных запросов!")
        for res in response.json():
            print(res)
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("=== Тест одиночного запроса ===")
    test_single_request()

    #print("\n=== Тест множественных запросов ===")
    #test_multiple_requests()