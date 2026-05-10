import requests

# URL backend FastAPI
BASE_URL = "http://127.0.0.1:8000"

def handle_response(response):
    if response.status_code in [200, 201]:
        return response.json(), None
    try:
        error_data = response.json()
        error_msg = error_data.get("detail", "Có lỗi xảy ra.")
    except Exception:
        error_msg = response.text or "Lỗi kết nối đến máy chủ."
    return None, error_msg

def get_headers(token):
    return {"Authorization": f"Bearer {token}"}

def register(email, password):
    url = f"{BASE_URL}/register"
    response = requests.post(url, json={"email": email, "password": password})
    return handle_response(response)

def login(email, password):
    url = f"{BASE_URL}/login"
    response = requests.post(url, json={"email": email, "password": password})
    return handle_response(response)

def login_google(code, redirect_uri):
    url = f"{BASE_URL}/login/google"
    response = requests.post(url, json={"code": code, "redirect_uri": redirect_uri})
    return handle_response(response)

def check_duplicate(token, name, description=""):
    url = f"{BASE_URL}/duplicate/check"
    payload = {"name": name, "description": description}
    response = requests.post(url, json=payload, headers=get_headers(token))
    return handle_response(response)

def add_product(token, name, description=""):
    url = f"{BASE_URL}/duplicate/add-product"
    payload = {"name": name, "description": description}
    response = requests.post(url, json=payload, headers=get_headers(token))
    return handle_response(response)
