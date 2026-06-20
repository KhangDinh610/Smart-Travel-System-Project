import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    r = requests.get('https://huefood.vn/', headers=headers, timeout=10)
    print("Status:", r.status_code)
    print("Headers:", dict(r.headers))
    print("Content length:", len(r.text))
    print("Preview:", r.text[:500])
except Exception as e:
    print("Error:", e)
