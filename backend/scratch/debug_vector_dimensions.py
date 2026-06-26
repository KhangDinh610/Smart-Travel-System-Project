import os
import sys
import json
import chromadb

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from database import SessionLocal, Product

def check_dimensions():
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.vector_json != None).first()
        if product:
            vector_sqlite = json.loads(product.vector_json)
            # Remove non-ascii characters for printing
            safe_name = product.name.encode('ascii', 'ignore').decode('ascii')
            print(f"SQLite product '{safe_name}' vector dimension: {len(vector_sqlite)}")
        else:
            print("No product vectors found in SQLite.")
    except Exception as e:
        print(f"SQLite error: {e}")
    finally:
        db.close()

    try:
        client = chromadb.PersistentClient(path=os.path.join(backend_dir, "chroma_db"))
        product_images = client.get_collection(name="product_images")
        print(f"product_images ChromaDB count: {product_images.count()}")
        if product_images.count() > 0:
            # Get a sample embedding from ChromaDB
            sample = product_images.get(include=["embeddings"], limit=1)
            # Fix truth value check
            if sample is not None and "embeddings" in sample and sample["embeddings"] is not None:
                embeddings = sample["embeddings"]
                if len(embeddings) > 0:
                    print(f"ChromaDB 'product_images' collection vector dimension: {len(embeddings[0])}")
                else:
                    print("Embeddings list is empty.")
            else:
                print("ChromaDB 'product_images' exists but has no embeddings fetched.")
        else:
            print("ChromaDB 'product_images' collection is empty.")
    except Exception as e:
        print(f"ChromaDB error: {e}")

if __name__ == "__main__":
    check_dimensions()
