import os
import sys
import json
import csv
import re
import asyncio
import pandas as pd

# Reconfigure stdout and stderr to handle UTF-8 printing in Windows terminal
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Add current, scratch, and parent directories to PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


from database import SessionLocal, Shop, Product, init_db
from ai_service import gemini_service
from translation_utils import smart_translate_name
from vector_db import vector_db

def clean_price(price_str):
    if not price_str:
        return 0.0
    # Extract digits only
    digits = re.sub(r'[^\d]', '', str(price_str))
    return float(digits) if digits else 0.0

def guess_category(name):
    name_lower = name.lower()
    if any(kw in name_lower for kw in ['trà', 'tea', 'cà phê', 'coffee', 'chè', 'sâm dứa', 'hoalài', 'lài']):
        return 'Trà & Cà phê'
    elif any(kw in name_lower for kw in ['bánh', 'kẹo', 'mứt', 'hạt', 'khô', 'tôm', 'mắm', 'đặc sản', 'ẩm thực', 'ăn vặt', 'giò', 'chả', 'ruốc', 'mè xửng', 'lạp xưởng', 'xoài', 'dừa']):
        return 'Đặc sản ẩm thực'
    elif any(kw in name_lower for kw in ['mỹ nghệ', 'gốm', 'sứ', 'đồng', 'tre', 'mây', 'tranh', 'tượng', 'đèn', 'thủ công', 'chitt', 'gỗ', 'đèn gỗ', 'decor', 'thêu']):
        return 'Thủ công mỹ nghệ'
    else:
        return 'Quà lưu niệm'

def guess_tag(name):
    name_lower = name.lower()
    if any(kw in name_lower for kw in ['trà', 'tea', 'cà phê', 'coffee']):
        return 'Tea'
    elif any(kw in name_lower for kw in ['bánh', 'kẹo', 'mứt', 'hạt', 'khô', 'tôm', 'mắm']):
        return 'Food'
    elif any(kw in name_lower for kw in ['gốm', 'sứ', 'đồng', 'tre', 'mây', 'tranh', 'tượng', 'đèn', 'mỹ nghệ']):
        return 'Handicrafts'
    else:
        return 'Souvenir'

