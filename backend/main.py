import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import init_db
from api_contract import router as api_router

# Load environment variables
load_dotenv()

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
