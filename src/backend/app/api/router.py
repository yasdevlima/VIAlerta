from fastapi import APIRouter
from app.api.ocorrencias import router as ocorrencias_router
from app.api.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(ocorrencias_router)
api_router.include_router(admin_router)
