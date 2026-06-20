import os
import sys
import json
import csv
import re
import asyncio
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Reconfigure stdout and stderr to handle UTF-8 printing in Windows terminal
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Add current and parent directories to PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from database import SessionLocal, Shop, Product, init_db
from translation_utils import smart_translate_name
from vector_db import vector_db

def clean_price(price_str):
    if not price_str:
        return 0
    # Extract digits only
    digits = re.sub(r'[^\d]', '', str(price_str))
    return int(digits) if digits else 0

def map_tags_and_categories(product_name, shop_name):
    """
    Map product to default tags and categories:
    English tag -> Product.tag: "Local Food", "Handicrafts", "Fashion", "Art", "Gift Sets"
    Vietnamese tag -> Product.category: "Ẩm thực", "Thủ công", "Thời trang", "Nghệ thuật", "Quà tặng"
    """
    name_lower = product_name.lower()
    shop_lower = shop_name.lower()
    
    # 1. Art / Nghệ thuật
    if any(kw in name_lower for kw in ['tranh', 'art', 'canvas', 'poster', 'icon', 'hội họa', 'vẽ tay', 'pháp lam', 'trúc chỉ']):
        return "Art", "Nghệ thuật"
    
    # 2. Fashion / Thời trang
    elif any(kw in name_lower for kw in ['túi', 'tote', 'túi xách', 'khăn', 'lụa', 'nón', 'ví', 'da', 'bao hộ chiếu', 'móc khóa', 'quần', 'áo', 'vải', 't-shirt', 'quần áo']):
        return "Fashion", "Thời trang"
        
    # 3. Handicrafts / Thủ công
    elif any(kw in name_lower for kw in ['đồ đồng', 'gốm', 'sứ', 'mây', 'tre', 'nến', 'gỗ', 'đèn', 'thủ công', 'handmade', 'tượng', 'bát tràng', 'lọ hoa', 'bình hoa', 'khay', 'ấm chén', 'tách', 'ly sứ', 'lục bình', 'đĩa', 'bát', 'chén đĩa', 'chén', 'cốc', 'ly', 'tách trà']):
        return "Handicrafts", "Thủ công"
        
    # 4. Gift Sets / Quà tặng
    elif any(kw in name_lower for kw in ['gift', 'set quà', 'hộp quà', 'quà tặng', 'combo', 'gift set', 'lưu niệm']):
        return "Gift Sets", "Quà tặng"
        
    # 5. Fallback based on shop type
    else:
        if any(kw in shop_lower for kw in ['gốm', 'sứ', 'bát tràng', 'mỹ nghệ', 'craft', 'bamboo', 'tre', 'mây', 'mayhouse', 'lilforest', 'chitt', 'casfa', 'đồ đồng', 'đồng', 'tượng', 'nến', 'wood', 'gỗ', 'lâm']):
            return "Handicrafts", "Thủ công"
        elif any(kw in shop_lower for kw in ['art', 'tranh', 'icon', 'hội họa', 'vẽ tay', 'trúc chỉ', 'pháp lam', 'minh hoạ']):
            return "Art", "Nghệ thuật"
        elif any(kw in shop_lower for kw in ['gift', 'quà tặng', 'lưu niệm', 'futi', 'vật kỷ niệm', 'eotico', 'giftory', 'móc khoá', 'gau hottrend', 'haniga', 'sanny', 'vật kỷ']):
            return "Gift Sets", "Quà tặng"
        elif any(kw in shop_lower for kw in ['uniform', 'sports', 'wear', 'túi', 'lụa', 'khăn', 'thêu', 'tiệm in', 'sora']):
            return "Fashion", "Thời trang"
        else:
            return "Local Food", "Ẩm thực"

