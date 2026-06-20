from scrapling.fetchers import Fetcher
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')

def inspect_html():
    shops_file = 'scratch/shops_to_scrape.json'
    if not os.path.exists(shops_file):
        print("shops_to_scrape.json not found")
        return
        
    with open(shops_file, 'r', encoding='utf-8') as f:
        shops = json.load(f)
        
    for idx, shop in enumerate(shops):
        name = shop['name']
        link = shop['link']
        if not link or "huefarm.vn" in link:
            continue
            
        print(f"\n=== Inspecting {name} ({link}) ===")
        try:
            page = Fetcher.get(link, timeout=15)
            print("Status:", page.status)
            
            # Print page title
            title = page.css('title::text').get()
            print("Page Title:", title)
            
            # Check for woocommerce class presence
            html_content = page.html_content or ""
            is_woo = "woocommerce" in html_content.lower()
            print("Is WooCommerce:", is_woo)
            
            # Try a few common container selectors
            containers = []
            selectors = ['.product', '.product-item', '.product-inner', '.item', 'li.product', '.product-card', '.entry-product']
            for sel in selectors:
                found = page.css(sel)
                if len(found) > 0:
                    containers.append((sel, len(found)))
            print("Container elements matched:", containers)
            
        except Exception as e:
            print("Error inspecting:", e)

if __name__ == "__main__":
    inspect_html()
