from scrapling.fetchers import Fetcher
from database import SessionLocal, Shop, Product, init_db
from vector_db import vector_db
import json
import re

def clean_price(price_str):
    if not price_str:
        return 0.0
    # Extract digits
    digits = re.sub(r'[^\d]', '', price_str)
    return float(digits) if digits else 0.0

def run_scraper():
    # Ensure database tables are created
    init_db()
    
    print("Starting full scraper for Gốm Sứ Bát Tràng...")
    page = Fetcher.get('https://gomsubattrang.vn/')
    if page.status != 200:
        print(f"Failed to fetch page: {page.status}")
        return

    db = SessionLocal()
    try:
        # 1. Create/Get Shop
        shop = db.query(Shop).filter(Shop.name == "Gốm Sứ Bát Tràng").first()
        if not shop:
            shop = Shop(
                name="Gốm Sứ Bát Tràng",
                address="Bát Tràng, Gia Lâm, Hà Nội"
            )
            db.add(shop)
            db.commit()
            db.refresh(shop)
            print(f"Created shop: {shop.name}")

        # 2. Scrape Products
        containers = page.css('.product-container')
        print(f"Found {len(containers)} products on page")

        for i, container in enumerate(containers):
            try:
                name = container.css('.product-name a::text').get()
                if not name:
                    name = container.css('.product-name::text').get()
                
                # Image
                image_url = container.css('img::attr(src)').get()
                if image_url and not image_url.startswith('http'):
                    image_url = "https://gomsubattrang.vn" + image_url

                # Price
                all_text = container.get_all_text()
                price_match = re.search(r'([\d.,]+)\s*[đ|VND]', all_text)
                price_str = price_match.group(0) if price_match else "0"
                price = clean_price(price_str)

                if not name:
                    continue

                name = name.strip()

                # 3. Save to SQLite
                new_product = Product(
                    name=name,
                    description=f"Sản phẩm gốm sứ Bát Tràng cao cấp: {name}",
                    price=price,
                    image_url=image_url,
                    category="Gốm sứ",
                    tag="Traditional",
                    shop_id=shop.id
                )
                db.add(new_product)
                db.commit()
                db.refresh(new_product)

                # 4. Generate Embedding and Save to ChromaDB
                # Combine name and description for better context
                text_to_embed = f"{name}. {new_product.description}"
                embedding = vector_db.default_embedding_fn([text_to_embed])[0].tolist()
                
                # Update SQLite with vector_json
                new_product.vector_json = json.dumps(embedding)
                db.commit()

                # Add to ChromaDB
                vector_db.add_documents(
                    ids=[f"prod_{new_product.id}"],
                    documents=[text_to_embed],
                    metadatas=[{
                        "product_id": new_product.id,
                        "name": name,
                        "price": price,
                        "shop_id": shop.id,
                        "shop_name": shop.name,
                        "image_url": image_url
                    }]
                )
                
                if i % 10 == 0:
                    print(f"Processed {i+1}/{len(containers)} products...")

            except Exception as e:
                print(f"Error processing product {i}: {e}")
                db.rollback()

        print("Scraping and data insertion complete.")

    finally:
        db.close()

if __name__ == "__main__":
    run_scraper()
