import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    r = requests.get('https://huefood.vn/51-0/san-pham/', headers=headers, timeout=10)
    print("Status:", r.status_code)
    print("Length:", len(r.text))
    
    soup = BeautifulSoup(r.text, 'html.parser')
    # Print the first 20 class names
    classes = set()
    for tag in soup.find_all(class_=True):
        classes.update(tag['class'])
    print("Unique classes found:", sorted(list(classes))[:50])
    
    # Check if there are tables or lists
    print("Table count:", len(soup.find_all('table')))
    print("Ul count:", len(soup.find_all('ul')))
    print("Div count:", len(soup.find_all('div')))
    
except Exception as e:
    print("Error:", e)
