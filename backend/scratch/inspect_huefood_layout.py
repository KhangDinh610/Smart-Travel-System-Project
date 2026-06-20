import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    r = requests.get('https://huefood.vn/51-0/san-pham/ ', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Print the outer layout elements to locate products
    print("Finding elements with classes related to list, grid, row, col:")
    for el in soup.find_all(class_=True)[:50]:
        cls_list = el['class']
        if any(kw in "".join(cls_list).lower() for kw in ['list', 'grid', 'row', 'col', 'item', 'block']):
            print(f"  Tag: {el.name} | Classes: {cls_list} | Text: {el.get_text(strip=True)[:50]}")
            
except Exception as e:
    print("Error:", e)
