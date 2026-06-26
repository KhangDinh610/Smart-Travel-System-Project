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
from vector_db import vector_db
from visual_search import ImageVectorExtractor

def test_accuracy():
    db = SessionLocal()
    try:
        # Get a product that has been successfully updated with 768-dim vector
        product = db.query(Product).filter(Product.id == 1).first()
        if not product:
            print("Product ID 1 not found.")
            return

        safe_target_name = product.name.encode('ascii', 'ignore').decode('ascii')
        print(f"Target Product for search: ID={product.id}, Name='{safe_target_name}'")
        print(f"Image URL: {product.image_url}")

        print("Initializing CLIP model...")
        extractor = ImageVectorExtractor()
        if not extractor.loaded:
            print("CLIP model not loaded.")
            return

        # Download target image
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(product.image_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Could not download target image. HTTP status {response.status_code}")
            return

        # Extract vector from downloaded image
        image = extractor.load_image(io.BytesIO(response.content))
        processed = extractor.preprocess_image(image)
        query_vector = extractor.extract_vector(processed).tolist()

        # Query ChromaDB collection
        print("\nQuerying ChromaDB 'product_images'...")
        results = vector_db.query(
            query_embeddings=[query_vector],
            n_results=5,
            collection_name="product_images"
        )

        print("\nSearch results:")
        if results and results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                meta = results["metadatas"][0][i]
                dist = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
                score = 1.0 - dist
                prod_id = meta.get("product_id")
                prod_name = meta.get("name")
                # Remove non-ascii characters for printing
                safe_name = prod_name.encode('ascii', 'ignore').decode('ascii')
                print(f"{i+1}. Product ID: {prod_id}, Name: '{safe_name}', Similarity Score: {score:.4f} (Cosine Distance: {dist:.4f})")
        else:
            print("No matches found.")

    except Exception as e:
        print(f"Test error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_accuracy()
