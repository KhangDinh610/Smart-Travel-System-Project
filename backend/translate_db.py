import os
import sys
import time
import json
import asyncio

# Ensure UTF-8 encoding for stdout and stderr to prevent UnicodeEncodeError in Windows terminals
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

# Add base directory to path so we can import local modules
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from database import SessionLocal, Product
from ai_service import gemini_service

async def translate_all():
    db = SessionLocal()
    products = db.query(Product).filter((Product.name_en == None) | (Product.name_en == "")).all()
    print(f"Found {len(products)} products to translate.")
    
    count = 0
    for p in products:
        print(f"[{count+1}/{len(products)}] Translating: {p.name}")
        prompt = (
            f"Translate the following Vietnamese product details into natural English for a shopping app.\n"
            f"Name: {p.name}\n"
            f"Description: {p.description or ''}\n"
            f"Format strictly as JSON: {{\"name_en\": \"...\", \"description_en\": \"...\"}}"
        )
        try:
            resp = await gemini_service.get_chat_response(prompt)
            if resp and not resp.startswith("Error"):
                # Clean markdown blocks if returned
                clean_json = resp.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)
                p.name_en = data.get("name_en", p.name)
                p.description_en = data.get("description_en", p.description)
                db.commit()
                print(f" -> Success: {p.name_en}")
            else:
                print(f" -> Failed: {resp}")
        except Exception as e:
            print(f" -> Error: {e}")
            db.rollback()
            
        count += 1
        # Sleep for 1.2 seconds to respect rate limits (50 RPM for Gemini Flash)
        await asyncio.sleep(1.2)
        
    db.close()
    print("Translation completed!")

if __name__ == "__main__":
    asyncio.run(translate_all())
