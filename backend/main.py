from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from backend.routers import chat, database, query, voice, visualization
from backend.services.database import db_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize resources if needed
    print("Starting AskDB API...")
    yield
    # Shutdown: Clean up resources
    print("Shutting down AskDB API...")
    try:
        db_service.disconnect()
    except Exception as e:
        print(f"Error during shutdown: {e}")

app = FastAPI(
    title="AskDB API",
    description="Backend API for AskDB - AI Database Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
origins = [
    "http://localhost:8501",  # Streamlit default port
    "http://localhost:3000",  # React default port (just in case)
    "*"  # Allow all for dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(database.router)
app.include_router(query.router)
app.include_router(voice.router)
app.include_router(visualization.router)

@app.get("/")
async def root():
    """
    Root endpoint to check if API is running.
    """
    return {
        "status": "running",
        "app": "AskDB API"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "version": app.version
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
