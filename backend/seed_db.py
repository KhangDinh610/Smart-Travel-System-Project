import json
import os
import sys
sys.path.append(os.getcwd())
from backend.database import SessionLocal, Product, Shop, init_db

def seed_database():
    print("Seeding database...")
    init_db()
    db = SessionLocal()
    
    seed_file = os.path.join(os.path.dirname(__file__), 'seed_data.json')
    if not os.path.exists(seed_file):
        print(f"Error: {seed_file} not found.")
        return

    try:
        with open(seed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Seed Shops
        for shop_data in data.get("shops", []):
            existing_shop = db.query(Shop).filter(Shop.id == shop_data['id']).first()
            if not existing_shop:
                shop = Shop(**shop_data)
                db.add(shop)
        
        db.commit()
        print(f"Imported {len(data.get('shops', []))} shops.")

        # Seed Products
        for prod_data in data.get("products", []):
            existing_prod = db.query(Product).filter(Product.id == prod_data['id']).first()
            if not existing_prod:
                product = Product(**prod_data)
                db.add(product)
        
        db.commit()
        print(f"Imported {len(data.get('products', []))} products.")
        
        print("Database seeding completed successfully.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
