from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from firebase_admin import firestore
from auth_middleware import verify_firebase_token
from detector_logic import DuplicateDetector

router = APIRouter(prefix="/duplicate", tags=["Duplicate Detection"])
detector = DuplicateDetector()

class DetectionRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class DetectionResponse(BaseModel):
    is_duplicate: bool
    confidence: float
    matched_item: Optional[dict] = None
    message: str

def get_db():
    return firestore.client()

def combine_text(name: str, desc: str) -> str:
    # Safely combine name and description
    n = name.strip() if name else ""
    d = desc.strip() if desc else ""
    if n and d:
        return f"{n} | {d}"
    return n or d

@router.post("/check", response_model=DetectionResponse)
def check_duplicate(request: DetectionRequest, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
    
    # Fetch all products (in a large app, we'd use vector search in DB)
    # For SSS demo, we fetch and compare in memory
    docs = db.collection("products").stream()
    existing_products = []
    for doc in docs:
        data = doc.to_dict()
        combined = combine_text(data.get("name", ""), data.get("description", ""))
        existing_products.append({"id": doc.id, "text": combined})
    
    if not existing_products:
        return {
            "is_duplicate": False,
            "confidence": 0.0,
            "matched_item": None,
            "message": "Cơ sở dữ liệu trống. Không tìm thấy trùng lặp."
        }

    target_text = combine_text(request.name, request.description)
    match = detector.check_duplicate(target_text, existing_products)
    
    if match and match.get("id"):
        return {
            "is_duplicate": True,
            "confidence": match["score"],
            "matched_item": {
                "id": match["id"],
                "text": match["text"], # Combined text
                "semantic_score": match["semantic_score"],
                "lexical_score": match["lexical_score"],
                "match_type": match["match_type"]
            },
            "message": f"Phát hiện trùng lặp tiềm ẩn với '{match['text']}' (Độ tin cậy: {match['score']:.2f} - Dạng: {match['match_type']})"
        }
    
    return {
        "is_duplicate": False,
        "confidence": match["score"] if match else 0.0,
        "matched_item": None,
        "message": "Không tìm thấy sản phẩm trùng lặp."
    }

@router.post("/add-product", tags=["Products"])
def add_product(request: DetectionRequest, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
    
    # First check for duplicate
    docs = db.collection("products").stream()
    existing_products = []
    for doc in docs:
        data = doc.to_dict()
        combined = combine_text(data.get("name", ""), data.get("description", ""))
        existing_products.append({"id": doc.id, "text": combined})
    
    target_text = combine_text(request.name, request.description)
    match = detector.check_duplicate(target_text, existing_products, semantic_threshold=0.9, lexical_threshold=0.9)
    
    if match and match.get("id"):
        # Since this is strict creation, we require a high threshold
        raise HTTPException(status_code=400, detail=f"Sản phẩm này đã tồn tại: {match['text']} (Lý do: {match['match_type']})")

    new_product = {
        "name": request.name,
        "description": request.description,
        "created_by": user_info["uid"],
        "created_at": firestore.SERVER_TIMESTAMP
    }
    
    doc_ref = db.collection("products").add(new_product)
    return {"message": "Thêm sản phẩm thành công", "id": doc_ref[1].id}
