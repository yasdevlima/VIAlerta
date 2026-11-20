from datetime import datetime, timezone, timedelta
from typing import List, Optional
from collections import Counter
from pathlib import Path
import random

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.models.ocorrencia import Ocorrencia
from app.models.imagem import Imagem
from app.models.resultado_ia import ResultadoIA
from app.models.historico_status import HistoricoStatus
from app.schemas.ocorrencia import (
    StatusUpdateIn,
    DashboardIndicadores,
    PontoMapa,
    OcorrenciaOut
)
from app.api.ocorrencias import serialize_ocorrencia

router = APIRouter(prefix="/admin", tags=["Administração e Auditoria"])

STATUS_VALIDOS = ["PENDENTE", "EM_ANALISE", "PROGRAMADA", "EM_ANDAMENTO", "CONCLUIDA", "REJEITADA"]

@router.patch("/ocorrencias/{ocorrencia_id}/status", response_model=OcorrenciaOut)
def atualizar_status_ocorrencia(
    ocorrencia_id: str,
    dados: StatusUpdateIn,
    db: Session = Depends(get_db)
):
    novo_status = dados.novo_status.strip().upper()
    if novo_status not in STATUS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status '{novo_status}' inválido. Valores aceitos: {', '.join(STATUS_VALIDOS)}."
        )

    ocorrencia = db.query(Ocorrencia).filter(Ocorrencia.id == ocorrencia_id).first()
    if not ocorrencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ocorrência não encontrada."
        )

    status_anterior = ocorrencia.status
    ocorrencia.status = novo_status
    ocorrencia.updated_at = datetime.now(timezone.utc)

    # Registra no histórico de auditoria
    historico = HistoricoStatus(
        ocorrencia_id=ocorrencia.id,
        status_anterior=status_anterior,
        status_novo=novo_status,
        motivo_observacao=dados.motivo_observacao or f"Status alterado para {novo_status}",
        autor=dados.autor or "Administrador ViaAlerta"
    )
    db.add(historico)
    db.commit()
    db.refresh(ocorrencia)

    return serialize_ocorrencia(ocorrencia)

@router.get("/dashboard", response_model=DashboardIndicadores)
def obter_indicadores_dashboard(db: Session = Depends(get_db)):
    ocorrencias = db.query(Ocorrencia).all()
    total = len(ocorrencias)

    if total == 0:
        return DashboardIndicadores(
            total_ocorrencias=0,
            total_buracos_detectados_ia=0,
            taxa_deteccao_pct=0.0,
            ocorrencias_pendentes=0,
            ocorrencias_em_andamento=0,
            ocorrencias_concluidas=0,
            ocorrencias_outros_status=0,
            total_possiveis_duplicidades=0,
            distribuicao_bairros={},
            distribuicao_severidade={},
            tempo_medio_resolucao_dias=0.0
        )

    buracos_count = 0
    pendentes = 0
    em_andamento = 0
    concluidas = 0
    outros = 0
    duplicidades = 0
    bairros = []
    severidades = []
    tempos_resolucao = []

    for o in ocorrencias:
        if o.status == "PENDENTE":
            pendentes += 1
        elif o.status in ["EM_ANDAMENTO", "EM_ANALISE", "PROGRAMADA"]:
            em_andamento += 1
        elif o.status == "CONCLUIDA":
            concluidas += 1
            if o.created_at and o.updated_at:
                c_at = o.created_at if o.created_at.tzinfo else o.created_at.replace(tzinfo=timezone.utc)
                u_at = o.updated_at if o.updated_at.tzinfo else o.updated_at.replace(tzinfo=timezone.utc)
                tempos_resolucao.append((u_at - c_at).total_seconds() / 86400.0)
        else:
            outros += 1

        if o.possivel_duplicidade:
            duplicidades += 1

        if o.bairro:
            bairros.append(o.bairro)

        if o.resultado_ia:
            if o.resultado_ia.buraco_detectado:
                buracos_count += 1
            severidades.append(o.resultado_ia.classificacao_visual)

    dist_bairros = dict(Counter(bairros).most_common(10))
    dist_sev = dict(Counter(severidades))

    taxa_deteccao = round((buracos_count / total) * 100, 1) if total > 0 else 0.0
    tempo_medio = round(sum(tempos_resolucao) / len(tempos_resolucao), 1) if tempos_resolucao else 0.0

    return DashboardIndicadores(
        total_ocorrencias=total,
        total_buracos_detectados_ia=buracos_count,
        taxa_deteccao_pct=taxa_deteccao,
        ocorrencias_pendentes=pendentes,
        ocorrencias_em_andamento=em_andamento,
        ocorrencias_concluidas=concluidas,
        ocorrencias_outros_status=outros,
        total_possiveis_duplicidades=duplicidades,
        distribuicao_bairros=dist_bairros,
        distribuicao_severidade=dist_sev,
        tempo_medio_resolucao_dias=tempo_medio
    )

