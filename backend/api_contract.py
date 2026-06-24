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
from ai_service import gemini_service, GeminiError, GeminiQuotaError
from visual_search import ImageVectorExtractor
from vector_db import vector_db  # Import vector_db
from translation_utils import smart_translate_name
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
    """Äá»“ng bá»™ dá»¯ liá»‡u vÄƒn báº£n tá»« SQLite sang ChromaDB Ä‘á»ƒ tÃ¬m kiáº¿m thÃ´ng minh"""
    from database import SessionLocal, Product, History, Shop
    db = SessionLocal()
    try:
        # 1. Äá»“ng bá»™ sáº£n pháº©m chung
        products = db.query(Product).all()
        if products:
            ids = [f"prod_{p.id}" for p in products]
            documents = [f"{p.name} {p.name_en or ''} - {p.description or ''} {p.description_en or ''} ({p.tag})" for p in products]

            metadatas = []
            for p in products:
                shop = db.query(Shop).filter(Shop.id == p.shop_id).first()
                metadatas.append({
                    "shop_id": p.shop_id,
                    "shop_name": shop.name if shop else "Unknown",
                    "shop_address": shop.address if shop else "Unknown",
                    "name": p.name,
                    "name_en": p.name_en or "",
                    "description": p.description or "",
                    "description_en": p.description_en or "",
                    "price": p.price or 0.0,
                    "tag": p.tag or "General",
                    "category": p.category or "Unknown",
                    "user_id": "system"
                })

            vector_db.add_documents(ids=ids, documents=documents, metadatas=metadatas)

        # 2. Đồng bộ lịch sử cá nhân
        histories = db.query(History).all()
        if histories:
            h_ids = []
            h_docs = []
            h_metas = []
            for h in histories:
                product = db.query(Product).filter(Product.id == int(h.product_id)).first()
                if product:
                    h_ids.append(f"hist_{h.id}")
                    h_docs.append(f"{product.name} | {product.description}")
                    h_metas.append({"user_id": h.user_id, "type": "history"})
            if h_ids:
                vector_db.add_documents(ids=h_ids, documents=h_docs, metadatas=h_metas)

        print(f"Synced text data to ChromaDB.")

        # 3. Äá»“ng bá»™ vector áº£nh (náº¿u cÃ³)
        sync_image_collection_from_sqlite()

    except Exception as e:
        print(f"Error syncing to VectorDB: {e}")
    finally:
        db.close()

def sync_image_collection_from_sqlite():
    """Äá»“ng bá»™ vector áº£nh (CLIP) tá»« SQLite sang ChromaDB collection riÃªng"""
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
                    "tag": p.tag or "General",
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
    name: Optional[str] = None

class FirebaseLoginRequest(BaseModel):
    token: str

class ShopBase(BaseModel):
    name: str
    address: str

class ShopCreate(ShopBase):
    pass

class ShopResponse(ShopBase):
    id: int

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    description: str
    description_en: Optional[str] = None
    price: float
    tag: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    shop_id: int
    shop_address: Optional[str] = None

class ProductResponse(ProductBase):
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

class WishlistAction(BaseModel):
    user_id: str
    product_id: int

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    is_read: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    title: str

class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    sender: str
    text: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    text: str

# --- Auth Endpoints ---

@router.post("/register", tags=["Auth"])
async def register_user(user_data: UserAuth):
    try:
        user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.name
        )
        return {"message": "User created successfully", "uid": user.uid}
    except Exception as e:
        error_str = str(e)
        if "EMAIL_EXISTS" in error_str or "already in use" in error_str.lower():
            detail = "Email này đã được sử dụng. Vui lòng đăng nhập hoặc dùng email khác."
        elif "WEAK_PASSWORD" in error_str:
            detail = "Mật khẩu quá yếu. Vui lòng nhập mật khẩu mạnh hơn (tối thiểu 6 ký tự)."
        else:
            detail = f"Lỗi đăng ký: {error_str}"
        
        print(f"Registration error for {user_data.email}: {e}")
        raise HTTPException(status_code=400, detail=detail)

