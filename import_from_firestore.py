import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys
import json
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from database import SessionLocal, Shop, Product, init_db
from vector_db import vector_db

def import_data():
    # 1. Initialize Firebase
    cred_path = os.path.join('backend', 'serviceAccountKey.json')
    if not os.path.exists(cred_path):
        print(f"Error: {cred_path} not found. Please place your serviceAccountKey.json in the backend folder.")
        return

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    db_fs = firestore.client()
    
    # 2. Initialize Local DB
    print("Initializing local database...")
    init_db()
    db_local = SessionLocal()

    # 3. Import Shops
    print("Fetching shops from Firestore...")
    shops_ref = db_fs.collection("shops").stream()
    shop_count = 0
    for doc in shops_ref:
        data = doc.to_dict()
        s_id = int(doc.id)
        
        # Check if shop exists
        existing = db_local.query(Shop).filter(Shop.id == s_id).first()
        if not existing:
            shop = Shop(
                id=s_id,
                name=data.get("name"),
                address=data.get("address"),
                latitude=data.get("latitude"),
                longitude=data.get("longitude")
            )
            db_local.add(shop)
            shop_count += 1
    
    db_local.commit()
    print(f"Imported {shop_count} shops.")

    # 4. Import Products
    print("Fetching products from Firestore...")
    products_ref = db_fs.collection("products").stream()
    prod_count = 0
    
    # Batch data for ChromaDB
    chroma_ids = []
    chroma_embeddings = []
    chroma_metadatas = []
    chroma_docs = []
    
    # Text data for ChromaDB (default collection)
    text_ids = []
    text_docs = []
    text_metas = []

    for doc in products_ref:
        data = doc.to_dict()
        p_id = int(doc.id)
        
        # Save to SQLite
        existing = db_local.query(Product).filter(Product.id == p_id).first()
        if not existing:
            product = Product(
                id=p_id,
                name=data.get("name"),
                description=data.get("description"),
                price=data.get("price", 0.0),
                vector_json=data.get("vector_json"),
                shop_id=data.get("shop_id")
            )
            db_local.add(product)
            prod_count += 1
            
            # Prepare for ChromaDB Image Collection (if vector exists)
            vector_json = data.get("vector_json")
            if vector_json and vector_json != "[]":
                try:
                    vector = json.loads(vector_json)
                    if isinstance(vector, list) and len(vector) > 0:
                        chroma_ids.append(f"img_prod_{p_id}")
                        chroma_embeddings.append(vector)
                        chroma_docs.append(data.get("name"))
                        
                        # Get shop info for metadata
                        shop = db_local.query(Shop).filter(Shop.id == data.get("shop_id")).first()
                        chroma_metadatas.append({
                            "product_id": p_id,
                            "name": data.get("name"),
                            "price": data.get("price", 0.0),
                            "shop_name": shop.name if shop else "Unknown",
                            "shop_address": shop.address if shop else "Unknown"
                        })
                except:
                    pass
            
            # Prepare for ChromaDB Text Collection
            text_ids.append(f"prod_{p_id}")
            text_docs.append(f"{data.get('name')} - {data.get('description') or ''}")
            shop = db_local.query(Shop).filter(Shop.id == data.get("shop_id")).first()
            text_metas.append({
                "shop_id": data.get("shop_id"),
                "name": data.get("name"),
                "price": data.get("price", 0.0),
                "user_id": "system"
            })

    db_local.commit()
    print(f"Imported {prod_count} products to SQLite.")

    # 5. Sync to ChromaDB in batches
    if chroma_ids:
        print(f"Syncing {len(chroma_ids)} products to ChromaDB Image Collection...")
        vector_db.add_with_embeddings(
            ids=chroma_ids,
            embeddings=chroma_embeddings,
            metadatas=chroma_metadatas,
            documents=chroma_docs,
            collection_name="product_images"
        )
    
    if text_ids:
        print(f"Syncing {len(text_ids)} products to ChromaDB Text Collection...")
        # Since add_documents might not support large batches well in all environments, 
        # we do it in chunks of 100
        for i in range(0, len(text_ids), 100):
            batch_end = min(i + 100, len(text_ids))
            vector_db.add_documents(
                ids=text_ids[i:batch_end],
                documents=text_docs[i:batch_end],
                metadatas=text_metas[i:batch_end]
            )
    
    print("Firestore import and ChromaDB sync completed!")
    db_local.close()

if __name__ == "__main__":
    import_data()
