from datetime import datetime, timezone, timedelta
from app.models.ocorrencia import Ocorrencia
from app.services.geo_service import haversine_distance
from app.services.priority_service import calcular_indice_prioridade
from app.services.deduplication_service import verificar_possivel_duplicidade

def test_haversine_known_distance():
    # Coordenadas conhecidas no centro de SP (MASP até Edifício Copan ~ 2.4 km)
    masp_lat, masp_lon = -23.5614, -46.6559
    copan_lat, copan_lon = -23.5475, -46.6450
    dist = haversine_distance(masp_lat, masp_lon, copan_lat, copan_lon)
    assert 1800 < dist < 2600

def test_deduplication_detection(db_session):
    # Cria ocorrência base
    base_lat, base_lon = -23.5505, -46.6333
    ocorrencia_original = Ocorrencia(
        protocolo="VIA-20261119-ORIG1",
        descricao="Buraco profundo",
        status="PENDENTE",
        latitude=base_lat,
        longitude=base_lon,
        endereco="Praça da Sé, 100",
        bairro="Sé",
        cidade="São Paulo",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(ocorrencia_original)
    db_session.commit()

    # Ponto a 15 metros (deve sinalizar duplicidade)
    lat_proxima = base_lat + 0.0001
    lon_proxima = base_lon + 0.0001
    is_dup, ref_id = verificar_possivel_duplicidade(db_session, lat_proxima, lon_proxima)
    assert is_dup is True
    assert ref_id == ocorrencia_original.id

    # Ponto a 2 km (não deve sinalizar duplicidade)
    lat_longe = base_lat + 0.02
    lon_longe = base_lon + 0.02
    is_dup_longe, _ = verificar_possivel_duplicidade(db_session, lat_longe, lon_longe)
    assert is_dup_longe is False

def test_priority_index_calculation(db_session):
    # Teste 1: Buraco severo perto de hospital
    ipm_severo = calcular_indice_prioridade(
        db=db_session,
        latitude=-23.5577, # Em frente ao HC
        longitude=-46.6710,
        buraco_detectado=True,
        classificacao_visual="Severa",
        area_relativa_pct=12.5,
        created_at=datetime.now(timezone.utc) - timedelta(days=10)
    )
    assert ipm_severo >= 65.0

    # Teste 2: Ocorrência sem detecção e recente longe de hospital
    ipm_baixo = calcular_indice_prioridade(
        db=db_session,
        latitude=-23.7000,
        longitude=-46.8000,
        buraco_detectado=False,
        classificacao_visual="Sem Buraco Identificado",
        area_relativa_pct=0.0,
        created_at=datetime.now(timezone.utc)
    )
    assert ipm_baixo < 40.0
    assert ipm_severo > ipm_baixo
