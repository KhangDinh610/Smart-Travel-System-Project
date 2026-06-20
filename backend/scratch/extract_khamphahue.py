import requests
from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    r = requests.get('https://khamphahue.com.vn/Du-lich/Chi-tiet/tid/Mua-Dac-san-Hue.html/pid/4313/cid/269', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Look for list items or paragraphs containing bold tags or strong tags
    # typically listing specialties
    for element in soup.find_all(['p', 'li']):
        text = element.get_text(strip=True)
        strong = element.find(['strong', 'b'])
        if strong and len(text) > 10:
            strong_text = strong.get_text(strip=True)
            if len(strong_text) > 3 and not any(kw in strong_text.lower() for kw in ['đọc', 'bài', 'du lịch', 'chia sẻ', 'liên hệ']):
                print(f"Strong: {strong_text} | Full text: {text[:150]}")
                
except Exception as e:
    print("Error:", e)
