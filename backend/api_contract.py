from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Security
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import json
import numpy as np
import io
import requests
import os
from detector_logic import DuplicateDetector
from ai_service import gemini_service
from visual_search import ImageVectorExtractor
from vector_db import vector_db  # Import vector_db
from firebase_admin import auth

# Authentication Middleware
from auth_middleware import verify_firebase_token

router = APIRouter()

# --- Lazy Loading for Services ---
_detector = None
_image_extractor = None

def get_detector():
    global _detector
    if _detector is None:
        print("Loading DuplicateDetector model...")
        _detector = DuplicateDetector()
    return _detector

def get_image_extractor():
    global _image_extractor
    if _image_extractor is None:
        print("Loading CLIP model...")
        _image_extractor = ImageVectorExtractor()
    return _image_extractor

# --- Sync Logic ---
def sync_db_to_vector():
    """Đồng bộ dữ liệu văn bản từ SQLite sang ChromaDB để tìm kiếm thông minh"""
    from database import SessionLocal, Product, History, Shop
    db = SessionLocal()
    try:
        # 1. Đồng bộ sản phẩm chung
        products = db.query(Product).all()
        if products:
            ids = [f"prod_{p.id}" for p in products]
            documents = [f"{p.name} - {p.description or ''}" for p in products]
            
            metadatas = []
            for p in products:
                shop = db.query(Shop).filter(Shop.id == p.shop_id).first()
                metadatas.append({
                    "shop_id": p.shop_id,
                    "shop_name": shop.name if shop else "Unknown",
                    "shop_address": shop.address if shop else "Unknown",
                    "name": p.name,
                    "description": p.description or "",
                    "price": p.price or 0.0,
                    "user_id": "system"
                })
            
            vector_db.add_documents(ids=ids, documents=documents, metadatas=metadatas)
        
        # 2. Đồng bộ lịch sử cá nhân
        histories = db.query(History).all()
        if histories:
            h_ids = [f"hist_{h.id}" for h in histories]
            h_docs = [f"{h.product_id} (Đã mua)" for h in histories]
            h_metas = [{"user_id": h.user_id, "type": "history"} for h in histories]
            vector_db.add_documents(ids=h_ids, documents=h_docs, metadatas=h_metas)
            
        print(f"Synced text data to ChromaDB.")
        
        # 3. Đồng bộ vector ảnh (nếu có)
        sync_image_collection_from_sqlite()
        
    except Exception as e:
        print(f"Error syncing to VectorDB: {e}")
    finally:
        db.close()

def sync_image_collection_from_sqlite():
    """Đồng bộ vector ảnh (CLIP) từ SQLite sang ChromaDB collection riêng"""
    from database import SessionLocal, Product, Shop
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.vector_json != None).all()
        if not products:
            print("No image vectors found in SQLite to sync.")
            return

        ids = []
        embeddings = []
        metadatas = []
        documents = []

        for p in products:
            try:
                vector = json.loads(p.vector_json)
                if not isinstance(vector, list):
                    continue
                
                shop = db.query(Shop).filter(Shop.id == p.shop_id).first()
                
                ids.append(f"img_prod_{p.id}")
                embeddings.append(vector)
                documents.append(p.name)
                metadatas.append({
                    "product_id": p.id,
                    "name": p.name,
                    "description": p.description or "",
                    "price": p.price or 0.0,
                    "shop_id": p.shop_id,
                    "shop_name": shop.name if shop else "Unknown",
                    "shop_address": shop.address if shop else "Unknown",
                })
            except Exception as ve:
                print(f"Error parsing vector for product {p.id}: {ve}")

        if ids:
            vector_db.add_with_embeddings(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents,
                collection_name="product_images"
            )
            print(f"Synced {len(ids)} image vectors to ChromaDB.")
    except Exception as e:
        print(f"Error syncing image collection: {e}")
    finally:
        db.close()

# --- Pydantic Models for API ---
class UserAuth(BaseModel):
    email: EmailStr
    password: str

