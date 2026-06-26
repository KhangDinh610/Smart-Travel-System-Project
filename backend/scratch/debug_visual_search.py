import os
import sys
import json
import chromadb

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from database import SessionLocal, Product
from vector_db import vector_db
from visual_search import ImageVectorExtractor

def debug_system():
    print("=== 1. CHECKING SQLITE PRODUCTS & VECTORS ===")
    db = SessionLocal()
    try:
        total_products = db.query(Product).count()
        products_with_vector = db.query(Product).filter(Product.vector_json != None).count()
        print(f"Total products in SQLite: {total_products}")
        print(f"Products with vector_json in SQLite: {products_with_vector}")
        
        if products_with_vector > 0:
            sample = db.query(Product).filter(Product.vector_json != None).first()
            vector_data = json.loads(sample.vector_json)
            print(f"Sample product: ID={sample.id}, Name={sample.name}")
            print(f"Vector length: {len(vector_data)} (Expected 512 for CLIP)")
    except Exception as e:
        print(f"SQLite check error: {e}")
    finally:
        db.close()

    print("\n=== 2. CHECKING CHROMADB COLLECTIONS ===")
    try:
        # Check text collection
        shopping_system = vector_db.collection
        print(f"ChromaDB shopping_system (text) count: {shopping_system.count()}")
        
        # Check image collection
        client = chromadb.PersistentClient(path=os.path.join(backend_dir, "chroma_db"))
        try:
            product_images = client.get_collection(name="product_images")
            print(f"ChromaDB product_images (image) count: {product_images.count()}")
            if product_images.count() > 0:
                sample_item = product_images.get(limit=1)
                print(f"Sample item from product_images ChromaDB: IDs={sample_item['ids']}")
        except Exception as ce:
            print(f"Error accessing product_images collection: {ce}")
    except Exception as e:
        print(f"ChromaDB check error: {e}")

    print("\n=== 3. CHECKING CLIP MODEL LOADING ===")
    try:
        print("Initializing ImageVectorExtractor (CLIP)...")
        extractor = ImageVectorExtractor()
        print(f"CLIP model loaded status: {extractor.loaded}")
        print(f"CLIP device: {extractor.device}")
    except Exception as e:
        print(f"CLIP model initialization error: {e}")

if __name__ == "__main__":
    debug_system()
