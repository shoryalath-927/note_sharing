"""
NoteShare AI — FastAPI backend entry point.
Run with: uvicorn main:app --reload --port 8000
"""
import sys
import os

# Add backend parent to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from backend.database import init_db
from backend.config import settings
from backend.routers import notes, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables
    await init_db()
    print("✅ Database initialized")
    # Pre-load embedding model in background
    from backend.services.embedder import get_model
    get_model()  # This downloads model on first run
    yield
    # Shutdown cleanup (if needed)


app = FastAPI(
    title="NoteShare AI",
    description="AI-powered handwritten note scoring and recommendation platform for BTech students",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(notes.router, prefix="/api")
app.include_router(search.router, prefix="/api")


# Serve uploaded PDFs
uploads_dir = Path(settings.upload_dir)
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/")
async def root():
    return {
        "app": "NoteShare AI",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
