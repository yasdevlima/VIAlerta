import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ResultadoIA(Base):
    __tablename__ = "resultados_ia"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ocorrencia_id = Column(String(36), ForeignKey("ocorrencias.id"), nullable=False, unique=True, index=True)
    
    buraco_detectado = Column(Boolean, nullable=False, default=False)
    quantidade_detectada = Column(Integer, nullable=False, default=0)
    confianca_media = Column(Float, nullable=False, default=0.0)
    area_relativa_total_pct = Column(Float, nullable=False, default=0.0)
    
    # Classificação visual baseada nas evidências da imagem: "Severa", "Moderada", "Leve", "Sem Buraco Identificado"
    classificacao_visual = Column(String(50), nullable=False, default="Sem Buraco Identificado")
    
    tempo_processamento_ms = Column(Float, nullable=False, default=0.0)
    status_processamento = Column(String(30), nullable=False, default="SUCESSO") # SUCESSO, SEM_DETECCAO, FALHA
    
    # JSON serializado com as coordenadas das caixas [xmin, ymin, xmax, ymax] e score de cada detecção
    detalhes_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ocorrencia = relationship("Ocorrencia", back_populates="resultado_ia")
