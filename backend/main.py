import os
import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables at the very beginning
load_dotenv()

# Get base directory of the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def initialize_firebase():
    if not firebase_admin._apps:
        # Try to get path from env, fallback to default name in backend dir
        env_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        
        # Check potential paths
        candidate_paths = []
        if env_path:
            candidate_paths.append(env_path)
            # Also try relative to project root if env_path is relative
            candidate_paths.append(os.path.abspath(env_path))
            # Also try relative to BASE_DIR
            candidate_paths.append(os.path.join(BASE_DIR, os.path.basename(env_path)))

        candidate_paths.append(os.path.join(BASE_DIR, "serviceAccountKey.json"))
        candidate_paths.append("serviceAccountKey.json")

        success = False
        for path in candidate_paths:
            if os.path.exists(path):
                try:
                    cred = credentials.Certificate(path)
                    firebase_admin.initialize_app(cred)
                    print(f"Firebase initialized successfully using {path}")
                    success = True
                    break
                except Exception as e:
                    print(f"Failed to initialize Firebase with {path}: {e}")
        
        if not success:
            print("CRITICAL: Could not initialize Firebase. Auth features will fail.")
            print(f"Checked paths: {candidate_paths}")

# Initialize Firebase BEFORE importing other modules that might use it
initialize_firebase()

from database import init_db
from api_contract import router as api_router

# Initialize database
init_db()

app = FastAPI(
    title="Smart Shopping System API",
    description="Backend API for Smart Shopping Project - BE 1",
    version="1.0.0"
)

# Register routers
app.include_router(api_router, prefix="/api/v1")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "env": os.getenv("APP_ENV", "development"),
        "version": "1.0.0"
    }

@app.get("/", tags=["System"])
async def root():
    return {"message": "Welcome to Smart Shopping System API"}
