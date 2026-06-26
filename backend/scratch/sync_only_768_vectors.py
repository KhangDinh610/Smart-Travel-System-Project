import os
import sys
import json
import chromadb

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from database import SessionLocal, Product, Shop
from vector_db import vector_db

def sync_768_vectors():
    print("Connecting to SQLite...")
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.vector_json != None).all()
        print(f"Total products with vectors in SQLite: {len(products)}")

        valid_products = []
        for p in products:
            try:
                vec = json.loads(p.vector_json)
                if isinstance(vec, list) and len(vec) == 768:
                    valid_products.append((p, vec))
            except Exception as e:
                pass

        print(f"Products with valid 768-dim image vectors: {len(valid_products)}")
        if not valid_products:
            print("No valid 768-dim image vectors found. Aborting sync.")
            return

        # Connect to ChromaDB and recreate collection
        print("Recreating product_images collection in ChromaDB...")
        try:
            vector_db.delete_collection("product_images")
            print("Deleted old product_images collection.")
        except Exception as e:
            print(f"Note: Could not delete old collection (might not exist): {e}")

        # Re-create empty collection
        # (This will automatically configure dimension on first insert, which is 768)
        client = chromadb.PersistentClient(path=os.path.join(backend_dir, "chroma_db"))
        product_images = client.get_or_create_collection(name="product_images")
        print("Created fresh product_images collection.")

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for p, vec in valid_products:
            shop = db.query(Shop).filter(Shop.id == p.shop_id).first()
            ids.append(f"img_prod_{p.id}")
            embeddings.append(vec)
            documents.append(p.name)
            metadatas.append({
                "product_id": p.id,
                "name": p.name,
                "description": p.description or "",
                "price": p.price or 0.0,
                "tag": p.tag or "General",
                "shop_id": p.shop_id,
                "shop_name": shop.name if shop else "Unknown",
                "shop_address": shop.address if shop else "Unknown",
            })

        # Insert to ChromaDB
        # Using batching to prevent large upload limits if any
        batch_size = 200
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            product_images.upsert(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx],
                documents=documents[i:end_idx]
            )
            print(f"Synced batch [{i}-{end_idx}] to ChromaDB.")

        print(f"\nSuccessfully synced {len(ids)} 768-dim image vectors to ChromaDB!")

    except Exception as e:
        print(f"Sync error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sync_768_vectors()
