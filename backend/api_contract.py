from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# --- Pydantic Models for API ---
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

# --- Mock Endpoints ---

@router.get("/shops", response_model=List[ShopResponse], tags=["Shops"])
async def get_shops():
    """Get list of all shops (Mock)"""
    return [
        {"id": 1, "name": "Co.op Mart", "address": "Dist 1, HCM", "latitude": 10.7769, "longitude": 106.7009},
        {"id": 2, "name": "WinMart", "address": "Dist 7, HCM", "latitude": 10.7289, "longitude": 106.7067}
    ]

@router.post("/shops", response_model=ShopResponse, tags=["Shops"])
async def create_shop(shop: ShopCreate):
    """Create a new shop (Mock)"""
    return {"id": 99, **shop.dict()}

@router.get("/history", response_model=List[HistoryResponse], tags=["History"])
async def get_history(user_id: Optional[str] = None):
    """Get shopping history (Mock)"""
    return [
        {"id": 1, "user_id": user_id or "user_1", "product_id": "prod_1", "shop_id": 1, "timestamp": datetime.now()}
    ]

@router.post("/history", response_model=HistoryResponse, tags=["History"])
async def create_history(history: HistoryCreate):
    """Log a shopping event (Mock)"""
    return {"id": 100, "timestamp": datetime.now(), **history.dict()}

import json
import numpy as np
from detector_logic import DuplicateDetector

detector = DuplicateDetector()

@router.post("/detect-duplicate", tags=["AI Logic"])
async def detect_duplicate(description: str):
    """
    Check if a product already exists using AI Vector Similarity.
    """
    # In a real app, you would fetch existing products from DB
    # Mocking some existing data for demonstration
    mock_existing_data = [
        {"id": 1, "text": "Sữa tươi Vinamilk 180ml", "vector": detector.get_embedding("Sữa tươi Vinamilk 180ml").tolist()},
        {"id": 2, "text": "Bánh quy Oreo socola", "vector": detector.get_embedding("Bánh quy Oreo socola").tolist()}
    ]
    
    match = detector.check_duplicate(description, mock_existing_data)
    
    if match and match['score'] > 0.8:
        return {
            "is_duplicate": True,
            "confidence": match['score'],
            "matched_product_id": match['id'],
            "message": f"Potential duplicate found (Score: {match['score']:.2f})"
        }
    
    return {
        "is_duplicate": False,
        "confidence": match['score'] if match else 0,
        "matched_product_id": None,
        "message": "No duplicate found. Safe to add."
    }