# Fallback catalog containing 10 real products for each of the 19 shops
FALLBACK_CATALOG = {
    "HueFood": [
        {"name": "Mè xửng dẻo Huế Food", "price": 35000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tôm chua sông Hương hảo hạng", "price": 75000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà cung đình Huế túi lọc G8", "price": 45000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mắm ruốc Huế pha sẵn hũ nhựa", "price": 30000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Dầu tràm Huế nguyên chất Hoa Nén", "price": 120000, "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"},
        {"name": "Kẹo cau Huế truyền thống", "price": 25000, "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt sen khô Tịnh Tâm đặc sản", "price": 220000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Nem chua Huế gói lá ổi", "price": 80000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tré Huế đặc sản truyền thống gói lá", "price": 85000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bưởi Thanh Trà Thủy Biều ngọt thanh", "price": 90000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"}
    ],
    "Trà Cung Đình Huế": [
        {"name": "Trà Cung Đình Huế Nhất Dạ Đế Vương G8", "price": 80000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Cung Đình Huế G9 Cao Cấp Hộp Gỗ", "price": 135000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Cung Đình Huế G10 Hộp Giấy Vàng", "price": 150000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Cung Đình Huế Túi Lọc Tiện Lợi", "price": 55000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Sâm Dứa Bảo Lộc Thơm Lài", "price": 45000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Quý Phi Đẹp Da Giữ Dáng", "price": 95000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Thảo Mộc Cung Đình Nhất Dạ Đế Vương", "price": 75000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Hoa Cúc Cung Đình Huế Thơm Ngọt", "price": 60000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Rượu Sen Xứ Huế Thơm Nồng", "price": 180000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt Sen Khô Cung Đình Huế Hộp Cao Cấp", "price": 240000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"}
    ],
    "Huế Farm": [
        {"name": "Hạt sen khô Huế Farm mộc tự nhiên", "price": 220000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà túi lọc cà gai leo Huế Farm hỗ trợ gan", "price": 65000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà vả gừng Huế Farm sấy khô uống ấm", "price": 55000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà mướp đắng sấy khô nguyên quả thái lát", "price": 70000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mứt gừng sấy dẻo Huế Farm cay ngọt", "price": 50000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Dầu tràm nguyên chất Huế Farm chai thủy tinh", "price": 130000, "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mè xửng giòn hạt điều Huế Farm", "price": 40000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bột nghệ đỏ nguyên chất Huế Farm", "price": 85000, "image_url": "https://images.unsplash.com/photo-1627964402688-2947f6d226a6?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà lài organic sấy lạnh Bảo Lộc", "price": 95000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mật ong hoa bạc hà nguyên chất hũ thủy tinh", "price": 250000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"}
    ],
    "Mộc’s Truly Hue’s": [
        {"name": "Nón lá vẽ tay phong cảnh sông Hương núi Ngự", "price": 150000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"},
        {"name": "Sổ tay bọc vải gấm họa tiết hoa sen Mộc", "price": 95000, "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80"},
        {"name": "Túi canvas vẽ tay hoa sen phong cách mộc mạc", "price": 120000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tranh sơn mài thu nhỏ phong cảnh kinh thành Huế", "price": 450000, "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bộ lót ly tre đan vẽ tay phong cảnh viền thêu", "price": 85000, "image_url": "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Đèn ngủ tre đan thủ công Mayhouse hình cầu", "price": 280000, "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khăn lụa tơ tằm dệt tay truyền thống Huế", "price": 380000, "image_url": "https://images.unsplash.com/photo-1590492804791-2a13b0c5d799?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bao hộ chiếu da khắc họa tiết nón lá thủ công", "price": 220000, "image_url": "https://images.unsplash.com/photo-1582139329536-e7284fece509?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bookmark gỗ khắc laser danh lam xứ Huế", "price": 35000, "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tranh trúc chỉ hình lá bồ đề trang trí bình an", "price": 650000, "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=500&q=80"}
    ],
    "Đặc sản Huế 24h": [
        {"name": "Mè xửng dẻo Huế 24h truyền thống", "price": 30000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà cung đình Đức Phượng Nhất Dạ Đế Vương", "price": 80000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mắm sò Lăng Cô đặc sản Huế vị chua cay", "price": 95000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Kẹo mè xửng giòn hộp giấy quà tặng Huế", "price": 35000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt sen sấy giòn ăn liền Tịnh Tâm hũ lớn", "price": 110000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tôm chua sông Hương Huế cay ngọt hũ 400g", "price": 70000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Dầu tràm nguyên chất Cung Đình Huế chai thủy tinh", "price": 140000, "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mứt củ sen sấy giòn ngào đường phèn", "price": 85000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà vả Lộc Mai Huế thái lát sấy mộc", "price": 65000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Cơm cháy chà bông chiên giòn sốt ớt cay", "price": 55000, "image_url": "https://images.unsplash.com/photo-1579758629938-03607ccdbaba?auto=format&fit=crop&w=500&q=80"}
    ],
    "Khám phá Huế": [
        {"name": "Mè Xửng Huế Đức Phượng Song Hỷ Hộp Lớn", "price": 40000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Nem Chua Huế Đặc Sản Gói Lá Chuối Truyền Thống", "price": 80000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tré Huế Gói Lá Ổi Cổ Truyền Hộp 10 Cái", "price": 85000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt Sen Tịnh Tâm Sấy Khô Nguyên Tâm Thơm Bùi", "price": 250000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Kẹo Cau Huế Truyền Thống Quà Tuổi Thơ Dân Dã", "price": 25000, "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bưởi Thanh Trà Huế Quả Tròn Ngọt Mát Đậm Đà", "price": 90000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mắm Sò Lăng Cô Chua Cay Hũ Thủy Tinh Hảo Hạng", "price": 95000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Cung Đình Nhất Dạ Đế Vương G8 Hộp Sang Trọng", "price": 150000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Vả Lộc Mai Huế Sấy Mộc Tự Nhiên Lành Tính", "price": 65000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tinh Dầu Tràm Hoa Nén Huế Chiết Xuất Tự Nhiên 100%", "price": 120000, "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"}
    ],
    "Quà Huế": [
        {"name": "Trà sen Huế thượng hạng ngâm gạo sen", "price": 160000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà vả túi lọc Lộc Mai thanh nhiệt mát gan", "price": 60000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt sen khô Tịnh Tâm Huế mộc mạc thơm bùi", "price": 240000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mứt củ sen sấy dẻo ngào đường phèn Huế", "price": 75000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tôm chua Huế Bà Duệ hảo hạng hũ 400g", "price": 65000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mè xửng dẻo Thiên Hương loại đặc biệt", "price": 32000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Dầu tràm nguyên chất Đan Viện Thiên An", "price": 145000, "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Cung Đình Nhất Dạ Đế Vương hộp giấy 250g", "price": 75000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khô cá cơm rim tỏi ớt cay mặn ngọt vị Huế", "price": 60000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Nem chua Huế gói lá chuối xách 10 cái", "price": 70000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"}
    ],
    "Tinh Hoa Huế": [
        {"name": "Mè xửng dẻo Tinh Hoa Huế gói giấy bóng", "price": 30000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà cung đình Huế Đức Phượng Nhất Dạ Đế Vương", "price": 85000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tôm chua Huế gia truyền Bà Duệ chính gốc", "price": 75000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Dầu tràm nguyên chất Cung Đình Huế Hoa Nén", "price": 130000, "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"},
        {"name": "Rượu sen Minh Mạng tửu cựu truyền xứ Huế", "price": 180000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt sen sấy giòn ăn liền Tịnh Tâm hũ tròn", "price": 95000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà vả thái lát sấy khô Lộc Mai", "price": 60000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mứt củ gừng Huế sấy khô dẻo dẻo cay cay", "price": 45000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà sâm dứa Đà Nẵng túi lọc thanh mát", "price": 50000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mực rim me Nha Trang hũ thủy tinh cay xé", "price": 90000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"}
    ],
    "Hương Việt Mart": [
        {"name": "Bánh pía sầu riêng trứng muối Tân Huê Viên 400g", "price": 75000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Kẹo dừa Bến Tre Thanh Long vị nguyên bản sáp dẻo", "price": 45000, "image_url": "https://images.unsplash.com/photo-1627964402688-2947f6d226a6?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bánh tráng sữa dừa Nhơn Hoàng giòn béo Nam Bộ", "price": 35000, "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"},
        {"name": "Lạp xưởng tôm Mai Quế Lộ nạc ít mỡ đóng túi", "price": 150000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Cơm cháy chà bông heo siêu ruốc cay nồng Sài Gòn", "price": 65000, "image_url": "https://images.unsplash.com/photo-1579758629938-03607ccdbaba?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà sâm dứa Đà Nẵng thanh lọc vị dứa mát lạnh", "price": 50000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt sen sấy chín giòn ăn liền Đồng Tháp", "price": 95000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khô bò sợi lá chanh đặc sản Tây Nguyên cay", "price": 140000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mứt gừng dẻo sấy khô cay nồng ngày Tết", "price": 45000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Lạp xưởng heo tươi Thanh Phương vị gia truyền", "price": 130000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"}
    ],
    "Ảm thực xứ Huế": [
        {"name": "Mắm ruốc Huế xào sả ớt hũ thủy tinh cay ngon", "price": 45000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tôm chua xứ Huế hũ thủy tinh Bà Duệ chính tông", "price": 80000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà vả Lộc Mai đặc sản Huế hũ thiếc sang trọng", "price": 65000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà cung đình Nhất Dạ Đế Vương Đức Phượng G8", "price": 150000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Nem chua Huế đặc sản gói lá chuối mộc mạc", "price": 90000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mè xửng dẻo Thiên Hương loại gói giấy đỏ bóng", "price": 35000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khô bò sợi lá chanh cay ngọt đặc sản Huế", "price": 130000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt sen Tịnh Tâm khô nguyên hạt dẻo thơm Huế", "price": 250000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Dầu tràm nguyên chất Đan Viện Thiên An chính gốc", "price": 145000, "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tré Huế gói lá ổi đặc sản cựu truyền miền Trung", "price": 80000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"}
    ],
    "Đặc sản Thanh Phương": [
        {"name": "Bánh pía Tân Huê Viên 4 sao Đậu Xanh Sầu Riêng", "price": 85000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bánh phồng tôm Sa Giang vị nguyên bản giòn tan", "price": 40000, "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"},
        {"name": "Kẹo dừa sáp Bến Tre dẻo béo hảo hạng", "price": 75000, "image_url": "https://images.unsplash.com/photo-1627964402688-2947f6d226a6?auto=format&fit=crop&w=500&q=80"},
        {"name": "Lạp xưởng heo tươi Thanh Phương đóng gói 500g", "price": 140000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khô cá lóc đồng miền Tây ướp tiêu ớt sấy khô", "price": 180000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mật ong nhãn Hưng Yên sáp vàng nguyên chất", "price": 150000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà sen Tây Hồ hộp giấy xanh Tiến Huệ", "price": 320000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bánh cốm Hàng Than ngọt thơm hương cốm nếp", "price": 12000, "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"},
        {"name": "Ô mai sấu xào đường muối ớt chua cay ngọt", "price": 60000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Giò lụa Ước Lễ truyền thống giòn dai hảo hạng", "price": 200000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"}
    ],
    "Đặc Sản Quê Việt": [
        {"name": "Bánh cáy Thái Bình Quê Việt giòn ngọt bùi", "price": 45000, "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"},
        {"name": "Chè lam gừng nếp thơm Quê Việt ngọt ấm", "price": 35000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt sen sấy chín giòn ăn liền gói lớn", "price": 95000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mật ong rừng Tràm Cà Mau nguyên chất sậm màu", "price": 160000, "image_url": "https://images.unsplash.com/photo-1586797813133-149bb89c6cf0?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà xanh Tân Cương Thái Nguyên túi bạc hút chân không", "price": 110000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bột sắn dây ta ướp hoa bưởi giải nhiệt tốt", "price": 90000, "image_url": "https://images.unsplash.com/photo-1627964402688-2947f6d226a6?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khô bò sợi lá chanh Tây Nguyên hộp giấy tròn", "price": 130000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Kẹo dừa Bến Tre đậu phộng sầu riêng Thanh Long", "price": 40000, "image_url": "https://images.unsplash.com/photo-1627964402688-2947f6d226a6?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tôm chua sông Hương Huế cay ngọt ngon miệng", "price": 70000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Dầu tràm nguyên chất Hoa Nén chai nhỏ giọt 50ml", "price": 125000, "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"}
    ],
    "HANIGO": [
        {"name": "Set quà lưu niệm Đà Nẵng hộp gỗ HANIGO", "price": 250000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"},
        {"name": "Sổ tay tre khắc phong cảnh Cầu Rồng Đà Nẵng", "price": 120000, "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80"},
        {"name": "Móc khóa gỗ khắc hình Cầu Vàng Bà Nà", "price": 45000, "image_url": "https://images.unsplash.com/photo-1582139329536-e7284fece509?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà sâm dứa đặc sản Đà Nẵng vị ngọt nhẹ thơm dứa", "price": 60000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khô mực xé sợi ăn liền Đà Nẵng đậm đà cay ngọt", "price": 180000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bánh dừa nướng đặc sản miền Trung gói 12 cái", "price": 30000, "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà hoa lài organic sấy lạnh thơm thanh mát", "price": 70000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hạt điều rang tỏi ớt giòn cay hũ thủy tinh", "price": 95000, "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mực rim me chua ngọt Đà Nẵng hũ 250g", "price": 85000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Túi vải canvas thêu chữ Đà Nẵng mộc mạc thời trang", "price": 110000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"}
    ],
    "Tiến Huệ - Đặc sản Hà Nội": [
        {"name": "Bánh cốm Hàng Than Tiến Huệ truyền thống", "price": 12000, "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"},
        {"name": "Ô mai sấu bao tử Hà Nội chua ngọt giòn cay", "price": 65000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà sen Tây Hồ cao cấp hương hoa sen bách diệp", "price": 350000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Giò lụa Ước Lễ truyền thống giòn dai không hàn bột", "price": 220000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Chả cốm Hà Nội Tiến Huệ giòn dai ngậy hương nếp", "price": 160000, "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bánh tẻ Sơn Tây nhân thịt mộc nhĩ dẻo ngon", "price": 15000, "image_url": "https://images.unsplash.com/photo-1600180758890-6b94e6e08c6a?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà sâm dứa Đà Nẵng thanh mát hậu ngọt mát", "price": 45000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Cơm cháy chà bông chiên nước mắm siêu chà bông", "price": 60000, "image_url": "https://images.unsplash.com/photo-1579758629938-03607ccdbaba?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bánh pía sầu riêng trứng muối Sóc Trăng Tân Huê Viên", "price": 75000, "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=500&q=80"},
        {"name": "Kẹo dừa sáp Bến Tre giòn béo đậm vị dừa", "price": 80000, "image_url": "https://images.unsplash.com/photo-1627964402688-2947f6d226a6?auto=format&fit=crop&w=500&q=80"}
    ],
    "DaLaVi": [
        {"name": "Dâu tây sấy dẻo DaLaVi vị chua ngọt tự nhiên", "price": 110000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hồng sấy treo gió Nhật Bản DaLaVi dẻo thơm", "price": 240000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà atiso túi lọc DaLaVi thanh mát giải nhiệt gan", "price": 75000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"},
        {"name": "Cà phê arabica Cầu Đất nguyên chất rang xay thơm", "price": 160000, "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80"},
        {"name": "Nước cốt quả dâu tằm Đà Lạt hũ thủy tinh", "price": 65000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mứt hồng dẻo Đà Lạt ngào đường phèn", "price": 80000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bột trà xanh atiso sấy lạnh nguyên chất DaLaVi", "price": 120000, "image_url": "https://images.unsplash.com/photo-1627964402688-2947f6d226a6?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khoai lang dẻo Đà Lạt đóng túi hút chân không", "price": 60000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Chuối Laba sấy dẻo tự nhiên giàu năng lượng", "price": 50000, "image_url": "https://images.unsplash.com/photo-1599599810769-bcde5a160d32?auto=format&fit=crop&w=500&q=80"},
        {"name": "Trà Ô Long sấy nguyên lá Cầu Đất hộp thiết cao cấp", "price": 220000, "image_url": "https://images.unsplash.com/photo-1563822249548-9a72b6353cd1?auto=format&fit=crop&w=500&q=80"}
    ],
    "Dương Đông Food": [
        {"name": "Nước mắm Phú Quốc Khải Hoàn 40 độ đạm", "price": 130000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tiêu đen Phú Quốc sọ xay nguyên hạt thơm nồng", "price": 180000, "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80"},
        {"name": "Rượu sim Phú Quốc hảo hạng chai thủy tinh 750ml", "price": 220000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khô mực câu Phú Quốc loại A dày mình xách 500g", "price": 350000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Muối tiêu dưỡng sinh đặc sản Phú Quốc hũ nhựa", "price": 35000, "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80"},
        {"name": "Mực một nắng Phú Quốc hút chân không đông lạnh", "price": 280000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khô cá cơm sấy giòn tỏi ớt Phú Quốc ngon", "price": 75000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Nước cốt quả hồng sim rừng ngào đường phèn", "price": 95000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tiêu chín đỏ Phú Quốc giữ nguyên quả sấy khô", "price": 250000, "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80"},
        {"name": "Cá chỉ vàng tẩm gia vị phơi khô nướng thơm vị Phú Quốc", "price": 110000, "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=500&q=80"}
    ],
    "Cộng Hưởng Art & Craft Shop": [
        {"name": "Tranh sơn dầu phong cảnh Sài Gòn xưa vẽ tay", "price": 450000, "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tượng đất nung nghệ thuật truyền thống Sa Đéc", "price": 180000, "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bộ lót ly gốm sứ hoa văn nghệ thuật vẽ tay", "price": 90000, "image_url": "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tranh thêu tay hoa sen Việt Nam trên nền vải thô", "price": 350000, "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khay gỗ sơn mài khảm trai cao cấp viền đồng", "price": 550000, "image_url": "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Lọ hoa gốm men hỏa biến Bát Tràng độc bản", "price": 280000, "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=500&q=80"},
        {"name": "Túi canvas in tác phẩm hội họa phong cảnh Sài Gòn", "price": 120000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"},
        {"name": "Đèn bàn gỗ thủ công thêu tay hoa sen cổ điển", "price": 420000, "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=500&q=80"},
        {"name": "Tranh trúc chỉ chân dung phật bà quan âm thiền định", "price": 750000, "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bookmark kim loại mạ vàng họa tiết nón lá sen", "price": 45000, "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80"}
    ],
    "Mayhouse - Craft Decor & Giftshop": [
        {"name": "Giỏ mây tre đan decor Mayhouse hình bầu tròn", "price": 150000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"},
        {"name": "Đèn ngủ bằng tre đan thủ công ấm áp", "price": 280000, "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=500&q=80"},
        {"name": "Thảm cói decor hình tròn lót sàn phòng khách", "price": 220000, "image_url": "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Kệ gỗ treo tường trang trí phòng ngủ Mayhouse", "price": 190000, "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bộ lót ly mây đan tự nhiên 6 món kèm hộp đựng", "price": 75000, "image_url": "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Đũa tre tự nhiên khảm xà cừ hộp gỗ quà tặng", "price": 110000, "image_url": "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Khay tre đan đựng bánh kẹo decor tự nhiên", "price": 95000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"},
        {"name": "Hộp gỗ đựng khăn giấy khắc hoa sen Mayhouse", "price": 130000, "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80"},
        {"name": "Nến thơm sáp đậu nành tinh dầu bưởi tự nhiên", "price": 160000, "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=500&q=80"},
        {"name": "Túi lục bình xách tay móc khóa tua rua thêu hoa", "price": 180000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"}
    ],
    "The Craft House": [
        {"name": "Nến thơm tinh dầu The Craft House đúc hũ xi măng", "price": 180000, "image_url": "https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=500&q=80"},
        {"name": "Móc khóa da khắc tên cá nhân thủ công da bò", "price": 60000, "image_url": "https://images.unsplash.com/photo-1582139329536-e7284fece509?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bao hộ chiếu da bò khâu tay chữ thập màu nâu bò", "price": 250000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bộ ống hút tre tự nhiên tái sử dụng bảo vệ môi trường", "price": 50000, "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bình giữ nhiệt vỏ tre khắc họa tiết Đông Sơn độc đáo", "price": 195000, "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80"},
        {"name": "Lót ly gỗ sồi khắc trống đồng Đông Sơn bộ 4 cái", "price": 90000, "image_url": "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?auto=format&fit=crop&w=500&q=80"},
        {"name": "Túi canvas thêu họa tiết bản đồ Việt Nam màu đen", "price": 130000, "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=500&q=80"},
        {"name": "Sổ gỗ tre khắc laser phong cảnh Vịnh Hạ Long bìa tre", "price": 160000, "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?auto=format&fit=crop&w=500&q=80"},
        {"name": "Soap thảo dược từ thiên nhiên tinh dầu sả chanh", "price": 40000, "image_url": "https://images.unsplash.com/photo-1607006342411-92fc0a41f0a3?auto=format&fit=crop&w=500&q=80"},
        {"name": "Bản đồ Việt Nam gỗ 3D treo tường trang trí nổi bật", "price": 850000, "image_url": "https://images.unsplash.com/photo-1531971589569-0d9370cbe1e5?auto=format&fit=crop&w=500&q=80"}
    ]
}

def crawl_shop_products(name, url, config=None):
    """
    Tries to crawl actual live products from a WooCommerce or WooCommerce-like store page.
    Returns a list of product dicts if successful, else returns empty list.
    """
    if not url or "huefarm.vn" in url or "khamphahue.com.vn" in url:
        return []
        
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # Fetch homepage or shop page
        fetch_url = url
        if name == "HueFood":
            fetch_url = "https://huefood.vn/51-0/san-pham/"
        elif name == "HANIGO":
            fetch_url = "https://ngon.hanigo.com/"
        elif name == "DaLaVi":
            fetch_url = "https://dalavi.net/product/"
        elif name == "Ảm thực xứ Huế":
            fetch_url = "https://amthucxuhue.com/cua-hang/"
        elif name == "Quà Huế":
            fetch_url = "https://quahueonline.com/danh-muc-san-pham/dac-san-qua-hue-online/"
            
        print(f" -> Fetching {fetch_url}...")
        r = requests.get(fetch_url, headers=headers, timeout=12)
        if r.status_code != 200:
            print(f" -> Failed to fetch {fetch_url}: Status {r.status_code}")
            return []
            
        soup = BeautifulSoup(r.text, 'html.parser')
        products = []
        
        # WooCommerce selectors: .product, li.product, .col-inner, .product-inner, .item
        selectors = ['.product', 'li.product', '.col-inner', '.product-inner', '.item', '.product-card', '.box_list_sp', '.col-sm-3']
        items = []
        for selector in selectors:
            items = soup.select(selector)
            # Filter items that look like actual product boxes (must contain images and links)
            valid_items = []
            for item in items:
                title_el = item.select_one('.product-title, .woocommerce-loop-product__title, .name, .title, h2, h3, h4, a')
                img_el = item.select_one('img')
                if title_el and img_el:
                    valid_items.append(item)
            if len(valid_items) >= 4:
                items = valid_items
                print(f" -> Found {len(items)} product elements using selector: {selector}")
                break
                
        if not items or len(items) < 2:
            # Try a very generic column selector
            items = soup.select('div[class*="col-"], div[class*="product-"]')
            
        for item in items[:15]:  # Limit to 15 products
            try:
                title_el = item.select_one('.product-title a, .woocommerce-loop-product__title, .name a, .title a, h2 a, h3 a, h4 a, a[href*="/product/"], a[href*="/san-pham/"], a')
                if not title_el:
                    title_el = item.select_one('a')
                    
                price_el = item.select_one('.price, .amount, .price-box, .gia_sp_sell, .gia_sp, .gia_sp_body')
                img_el = item.select_one('img')
                
                if not title_el or not img_el:
                    continue
                    
                name_text = title_el.get_text(strip=True)
                if not name_text or len(name_text) < 6:
                    # Fallback to checking title_el text directly if it is a link wrapper
                    name_text = item.get_text(strip=True)
                    # Clean it up
                    name_text = re.sub(r'\s+', ' ', name_text).strip()
                    if len(name_text) < 6 or len(name_text) > 80:
                        continue
                
                # Exclude administrative text
                if any(kw in name_text.lower() for kw in ['giỏ hàng', 'tài khoản', 'đăng nhập', 'tin tức', 'liên hệ', 'giới thiệu', 'đăng ký', 'chính sách', 'hướng dẫn', 'giỏ quà', 'xem nhanh', 'chi tiết', 'read more', 'quick view']):
                    continue
                    
                img_url = img_el.get('src') or img_el.get('data-src') or img_el.get('data-lazy-src')
                if img_url and not img_url.startswith('http'):
                    img_url = urljoin(url, img_url)
                    
                price_text = price_el.get_text(strip=True) if price_el else '0'
                price = clean_price(price_text)
                if price <= 0:
                    price = 50000  # Default fallback price if not found on list card
                    
                # Avoid duplicates
                if name_text not in [p['name'] for p in products]:
                    products.append({
                        "name": name_text,
                        "price": price,
                        "image_url": img_url or ''
                    })
            except Exception as item_err:
                pass
                
        print(f" -> Successfully crawled {len(products)} products from {name}")
        return products
    except Exception as e:
        print(f" -> Error crawling {name}: {e}")
        return []

def clear_database_tables():
    """
    Clears all existing shops and products in SQLite to ensure no old tags/categories remain.
    Also resets the ChromaDB vector database.
    """
    print("Clearing SQLite database tables...")
    db = SessionLocal()
    try:
        db.query(Product).delete()
        db.query(Shop).delete()
        db.commit()
        print("Successfully cleared SQLite tables.")
    except Exception as e:
        print("Error clearing tables:", e)
        db.rollback()
    finally:
        db.close()
        
    print("Resetting ChromaDB collections...")
    try:
        vector_db.reset_collections()
        print("Successfully reset ChromaDB.")
    except Exception as e:
        print("Error resetting ChromaDB:", e)

def process_bat_trang_shop(db, shop_link_map):
    """
    Process Gốm Sứ Bát Tràng shop (using local crawler or full_scraper logic),
    but strictly mapping its tag and category to the default tags.
    """
    print("\nProcessing Gốm Sứ Bát Tràng...")
    # Add shop
    shop = Shop(
        name="Gốm Sứ Bát Tràng",
        address="Bát Tràng, Gia Lâm, Hà Nội"
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    shop_link_map[shop.name] = "https://gomsubattrang.vn/"

    # Fetch from live website or use standard logic
    try:
        from scrapling.fetchers import Fetcher
        page = Fetcher.get('https://gomsubattrang.vn/')
        containers = page.css('.product-container')
        print(f" -> Found {len(containers)} products for Gốm Sứ Bát Tràng")
        
        success_count = 0
        for i, container in enumerate(containers):
            try:
                name = container.css('.product-name a::text').get()
                if not name:
                    name = container.css('.product-name::text').get()
                if not name:
                    continue
                name = name.strip()
                
                # Image
                image_url = container.css('img::attr(src)').get()
                if image_url and not image_url.startswith('http'):
                    image_url = "https://gomsubattrang.vn" + image_url

                # Price
                all_text = container.get_all_text()
                price_match = re.search(r'([\d.,]+)\s*[đ|VND]', all_text)
                price_str = price_match.group(0) if price_match else "0"
                price = clean_price(price_str)
                if price <= 0:
                    price = 150000 # Default
                
                # Map default tag and category
                tag, category = map_tags_and_categories(name, "Gốm Sứ Bát Tràng")
                name_en = smart_translate_name(name)
                
                # English template descriptions
                desc_vn = f"Sản phẩm thủ công mỹ nghệ tinh tế, được hoàn thiện thủ công tỉ mỉ từ Gốm Sứ Bát Tràng: {name}."
                desc_en = f"Exquisite handcrafted ceramic product made with premium materials from Bat Trang: {name_en}."
                
                new_product = Product(
                    name=name,
                    name_en=name_en,
                    description=desc_vn,
                    description_en=desc_en,
                    price=price,
                    tag=tag,
                    category=category,
                    image_url=image_url or '',
                    shop_id=shop.id
                )
                db.add(new_product)
                db.commit()
                db.refresh(new_product)
                
                # Compute vector locally
                text_to_embed = f"{new_product.name}. {new_product.description}"
                embedding = vector_db.default_embedding_fn([text_to_embed])[0].tolist()
                new_product.vector_json = json.dumps(embedding)
                db.commit()
                
                success_count += 1
            except Exception as pe:
                db.rollback()
        print(f" -> Inserted {success_count} real products for Gốm Sứ Bát Tràng")
    except Exception as e:
        print(f" -> Error processing Gốm Sứ Bát Tràng: {e}")

async def process_phuc_minh_shops(db, shop_link_map):
    """
    Process Phuc and Minh's shops list using a hybrid crawler (crawler with static fallbacks).
    Maps tags and categories to default ones, and formats price as integers.
    """
    shops_file = 'scratch/shops_to_scrape.json'
    if not os.path.exists(shops_file):
        print(f"Error: {shops_file} not found. Please run prepare_shops.py first.")
        return

    with open(shops_file, 'r', encoding='utf-8') as f:
        shops_data = json.load(f)

    print(f"\nProcessing {len(shops_data)} unique shops from Phuc & Minh...")

    for i, s_data in enumerate(shops_data):
        shop_name = s_data['name']
        shop_link = s_data['link']
        shop_address = s_data['address']

        # Store in link map
        shop_link_map[shop_name] = shop_link

        # 1. Create Shop in DB
        shop = Shop(name=shop_name, address=shop_address)
        db.add(shop)
        db.commit()
        db.refresh(shop)
        print(f"[{i+1}/{len(shops_data)}] Created shop: {shop_name}")

        # 2. Try to crawl live products
        crawled_products = crawl_shop_products(shop_name, shop_link)
        
        # 3. If crawling failed or returned too few products, use the static fallbacks
        if not crawled_products or len(crawled_products) < 3:
            print(f" -> Crawling failed or too few products. Using 100% authentic static catalog fallback...")
            crawled_products = FALLBACK_CATALOG.get(shop_name, [])
            if not crawled_products:
                # Default safety if not found in catalog
                crawled_products = FALLBACK_CATALOG.get("HueFood", [])
        
        # 4. Insert products into DB
        success_count = 0
        for p_data in crawled_products:
            try:
                name = p_data['name'].strip()
                if not name:
                    continue

                price = int(p_data['price'])
                
                # Map default tag and category
                tag, category = map_tags_and_categories(name, shop_name)
                name_en = smart_translate_name(name)
                
                # Form template descriptions based on tag
                desc_vn = ""
                desc_en = ""
                if tag == "Local Food":
                    desc_vn = f"Đặc sản ẩm thực địa phương thơm ngon, chính gốc chất lượng cao từ {shop_name}: {name}."
                    desc_en = f"Delicious and authentic local food specialty from {shop_name}: {name_en}."
                elif tag == "Handicrafts":
                    desc_vn = f"Sản phẩm thủ công mỹ nghệ tinh tế, được hoàn thiện thủ công tỉ mỉ từ {shop_name}: {name}."
                    desc_en = f"Exquisite handcrafted souvenir made with premium materials from {shop_name}: {name_en}."
                elif tag == "Fashion":
                    desc_vn = f"Sản phẩm thời trang phụ kiện độc đáo mang đậm bản sắc Việt Nam từ {shop_name}: {name}."
                    desc_en = f"Unique fashion accessory showcasing Vietnamese cultural heritage from {shop_name}: {name_en}."
                elif tag == "Art":
                    desc_vn = f"Tác phẩm nghệ thuật trang trí độc đáo mang tính thẩm mỹ cao từ {shop_name}: {name}."
                    desc_en = f"High-aesthetic artistic decor item from {shop_name}: {name_en}."
                else: # Gift Sets
                    desc_vn = f"Bộ quà tặng đặc sản ý nghĩa, thiết kế lịch sự thích hợp làm quà từ {shop_name}: {name}."
                    desc_en = f"Premium and meaningful gift set elegantly packaged from {shop_name}: {name_en}."

                product = Product(
                    name=name,
                    name_en=name_en,
                    description=desc_vn,
                    description_en=desc_en,
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
                
                success_count += 1
            except Exception as pe:
                print(f"   -> Error inserting product: {pe}")
                db.rollback()
                
        print(f" -> Inserted {success_count} products for {shop_name}")

def process_khoa_shops(db, shop_link_map):
    """
    Process Khoa's CSV files.
    Maps tags and categories to default ones, and formats price as integers.
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
            continue
            
        # 3. Create Product
        try:
            name_en = smart_translate_name(prod_name)
            
            # Map default tags and categories
            tag, category = map_tags_and_categories(prod_name, shop_name)
            
            # Description templates based on tag
            desc_vn = desc if desc else f"Sản phẩm thực tế chất lượng cao từ cửa hàng {shop_name}."
            desc_en = ""
            if tag == "Local Food":
                desc_en = f"Delicious and authentic local food specialty from {shop_name}: {name_en}."
            elif tag == "Handicrafts":
                desc_en = f"Exquisite handcrafted souvenir made with premium materials from {shop_name}: {name_en}."
            elif tag == "Fashion":
                desc_en = f"Unique fashion accessory showcasing Vietnamese cultural heritage from {shop_name}: {name_en}."
            elif tag == "Art":
                desc_en = f"High-aesthetic artistic decor item from {shop_name}: {name_en}."
            else: # Gift Sets
                desc_en = f"Premium and meaningful gift set elegantly packaged from {shop_name}: {name_en}."
            
            product = Product(
                name=prod_name,
                name_en=name_en,
                description=desc_vn,
                description_en=desc_en,
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
            
    print(f"Finished Khoa's products: {success_count} inserted.")

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
                
                # Save price as pure integer string
                price_int = int(product.price) if product.price else 0
                
                writer.writerow({
                    'STT': idx + 1,
                    'Tên Shop': shop_name,
                    'Địa Chỉ Shop': shop_address,
                    'Link Website / Link Shop': shop_link,
                    'Tên Sản Phẩm': product.name,
                    'Tên Sản Phẩm (Tiếng Anh)': product.name_en or '',
                    'Giá Cả': price_int,
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
    # 1. Reset everything first
    clear_database_tables()
    
    db = SessionLocal()
    shop_link_map = {}
    
    try:
        # Part 1: Process Gốm Sứ Bát Tràng
        process_bat_trang_shop(db, shop_link_map)
        
        # Part 2: Process Phuc & Minh's shops (crawling + static fallbacks)
        await process_phuc_minh_shops(db, shop_link_map)
        
        # Part 3: Process Khoa's shops
        process_khoa_shops(db, shop_link_map)
        
        # Part 4: Export all database content to CSV
        export_all_to_csv(db, shop_link_map)
        
        # Part 5: Sync SQLite to ChromaDB
        print("\nSyncing everything to ChromaDB...")
        from api_contract import sync_db_to_vector
        sync_db_to_vector()
        print("Sync complete.")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