@router.post("/login", tags=["Auth"])
async def login_user(user_data: UserAuth):
    api_key = os.getenv("FIREBASE_WEB_API_KEY")
    if not api_key or api_key == "your_firebase_web_api_key_here":
        # Fallback for development if key is missing
        print("Warning: FIREBASE_WEB_API_KEY not configured. Checking for mock login...")
        if user_data.email == "test@example.com" and user_data.password == "password":
            return {
                "token": "mock_token_demo",
                "email": user_data.email,
                "uid": "mock_uid",
                "name": "Test User"
            }
        raise HTTPException(
            status_code=500, 
            detail="Firebase Web API Key is not configured on the server. Please check your .env file."
        )

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user_data.email,
        "password": user_data.password,
        "returnSecureToken": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Get display name using Admin SDK
            try:
                user_record = auth.get_user(data["localId"])
                display_name = user_record.display_name or data["email"].split("@")[0]
            except:
                display_name = data["email"].split("@")[0]
                
            return {
                "token": data["idToken"],
                "email": data["email"],
                "uid": data["localId"],
                "name": display_name
            }
        else:
            error_data = response.json().get("error", {})
            error_code = error_data.get("message", "Login failed")
            
            # Map Firebase error codes to user-friendly messages
            error_map = {
                "EMAIL_NOT_FOUND": "Email không tồn tại trong hệ thống.",
                "INVALID_PASSWORD": "Mật khẩu không chính xác.",
                "USER_DISABLED": "Tài khoản của bạn đã bị khóa.",
                "TOO_MANY_ATTEMPTS_TRY_LATER": "Quá nhiều lần thử thất bại. Vui lòng quay lại sau.",
                "INVALID_EMAIL": "Định dạng email không hợp lệ."
            }
            detail = error_map.get(error_code, f"Đăng nhập thất bại: {error_code}")
            raise HTTPException(status_code=401, detail=detail)
    except requests.exceptions.RequestException as e:
        print(f"Connection error to Firebase: {e}")
        raise HTTPException(status_code=503, detail="Không thể kết nối đến máy chủ xác thực. Vui lòng thử lại sau.")

