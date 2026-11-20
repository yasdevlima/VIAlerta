import uuid
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, List
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.config import settings
from app.models.ocorrencia import Ocorrencia
from app.models.imagem import Imagem
from app.models.resultado_ia import ResultadoIA
from app.models.historico_status import HistoricoStatus
from app.schemas.ocorrencia import (
    OcorrenciaOut,
    OcorrenciaCreateResponse,
    ImagemOut,
    ResultadoIAOut,
    HistoricoStatusOut,
    DeteccaoBox
)
from app.services.ai_service import pothole_service
from app.services.deduplication_service import verificar_possivel_duplicidade
from app.services.priority_service import calcular_indice_prioridade

router = APIRouter(prefix="/ocorrencias", tags=["Ocorrências"])

def gerar_protocolo() -> str:
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_suffix = uuid.uuid4().hex[:5].upper()
    return f"VIA-{now_str}-{random_suffix}"

def serialize_ocorrencia(o: Ocorrencia) -> dict:
    img_out = None
    if o.imagem:
        img_out = {
            "id": o.imagem.id,
            "nome_arquivo_original": o.imagem.nome_arquivo_original,
            "nome_arquivo_anotada": o.imagem.nome_arquivo_anotada,
            "url_original": f"/uploads/originais/{o.imagem.nome_arquivo_original}",
            "url_anotada": f"/uploads/anotadas/{o.imagem.nome_arquivo_anotada}" if o.imagem.nome_arquivo_anotada else None,
            "tamanho_bytes": o.imagem.tamanho_bytes,
            "mime_type": o.imagem.mime_type,
            "created_at": o.imagem.created_at
        }

    ia_out = None
    if o.resultado_ia:
        detalhes_list = []
        if o.resultado_ia.detalhes_json:
            try:
                raw_boxes = json.loads(o.resultado_ia.detalhes_json)
                detalhes_list = [DeteccaoBox(**box) for box in raw_boxes]
            except Exception:
                detalhes_list = []

        ia_out = {
            "id": o.resultado_ia.id,
            "buraco_detectado": o.resultado_ia.buraco_detectado,
            "quantidade_detectada": o.resultado_ia.quantidade_detectada,
            "confianca_media": o.resultado_ia.confianca_media,
            "area_relativa_total_pct": o.resultado_ia.area_relativa_total_pct,
            "classificacao_visual": o.resultado_ia.classificacao_visual,
            "tempo_processamento_ms": o.resultado_ia.tempo_processamento_ms,
            "status_processamento": o.resultado_ia.status_processamento,
            "detalhes": detalhes_list,
            "created_at": o.resultado_ia.created_at
        }

    historico_list = [
        {
            "id": h.id,
            "status_anterior": h.status_anterior,
            "status_novo": h.status_novo,
            "motivo_observacao": h.motivo_observacao,
            "autor": h.autor,
            "created_at": h.created_at
        }
        for h in (o.historico or [])
    ]

    return {
        "id": o.id,
        "protocolo": o.protocolo,
        "descricao": o.descricao,
        "status": o.status,
        "latitude": o.latitude,
        "longitude": o.longitude,
        "endereco": o.endereco,
        "bairro": o.bairro,
        "cidade": o.cidade,
        "indice_prioridade": o.indice_prioridade,
        "possivel_duplicidade": o.possivel_duplicidade,
        "ocorrencia_referencia_id": o.ocorrencia_referencia_id,
        "dados_demonstrativos": o.dados_demonstrativos,
        "created_at": o.created_at,
        "updated_at": o.updated_at,
        "imagem": img_out,
        "resultado_ia": ia_out,
        "historico": historico_list
    }

