import os
import requests
import firebase_admin
from firebase_admin import credentials, auth, firestore
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import routes
from routes import duplicate

load_dotenv()

# Khởi tạo Firebase Admin SDK
try:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
except Exception as e:
    print("Cảnh báo: Không thể khởi tạo Firebase Admin SDK. Cần có serviceAccountKey.json hợp lệ.", e)

app = FastAPI(
    title="Smart Shopping System API",
    description="Backend API for Smart Shopping Project with Duplicate Detection",
    version="1.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = firestore.client()

# Register routers
app.include_router(duplicate.router)

# --- Auth Models & Logic (Tham khảo từ todo_app) ---

class AuthRequest(BaseModel):
    email: str
    password: str

FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "key1")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "key2")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "key3")

@app.post("/register", tags=["Auth"])
def register(request: AuthRequest):
    try:
        user = auth.create_user(
            email=request.email,
            password=request.password
        )
        # Khởi tạo user trong Firestore
        db.collection("users").document(user.uid).set({
            "email": request.email,
            "role": "user"
        })
        return {"message": "Tạo tài khoản thành công", "uid": user.uid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login", tags=["Auth"])
def login(user: AuthRequest):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if response.status_code == 200:
        return {
            "message": "Login successful",
            "idToken": data["idToken"],
            "localId": data["localId"]
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid email or password")

class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: str

@app.post("/login/google", tags=["Auth"])
def login_google(request: GoogleAuthRequest):
    # Đổi code lấy Google tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": request.code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": request.redirect_uri,
        "grant_type": "authorization_code"
    }
    token_r = requests.post(token_url, data=token_data)
    if token_r.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Xác thực với Google thất bại. Chi tiết: {token_r.text}")
    
    google_tokens = token_r.json()
    google_id_token = google_tokens.get("id_token")
    
    # Verify Google token
    tokeninfo_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={google_id_token}"
    info_r = requests.get(tokeninfo_url)
    if info_r.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token từ Google không hợp lệ. Chi tiết: {info_r.text}")
        
    user_info = info_r.json()
    email = user_info.get("email")
    
    try:
        user_record = auth.get_user_by_email(email)
        uid = user_record.uid
    except Exception:
        user_record = auth.create_user(email=email)
        uid = user_record.uid
        
    custom_token = auth.create_custom_token(uid)
    if isinstance(custom_token, bytes):
        custom_token = custom_token.decode("utf-8")
        
    firebase_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={FIREBASE_WEB_API_KEY}"
    firebase_payload = {"token": custom_token, "returnSecureToken": True}
    firebase_r = requests.post(firebase_url, json=firebase_payload)
    if firebase_r.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Đăng nhập Firebase bằng Custom Token thất bại. Chi tiết: {firebase_r.text}")
        
    firebase_data = firebase_r.json()
    
    # Cập nhật Firestore
    user_ref = db.collection("users").document(uid)
    if not user_ref.get().exists:
        user_ref.set({"email": email, "role": "user"})
        
    return {
        "message": "Google Login successful",
        "idToken": firebase_data["idToken"],
        "localId": uid
    }

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "version": "1.1.0"}

@app.get("/", tags=["System"])
async def root():
    return {"message": "Welcome to Smart Shopping System API with Duplicate Detection"}
