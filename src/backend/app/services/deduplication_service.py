from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.ocorrencia import Ocorrencia
from app.services.geo_service import haversine_distance
from app.core.config import settings

def verificar_possivel_duplicidade(
    db: Session,
    latitude: float,
    longitude: float,
    current_id: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Verifica se existe ocorrência aberta ou recente registrada num raio <= 50 metros
    dentro do intervalo de 30 dias.
    Retorna (is_duplicata, id_ocorrencia_referencia).
    """
    limite_tempo = datetime.now(timezone.utc) - timedelta(days=settings.DEDUP_DAYS_WINDOW)
    
    # Busca ocorrências ativas ou recentes
    query = db.query(Ocorrencia).filter(Ocorrencia.created_at >= limite_tempo)
    if current_id:
        query = query.filter(Ocorrencia.id != current_id)
        
    candidatos = query.all()

    for cand in candidatos:
        distancia = haversine_distance(latitude, longitude, cand.latitude, cand.longitude)
        if distancia <= settings.DEDUP_DISTANCE_METERS:
            # Encontrou ocorrência próxima e temporalmente correlacionada
            ref_id = cand.ocorrencia_referencia_id if cand.ocorrencia_referencia_id else cand.id
            return True, ref_id

    return False, None
