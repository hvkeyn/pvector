
# UPVector Server

UPVector Server is a universal web crawler and proxy manager implemented using FastAPI and Playwright. The server supports GET and POST requests, page processing with proxy usage, proxy management, and returns headers and cookies.

## Features

- **Web Page Crawling**:
  - GET and POST requests.
  - Support for custom headers and cookies.
  - Internal and external proxy support.

- **Proxy Manager**:
  - Add, remove, and list proxies.
  - Check proxy availability.

- **Meta Information Retrieval**:
  - Cookies, headers, and latency.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/hvkeyn/upvector.git
cd upvector
```

### 2. Install Dependencies

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

pip install -r requirements.txt
playwright install
```

---

## Running the Server

To start the server, use:

```bash
python vector.py
```

The server will start on port `8000` by default.

---

## Testing

To test the server, run the client script:

```bash
python test.py
```

---

## API Endpoints

### 1. System Routes

| Endpoint            | Method | Description                              |
|---------------------|--------|------------------------------------------|
| `/test_connection`  | GET    | Check the server connection.             |
| `/routes`           | GET    | List all available routes.               |

---

### 2. Proxy Manager

| Endpoint            | Method | Description                              |
|---------------------|--------|------------------------------------------|
| `/proxy/add`        | POST   | Add a proxy.                             |
| `/proxy/remove`     | DELETE | Remove a proxy.                          |
| `/proxy/list`       | GET    | Get a list of all proxies.               |
| `/proxy/check`      | GET    | Check the status of a single proxy.      |
| `/proxy/check/all`  | GET    | Check all proxies.                       |

Example request to add a proxy:
```json
{
  "proxy": "127.0.0.1:8080"
}
```

---

### 3. Crawling

| Endpoint            | Method | Description                              |
|---------------------|--------|------------------------------------------|
| `/crawl`            | POST   | Single GET request.                      |
| `/post_crawl`       | POST   | POST request with parameters and cookies.|
| `/crawl/multiple`   | POST   | Multiple requests.                       |

Example body for `/post_crawl`:
```json
{
  "url": "https://httpbin.org/post",
  "post_data": {"key": "value"},
  "headers": {"Authorization": "Bearer test-token"},
  "cookies": {"session_id": "12345"}
}
```

---

## Dependencies

The project uses the following libraries:

- `fastapi` — for API implementation.
- `playwright` — for browser interaction.
- `aiohttp` — for asynchronous HTTP requests.
- `uvicorn` — for running FastAPI.

Install dependencies via `requirements.txt`.

---

## Usage Example

Test requests can be found in the `test.py` file. To run the tests, execute:

```bash
python test.py
```

---

## License

This project is licensed under Apache-2.0. See the `LICENSE` file for details.
