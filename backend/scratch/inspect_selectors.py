import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    r = requests.get('https://huefood.vn/', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Print some links and text to find products
    print("=== Links containing /san-pham/ or /chi-tiet/ ===")
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        if any(kw in href for kw in ['san-pham', 'sp', 'detail', 'product', 'mua']) and len(text) > 10:
            print(f"  Text: {text} | Href: {href}")
            
    # Print elements with classes containing product or pro
    print("\n=== Elements with classes containing product/pro ===")
    seen_classes = set()
    for el in soup.find_all(class_=True):
        for cls in el['class']:
            if 'product' in cls or 'pro' in cls:
                seen_classes.add(cls)
    print("Classes found:", list(seen_classes))
    
except Exception as e:
    print("Error:", e)
