import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Ocorrencia(Base):
    __tablename__ = "ocorrencias"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    protocolo = Column(String(32), unique=True, index=True, nullable=False)
    descricao = Column(Text, nullable=True)
    status = Column(String(30), default="PENDENTE", index=True, nullable=False)
    # Status possíveis: PENDENTE, EM_ANALISE, PROGRAMADA, EM_ANDAMENTO, CONCLUIDA, REJEITADA
    
    # Geolocalização
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    endereco = Column(String(255), nullable=False)
    bairro = Column(String(100), nullable=False, index=True)
    cidade = Column(String(100), default="São Paulo", nullable=False)
    
    # Inteligência & Análise
    indice_prioridade = Column(Float, default=0.0) # 0 a 100
    possivel_duplicidade = Column(Boolean, default=False, index=True)
    ocorrencia_referencia_id = Column(String(36), ForeignKey("ocorrencias.id"), nullable=True)
    dados_demonstrativos = Column(Boolean, default=False)
    
    # Rastreabilidade temporal
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    imagem = relationship("Imagem", back_populates="ocorrencia", uselist=False, cascade="all, delete-orphan")
    resultado_ia = relationship("ResultadoIA", back_populates="ocorrencia", uselist=False, cascade="all, delete-orphan")
    historico = relationship("HistoricoStatus", back_populates="ocorrencia", cascade="all, delete-orphan", order_by="HistoricoStatus.created_at.desc()")
