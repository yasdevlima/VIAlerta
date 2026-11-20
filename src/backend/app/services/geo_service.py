import math
from typing import List, Tuple

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância em metros entre duas coordenadas geográficas
    utilizando a fórmula de Haversine.
    """
    R = 6371000.0  # Raio da Terra em metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c

# Pontos de referência de equipamentos públicos sensíveis (hospitais e polos educacionais em SP)
# Utilizados estritamente para demonstração fundamentada do cálculo do componente de proximidade sensível
EQUIPAMENTOS_SENSIVEIS: List[Tuple[str, str, float, float]] = [
    ("Hospital das Clínicas da FMUSP", "Saúde", -23.5577, -46.6710),
    ("Hospital São Paulo (UNIFESP)", "Saúde", -23.5976, -46.6433),
    ("Hospital Municipal Dr. Carmino Caricchio (Tatuapé)", "Saúde", -23.5358, -46.5746),
    ("Instituto do Coração (InCor)", "Saúde", -23.5571, -46.6698),
    ("Escola Estadual Caetano de Campos", "Educação", -23.5385, -46.6508),
    ("Colégio Bandeirantes", "Educação", -23.5786, -46.6496),
    ("Terminal Intermodal Palmeiras-Barra Funda", "Mobilidade/Tráfego", -23.5255, -46.6669),
    ("Terminal Rodoviário Tietê", "Mobilidade/Tráfego", -23.5161, -46.6248),
]

def obter_distancia_equipamento_mais_proximo(lat: float, lon: float) -> Tuple[float, str, str]:
    """
    Retorna a menor distância (em metros), nome e categoria do equipamento público sensível mais próximo.
    """
    menor_dist = float("inf")
    equipamento_nome = "Nenhum mapeado no raio"
    categoria = "Geral"

    for nome, cat, eq_lat, eq_lon in EQUIPAMENTOS_SENSIVEIS:
        dist = haversine_distance(lat, lon, eq_lat, eq_lon)
        if dist < menor_dist:
            menor_dist = dist
            equipamento_nome = nome
            categoria = cat

    return menor_dist, equipamento_nome, categoria
