import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Garante registro dos modelos no SQLAlchemy
from app.api.router import api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("viaalerta")

# Cria tabelas do banco de dados na inicialização
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ViaAlerta API — Inteligência Artificial aplicada à identificação e priorização de buracos nas vias urbanas.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir acesso irrestrito do frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir imagens estáticas de uploads (originais e anotadas)
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# Inclui rotas da API
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "projeto": "ViaAlerta",
        "tema": "CitizenTech — Global Solution FIAP 2026.2",
        "status": "Online",
        "versao": settings.VERSION,
        "docs_url": "/docs",
        "endpoints_principais": {
            "criar_ocorrencia": "POST /api/ocorrencias",
            "consultar_protocolo": "GET /api/ocorrencias/{protocolo}",
            "listar_ocorrencias": "GET /api/ocorrencias",
            "dashboard_admin": "GET /api/admin/dashboard",
            "mapa_pontos": "GET /api/admin/mapa",
            "atualizar_status": "PATCH /api/admin/ocorrencias/{id}/status"
        }
    }
