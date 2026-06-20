from scrapling.fetchers import Fetcher
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_shop(name, url):
    print(f"\n--- Checking {name} ({url}) ---")
    try:
        page = Fetcher.get(url, timeout=15)
        # Search for tags containing 'đ' or 'VND' and check their parent elements
        # Or look for common elements
        print("HTML content length:", len(page.html_content or ""))
        
        # Let's search for some text patterns
        # WooCommerce might have 'col-inner'
        col_inners = page.css('.col-inner')
        print(f"col-inner count: {len(col_inners)}")
        
        # Look for images and links
        a_tags = page.css('a')
        print(f"a tags count: {len(a_tags)}")
        
        # Let's dump the first 10 links
        links = []
        for a in a_tags[:30]:
            href = a.attrib.get('href')
            text = a.get_all_text().strip()
            if href and ('product' in href or 'san-pham' in href or len(text) > 10):
                links.append((text, href))
        print("Sample product-like links:")
        for l in links[:5]:
            print(f"  Text: {l[0]} | Href: {l[1]}")
            
    except Exception as e:
        print("Error:", e)

check_shop("Hương Việt Mart", "https://huongvietmart.vn/")
check_shop("DaLaVi", "https://dalavi.net/")
check_shop("HANIGO", "https://hanigo.com/")
check_shop("Đặc Sản Quê Việt", "https://dacsanqueviet.com/")
