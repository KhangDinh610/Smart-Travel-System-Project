import os
import sys
import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
# Try to find .env in current dir, then in parent dir
if not load_dotenv():
    # If not found in current dir, try parent dir
    root_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(root_env):
        load_dotenv(root_env)
        print(f"Loaded environment variables from {root_env}")
    else:
        print("Warning: .env file not found. Environment variables might not be set.")
else:
    print("Loaded environment variables from .env")

# Get base directory of the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add BASE_DIR to sys.path to ensure local modules can be imported
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

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

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Initialize Firebase BEFORE importing other modules that might use it
initialize_firebase()

from database import init_db
from api_contract import router as api_router

# Sync to VectorDB for smart features
from api_contract import sync_db_to_vector

def check_and_seed_db():
    from database import SessionLocal, Product
    db = SessionLocal()
    try:
        count = db.query(Product).count()
        if count == 0:
            print("Database is empty. Running seeding script...")
            from seed_db import seed_database
            seed_database()
        else:
            print(f"Database already has {count} products.")
    except Exception as e:
        print(f"Error checking/seeding database: {e}")
    finally:
        db.close()

# Initialize database and seed if empty
init_db()
check_and_seed_db()

# Sync to VectorDB
sync_db_to_vector()

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

# Serve static files from the frontend build directory
# This allows the backend to host the frontend on the same port
# We use path.join(os.path.dirname(BASE_DIR), "frontend", "dist")
frontend_dist = os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    print(f"Warning: Frontend distribution directory not found at {frontend_dist}")

