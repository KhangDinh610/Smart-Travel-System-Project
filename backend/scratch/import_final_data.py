import csv
import os
import sys
import json
import io
import requests
from PIL import Image

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from database import SessionLocal, Product, Shop, Base, init_db, engine
from vector_db import vector_db
from api_contract import sync_db_to_vector
from visual_search import ImageVectorExtractor

def import_data():
    print("Step 1: Dropping and recreating SQLite tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("SQLite tables recreated successfully.")

    print("\nStep 2: Resetting ChromaDB collections...")
    vector_db.reset_collections()

    csv_path = os.path.join(os.path.dirname(backend_dir), "final_data.csv")
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    db = SessionLocal()
    try:
        print(f"\nStep 3: Importing data from {csv_path}...")
        shops_dict = {} # (name, address) -> shop_id
        
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        print(f"Total rows to process: {len(rows)}")
        
        # Parse shops first to ensure they are created
        for row in rows:
            shop_name = row.get("Shop", "").strip()
            shop_address = row.get("Address", "").strip()
            if not shop_name:
                continue
                
            shop_key = (shop_name, shop_address)
            if shop_key not in shops_dict:
                # Insert shop
                shop = Shop(name=shop_name, address=shop_address)
                db.add(shop)
                db.commit()
                db.refresh(shop)
                shops_dict[shop_key] = shop.id
                print(f"Created Shop: {shop_name} (ID: {shop.id})")

        # Parse products
        product_count = 0
        for row in rows:
            prod_name = row.get("Name_product", "").strip()
            if not prod_name:
                continue
                
            shop_name = row.get("Shop", "").strip()
            shop_address = row.get("Address", "").strip()
            shop_id = shops_dict.get((shop_name, shop_address))
            
            try:
                price_val = float(row.get("Price", "0").replace(",", "").strip())
            except ValueError:
                price_val = 0.0
                
            product = Product(
                name=prod_name,
                name_en=row.get("Name_product_en", "").strip(),
                description=row.get("Description", "").strip(),
                description_en=row.get("Description_en", "").strip(),
                price=price_val,
                tag=row.get("Tag_en", "").strip(),
                category=row.get("Tag", "").strip(),
                image_url=row.get("URL_images", "").strip(),
                shop_id=shop_id
            )
            db.add(product)
            product_count += 1

        db.commit()
        print(f"Successfully imported {product_count} products into SQLite.")

        # Step 4: Sync text data to VectorDB (ChromaDB)
        print("\nStep 4: Syncing text data to ChromaDB...")
        sync_db_to_vector()

        # Step 5: Generate and sync CLIP image vectors
        print("\nStep 5: Extracting image vectors using CLIP...")
        print("Initializing CLIP model...")
        extractor = ImageVectorExtractor()
        if not extractor.loaded:
            print("Error: CLIP model could not be loaded. Visual search embeddings will be empty.")
            return

        products = db.query(Product).all()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        success_count = 0
        fail_count = 0

        for idx, p in enumerate(products):
            if not p.image_url:
                continue
                
            print(f"[{idx+1}/{len(products)}] Processing vector for product: {p.name}")
            try:
                # 1. Download image
                response = requests.get(p.image_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"  Failed to download image: HTTP {response.status_code}")
                    fail_count += 1
                    continue

                # 2. Extract image vector using CLIP
                image = extractor.load_image(io.BytesIO(response.content))
                processed = extractor.preprocess_image(image)
                vector = extractor.extract_vector(processed)
                
                # Convert numpy array to list
                vector_list = vector.tolist()
                
                # 3. Update in database
                p.vector_json = json.dumps(vector_list)
                success_count += 1

                # Commit every 10 products
                if success_count % 10 == 0:
                    db.commit()
                    print(f"  Committed {success_count} vectors...")

            except Exception as e:
                print(f"  Error processing image: {e}")
                fail_count += 1

        db.commit()
        print(f"\nImage vector extraction completed. Success: {success_count}, Fail: {fail_count}")

        # Synchronize vectors to ChromaDB
        print("\nStep 6: Synchronizing 768-dim image vectors from SQLite to ChromaDB...")
        from api_contract import sync_image_collection_from_sqlite
        sync_image_collection_from_sqlite()
        print("Database sync completed successfully!")

    except Exception as e:
        print(f"Error during import process: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_data()
