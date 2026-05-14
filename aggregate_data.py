import json
import os
import sys
import csv

# Add backend to path to import database
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from database import SessionLocal, Shop, Product, init_db, engine, Base

def clean_db():
    Base.metadata.drop_all(bind=engine)
    init_db()

def aggregate_data():
    clean_db()
    db = SessionLocal()

    data_dir = 'data'
    files = os.listdir(data_dir)

    shop_cache = {}

    def get_or_create_shop(name, address="Unknown", lat=0.0, lng=0.0):
        if not name or name == 'Unknown Shop':
            name = 'Unknown'
        
        # Normalize name for caching
        norm_name = name.strip().lower()
        if norm_name in shop_cache:
            return shop_cache[norm_name]
        
        shop = db.query(Shop).filter(Shop.name == name).first()
        if not shop:
            shop = Shop(name=name, address=address or "Unknown", latitude=lat or 0.0, longitude=lng or 0.0)
            db.add(shop)
            db.commit()
            db.refresh(shop)
        
        shop_cache[norm_name] = shop.id
        return shop.id

    def add_product(name, description, shop_id):
        if not name:
            return
        # Simple deduplication: check if product exists in this shop
        exists = db.query(Product).filter(Product.name == name, Product.shop_id == shop_id).first()
        if not exists:
            product = Product(
                name=name,
                description=description or "",
                vector_json="[]",
                shop_id=shop_id
            )
            db.add(product)

    for filename in files:
        filepath = os.path.join(data_dir, filename)
        print(f"Processing {filename}...")
        
        if filename.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue
                if not isinstance(data, list):
                    continue
                for item in data:
                    if filename in ['adaptive_products.json', 'ultimate_products.json']:
                        shop_id = get_or_create_shop(item.get('Source_URL'))
                        add_product(item.get('Product_Name'), f"Price: {item.get('Price')}. Link: {item.get('Detail_Link')}", shop_id)
                    elif filename == 'hue_knowledge_base.json':
                        shop_id = get_or_create_shop(item.get('Địa_điểm_gợi_ý'))
                        add_product(item.get('Sản_phẩm'), f"{item.get('Mô_tả_chi_tiết')}. Price: {item.get('Giá_tham_khảo')}", shop_id)
                    elif filename == 'results_multi.json':
                        shop_name = item.get('nền_tảng')
                        address = item.get('khu_vực') or item.get('khu_ vực')
                        shop_id = get_or_create_shop(shop_name, address=address)
                        add_product(item.get('tên_sản_phẩm'), f"Price: {item.get('giá')}. Link: {item.get('liên_kết')}", shop_id)

        elif filename.endswith('.csv'):
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1']
            reader = None
            f = None
            for enc in encodings:
                try:
                    f = open(filepath, 'r', encoding=enc)
                    # Use Sniffer to check dialect
                    content = f.read(4096)
                    f.seek(0)
                    dialect = csv.Sniffer().sniff(content)
                    reader = csv.DictReader(f, dialect=dialect)
                    break
                except Exception:
                    if f: f.close()
                    continue
            
            if not reader:
                print(f"Could not read {filename}")
                continue

            for row in reader:
                try:
                    # Logic based on headers
                    if 'Product_Name' in row and 'Source_URL' in row:
                        shop_id = get_or_create_shop(row.get('Source_URL'))
                        add_product(row.get('Product_Name'), f"Price: {row.get('Price')}. Link: {row.get('Detail_Link')}", shop_id)
                    
                    elif 'product_name' in row and 'store_name' in row:
                        lat = float(row.get('store_lat', 0) or 0)
                        lng = float(row.get('store_lng', 0) or 0)
                        shop_id = get_or_create_shop(row.get('store_name'), address=row.get('store_address'), lat=lat, lng=lng)
                        add_product(row.get('product_name'), f"{row.get('description')}. Price: {row.get('price_text')}. Category: {row.get('category')}", shop_id)
                    
                    elif 'Tên Sản Phẩm' in row and 'Tên Cửa Hàng' in row:
                        shop_id = get_or_create_shop(row.get('Tên Cửa Hàng'), address=row.get('Địa Chỉ'))
                        add_product(row.get('Tên Sản Phẩm'), f"Price: {row.get('Giá')}. Category: {row.get('Danh Mục')}", shop_id)

                    elif 'Tên sản phẩm' in row and 'Tên shop' in row:
                        shop_id = get_or_create_shop(row.get('Tên shop'), address=row.get('Tỉnh thành'))
                        add_product(row.get('Tên sản phẩm'), f"Price: {row.get('Giá')}. ID: {row.get('ID')}", shop_id)

                    elif 'item_name' in row and 'seller_name' in row:
                        shop_id = get_or_create_shop(row.get('seller_name'))
                        add_product(row.get('item_name'), f"Category: {row.get('category')}. Price Range: {row.get('price_range')}", shop_id)

                    elif 'Sản_phẩm' in row and 'Địa_điểm_gợi_ý' in row:
                        shop_id = get_or_create_shop(row.get('Địa_điểm_gợi_ý'))
                        add_product(row.get('Sản_phẩm'), f"{row.get('Mô_tả_chi_tiết')}. Price: {row.get('Giá_tham_khảo')}", shop_id)

                    elif 'Product_Name' in row and 'Shop_Name' in row: # hue_products_data.csv / hue_products_detailed.csv
                        shop_id = get_or_create_shop(row.get('Shop_Name'))
                        add_product(row.get('Product_Name'), f"Price: {row.get('Price')}", shop_id)
                    
                    elif 'Name' in row and 'Address' in row and 'Website' in row: # hue_shops_info_final.csv / hue_souvenir_shops.csv
                        # This is a shop list, might not have products in the same file
                        get_or_create_shop(row.get('Name'), address=row.get('Address'), lat=float(row.get('Latitude', 0) or 0), lng=float(row.get('Longitude', 0) or 0))

                except Exception as e:
                    continue
            
            if f: f.close()
        
        db.commit() # Commit after each file

    db.close()
    print("Comprehensive data aggregation completed successfully.")

if __name__ == "__main__":
    aggregate_data()
