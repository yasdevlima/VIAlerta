from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

class ImagemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome_arquivo_original: str
    nome_arquivo_anotada: Optional[str] = None
    url_original: str
    url_anotada: Optional[str] = None
    tamanho_bytes: int
    mime_type: str
    created_at: datetime

class DeteccaoBox(BaseModel):
    classe: str
    confianca: float
    box_xyxy: List[float] # [xmin, ymin, xmax, ymax]
    area_pct: float

class ResultadoIAOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    buraco_detectado: bool
    quantidade_detectada: int
    confianca_media: float
    area_relativa_total_pct: float
    classificacao_visual: str
    tempo_processamento_ms: float
    status_processamento: str
    detalhes: Optional[List[DeteccaoBox]] = None
    created_at: datetime

class HistoricoStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status_anterior: Optional[str] = None
    status_novo: str
    motivo_observacao: Optional[str] = None
    autor: str
    created_at: datetime

class OcorrenciaCreateResponse(BaseModel):
    protocolo: str
    id: str
    status: str
    mensagem: str
    indice_prioridade: float
    possivel_duplicidade: bool
    buraco_detectado: bool
    quantidade_detectada: int
    classificacao_visual: str
    created_at: datetime

class OcorrenciaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    protocolo: str
    descricao: Optional[str] = None
    status: str
    latitude: float
    longitude: float
    endereco: str
    bairro: str
    cidade: str
    indice_prioridade: float
    possivel_duplicidade: bool
    ocorrencia_referencia_id: Optional[str] = None
    dados_demonstrativos: bool
    created_at: datetime
    updated_at: datetime
    
    imagem: Optional[ImagemOut] = None
    resultado_ia: Optional[ResultadoIAOut] = None
    historico: Optional[List[HistoricoStatusOut]] = None

class StatusUpdateIn(BaseModel):
    novo_status: str = Field(..., description="PENDENTE, EM_ANALISE, PROGRAMADA, EM_ANDAMENTO, CONCLUIDA, REJEITADA")
    motivo_observacao: Optional[str] = Field(None, description="Justificativa da alteração técnica")
    autor: Optional[str] = Field("Equipe Técnica ViaAlerta", description="Responsável pela atualização")

class DashboardIndicadores(BaseModel):
    total_ocorrencias: int
    total_buracos_detectados_ia: int
    taxa_deteccao_pct: float
    ocorrencias_pendentes: int
    ocorrencias_em_andamento: int
    ocorrencias_concluidas: int
    ocorrencias_outros_status: int
    total_possiveis_duplicidades: int
    distribuicao_bairros: dict[str, int]
    distribuicao_severidade: dict[str, int]
    tempo_medio_resolucao_dias: float
    aviso_dados_demonstrativos: str = "A plataforma inclui registros de teste identificados com flag demonstrativa para validação de layout e fluxos acadêmicos."

class PontoMapa(BaseModel):
    id: str
    protocolo: str
    latitude: float
    longitude: float
    endereco: str
    bairro: str
    status: str
    indice_prioridade: float
    buraco_detectado: bool
    quantidade_detectada: int
    classificacao_visual: str
    url_thumbnail: Optional[str] = None
    possivel_duplicidade: bool
    created_at: datetime
