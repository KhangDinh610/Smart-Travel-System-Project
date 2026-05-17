import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore
import os

def migrate():
    # Initialize Firebase
    cred_path = os.path.join('backend', 'serviceAccountKey.json')
    if not os.path.exists(cred_path):
        print(f"Error: {cred_path} not found.")
        return

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db_fs = firestore.client()

    # Connect to SQLite
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Migrate Shops
    print("Migrating Shops...")
    cursor.execute("SELECT id, name, address, latitude, longitude FROM shops")
    shops = cursor.fetchall()
    
    batch = db_fs.batch()
    count = 0
    for shop in shops:
        s_id, name, address, lat, lng = shop
        doc_ref = db_fs.collection("shops").document(str(s_id))
        batch.set(doc_ref, {
            "name": name,
            "address": address,
            "latitude": lat,
            "longitude": lng
        })
        count += 1
        if count % 500 == 0:
            batch.commit()
            batch = db_fs.batch()
    batch.commit()
    print(f"Migrated {count} shops.")

    # Migrate Products
    print("Migrating Products...")
    cursor.execute("SELECT id, name, description, vector_json, shop_id FROM products")
    products = cursor.fetchall()

    batch = db_fs.batch()
    count = 0
    for prod in products:
        p_id, name, desc, vector, shop_id = prod
        doc_ref = db_fs.collection("products").document(str(p_id))
        batch.set(doc_ref, {
            "name": name,
            "description": desc,
            "vector_json": vector,
            "shop_id": shop_id
        })
        count += 1
        if count % 500 == 0:
            batch.commit()
            batch = db_fs.batch()
            print(f"Uploaded {count} products...")
    batch.commit()
    print(f"Migrated {count} products.")

    conn.close()
    print("Migration to Firestore completed successfully.")

if __name__ == "__main__":
    migrate()