async def generate_products_for_shop(shop_name, shop_link, shop_address):
    """
    Query Gemini to generate 10 realistic products for a shop based on its name and link.
    """
    prompt = f"""
Bạn là một chuyên gia về đặc sản và quà lưu niệm Việt Nam.
Tôi có một cửa hàng sau:
Tên cửa hàng: {shop_name}
Link website: {shop_link}
Địa chỉ: {shop_address}

Dựa vào thông tin tên cửa hàng và link website, hãy đề xuất 10 sản phẩm đặc trưng nhất mà cửa hàng này bán.
Với mỗi sản phẩm, hãy tạo các thông tin đầy đủ sau đây:
1. name: Tên tiếng Việt của sản phẩm (ví dụ: 'Mè xửng Thiên Hương loại đặc biệt')
2. name_en: Tên tiếng Anh của sản phẩm (ví dụ: 'Thien Huong Special Sesame Candy')
3. description: Mô tả chi tiết tiếng Việt về sản phẩm (thành phần, hương vị, ý nghĩa, khoảng 1-2 câu)
4. description_en: Mô tả chi tiết tiếng Anh của sản phẩm (khoảng 1-2 câu)
5. price: Giá tiền ước lượng phù hợp bằng tiền VNĐ (kiểu float, ví dụ: 45000.0)
6. tag: Thẻ phân loại tiếng Anh (ví dụ: 'Food', 'Tea', 'Handicrafts', 'Traditional', 'Souvenir')
7. category: Danh mục tiếng Việt (chọn một trong các danh mục: 'Đặc sản ẩm thực', 'Trà & Cà phê', 'Thủ công mỹ nghệ', 'Quà lưu niệm')
8. image_url: Một link ảnh minh họa giả định phù hợp (ví dụ: một link ảnh từ Unsplash như https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80 hoặc tương tự)

Hãy trả về kết quả dưới dạng một mảng JSON duy nhất chứa 10 đối tượng sản phẩm. 
Không thêm bất kỳ chữ nào khác ngoài mã nguồn JSON (không dùng markdown block ```json ... ```, chỉ trả về chuỗi JSON thô để có thể load trực tiếp bằng json.loads()).
"""
    # Fallbacks for specific shops to bypass Gemini daily limit exhaustion
    if "hương việt" in shop_name.lower():
        return [
            {
                "name": "Kẹo dừa Bến Tre truyền thống",
                "name_en": "Traditional Ben Tre Coconut Candy",
                "description": "Đặc sản nổi tiếng miền Tây, dẻo ngọt, thơm béo vị nước cốt dừa tự nhiên hòa quyện mạch nha.",
                "description_en": "Famous Western Vietnam specialty, chewy and sweet, featuring rich natural coconut milk blended with malt.",
                "price": 45000.0,
                "tag": "Food, Traditional",
                "category": "Đặc sản ẩm thực",
                "image_url": "https://images.unsplash.com/photo-1627964402688-2947f6d226a6?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Bánh pía sầu riêng trứng muối Sóc Trăng",
                "name_en": "Soc Trang Durian Pia Cake with Salted Egg",
                "description": "Bánh pía mềm mịn, nhân sầu riêng tươi thơm phức kết hợp với lòng đỏ trứng muối bùi béo đặc trưng.",
                "description_en": "Soft and smooth pia cake with fragrant fresh durian filling combined with rich salted egg yolk.",
                "price": 75000.0,
                "tag": "Food, Traditional",
                "category": "Đặc sản ẩm thực",
                "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Hạt sen sấy giòn ăn liền Tịnh Tâm",
                "name_en": "Tinh Tam Crispy Dried Lotus Seeds",
                "description": "Hạt sen chọn lọc từ hồ sen Tịnh Tâm Huế, sấy giòn tự nhiên, vị bùi ngọt thanh, giàu dinh dưỡng.",
                "description_en": "Selected lotus seeds from Tinh Tam Lake in Hue, naturally dried and crispy, offering a sweet nutty taste.",
                "price": 95000.0,
                "tag": "Food, Healthy",
                "category": "Đặc sản ẩm thực",
                "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Mực rim me Nha Trang ăn liền",
                "name_en": "Nha Trang Sweet & Sour Tamarind Squid",
                "description": "Mực khô phơi một nắng xé nhỏ rim cùng nước cốt me chua ngọt, ớt cay nồng, thích hợp ăn vặt.",
                "description_en": "Sun-dried squid simmered in sweet and sour tamarind sauce with spicy chili, perfect for snacking.",
                "price": 85000.0,
                "tag": "Food, Seafood",
                "category": "Đặc sản ẩm thực",
                "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Trà lài đặc sản Bảo Lộc Lâm Đồng",
                "name_en": "Bao Loc Premium Jasmine Tea",
                "description": "Lá trà xanh Bảo Lộc ướp hương hoa lài tự nhiên thơm mát, vị chát dịu hậu ngọt thanh tao.",
                "description_en": "Bao Loc green tea leaves infused with natural jasmine scent, presenting a mild astringency and sweet finish.",
                "price": 60000.0,
                "tag": "Tea, Traditional",
                "category": "Trà & Cà phê",
                "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Bánh phồng sữa sầu riêng Miền Tây",
                "name_en": "Western Durian Milk Rice Paper",
                "description": "Bánh phồng sữa mềm dẻo, thơm ngậy vị sữa dừa và sầu riêng, món ăn vặt mộc mạc Nam Bộ.",
                "description_en": "Soft and chewy milk rice paper with rich coconut milk and durian flavor, a simple Southern snack.",
                "price": 35000.0,
                "tag": "Food, Sweet",
                "category": "Đặc sản ẩm thực",
                "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Cơm cháy chà bông siêu ruốc Sài Gòn",
                "name_en": "Saigon Crispy Rice Paper with Pork Floss",
                "description": "Cơm cháy chiên giòn rụm phủ lớp nước mắm ớt và chà bông heo dày đặc, đậm đà khó cưỡng.",
                "description_en": "Crispy fried rice crust topped with thick pork floss and chili fish sauce, highly savory and delicious.",
                "price": 65000.0,
                "tag": "Food, Snack",
                "category": "Đặc sản ẩm thực",
                "image_url": "https://images.unsplash.com/photo-1579758629938-03607ccdbaba?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Mứt gừng Huế dẻo cay thơm nồng",
                "name_en": "Hue Chewy Spicy Ginger Jam",
                "description": "Mứt gừng truyền thống làm từ củ gừng non xứ Huế, vị cay nồng ấm, ngọt dịu phù hợp ngày Tết.",
                "description_en": "Traditional ginger jam made from young Hue ginger, offering a warm spicy flavor and gentle sweetness.",
                "price": 50000.0,
                "tag": "Food, Sweet",
                "category": "Đặc sản ẩm thực",
                "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Hạt điều rang muối vỏ lụa Bình Phước",
                "name_en": "Binh Phuoc Roasted Cashews with Salt",
                "description": "Hạt điều Bình Phước loại A rang củi muối giữ nguyên vỏ lụa, giòn tan, vị bùi béo đậm đà.",
                "description_en": "Grade-A Binh Phuoc cashews wood-roasted with salt, keeping their skin, crispy and rich.",
                "price": 120000.0,
                "tag": "Food, Healthy",
                "category": "Đặc sản ẩm thực",
                "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Khô bò sợi lá chanh đặc sản Tây Nguyên",
                "name_en": "Central Highlands Shredded Beef Jerky with Lime Leaves",
                "description": "Thịt bò tươi tẩm ướp gia vị sấy khô, xé sợi trộn lá chanh sấy thơm nồng, cay ngọt hài hòa.",
                "description_en": "Dried beef seasoned and shredded, mixed with fragrant lime leaves, presenting a spicy and sweet harmony.",
                "price": 150000.0,
                "tag": "Food, Meat",
                "category": "Đặc sản ẩm thực",
                "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"
            }
        ]

    if "craft house" in shop_name.lower():
        return [
            {
                "name": "Nến thơm tinh dầu tự nhiên đúc tay",
                "name_en": "Hand-poured Scented Soy Candle",
                "description": "Nến thơm làm từ sáp đậu nành thiên nhiên hòa quyện tinh dầu hoa nhài và gỗ thông ấm áp, thư giãn.",
                "description_en": "Handcrafted soy wax candle infused with jasmine and pine wood essential oils, warm and relaxing.",
                "price": 180000.0,
                "tag": "Decor, Souvenir",
                "category": "Quà lưu niệm",
                "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Bao hộ chiếu da bò thật khắc tên",
                "name_en": "Custom Engraved Leather Passport Holder",
                "description": "Bao hộ chiếu khâu tay từ da bò thật cao cấp, thiết kế tối giản, hỗ trợ khắc tên cá nhân theo yêu cầu.",
                "description_en": "Hand-stitched premium leather passport holder, minimalist design, supporting custom name engraving.",
                "price": 250000.0,
                "tag": "Leather, Souvenir",
                "category": "Quà lưu niệm",
                "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Túi tote vải canvas thêu họa tiết Việt Nam",
                "name_en": "Embroidered Canvas Tote Bag",
                "description": "Túi vải canvas dày dặn, thêu tay hình nón lá và hoa sen tinh tế, thời trang và tiện dụng.",
                "description_en": "Thick canvas tote bag featuring delicate hand-embroidered lotus and leaf hat, stylish and practical.",
                "price": 120000.0,
                "tag": "Fashion, Souvenir",
                "category": "Quà lưu niệm",
                "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Bộ ống hút tre tự nhiên thân thiện môi trường",
                "name_en": "Eco-friendly Bamboo Straw Set",
                "description": "Gồm 5 ống hút tre tự nhiên, 1 cọ rửa xơ dừa đựng trong túi vải canvas xinh xắn, tái sử dụng nhiều lần.",
                "description_en": "Includes 5 natural bamboo straws, 1 coconut brush in a lovely canvas pouch, reusable and eco-friendly.",
                "price": 45000.0,
                "tag": "Eco, Souvenir",
                "category": "Quà lưu niệm",
                "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Lót ly gỗ sồi khắc họa tiết trống đồng",
                "name_en": "Oak Coasters with Dong Son Drum Pattern",
                "description": "Bộ 4 miếng lót ly làm từ gỗ sồi tự nhiên, khắc laser họa tiết trống đồng Đông Sơn tinh xảo.",
                "description_en": "Set of 4 natural oak wood coasters laser-engraved with delicate Dong Son drum patterns.",
                "price": 90000.0,
                "tag": "Decor, Wood",
                "category": "Thủ công mỹ nghệ",
                "image_url": "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Móc khóa da bò handmade khâu tay",
                "name_en": "Handmade Hand-stitched Leather Keychain",
                "description": "Móc khóa làm từ da sáp bò thật khâu tay chữ thập tỉ mỉ, độ bền cao, phong cách bụi bặm cá tính.",
                "description_en": "Keychain made of hand-stitched pull-up cowhide, highly durable, showcasing a rugged personal style.",
                "price": 55000.0,
                "tag": "Leather, Souvenir",
                "category": "Quà lưu niệm",
                "image_url": "https://images.unsplash.com/photo-1582139329536-e7284fece509?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Sổ tay bìa gỗ khắc laser phong cảnh Việt Nam",
                "name_en": "Laser-engraved Wood Cover Notebook",
                "description": "Sổ tay độc đáo với bìa làm bằng gỗ vân tre tự nhiên khắc hình Vịnh Hạ Long, ruột giấy kraft bảo vệ mắt.",
                "description_en": "Unique notebook with natural bamboo wood cover laser-etched with Halong Bay, containing eye-friendly kraft pages.",
                "price": 150000.0,
                "tag": "Wood, Souvenir",
                "category": "Quà lưu niệm",
                "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Xà bông sinh dược thảo dược tự nhiên",
                "name_en": "Natural Herbal Spa Soap",
                "description": "Xà bông tắm thảo dược làm từ dầu dừa và các vị thuốc Nam như mướp đắng, bạc hà, mật ong, tốt cho da.",
                "description_en": "Herbal soap made from coconut oil and traditional Vietnamese herbs like bitter melon, mint, and honey.",
                "price": 40000.0,
                "tag": "Healthy, Souvenir",
                "category": "Quà lưu niệm",
                "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Tranh vẽ tay phong cảnh phố cổ Hà Nội",
                "name_en": "Hand-painted Hanoi Old Quarter Canvas",
                "description": "Bức tranh acrylic vẽ tay thu nhỏ tái hiện khung cảnh phố cổ Hà Nội bình yên, mộc mạc làm kỷ niệm.",
                "description_en": "Miniature hand-painted acrylic painting capturing the peaceful, simple Hanoi Old Quarter landscape.",
                "price": 320000.0,
                "tag": "Art, Souvenir",
                "category": "Thủ công mỹ nghệ",
                "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Bộ postcard danh lam thắng cảnh Việt Nam",
                "name_en": "Vietnam Scenic Landmark Postcard Set",
                "description": "Hộp gồm 12 tấm bưu thiếp vẽ minh họa màu nước các danh lam thắng cảnh Hà Nội, Huế, Hội An, Sài Gòn.",
                "description_en": "Box set of 12 watercolor-illustrated postcards depicting landmarks of Hanoi, Hue, Hoi An, and Saigon.",
                "price": 50000.0,
                "tag": "Art, Souvenir",
                "category": "Quà lưu niệm",
                "image_url": "https://images.unsplash.com/photo-1579783928591-724f1a172ddb?auto=format&fit=crop&w=500&q=80"
            }
        ]

    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = await gemini_service.get_chat_response(prompt)
            if resp:
                # Clean up potential markdown formatting
                clean_json = resp.replace("```json", "").replace("```", "").strip()
                products = json.loads(clean_json)
                if isinstance(products, list) and len(products) > 0:
                    return products
            print(f"[{shop_name}] Attempt {attempt+1} failed to yield valid JSON. Retrying...")
            await asyncio.sleep(2)
        except Exception as e:
            error_str = str(e)
            print(f"[{shop_name}] Error on attempt {attempt+1}: {error_str}")
            if "429" in error_str or "quota" in error_str.lower() or "limit" in error_str.lower() or "exhausted" in error_str.lower():
                print(f"[{shop_name}] Rate limit (429) detected. Sleeping for 65 seconds to reset quota...")
                await asyncio.sleep(65)
            else:
                await asyncio.sleep(2)
    return []

