import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    r = requests.get('https://khamphahue.com.vn/Du-lich/Chi-tiet/tid/Mua-Dac-san-Hue.html/pid/4313/cid/269', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Print the title and first few paragraphs or headings
    print("Page Title:", soup.title.get_text() if soup.title else "No Title")
    
    # Print text content
    text_content = soup.get_text()
    print("Length of text content:", len(text_content))
    
    # Print headings
    print("\nH1 headings:")
    for h1 in soup.find_all('h1'):
        print("  -", h1.get_text().strip())
    print("\nH2 headings:")
    for h2 in soup.find_all('h2'):
        print("  -", h2.get_text().strip())
    print("\nH3 headings:")
    for h3 in soup.find_all('h3'):
        print("  -", h3.get_text().strip())
        
except Exception as e:
    print("Error:", e)