@router.post("/login/firebase", tags=["Auth"])
async def login_firebase(data: FirebaseLoginRequest):
    try:
        decoded_token = auth.verify_id_token(data.token)
        uid = decoded_token.get('uid')
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', email.split("@")[0] if email else "User")
        
        return {
            "token": data.token,
            "email": email,
            "uid": uid,
            "name": name
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Xác thực Firebase thất bại: {e}")

from database import get_db, History, Product, Shop, Wishlist, Notification, ChatSession, ChatMessage
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

# --- Chat Session Endpoints ---

@router.post("/chat/sessions", response_model=ChatSessionResponse, tags=["Business"])
async def create_chat_session(session_data: ChatSessionBase, db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    db_session = ChatSession(user_id=user["uid"], title=session_data.title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/chat/sessions", response_model=List[ChatSessionResponse], tags=["Business"])
async def get_chat_sessions(db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    return db.query(ChatSession).filter(ChatSession.user_id == user["uid"]).order_by(ChatSession.created_at.desc()).all()

@router.delete("/chat/sessions/{session_id}", tags=["Business"])
async def delete_chat_session(session_id: int, db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    # Verify ownership
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user["uid"]).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Delete associated messages first
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    
    # Delete the session
    db.delete(session)
    db.commit()
    return {"message": "Chat session deleted successfully"}

@router.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessageResponse], tags=["Business"])
async def get_chat_messages(session_id: int, db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    # Verify ownership
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user["uid"]).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.asc()).all()

@router.post("/chat/sessions/{session_id}/message", response_model=ChatMessageResponse, tags=["Business"])
async def send_chat_message(session_id: int, message_data: ChatMessageCreate, db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    # Verify ownership
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user["uid"]).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Save user message
    user_msg = ChatMessage(session_id=session_id, sender="user", text=message_data.text)
    db.add(user_msg)
    
    # Get AI response (RAG)
    context = ""
    try:
        where_filter = {"$or": [{"user_id": "system"}, {"user_id": user["uid"]}]}
        search_results = vector_db.query(query_texts=[message_data.text], n_results=3, where=where_filter)
        if search_results and search_results["documents"] and search_results["documents"][0]:
            context = "Thông tin liên quan: " + " | ".join(search_results["documents"][0])
    except Exception as e:
        print(f"RAG Error: {e}")

    try:
        ai_reply_text = await gemini_service.get_chat_response(message_data.text, context=context)
    except GeminiQuotaError as eq:
        raise HTTPException(status_code=429, detail={"message": eq.message, "reset_time": eq.reset_time_msg})
    except GeminiError as eg:
        raise HTTPException(status_code=500, detail={"message": eg.message, "technical_details": eg.details})
    
    # Save AI message
    ai_msg = ChatMessage(session_id=session_id, sender="ai", text=ai_reply_text)
    db.add(ai_msg)
    
    db.commit()
    db.refresh(ai_msg)
    return ai_msg

# --- Business Endpoints ---

@router.get("/products", response_model=List[ProductResponse], tags=["Business"])
async def get_products(search: Optional[str] = None, category: Optional[str] = None, lang: str = "vi", db: Session = Depends(get_db)):
    all_products = []
    
    if search:
        # Hybrid Search with Bucket Ranking & Semantic Search (No API calls, ultra fast)
        search_query = search.strip()
        terms = [t.strip() for t in search_query.split() if len(t.strip()) > 1]
        
        scores = {}  # {product_id: score}
        
        # Define category filter if specified
        category_filter_expr = None
        cat_map = {
            "food": ["food", "ẩm thực", "ăn", "uống"],
            "crafts": ["craft", "thủ công", "gốm", "sứ"],
            "clothing": ["cloth", "thời trang", "áo", "quần", "lụa"],
            "art": ["art", "nghệ thuật", "tranh", "tượng"],
            "gifts": ["gift", "quà"]
        }
        if category and category.lower() != "all":
            mapped_terms = cat_map.get(category.lower(), [category])
            category_filter_expr = or_(*(
                [Product.category.ilike(f"%{mt}%") for mt in mapped_terms] +
                [Product.tag.ilike(f"%{mt}%") for mt in mapped_terms]
            ))

        # --- 1. SQLite Keyword Search (Bucket Ranking) ---
        
        # Bucket 1: Exact phrase match in Name or Name EN (Score: 100)
        exact_name_filters = [
            Product.name.ilike(f"%{search_query}%"),
            Product.name_en.ilike(f"%{search_query}%")
        ]
        query = db.query(Product).filter(or_(*exact_name_filters))
        if category_filter_expr is not None:
            query = query.filter(category_filter_expr)
        for p in query.limit(50).all():
            scores[p.id] = scores.get(p.id, 0.0) + 100.0
            
        # Bucket 1b: Exact phrase match in Description or Description EN (Score: 30)
        exact_desc_filters = [
            Product.description.ilike(f"%{search_query}%"),
            Product.description_en.ilike(f"%{search_query}%")
        ]
        query = db.query(Product).filter(or_(*exact_desc_filters))
        if category_filter_expr is not None:
            query = query.filter(category_filter_expr)
        for p in query.limit(50).all():
            scores[p.id] = scores.get(p.id, 0.0) + 30.0
            
        # Bucket 2: AND terms match (ALL words in query must match name/desc) (Score: 50)
        if len(terms) > 1:
            and_filters = []
            for term in terms:
                and_filters.append(or_(
                    Product.name.ilike(f"%{term}%"),
                    Product.name_en.ilike(f"%{term}%"),
                    Product.description.ilike(f"%{term}%"),
                    Product.description_en.ilike(f"%{term}%")
                ))
            query = db.query(Product).filter(and_(*and_filters))
            if category_filter_expr is not None:
                query = query.filter(category_filter_expr)
            for p in query.limit(50).all():
                scores[p.id] = scores.get(p.id, 0.0) + 50.0
                
        # Bucket 3: OR terms match (Some words in query match name/desc) (Score: matching fraction * 15)
        if terms:
            for term in terms:
                # To keep it relevant, only match on name fields for OR term match
                term_filters = [
                    Product.name.ilike(f"%{term}%"),
                    Product.name_en.ilike(f"%{term}%")
                ]
                query = db.query(Product).filter(or_(*term_filters))
                if category_filter_expr is not None:
                    query = query.filter(category_filter_expr)
                for p in query.limit(50).all():
                    scores[p.id] = scores.get(p.id, 0.0) + (15.0 / len(terms))

        # --- 2. Vector DB Semantic Search ---
        try:
            results = vector_db.query(
                query_texts=[search_query],
                n_results=40,
                where={"user_id": "system"}
            )
            if results and results["ids"] and results["ids"][0]:
                for rid, dist in zip(results["ids"][0], results["distances"][0]):
                    if rid.startswith("prod_"):
                        pid = int(rid.replace("prod_", ""))
                        # Convert distance to similarity score
                        similarity_score = max(0.0, 1.0 - dist) * 40.0
                        scores[pid] = scores.get(pid, 0.0) + similarity_score
        except Exception as e:
            print(f"Vector search error: {e}")

        if not scores:
            return []
            
        # Sort product IDs by total score descending
        sorted_ids = [pid for pid, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)]
        
        # Retrieve actual products and respect category filter
        query = db.query(Product).filter(Product.id.in_(sorted_ids))
        if category_filter_expr is not None:
            query = query.filter(category_filter_expr)
        matched_products = query.all()
        id_to_product = {p.id: p for p in matched_products}
        
        # Sort them back to the correct order of scores
        all_products = [id_to_product[pid] for pid in sorted_ids if pid in id_to_product]

    else:
        # Standard category filtering
        query = db.query(Product)
        if category and category.lower() != "all":
            cat_map = {
                "food": ["food", "ẩm thực", "ăn", "uống"],
                "crafts": ["craft", "thủ công", "gốm", "sứ"],
                "clothing": ["cloth", "thời trang", "áo", "quần", "lụa"],
                "art": ["art", "nghệ thuật", "tranh", "tượng"],
                "gifts": ["gift", "quà"]
            }
            mapped_terms = cat_map.get(category.lower(), [category])
            cat_filters = [Product.category.ilike(f"%{mt}%") for mt in mapped_terms] + \
                          [Product.tag.ilike(f"%{mt}%") for mt in mapped_terms]
            query = query.filter(or_(*cat_filters))
        all_products = query.limit(40).all()
    
    # Handle Localization
    results = []
    for p in all_products:
        p_res = ProductResponse.from_orm(p)
        if lang == "en":
            # 1. Use high-quality AI translation if already available
            if p.name_en and not p.name_en.startswith("Error"):
                p_res.name = p.name_en
                if p.description_en: p_res.description = p.description_en
            else:
                # 2. Hybrid fallback: Use smart dictionary-based translation (instant & reliable)
                p_res.name = smart_translate_name(p.name)
        
        shop = db.query(Shop).filter(Shop.id == p.shop_id).first()
        if shop:
            p_res.shop_address = shop.address
        results.append(p_res)
        
    return results

