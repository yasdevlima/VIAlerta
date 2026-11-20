import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class HistoricoStatus(Base):
    __tablename__ = "historico_status"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ocorrencia_id = Column(String(36), ForeignKey("ocorrencias.id"), nullable=False, index=True)
    
    status_anterior = Column(String(30), nullable=True)
    status_novo = Column(String(30), nullable=False)
    motivo_observacao = Column(Text, nullable=True)
    autor = Column(String(100), default="Sistema ViaAlerta", nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ocorrencia = relationship("Ocorrencia", back_populates="historico")
