import os
import requests
from requests.exceptions import RequestException, ConnectTimeout, ConnectionError

# URL backend FastAPI
BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 5

def handle_response(response):
    if response.status_code in [200, 201]:
        return response.json(), None
    try:
        error_data = response.json()
        error_msg = error_data.get("detail", "Có lỗi xảy ra.")
    except Exception:
        error_msg = response.text or "Lỗi kết nối đến máy chủ."
    return None, error_msg


def safe_post(url, json=None, headers=None):
    try:
        response = requests.post(url, json=json, headers=headers, timeout=TIMEOUT_SECONDS)
        return handle_response(response)
    except (ConnectTimeout, ConnectionError):
        return None, f"Không thể kết nối đến backend tại {url}. Hãy đảm bảo backend đang chạy và URL đúng."
    except RequestException as exc:
        return None, f"Lỗi khi gọi backend: {exc}"

def get_headers(token):
    return {"Authorization": f"Bearer {token}"}

def register(email, password):
    url = f"{BASE_URL}/register"
    return safe_post(url, json={"email": email, "password": password})


def login(email, password):
    url = f"{BASE_URL}/login"
    return safe_post(url, json={"email": email, "password": password})


def login_google(code, redirect_uri):
    url = f"{BASE_URL}/login/google"
    return safe_post(url, json={"code": code, "redirect_uri": redirect_uri})


def check_duplicate(token, name, description=""):
    url = f"{BASE_URL}/duplicate/check"
    payload = {"name": name, "description": description}
    return safe_post(url, json=payload, headers=get_headers(token))


def add_product(token, name, description=""):
    url = f"{BASE_URL}/duplicate/add-product"
    payload = {"name": name, "description": description}
    return safe_post(url, json=payload, headers=get_headers(token))


def chatbot_ask(token, query):
    url = f"{BASE_URL}/chatbot/ask"
    payload = {"query": query}
    return safe_post(url, json=payload, headers=get_headers(token))


def get_recommendations(token, preference="", budget=None, location_lat=None, location_lon=None, top_k=5):
    url = f"{BASE_URL}/recommend/recommend"
    payload = {
        "preference": preference,
        "budget": budget,
        "location_lat": location_lat,
        "location_lon": location_lon,
        "top_k": top_k
    }
    return safe_post(url, json=payload, headers=get_headers(token))


def log_purchase(token, product_id, shop_id=None):
    url = f"{BASE_URL}/recommend/history/log"
    payload = {"product_id": product_id, "shop_id": shop_id}
    return safe_post(url, json=payload, headers=get_headers(token))
