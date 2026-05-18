import sys
import os
import json
import numpy as np
from PIL import Image
import io

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from database import SessionLocal, Shop, Product, init_db
from visual_search import ImageVectorExtractor

def populate():
    print("Initializing database...")
    init_db()
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(Shop).first():
        print("Database already contains data. Skipping population.")
        # But we might need to update vector_json if it's empty
    
    print("Creating extractor...")
    extractor = ImageVectorExtractor()
    
    # 1. Create Shops
    shops_data = [
        {"name": "VinMart Landmark 81", "address": "Vinhomes Central Park, Bình Thạnh", "lat": 10.795, "lng": 106.722},
        {"name": "Co.op Mart Cống Quỳnh", "address": "189 Cống Quỳnh, Quận 1", "lat": 10.768, "lng": 106.689},
        {"name": "Bach Hoa Xanh Quận 7", "address": "Số 10, Đường 15, Quận 7", "lat": 10.732, "lng": 106.715},
    ]
    
    shops = []
    for s in shops_data:
        shop = db.query(Shop).filter(Shop.name == s["name"]).first()
        if not shop:
            shop = Shop(name=s["name"], address=s["address"], latitude=s["lat"], longitude=s["lng"])
            db.add(shop)
            db.commit()
            db.refresh(shop)
        shops.append(shop)
    
    # 2. Create Products (Focus on Souvenirs and Cultural items)
    products_data = [
        {"name": "Bộ Ấm Trà Gốm Bát Tràng", "desc": "Gốm sứ cao cấp, hoa văn vẽ tay tinh xảo", "price": 450000.0, "color": "blue"},
        {"name": "Áo Dài Lụa Tơ Tằm Vạn Phúc", "desc": "Lụa tự nhiên, mềm mại, hoa văn truyền thống", "price": 1200000.0, "color": "red"},
        {"name": "Tranh Đông Hồ 'Vinh Hoa Phú Quý'", "desc": "Tranh dân gian làm từ giấy điệp tự nhiên", "price": 150000.0, "color": "yellow"},
        {"name": "Nón Lá Làng Chuông", "desc": "Sản phẩm thủ công truyền thống nổi tiếng", "price": 85000.0, "color": "white"},
        {"name": "Tượng Gỗ Khắc Thủ Công", "desc": "Gỗ mỹ nghệ, chạm khắc tinh xảo từ làng nghề", "price": 350000.0, "color": "brown"},
    ]
    
    for i, p in enumerate(products_data):
        existing = db.query(Product).filter(Product.name == p["name"]).first()
        if not existing:
            print(f"Adding product: {p['name']}...")
            # Create a placeholder image to get a real CLIP vector
            img = Image.new('RGB', (224, 224), color = p["color"])
            vector = extractor.extract_vector(img)
            
            product = Product(
                name=p["name"],
                description=p["desc"],
                price=p["price"],
                vector_json=json.dumps(vector.tolist()),
                shop_id=shops[i % len(shops)].id
            )
            db.add(product)
    
    db.commit()
    print("Population completed!")
    
    # 3. Sync to ChromaDB
    print("Syncing to ChromaDB...")
    from api_contract import sync_db_to_vector
    sync_db_to_vector()
    print("Sync completed!")
    
    db.close()

if __name__ == "__main__":
    populate()
