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

from database import SessionLocal, Product
from visual_search import ImageVectorExtractor
from api_contract import sync_image_collection_from_sqlite

def update_vectors():
    print("Initializing CLIP model...")
    extractor = ImageVectorExtractor()
    if not extractor.loaded:
        print("Error: CLIP model could not be loaded. Aborting.")
        return

    db = SessionLocal()
    try:
        # Fetch products that need vector updates
        # We target products that have no vectors or have 384-dimensional text vectors
        products = db.query(Product).all()
        print(f"Total products in SQLite: {len(products)}")

        to_update = []
        for p in products:
            if not p.vector_json:
                to_update.append(p)
            else:
                try:
                    vec = json.loads(p.vector_json)
                    if len(vec) != 768: # Dimensions mismatch (old 384-dim text embedding)
                        to_update.append(p)
                except:
                    to_update.append(p)

        print(f"Products requiring image vector extraction: {len(to_update)}")
        if not to_update:
            print("All products already have 768-dimensional image vectors.")
            return

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        success_count = 0
        fail_count = 0

        for idx, p in enumerate(to_update):
            if not p.image_url:
                continue

            try:
                # 1. Download image
                response = requests.get(p.image_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"[{idx+1}/{len(to_update)}] Failed to download image for Product ID {p.id}: HTTP {response.status_code}")
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

                if success_count % 50 == 0:
                    db.commit()
                    print(f"Committed {success_count} vectors to SQLite...")

            except Exception as e:
                print(f"[{idx+1}/{len(to_update)}] Error processing Product ID {p.id}: {e}")
                fail_count += 1

        db.commit()
        print(f"\nExtraction completed. Success: {success_count}, Fail: {fail_count}")

    except Exception as e:
        print(f"Database error: {e}")
        db.rollback()
    finally:
        db.close()

    print("\nSynchronizing updated 768-dim image vectors from SQLite to ChromaDB...")
    try:
        sync_image_collection_from_sqlite()
        print("Synchronization completed successfully!")
    except Exception as e:
        print(f"Synchronization error: {e}")

if __name__ == "__main__":
    update_vectors()
