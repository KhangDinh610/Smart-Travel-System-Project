import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal, Shop, Product, init_db

sys.stdout.reconfigure(encoding='utf-8')

def count_shop_products():
    db = SessionLocal()
    try:
        shops = db.query(Shop).all()
        print(f"Total shops: {len(shops)}")
        for s in shops:
            p_count = db.query(Product).filter(Product.shop_id == s.id).count()
            print(f"Shop ID {s.id}: {s.name} ({p_count} products)")
    finally:
        db.close()

if __name__ == "__main__":
    count_shop_products()
