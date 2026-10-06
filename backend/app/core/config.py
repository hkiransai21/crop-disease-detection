"""Application configuration settings managed via Pydantic v2."""
import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Settings
    PROJECT_NAME: str = "AgriShield AI Crop Disease & Outbreak Risk System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"
    ]

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-0123456789abcdef"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours for seamless farmer access
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./backend/app.db"

    # Storage
    UPLOAD_DIR: str = "./backend/app/static/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]

    # ML Inference
    MODEL_PATH: str = "./ml/models/efficientnet_b0_plantvillage.onnx"
    QUANTIZED_MODEL_PATH: str = "./ml/models/efficientnet_b0_plantvillage_int8.onnx"
    LABELS_PATH: str = "./ml/models/labels.json"
    MODEL_VERSION_PATH: str = "./ml/models/model_version"
    TEMPERATURE_PATH: str = "./ml/models/temperature.json"
    CONFIDENCE_THRESHOLD: float = 0.60
    UNCERTAIN_ENTROPY_THRESHOLD: float = 2.20

    # Knowledge Base
    KNOWLEDGE_BASE_PATH: str = "./backend/app/knowledge_base/diseases.yaml"

    # Weather & Geocoding APIs (Free Open-Meteo)
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    GEOCODING_BASE_URL: str = "https://geocoding-api.open-meteo.com/v1"
    WEATHER_CACHE_TTL_SECONDS: int = 1800 # 30 minutes cache

    # Rate Limiting
    RATE_LIMIT_ANALYZE: str = "30/minute"
    RATE_LIMIT_AUTH: str = "15/minute"


settings = Settings()
