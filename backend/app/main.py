"""Main FastAPI application entry point with lifespan management, CORS, static uploads, and Prometheus metrics."""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

from backend.app.core.config import settings
from backend.app.api.router import api_router
from backend.app.api.deps import limiter
from backend.app.db.session import init_db
from backend.app.ml.inference import load_inference_artifacts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler: run migrations/init_db and load ONNX model once."""
    print("=== Starting AgriShield AI Backend Service ===")
    # 1. Ensure upload directory exists
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # 2. Initialize Database tables
    await init_db()
    print("Database tables initialized.")
    
    # 3. Load ML model into memory
    load_inference_artifacts()
    
    yield
    print("=== Stopping AgriShield AI Backend Service ===")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered Crop Disease Detection and Environmental Outbreak Risk Prediction Platform for Farmers.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set SlowAPI rate limiter
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}. Please slow down your requests."}
    )


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploaded images
static_dir = Path("backend/app/static")
static_dir.mkdir(parents=True, exist_ok=True)
uploads_dir = static_dir / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include API v1 routes
app.include_router(api_router)

# Prometheus Metrics Instrumentation
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/docs",
        "health": "/api/v1/health",
        "model_info": "/api/v1/model/info"
    }
