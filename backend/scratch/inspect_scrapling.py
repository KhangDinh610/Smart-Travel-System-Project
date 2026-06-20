from scrapling.fetchers import Fetcher
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    page = Fetcher.get('https://huefood.vn/', timeout=10)
    print("Page keys/dir:")
    print(dir(page))
    
    # Check if page has some HTML
    print("Page status:", page.status)
    if hasattr(page, 'html'):
        print("Page.html type:", type(page.html))
        # Print first 200 chars of page.html if string
        print("Page.html preview:", str(page.html)[:200])
    
    # Check if we can do css search
    titles = page.css('title::text').get_all()
    print("Titles found via CSS selection:", titles)
except Exception as e:
    print("Error:", e)