async def process_phuc_minh_shops(db, shop_link_map):
    """
    Process Phuc and Minh's shops list.
    """
    shops_file = 'scratch/shops_to_scrape.json'
    if not os.path.exists(shops_file):
        print(f"Error: {shops_file} not found. Please run prepare_shops.py first.")
        return

    with open(shops_file, 'r', encoding='utf-8') as f:
        shops_data = json.load(f)

    print(f"Found {len(shops_data)} unique shops from Phuc & Minh's lists.")

    for i, s_data in enumerate(shops_data):
        shop_name = s_data['name']
        shop_link = s_data['link']
        shop_address = s_data['address']

        # Store in link map
        shop_link_map[shop_name] = shop_link

        # 1. Ensure Shop exists in DB
        shop = db.query(Shop).filter(Shop.name == shop_name).first()
        if not shop:
            shop = Shop(name=shop_name, address=shop_address)
            db.add(shop)
            db.commit()
            db.refresh(shop)
            print(f"[{i+1}/{len(shops_data)}] Created shop: {shop_name}")
        else:
            print(f"[{i+1}/{len(shops_data)}] Shop already exists: {shop_name}")

        # 2. Check if products already exist for this shop
        existing_products_count = db.query(Product).filter(Product.shop_id == shop.id).count()
        if existing_products_count > 0:
            print(f" -> Shop already has {existing_products_count} products. Skipping generation.")
            continue

        # 3. Generate products via Gemini
        print(f" -> Generating products for {shop_name} via Gemini...")
        gemini_products = await generate_products_for_shop(shop_name, shop_link, shop_address)
        if not gemini_products:
            print(f" -> Failed to generate products for {shop_name}")
            continue

        print(f" -> Successfully generated {len(gemini_products)} products. Inserting into SQLite...")
        for p_data in gemini_products:
            try:
                name = p_data.get('name', '').strip()
                if not name:
                    continue

                # Clean price
                price = float(p_data.get('price', 0))

                tag = p_data.get('tag', 'Souvenir')
                if isinstance(tag, list):
                    tag = ", ".join(str(t) for t in tag)
                elif not isinstance(tag, str):
                    tag = str(tag)

                category = p_data.get('category', 'Quà lưu niệm')
                if isinstance(category, list):
                    category = ", ".join(str(c) for c in category)
                elif not isinstance(category, str):
                    category = str(category)

                product = Product(
                    name=name,
                    name_en=p_data.get('name_en', smart_translate_name(name)),
                    description=p_data.get('description', ''),
                    description_en=p_data.get('description_en', ''),
                    price=price,
                    tag=tag,
                    category=category,
                    image_url=p_data.get('image_url', ''),
                    shop_id=shop.id
                )
                db.add(product)
                db.commit()
                db.refresh(product)

                # Compute embedding
                text_to_embed = f"{product.name}. {product.description or ''}"
                embedding = vector_db.default_embedding_fn([text_to_embed])[0].tolist()
                product.vector_json = json.dumps(embedding)
                db.commit()

            except Exception as pe:
                print(f"   -> Error inserting product: {pe}")
                db.rollback()

        # Respect API Rate limit (50 RPM for free tier Gemini-2.5-flash)
        await asyncio.sleep(1.5)

