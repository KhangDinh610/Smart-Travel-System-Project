from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from auth_middleware import verify_firebase_token
from firebase_admin import firestore
from ai_utils import RecommendationEngine, get_firestore_client

router = APIRouter(prefix="/recommend", tags=["Recommendation"])
engine = RecommendationEngine()

class RecommendRequest(BaseModel):
    preference: Optional[str] = ""
    budget: Optional[float] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    top_k: Optional[int] = 5

class RecommendationItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    rating: float
    shop_name: str
    score: float
    semantic_score: float
    tag_score: float
    novelty_score: float
    proximity_score: float
    budget_score: float

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]

class PurchaseHistoryRequest(BaseModel):
    product_id: str
    shop_id: Optional[str] = None

class PurchaseHistoryResponse(BaseModel):
    success: bool
    message: str

@router.post("/recommend", response_model=RecommendationResponse)
def get_recommendations(request: RecommendRequest, user_info: dict = Depends(verify_firebase_token)):
    user_id = user_info["uid"]
    if request.top_k is None or request.top_k <= 0:
        request.top_k = 5

    recommendations = engine.recommend(
        user_id=user_id,
        preference=request.preference,
        budget=request.budget,
        location_lat=request.location_lat,
        location_lon=request.location_lon,
        top_k=request.top_k
    )
    return {"recommendations": recommendations}

@router.post("/history/log", response_model=PurchaseHistoryResponse)
def log_purchase(request: PurchaseHistoryRequest, user_info: dict = Depends(verify_firebase_token)):
    db = get_firestore_client()
    if not db:
        raise HTTPException(status_code=500, detail="Không thể kết nối đến Firestore để lưu lịch sử mua hàng.")

    try:
        db.collection("history").add({
            "user_id": user_info["uid"],
            "product_id": request.product_id,
            "shop_id": request.shop_id or "",
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        return {"success": True, "message": "Lịch sử mua hàng đã được lưu."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Lưu lịch sử thất bại: {exc}")