@router.get("/mapa", response_model=List[PontoMapa])
def obter_pontos_mapa(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    query = db.query(Ocorrencia)
    if status_filter:
        query = query.filter(Ocorrencia.status == status_filter.upper())

    ocorrencias = query.all()
    pontos = []

    for o in ocorrencias:
        url_thumb = None
        if o.imagem:
            url_thumb = f"/uploads/anotadas/{o.imagem.nome_arquivo_anotada}" if o.imagem.nome_arquivo_anotada else f"/uploads/originais/{o.imagem.nome_arquivo_original}"

        buraco_det = o.resultado_ia.buraco_detectado if o.resultado_ia else False
        qtd_det = o.resultado_ia.quantidade_detectada if o.resultado_ia else 0
        classe_vis = o.resultado_ia.classificacao_visual if o.resultado_ia else "Sem Análise"

        pontos.append(PontoMapa(
            id=o.id,
            protocolo=o.protocolo,
            latitude=o.latitude,
            longitude=o.longitude,
            endereco=o.endereco,
            bairro=o.bairro,
            status=o.status,
            indice_prioridade=o.indice_prioridade,
            buraco_detectado=buraco_det,
            quantidade_detectada=qtd_det,
            classificacao_visual=classe_vis,
            url_thumbnail=url_thumb,
            possivel_duplicidade=o.possivel_duplicidade,
            created_at=o.created_at
        ))

    return pontos

@router.post("/seed-demo")
def semear_dados_demonstracao(db: Session = Depends(get_db)):
    """
    Semeia ocorrências demonstrativas realistas para apresentação e testes no mapa.
    Todos os registros são formalmente marcados com dados_demonstrativos = True.
    """
    existentes = db.query(Ocorrencia).filter(Ocorrencia.dados_demonstrativos == True).count()
    if existentes >= 5:
        return {"mensagem": f"Base demonstrativa já populada ({existentes} registros de teste existentes)."}

    # Pontos reais em bairros de São Paulo para consistência cartográfica
    amostras_sp = [
        {"endereco": "Av. Paulista, 1100", "bairro": "Bela Vista", "lat": -23.5645, "lon": -46.6521, "sev": "Moderada", "buraco": True, "qtd": 1, "status": "PENDENTE", "ipm": 72.5},
        {"endereco": "Rua Augusta, 1500", "bairro": "Consolação", "lat": -23.5539, "lon": -46.6578, "sev": "Severa", "buraco": True, "qtd": 3, "status": "EM_ANDAMENTO", "ipm": 88.0},
        {"endereco": "Av. Brigadeiro Faria Lima, 2232", "bairro": "Pinheiros", "lat": -23.5768, "lon": -46.6892, "sev": "Leve", "buraco": True, "qtd": 1, "status": "PROGRAMADA", "ipm": 48.0},
        {"endereco": "Rua Domingos de Morais, 1200", "bairro": "Vila Mariana", "lat": -23.5852, "lon": -46.6385, "sev": "Severa", "buraco": True, "qtd": 2, "status": "PENDENTE", "ipm": 85.0},
        {"endereco": "Rua da Mooca, 2500", "bairro": "Mooca", "lat": -23.5558, "lon": -46.6025, "sev": "Moderada", "buraco": True, "qtd": 2, "status": "CONCLUIDA", "ipm": 66.0},
        {"endereco": "Rua Voluntários da Pátria, 1800", "bairro": "Santana", "lat": -23.5042, "lon": -46.6272, "sev": "Sem Buraco Identificado", "buraco": False, "qtd": 0, "status": "REJEITADA", "ipm": 12.0},
        {"endereco": "Av. Rebouças, 2000", "bairro": "Pinheiros", "lat": -23.5670, "lon": -46.6780, "sev": "Severa", "buraco": True, "qtd": 3, "status": "EM_ANALISE", "ipm": 91.5},
    ]

    criados = 0
    now = datetime.now(timezone.utc)

    for i, item in enumerate(amostras_sp):
        dt_criacao = now - timedelta(days=random.randint(1, 14), hours=random.randint(1, 12))
        proto = f"VIA-{dt_criacao.strftime('%Y%m%d')}-DEMO{i+1}"
        
        nova = Ocorrencia(
            protocolo=proto,
            descricao=f"Registro demonstrativo para homologação do sistema ({item['sev']}).",
            status=item["status"],
            latitude=item["lat"],
            longitude=item["lon"],
            endereco=item["endereco"],
            bairro=item["bairro"],
            cidade="São Paulo",
            indice_prioridade=item["ipm"],
            possivel_duplicidade=(i == 3), # Exemplo de duplicidade demonstrativa
            dados_demonstrativos=True,
            created_at=dt_criacao,
            updated_at=dt_criacao + timedelta(hours=4)
        )
        db.add(nova)
        db.flush()

        # Cria imagem e resultado IA fictício demonstrativo
        img = Imagem(
            ocorrencia_id=nova.id,
            nome_arquivo_original="sample_demo.jpg",
            nome_arquivo_anotada="sample_demo_anotada.jpg" if item["buraco"] else None,
            caminho_relativo_original="uploads/originais/sample_demo.jpg",
            caminho_relativo_anotada="uploads/anotadas/sample_demo_anotada.jpg",
            tamanho_bytes=45200,
            mime_type="image/jpeg",
            hash_sha256=f"demo_hash_{i}_{nova.id}"
        )
        db.add(img)

        ia = ResultadoIA(
            ocorrencia_id=nova.id,
            buraco_detectado=item["buraco"],
            quantidade_detectada=item["qtd"],
            confianca_media=0.84 if item["buraco"] else 0.0,
            area_relativa_total_pct=8.5 if item["buraco"] else 0.0,
            classificacao_visual=item["sev"],
            tempo_processamento_ms=2800.0,
            status_processamento="SUCESSO" if item["buraco"] else "SEM_DETECCAO",
            detalhes_json="[]"
        )
        db.add(ia)

        hist = HistoricoStatus(
            ocorrencia_id=nova.id,
            status_anterior=None,
            status_novo=item["status"],
            motivo_observacao="Registro gerado para homologação e testes de interface.",
            autor="Simulador ViaAlerta",
            created_at=dt_criacao
        )
        db.add(hist)
        criados += 1

    db.commit()
    return {"mensagem": f"Sucesso! {criados} registros demonstrativos foram inseridos com a flag dados_demonstrativos=True."}