def process_khoa_shops(db, shop_link_map):
    """
    Process Khoa's CSV files.
    """
    print("\nProcessing Khoa's CSV files...")
    
    khoa_products = []
    seen = set()
    
    for filename in ['khoa.csv', 'khoa2.csv']:
        if not os.path.exists(filename):
            print(f"Warning: {filename} not found.")
            continue
        try:
            df = pd.read_csv(filename)
            for idx, row in df.iterrows():
                shop_name = str(row['Tên Shop']).strip() if pd.notna(row['Tên Shop']) else ''
                prod_name = str(row['Tên Sản Phẩm']).strip() if pd.notna(row['Tên Sản Phẩm']) else ''
                if not shop_name or not prod_name or shop_name.lower() == 'nan' or prod_name.lower() == 'nan':
                    continue
                
                key = (shop_name.lower(), prod_name.lower())
                if key in seen:
                    continue
                seen.add(key)
                
                address = str(row['Địa Chỉ Shop']).strip() if pd.notna(row['Địa Chỉ Shop']) else ''
                link = str(row['Link Website / Link Shop']).strip() if pd.notna(row['Link Website / Link Shop']) else ''
                price_str = str(row['Giá Cả']).strip() if pd.notna(row['Giá Cả']) else '0'
                desc = str(row['Mô Tả Sản Phẩm']).strip() if pd.notna(row['Mô Tả Sản Phẩm']) else ''
                image_url = str(row['Link Hình Ảnh']).strip() if pd.notna(row['Link Hình Ảnh']) else ''
                
                # Check link to add to mapping
                if link and shop_name not in shop_link_map:
                    shop_link_map[shop_name] = link
                
                khoa_products.append({
                    "shop_name": shop_name,
                    "shop_address": address,
                    "shop_link": link,
                    "product_name": prod_name,
                    "price_str": price_str,
                    "description": desc,
                    "image_url": image_url
                })
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    print(f"Loaded {len(khoa_products)} unique products from Khoa's files.")
    
    # Insert into SQLite
    success_count = 0
    skipped_count = 0
    
    for i, p_data in enumerate(khoa_products):
        shop_name = p_data['shop_name']
        shop_address = p_data['shop_address']
        prod_name = p_data['product_name']
        price = clean_price(p_data['price_str'])
        desc = p_data['description']
        image_url = p_data['image_url']
        
        # 1. Ensure Shop exists
        shop = db.query(Shop).filter(Shop.name == shop_name).first()
        if not shop:
            shop = Shop(name=shop_name, address=shop_address if shop_address and shop_address.lower() != 'n/a' else '')
            db.add(shop)
            db.commit()
            db.refresh(shop)
            
        # 2. Ensure Product doesn't exist
        existing_prod = db.query(Product).filter(Product.shop_id == shop.id, Product.name == prod_name).first()
        if existing_prod:
            skipped_count += 1
            continue
            
        # 3. Create Product
        try:
            # Local translation fallback
            name_en = smart_translate_name(prod_name)
            tag = guess_tag(prod_name)
            category = guess_category(prod_name)
            
            product = Product(
                name=prod_name,
                name_en=name_en,
                description=desc,
                description_en='',
                price=price,
                tag=tag,
                category=category,
                image_url=image_url,
                shop_id=shop.id
            )
            db.add(product)
            db.commit()
            db.refresh(product)
            
            # Compute embedding
            text_to_embed = f"{product.name}. {product.description or ''}"
            embedding = vector_db.default_embedding_fn([text_to_embed])[0].tolist()
            product.vector_json = json.dumps(embedding)
            db.commit()
            
            success_count += 1
            if success_count % 100 == 0:
                print(f" -> Inserted {success_count}/{len(khoa_products)} Khoa products...")
                
        except Exception as pe:
            print(f"Error inserting Khoa product {prod_name}: {pe}")
            db.rollback()
            
    print(f"Finished Khoa's products: {success_count} inserted, {skipped_count} skipped (duplicates).")

