"""Central API router grouping all v1 sub-routers."""
from fastapi import APIRouter
from backend.app.api.routes import auth, analyze, history, feedback, weather, diseases, health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(analyze.router)
api_router.include_router(history.router)
api_router.include_router(feedback.router)
api_router.include_router(weather.router)
api_router.include_router(diseases.router)
api_router.include_router(health.router)