@router.get("/products/{product_id}", response_model=ProductResponse, tags=["Business"])
async def get_product(product_id: int, lang: str = "vi", db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    p_res = ProductResponse.from_orm(product)
    if lang == "en":
        # On-demand translation is okay for a single product detail view
        if not product.name_en or product.name_en.startswith("Error"):
            try:
                prompt = (
                    f"Translate the following Vietnamese product details into natural English for a shopping app.\n"
                    f"Name: {product.name}\n"
                    f"Description: {product.description}\n"
                    f"Format as JSON: {{\"name_en\": \"...\", \"description_en\": \"...\"}}"
                )
                resp = await gemini_service.get_chat_response(prompt)
                if resp and not resp.startswith("Error"):
                    clean_json = resp.replace("```json", "").replace("```", "").strip()
                    import json
                    data = json.loads(clean_json)
                    product.name_en = data.get("name_en", product.name)
                    product.description_en = data.get("description_en", product.description)
                    db.commit()
            except:
                pass
        
        if product.name_en and not product.name_en.startswith("Error"): 
            p_res.name = product.name_en
        if product.description_en and not product.description_en.startswith("Error"): 
            p_res.description = product.description_en

    shop = db.query(Shop).filter(Shop.id == product.shop_id).first()
    if shop:
        p_res.shop_address = shop.address
    return p_res

@router.get("/products/{product_id}/related", response_model=List[ProductResponse], tags=["Business"])
async def get_related_products(product_id: int, lang: str = "vi", db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Use Vector DB to find related products based on description and name
    query_text = f"{product.name} {product.description}"
    try:
        # Search for similar products, excluding the current one
        # ChromaDB 'where' filter can be used to exclude IDs
        results = vector_db.query(
            query_texts=[query_text],
            n_results=5,
            where={"$and": [
                {"user_id": "system"},
                {"name": {"$ne": product.name}} # Simplistic exclusion, better to use ID if metadata has it
            ]}
        )
        
        related_ids = []
        if results and results["ids"] and results["ids"][0]:
            # IDs are in format "prod_123"
            for rid in results["ids"][0]:
                try:
                    actual_id = int(rid.replace("prod_", ""))
                    if actual_id != product_id:
                        related_ids.append(actual_id)
                except:
                    continue

        if not related_ids:
            # Fallback to category-based if vector search yields nothing
            related_products = db.query(Product).filter(
                Product.category == product.category,
                Product.id != product_id
            ).limit(4).all()
        else:
            # Fetch full product objects for the found IDs
            related_products = db.query(Product).filter(Product.id.in_(related_ids)).all()
            
    except Exception as e:
        print(f"Error finding related products: {e}")
        # Fallback
        related_products = db.query(Product).filter(
            Product.category == product.category,
            Product.id != product_id
        ).limit(4).all()

    results = []
    for p in related_products:
        p_res = ProductResponse.from_orm(p)
        if lang == "en":
            # 1. Use high-quality AI translation if already available
            if p.name_en and not p.name_en.startswith("Error") and p.name_en != "":
                p_res.name = p.name_en
                if p.description_en: p_res.description = p.description_en
            else:
                # 2. Hybrid fallback: Use smart dictionary-based translation (instant & reliable)
                p_res.name = smart_translate_name(p.name)

        shop = db.query(Shop).filter(Shop.id == p.shop_id).first()
        if shop:
            p_res.shop_address = shop.address
        results.append(p_res)
            
    return results

@router.get("/shops/{shop_id}", response_model=ShopResponse, tags=["Business"])
async def get_shop(shop_id: int, db: Session = Depends(get_db)):
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop

@router.post("/chat", tags=["Business"])
async def chat(request: ChatRequest, user: dict = Depends(verify_firebase_token)):
    context = ""
    try:
        # Filter results to include only system documents or documents for this specific user
        where_filter = {
            "$or": [
                {"user_id": "system"},
                {"user_id": user["uid"]}
            ]
        }
        search_results = vector_db.query(
            query_texts=[request.message], 
            n_results=2,
            where=where_filter
        )
        if search_results and search_results["documents"] and search_results["documents"][0]:
            relevant_docs = search_results["documents"][0]
            context = "Thông tin sản phẩm liên quan: " + " | ".join(relevant_docs)
    except Exception as e:
        print(f"RAG Error: {e}")

    try:
        reply = await gemini_service.get_chat_response(request.message, context=context)
    except GeminiQuotaError as eq:
        raise HTTPException(status_code=429, detail={"message": eq.message, "reset_time": eq.reset_time_msg})
    except GeminiError as eg:
        raise HTTPException(status_code=500, detail={"message": eg.message, "technical_details": eg.details})
    return {"reply": reply}

@router.post("/history", response_model=HistoryResponse, tags=["Business"])
async def create_history(history: HistoryCreate, db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    db_history = History(user_id=user["uid"], product_id=history.product_id, shop_id=history.shop_id)       
    db.add(db_history)
    db.commit()
    db.refresh(db_history)

    product = db.query(Product).filter(Product.id == int(history.product_id)).first()
    if product:
        try:
            vector_db.add_documents(
                ids=[f"hist_{db_history.id}"],
                documents=[f"{product.name} | {product.description}"],
                metadatas=[{"user_id": user["uid"], "type": "history"}]
            )
        except Exception as e:
            print(f"Error updating VectorDB from history: {e}")
    return db_history

@router.get("/history/{user_id}", tags=["Business"])
async def get_history(user_id: str, lang: str = "vi", db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    if user_id != user["uid"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    # Get history and join with Product to get product details
    histories = db.query(History).filter(History.user_id == user["uid"]).order_by(History.timestamp.desc()).all()
    results = []
    for h in histories:
        product = db.query(Product).filter(Product.id == int(h.product_id)).first()
        if product:
            p_res = ProductResponse.from_orm(product)
            if lang == "en":
                if not product.name_en:
                    try:
                        prompt = f"Translate to English: {product.name}. Concise title."
                        p_res.name = await gemini_service.get_chat_response(prompt)
                        product.name_en = p_res.name
                        db.commit()
                    except:
                        p_res.name = product.name
                else:
                    p_res.name = product.name_en
                
                if product.description_en:
                    p_res.description = product.description_en

            shop = db.query(Shop).filter(Shop.id == product.shop_id).first()
            if shop:
                p_res.shop_address = shop.address
            results.append({
                "history_id": h.id,
                "timestamp": h.timestamp,
                "product": p_res
            })
    return results

@router.get("/wishlist/{user_id}", tags=["Business"])
async def get_wishlist(user_id: str, db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    if user_id != user["uid"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    items = db.query(Wishlist).filter(Wishlist.user_id == user["uid"]).all()
    return {"product_ids": [item.product_id for item in items]}

@router.get("/wishlist/{user_id}/products", response_model=List[ProductResponse], tags=["Business"])
async def get_wishlist_products(user_id: str, lang: str = "vi", db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    if user_id != user["uid"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == user["uid"]).all()
    product_ids = [item.product_id for item in wishlist_items]
    
    if not product_ids:
        return []
        
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    
    results = []
    # Re-order fetched products to match the wishlist addition order or index them
    for p in products:
        p_res = ProductResponse.from_orm(p)
        if lang == "en":
            if p.name_en and not p.name_en.startswith("Error") and p.name_en != "":
                p_res.name = p.name_en
                if p.description_en: p_res.description = p.description_en
            else:
                p_res.name = smart_translate_name(p.name)
        
        shop = db.query(Shop).filter(Shop.id == p.shop_id).first()
        if shop:
            p_res.shop_address = shop.address
        results.append(p_res)
        
    return results

@router.post("/wishlist", tags=["Business"])
async def toggle_wishlist(action: WishlistAction, db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user["uid"],
        Wishlist.product_id == action.product_id
    ).first()
    
    if existing:
        db.delete(existing)
        db.commit()
        return {"status": "removed", "product_id": action.product_id}
    else:
        new_item = Wishlist(user_id=user["uid"], product_id=action.product_id)
        db.add(new_item)
        db.commit()
        return {"status": "added", "product_id": action.product_id}

@router.get("/notifications/{user_id}", response_model=List[NotificationResponse], tags=["Business"])
async def get_notifications(user_id: str, db: Session = Depends(get_db)):
    # Automatically add a mock notification if the user has none (for demo purposes)
    count = db.query(Notification).filter(Notification.user_id == user_id).count()
    if count == 0:
        mock1 = Notification(user_id=user_id, title="New AI Picks 🎁", message="Check out the latest curated items in Hoi An.", is_read=0)
        mock2 = Notification(user_id=user_id, title="Order Shipped 🚚", message="Your ceramic vase is on the way!", is_read=0)
        db.add(mock1)
        db.add(mock2)
        db.commit()
    
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.timestamp.desc()).all()

@router.post("/scan-product", tags=["Business"])
async def scan_product(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        analysis = await gemini_service.analyze_product_image(contents)
    except GeminiQuotaError as eq:
        raise HTTPException(status_code=429, detail={"message": eq.message, "reset_time": eq.reset_time_msg})
    except GeminiError as eg:
        raise HTTPException(status_code=500, detail={"message": eg.message, "technical_details": eg.details})
    return {"analysis": analysis}

@router.post("/visual-search", tags=["Business"])
async def visual_search(file: UploadFile = File(...), db: Session = Depends(get_db)):
    from google.genai import types
    try:
        contents = await file.read()
        
        # 1. Ask Gemini to identify the main product in the image and return search keywords
        prompt = (
            "Identify the main product shown in this image. "
            "Return a short search query in Vietnamese of 2-5 words (e.g., 'bộ ấm chén Bát Tràng', 'lọ hoa gốm sứ', 'cốc sứ có nắp') "
            "that can be used to search for this product in a database. "
            "Return ONLY the search query, nothing else."
        )
        input_content = [
            prompt,
            types.Part.from_bytes(data=contents, mime_type="image/jpeg")
        ]
        
        search_query = await gemini_service._generate_with_retry(contents=input_content)
        search_query = search_query.strip().replace("`", "").replace('"', '').replace("'", "")
        print(f"Visual search query extracted: '{search_query}'")
        
        # 2. Run our optimized get_products function using this extracted search query
        products_list = await get_products(search=search_query, db=db)
        
        # 3. Format the results as expected by the frontend
        products = []
        for p in products_list[:10]: # Return top 10 matches
            shop = db.query(Shop).filter(Shop.id == p.shop_id).first()
            products.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "tag": p.tag,
                "shop_name": shop.name if shop else "Unknown",
                "shop_address": shop.address if shop else "Unknown Address",
                "score": 0.95
            })
            
        return {"products": products}
        
    except Exception as e:
        print(f"Visual search error: {e}")
        return {"products": [], "error": str(e)}

@router.post("/sync", tags=["System"])
async def trigger_sync():
    try:
        sync_db_to_vector()
        return {"message": "Sync completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DetectDuplicateRequest(BaseModel):
    description: str
    user_id: str

@router.post("/detect-duplicate", tags=["Business"])
async def detect_duplicate(request: DetectDuplicateRequest, db: Session = Depends(get_db), user: dict = Depends(verify_firebase_token)):
    try:
        histories = db.query(History).filter(History.user_id == user["uid"]).all()
        existing_products = []
        for h in histories:
            product = db.query(Product).filter(Product.id == int(h.product_id)).first()
            if product:
                existing_products.append({
                    "id": product.id,
                    "text": f"{product.name} | {product.description}"
                })
        
        if not existing_products:
            return {
                "id": None,
                "text": None,
                "score": 0.0,
                "match_type": "None",
                "semantic_score": 0.0,
                "lexical_score": 0.0
            }

        detector = get_detector()
        result = detector.check_duplicate(request.description, existing_products)
        if result:
            return result
    except Exception as e:
        print(f"Duplicate detection error: {e}")

    return {
        "id": None,
        "text": None,
        "score": 0.0,
        "match_type": "None",
        "semantic_score": 0.0,
        "lexical_score": 0.0
    }
