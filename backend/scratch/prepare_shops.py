import json
import csv
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

def extract_shops():
    shops = {}
    
    # 1. Parse Phuc's JSON
    phuc_json = 'scratch/phuc_parsed.json'
    if os.path.exists(phuc_json):
        with open(phuc_json, 'r', encoding='utf-8') as f:
            phuc_data = json.load(f)
        for row in phuc_data:
            # Skip header or empty rows
            name = row.get('A')
            link = row.get('C')
            address = row.get('E')
            if not name or name == 'Tên':
                continue
            name = name.strip()
            link = link.strip() if link else ''
            address = address.strip() if address else ''
            
            # Use link as unique key to avoid duplicate domains, fallback to name
            key = link.lower() if link else name.lower()
            shops[key] = {
                "name": name,
                "link": link,
                "address": address,
                "source": "phuc"
            }
            
    # 2. Parse Minh's CSV
    minh_csv = 'minh.csv'
    if os.path.exists(minh_csv):
        with open(minh_csv, 'r', encoding='utf-8') as f:
            # Use skipinitialspace=True to ignore spaces after commas so quotes parse correctly
            reader = csv.DictReader(f, skipinitialspace=True)
            for raw_row in reader:
                # Clean headers and values (strip whitespace)
                row = {k.strip(): v.strip() for k, v in raw_row.items() if k is not None and v is not None}
                name = row.get('Tên shop')
                link = row.get('Link')
                address = row.get('Địa chỉ')
                if not name:
                    continue
                name = name.strip()
                link = link.strip() if link else ''
                address = address.strip() if address else ''
                
                key = link.lower() if link else name.lower()
                # Merge or overwrite if the name is cleaner (e.g. Hương Việt vs Hương Việt Mart)
                if key in shops:
                    # Keep the one with longer name or more details
                    if len(name) > len(shops[key]["name"]):
                        shops[key]["name"] = name
                    if not shops[key]["address"] and address:
                        shops[key]["address"] = address
                    shops[key]["source"] = "both"
                else:
                    shops[key] = {
                        "name": name,
                        "link": link,
                        "address": address,
                        "source": "minh"
                    }
                    
    print(f"Total unique shops extracted: {len(shops)}")
    for i, (k, s) in enumerate(shops.items()):
        print(f"{i+1}. {s['name']} | Link: {s['link']} | Address: {s['address']} | Source: {s['source']}")
        
    # Write to a JSON file for the main scraper script to use
    with open('scratch/shops_to_scrape.json', 'w', encoding='utf-8') as f:
        json.dump(list(shops.values()), f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extract_shops()
