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
    reply = await gemini_service.get_chat_response(request.message)
    return {"reply": reply}

@router.post("/history", response_model=HistoryResponse, tags=["Business"])
async def create_history(history: HistoryCreate, db: Session = Depends(get_db)):
    db_history = History(user_id=history.user_id, product_id=history.product_id, shop_id=history.shop_id)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
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
    return {"vector": vector.tolist()}

@router.post("/detect-duplicate", tags=["Business"])
async def detect_duplicate(description: str):
    detector = get_detector()
    result = detector.check_duplicate(description, MOCK_PRODUCTS)
    if result:
        return result
    return {
        "score": 0.0, 
        "match_type": "None", 
        "semantic_score": 0.0, 
        "lexical_score": 0.0
    }
