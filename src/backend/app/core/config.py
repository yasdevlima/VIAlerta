import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    PROJECT_NAME: str = "ViaAlerta API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    ORIGINAIS_DIR: Path = UPLOAD_DIR / "originais"
    ANOTADAS_DIR: Path = UPLOAD_DIR / "anotadas"
    
    # AI Model Path (points to data/models/pothole_yolov8.pt)
    ROOT_DATA_DIR: Path = BASE_DIR.parent.parent / "data"
    MODEL_PATH: Path = ROOT_DATA_DIR / "models" / "pothole_yolov8.pt"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/viaalerta.db")
    
    # Security & limits
    MAX_IMAGE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_MIME_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Priority & Deduplication thresholds
    DEDUP_DISTANCE_METERS: float = 50.0
    DEDUP_DAYS_WINDOW: int = 30
    


settings = Settings()

# Ensure directories exist
settings.ORIGINAIS_DIR.mkdir(parents=True, exist_ok=True)
settings.ANOTADAS_DIR.mkdir(parents=True, exist_ok=True)