class ShopBase(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float

class ShopCreate(ShopBase):
    pass

class ShopResponse(ShopBase):
    id: int

    class Config:
        from_attributes = True

class HistoryBase(BaseModel):
    user_id: str
    product_id: str
    shop_id: int

class HistoryCreate(HistoryBase):
    pass

class HistoryResponse(HistoryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    user_id: str

# --- Mock Data for Testing ---
MOCK_PRODUCTS = [
    {"id": 1, "text": "Sữa tươi Vinamilk 180ml | Thùng 48 hộp"},
    {"id": 2, "text": "Bánh quy Oreo socola 133g"},
    {"id": 3, "text": "Nước tương Chinsu tỏi ớt 250ml"},
    {"id": 4, "text": "Mì Hảo Hảo Tôm chua cay | Gói 75g"},
    {"id": 5, "text": "Dầu ăn Simply 1L"},
]

# --- Auth Endpoints ---

@router.post("/register", tags=["Auth"])
async def register_user(user_data: UserAuth):
    """
    Đăng ký người dùng mới trên Firebase.
    """
    try:
        user = auth.create_user(
            email=user_data.email,
            password=user_data.password
        )
        return {"message": "User created successfully", "uid": user.uid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", tags=["Auth"])
async def login_user(user_data: UserAuth):
    """
    Đăng nhập bằng Email/Password. 
    Lưu ý: Firebase Admin SDK không hỗ trợ kiểm tra password trực tiếp.
    Chúng ta phải sử dụng Firebase Auth REST API.
    """
    # Lấy Web API Key từ môi trường (Bạn cần lấy key này từ Project Settings > General trong Firebase Console)
    # Nếu chưa có, bạn có thể hướng dẫn người dùng lấy sau.
    api_key = os.getenv("FIREBASE_WEB_API_KEY")
    if not api_key:
        # Fallback to mock for demo if API key is missing
        return {"status": "success", "token": "mock_token_demo", "email": user_data.email, "uid": "mock_uid"}

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user_data.email,
        "password": user_data.password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return {
            "token": data["idToken"],
            "email": data["email"],
            "uid": data["localId"]
        }
    else:
        error_msg = response.json().get("error", {}).get("message", "Login failed")
        raise HTTPException(status_code=401, detail=error_msg)

# --- Business Endpoints ---

from database import get_db, History
from sqlalchemy.orm import Session

@router.post("/chat", tags=["Business"])
async def chat(request: ChatRequest):
    # --- RAG Implementation ---
    # 1. Tìm thông tin liên quan từ VectorDB
    context = ""
    try:
        search_results = vector_db.query(query_texts=[request.message], n_results=2)
        if search_results and search_results['documents'] and search_results['documents'][0]:
            relevant_docs = search_results['documents'][0]
            context = "Thông tin sản phẩm liên quan: " + " | ".join(relevant_docs)
    except Exception as e:
        print(f"RAG Error: {e}")

    # 2. Gửi cho Gemini kèm Context
    reply = await gemini_service.get_chat_response(request.message, context=context)
    return {"reply": reply}

@router.post("/history", response_model=HistoryResponse, tags=["Business"])
async def create_history(history: HistoryCreate, db: Session = Depends(get_db)):
    # 1. Lưu vào SQLite
    db_history = History(user_id=history.user_id, product_id=history.product_id, shop_id=history.shop_id)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    # 2. Đồng bộ ngay lập tức sang ChromaDB để AI nhận diện được
    try:
        vector_db.add_documents(
            ids=[f"hist_{db_history.id}"],
            documents=[f"{history.product_id} (Đã mua)"],
            metadatas=[{"user_id": history.user_id, "type": "history"}]
        )
        print(f"Added history item '{history.product_id}' to VectorDB.")
    except Exception as e:
        print(f"Error updating VectorDB from history: {e}")
        
    return db_history

@router.post("/scan-product", tags=["Business"])
async def scan_product(file: UploadFile = File(...)):
    contents = await file.read()
    analysis = await gemini_service.analyze_product_image(contents)
    return {"analysis": analysis}

@router.post("/visual-search", tags=["Business"])
async def visual_search(file: UploadFile = File(...)):
    from PIL import Image
    import io
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    extractor = get_image_extractor()
    vector = extractor.extract_vector(image)
    
    # Tìm kiếm trong ChromaDB collection dành cho ảnh
    try:
        results = vector_db.query(
            query_embeddings=[vector.tolist()],
            n_results=5,
            collection_name="product_images"
        )
        
        products = []
        if results and results['metadatas'] and results['metadatas'][0]:
            for i in range(len(results['metadatas'][0])):
                meta = results['metadatas'][0][i]
                dist = results['distances'][0][i]
                products.append({
                    "id": meta.get("product_id"),
                    "name": meta.get("name"),
                    "description": meta.get("description"),
                    "price": meta.get("price"),
                    "shop_name": meta.get("shop_name"),
                    "shop_address": meta.get("shop_address"),
                    "score": float(max(0, 1 - dist))
                })
        
        return {"products": products}
    except Exception as e:
        print(f"Visual search error: {e}")
        return {"products": [], "error": str(e)}

@router.post("/sync", tags=["System"])
async def trigger_sync():
    """Trigger manual sync from SQLite to ChromaDB"""
    try:
        sync_db_to_vector()
        return {"message": "Sync completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-duplicate", tags=["Business"])
async def detect_duplicate(description: str, user_id: str):
    # Sử dụng ChromaDB để tìm kiếm sản phẩm tương tự của CHÍNH NGƯỜI DÙNG ĐÓ
    try:
        # Thêm filter where={"user_id": user_id} để cách ly dữ liệu
        results = vector_db.query(
            query_texts=[description], 
            n_results=1,
            where={"user_id": user_id}
        )
        if results and results['documents'] and results['documents'][0]:
            distance = results['distances'][0][0]
            score = max(0, 1 - distance)
            matched_text = results['documents'][0][0]
            
            if score > 0.7:
                return {
                    "id": results['ids'][0][0],
                    "text": matched_text,
                    "score": float(score),
                    "semantic_score": float(score),
                    "lexical_score": 0.0,
                    "match_type": "ChromaDB-User-Specific"
                }
    except Exception as e:
        print(f"Vector search error: {e}")

    return {
        "score": 0.0, 
        "match_type": "None", 
        "semantic_score": 0.0, 
        "lexical_score": 0.0
    }
