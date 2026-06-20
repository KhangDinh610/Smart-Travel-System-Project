import json
import os
import sys
import requests
from scrapling.fetchers import Fetcher

sys.stdout.reconfigure(encoding='utf-8')

def test_fetch():
    shops_file = 'scratch/shops_to_scrape.json'
    if not os.path.exists(shops_file):
        print("shops_to_scrape.json not found")
        return
        
    with open(shops_file, 'r', encoding='utf-8') as f:
        shops = json.load(f)
        
    print(f"Testing {len(shops)} shops...")
    for idx, shop in enumerate(shops):
        name = shop['name']
        link = shop['link']
        if not link:
            print(f"{idx+1}. {name}: No link")
            continue
            
        # Test with scrapling Fetcher
        try:
            page = Fetcher.get(link, timeout=10)
            status = page.status
            html_len = len(page.text) if page.text else 0
            print(f"{idx+1}. {name} ({link}) -> Scrapling Status: {status}, HTML Length: {html_len}")
        except Exception as e:
            # Test with requests
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
                r = requests.get(link, headers=headers, timeout=10)
                print(f"{idx+1}. {name} ({link}) -> Requests Status: {r.status_code}, HTML Length: {len(r.text)}")
            except Exception as re:
                print(f"{idx+1}. {name} ({link}) -> Failed both. Error: {re}")

if __name__ == "__main__":
    test_fetch()
