import csv
import os
from database import SessionLocal, Product, Shop

def export_products_to_csv():
    print("Exporting products from database to CSV...")
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        if not products:
            print("No products found in database.")
            return

        file_path = os.path.join(os.path.dirname(__file__), 'scraped_products.csv')
        
        # Get all column names from the Product model
        columns = [column.name for column in Product.__table__.columns]
        # Optionally add shop name
        columns.append('shop_name')

        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            
            for product in products:
                data = {column.name: getattr(product, column.name) for column in Product.__table__.columns}
                # Get shop name
                shop = db.query(Shop).filter(Shop.id == product.shop_id).first()
                data['shop_name'] = shop.name if shop else "Unknown"
                writer.writerow(data)
                
        print(f"Successfully exported {len(products)} products to {file_path}")

    except Exception as e:
        print(f"Error exporting to CSV: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_products_to_csv()