@router.post("", response_model=OcorrenciaCreateResponse, status_code=status.HTTP_201_CREATED)
async def criar_ocorrencia(
    foto: UploadFile = File(..., description="Fotografia da via pública"),
    latitude: float = Form(..., description="Latitude da ocorrência"),
    longitude: float = Form(..., description="Longitude da ocorrência"),
    endereco: str = Form(..., min_length=3, description="Endereço aproximado ou logradouro"),
    bairro: str = Form(..., min_length=2, description="Bairro do logradouro"),
    descricao: Optional[str] = Form(None, description="Observações complementares do cidadão"),
    cidade: Optional[str] = Form("São Paulo", description="Cidade da ocorrência"),
    db: Session = Depends(get_db)
):
    # 1. Validação de formato da imagem
    if foto.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de imagem inválido ({foto.content_type}). Permitidos: JPEG, PNG, WEBP."
        )

    # 2. Leitura e limitação de tamanho
    conteudo = await foto.read()
    tamanho_bytes = len(conteudo)
    if tamanho_bytes > settings.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo excede o limite máximo permitido de {settings.MAX_IMAGE_SIZE_BYTES // (1024*1024)}MB."
        )

    # 3. Hash SHA256 para auditoria
    sha256_hash = hashlib.sha256(conteudo).hexdigest()

    # 4. Gravação física em diretório seguro
    extensao = Path(foto.filename or "imagem.jpg").suffix.lower()
    if not extensao or extensao not in [".jpg", ".jpeg", ".png", ".webp"]:
        extensao = ".jpg"
    
    file_id = uuid.uuid4().hex
    nome_original = f"{file_id}_original{extensao}"
    nome_anotada = f"{file_id}_anotada.jpg"
    
    path_original = settings.ORIGINAIS_DIR / nome_original
    path_anotada = settings.ANOTADAS_DIR / nome_anotada

    with open(path_original, "wb") as f:
        f.write(conteudo)

    # 5. Execução real do componente de IA e Visão Computacional
    ai_result = pothole_service.process_image(path_original, path_anotada)

    # 6. Verificação de Duplicidade Geoespacial & Temporal (Haversine)
    is_duplicata, ref_id = verificar_possivel_duplicidade(db, latitude, longitude)

    # 7. Cálculo do Índice de Prioridade de Manutenção (IPM)
    ipm = calcular_indice_prioridade(
        db=db,
        latitude=latitude,
        longitude=longitude,
        buraco_detectado=ai_result["buraco_detectado"],
        classificacao_visual=ai_result["classificacao_visual"],
        area_relativa_pct=ai_result["area_relativa_total_pct"]
    )

    # 8. Persistência transacional
    protocolo = gerar_protocolo()
    nova_ocorrencia = Ocorrencia(
        protocolo=protocolo,
        descricao=descricao,
        status="PENDENTE",
        latitude=latitude,
        longitude=longitude,
        endereco=endereco.strip(),
        bairro=bairro.strip(),
        cidade=cidade.strip(),
        indice_prioridade=ipm,
        possivel_duplicidade=is_duplicata,
        ocorrencia_referencia_id=ref_id,
        dados_demonstrativos=False
    )
    db.add(nova_ocorrencia)
    db.flush()

    # Registra imagem
    img_model = Imagem(
        ocorrencia_id=nova_ocorrencia.id,
        nome_arquivo_original=nome_original,
        nome_arquivo_anotada=nome_anotada if ai_result["buraco_detectado"] or path_anotada.exists() else None,
        caminho_relativo_original=f"uploads/originais/{nome_original}",
        caminho_relativo_anotada=f"uploads/anotadas/{nome_anotada}",
        tamanho_bytes=tamanho_bytes,
        mime_type=foto.content_type,
        hash_sha256=sha256_hash
    )
    db.add(img_model)

    # Registra resultado IA
    resultado_ia_model = ResultadoIA(
        ocorrencia_id=nova_ocorrencia.id,
        buraco_detectado=ai_result["buraco_detectado"],
        quantidade_detectada=ai_result["quantidade_detectada"],
        confianca_media=ai_result["confianca_media"],
        area_relativa_total_pct=ai_result["area_relativa_total_pct"],
        classificacao_visual=ai_result["classificacao_visual"],
        tempo_processamento_ms=ai_result["tempo_processamento_ms"],
        status_processamento=ai_result["status_processamento"],
        detalhes_json=json.dumps(ai_result["detalhes"])
    )
    db.add(resultado_ia_model)

    # Registra histórico inicial
    hist = HistoricoStatus(
        ocorrencia_id=nova_ocorrencia.id,
        status_anterior=None,
        status_novo="PENDENTE",
        motivo_observacao=f"Ocorrência registrada pelo cidadão. Processamento de IA: {ai_result['classificacao_visual']} ({ai_result['quantidade_detectada']} detecções).",
        autor="Sistema ViaAlerta"
    )
    db.add(hist)

    db.commit()
    db.refresh(nova_ocorrencia)

    return OcorrenciaCreateResponse(
        protocolo=nova_ocorrencia.protocolo,
        id=nova_ocorrencia.id,
        status=nova_ocorrencia.status,
        mensagem="Ocorrência registrada e analisada com sucesso!",
        indice_prioridade=nova_ocorrencia.indice_prioridade,
        possivel_duplicidade=nova_ocorrencia.possivel_duplicidade,
        buraco_detectado=ai_result["buraco_detectado"],
        quantidade_detectada=ai_result["quantidade_detectada"],
        classificacao_visual=ai_result["classificacao_visual"],
        created_at=nova_ocorrencia.created_at
    )

@router.get("/{protocolo}", response_model=OcorrenciaOut)
def consultar_por_protocolo(protocolo: str, db: Session = Depends(get_db)):
    ocorrencia = db.query(Ocorrencia).filter(Ocorrencia.protocolo == protocolo.strip().upper()).first()
    if not ocorrencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhuma ocorrência encontrada com o protocolo '{protocolo}'."
        )
    return serialize_ocorrencia(ocorrencia)

@router.get("", response_model=List[OcorrenciaOut])
def listar_ocorrencias(
    status_filter: Optional[str] = Query(None, alias="status"),
    bairro: Optional[str] = None,
    buraco_detectado: Optional[bool] = None,
    possivel_duplicidade: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Ocorrencia).order_by(desc(Ocorrencia.created_at))

    if status_filter:
        query = query.filter(Ocorrencia.status == status_filter.upper())
    if bairro:
        query = query.filter(Ocorrencia.bairro.ilike(f"%{bairro}%"))
    if possivel_duplicidade is not None:
        query = query.filter(Ocorrencia.possivel_duplicidade == possivel_duplicidade)
    if buraco_detectado is not None:
        query = query.join(Ocorrencia.resultado_ia).filter(ResultadoIA.buraco_detectado == buraco_detectado)

    registros = query.offset(offset).limit(limit).all()
    return [serialize_ocorrencia(o) for o in registros]
