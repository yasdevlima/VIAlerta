import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Imagem(Base):
    __tablename__ = "imagens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ocorrencia_id = Column(String(36), ForeignKey("ocorrencias.id"), nullable=False, unique=True, index=True)
    
    nome_arquivo_original = Column(String(255), nullable=False)
    nome_arquivo_anotada = Column(String(255), nullable=True)
    caminho_relativo_original = Column(String(500), nullable=False)
    caminho_relativo_anotada = Column(String(500), nullable=True)
    
    tamanho_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(50), nullable=False)
    hash_sha256 = Column(String(64), nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ocorrencia = relationship("Ocorrencia", back_populates="imagem")
