import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')

seed_file = 'seed_data.json'
if os.path.exists(seed_file):
    with open(seed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("Keys in seed_data.json:", list(data.keys()))
    print("Number of shops:", len(data.get("shops", [])))
    print("Shops:")
    for shop in data.get("shops", []):
        print(f"  - ID: {shop.get('id')}, Name: {shop.get('name')}, Address: {shop.get('address')}")
    print("Number of products:", len(data.get("products", [])))
else:
    print("seed_data.json does not exist")
