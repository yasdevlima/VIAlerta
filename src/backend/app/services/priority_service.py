from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.ocorrencia import Ocorrencia
from app.services.geo_service import haversine_distance, obter_distancia_equipamento_mais_proximo

def calcular_indice_prioridade(
    db: Session,
    latitude: float,
    longitude: float,
    buraco_detectado: bool,
    classificacao_visual: str,
    area_relativa_pct: float,
    created_at: datetime = None
) -> float:
    """
    Calcula o Índice de Prioridade de Manutenção (IPM) em escala de 0 a 100 pontos:
    
    IPM = w1*S_visual + w2*S_reincidencia + w3*S_tempo + w4*S_sensivel
    
    Pesos:
    - w1 (Visual): 0.35
    - w2 (Reincidência): 0.25
    - w3 (Tempo/Espera): 0.20
    - w4 (Equipamento Sensível): 0.20
    
    Transparência: A pontuação é uma recomendação de apoio à decisão operacional,
    não substituindo avaliação técnica presencial.
    """
    # 1. Componente Visual (0 a 100)
    if not buraco_detectado:
        s_visual = 10.0  # Pontuação mínima para verificação caso cidadão tenha apontado algo
    else:
        if classificacao_visual == "Severa":
            s_visual = min(100.0, 75.0 + (area_relativa_pct * 1.5))
        elif classificacao_visual == "Moderada":
            s_visual = min(74.0, 50.0 + (area_relativa_pct * 2.0))
        else: # Leve
            s_visual = min(49.0, 25.0 + (area_relativa_pct * 3.0))

    # 2. Componente de Reincidência na Região (0 a 100)
    # Contabiliza quantos outros chamados foram abertos num raio de 150m
    ocorrencias_proximas = 0
    candidatos = db.query(Ocorrencia).filter(Ocorrencia.status != "CONCLUIDA").all()
    for o in candidatos:
        if haversine_distance(latitude, longitude, o.latitude, o.longitude) <= 150.0:
            ocorrencias_proximas += 1

    # Escala de reincidência: 1 chamado = 20 pts, 2 = 45 pts, 3 = 70 pts, 4+ = 100 pts
    if ocorrencias_proximas <= 1:
        s_reincidencia = 20.0
    elif ocorrencias_proximas == 2:
        s_reincidencia = 45.0
    elif ocorrencias_proximas == 3:
        s_reincidencia = 70.0
    else:
        s_reincidencia = 100.0

    # 3. Componente de Tempo de Espera (0 a 100)
    now_utc = datetime.now(timezone.utc)
    if created_at is None:
        created_at = now_utc
    elif created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    
    delta = now_utc - created_at
    dias_espera = max(0.0, delta.total_seconds() / 86400.0)
    # 0 dias = 15 pts; a cada 5 dias acrescenta 20 pts até teto de 100
    s_tempo = min(100.0, 15.0 + (dias_espera * 4.0))

    # 4. Componente de Proximidade com Equipamentos Sensíveis (0 a 100)
    # Se <= 150m de hospital/escola: 100 pts
    # Se <= 350m: 75 pts
    # Se <= 700m: 45 pts
    # Acima de 700m: 15 pts
    dist_sensivel, _, _ = obter_distancia_equipamento_mais_proximo(latitude, longitude)
    if dist_sensivel <= 150.0:
        s_sensivel = 100.0
    elif dist_sensivel <= 350.0:
        s_sensivel = 75.0
    elif dist_sensivel <= 700.0:
        s_sensivel = 45.0
    else:
        s_sensivel = 15.0

    # Combinação ponderada linear
    ipm = (0.35 * s_visual) + (0.25 * s_reincidencia) + (0.20 * s_tempo) + (0.20 * s_sensivel)
    
    return round(float(min(100.0, max(0.0, ipm))), 1)
