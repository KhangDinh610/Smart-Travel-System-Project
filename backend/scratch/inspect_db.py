import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal, Shop, Product, init_db

# Configure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def inspect():
    init_db()
    db = SessionLocal()
    try:
        shops_count = db.query(Shop).count()
        products_count = db.query(Product).count()
        print(f"Shops in DB: {shops_count}")
        print(f"Products in DB: {products_count}")
        
        print("\nShops list:")
        for shop in db.query(Shop).all():
            print(f"ID: {shop.id}, Name: {shop.name}, Address: {shop.address}")
            
        print("\nSample 5 products:")
        for prod in db.query(Product).limit(5).all():
            print(f"ID: {prod.id}, Name: {prod.name}, Price: {prod.price}, Shop ID: {prod.shop_id}")
    except Exception as e:
        print("Error inspecting DB:", e)
    finally:
        db.close()

if __name__ == "__main__":
    inspect()