def export_all_to_csv(db, shop_link_map):
    """
    Export all products and their shops in the SQLite database to a single CSV.
    """
    print("\nExporting all database products to all_products.csv...")
    try:
        products = db.query(Product).all()
        if not products:
            print("No products found in database to export.")
            return

        file_path = os.path.join(PARENT_DIR, 'all_products.csv')
        
        headers = [
            'STT', 
            'Tên Shop', 
            'Địa Chỉ Shop', 
            'Link Website / Link Shop', 
            'Tên Sản Phẩm', 
            'Tên Sản Phẩm (Tiếng Anh)', 
            'Giá Cả', 
            'Mô Tả Sản Phẩm', 
            'Mô Tả Sản Phẩm (Tiếng Anh)', 
            'Tag', 
            'Category', 
            'Link Hình Ảnh'
        ]

        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            
            for idx, product in enumerate(products):
                shop = db.query(Shop).filter(Shop.id == product.shop_id).first()
                shop_name = shop.name if shop else "Unknown"
                shop_address = shop.address if shop else "Unknown"
                
                # Fetch link from link map
                shop_link = shop_link_map.get(shop_name, '')
                if not shop_link and shop_name == 'Gốm Sứ Bát Tràng':
                    shop_link = 'https://gomsubattrang.vn/'
                
                writer.writerow({
                    'STT': idx + 1,
                    'Tên Shop': shop_name,
                    'Địa Chỉ Shop': shop_address,
                    'Link Website / Link Shop': shop_link,
                    'Tên Sản Phẩm': product.name,
                    'Tên Sản Phẩm (Tiếng Anh)': product.name_en or '',
                    'Giá Cả': product.price,
                    'Mô Tả Sản Phẩm': product.description or '',
                    'Mô Tả Sản Phẩm (Tiếng Anh)': product.description_en or '',
                    'Tag': product.tag or 'Souvenir',
                    'Category': product.category or 'Quà lưu niệm',
                    'Link Hình Ảnh': product.image_url or ''
                })
                
        print(f"Successfully exported {len(products)} products to {file_path}")

    except Exception as e:
        print(f"Error exporting to CSV: {e}")

async def main():
    init_db()
    db = SessionLocal()
    
    # Store mappings for shop links to output in the CSV
    shop_link_map = {}
    
    # Pre-populate Gốm Sứ Bát Tràng link
    shop_link_map['Gốm Sứ Bát Tràng'] = 'https://gomsubattrang.vn/'
    
    try:
        # Part 1: Process Phuc & Minh's shops
        await process_phuc_minh_shops(db, shop_link_map)
        
        # Part 2: Process Khoa's shops
        process_khoa_shops(db, shop_link_map)
        
        # Part 3: Export all database content to CSV
        export_all_to_csv(db, shop_link_map)
        
        # Part 4: Sync SQLite to ChromaDB
        print("\nSyncing everything to ChromaDB...")
        from api_contract import sync_db_to_vector
        sync_db_to_vector()
        print("Sync complete.")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
