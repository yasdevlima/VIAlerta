# MODELAGEM DO BANCO DE DADOS — VIAALERTA

A modelagem do banco de dados do **ViaAlerta** prioriza a integridade referencial, rastreabilidade temporal e a minimização da coleta de dados pessoais, em total conformidade com a Lei Geral de Proteção de Dados (LGPD).

---

## 1. DIAGRAMA ENTIDADE-RELACIONAMENTO (MERMAID)

```mermaid
erDiagram
    OCORRENCIAS ||--o| IMAGENS : "possui"
    OCORRENCIAS ||--o| RESULTADOS_IA : "gera"
    OCORRENCIAS ||--o{ HISTORICO_STATUS : "registra"
    OCORRENCIAS ||--o| OCORRENCIAS : "duplicata_de"

    OCORRENCIAS {
        string id PK "UUIDv4"
        string protocolo UK "VIA-YYYYMMDD-XXXX"
        text descricao "Opcional"
        string status "PENDENTE | EM_ANALISE | PROGRAMADA | EM_ANDAMENTO | CONCLUIDA | REJEITADA"
        float latitude "Graus decimais"
        float longitude "Graus decimais"
        string endereco "Logradouro"
        string bairro "Bairro indexado"
        string cidade "Cidade (padrão São Paulo)"
        float indice_prioridade "IPM (0 a 100)"
        boolean possivel_duplicidade "Haversine <= 50m"
        string ocorrencia_referencia_id FK "Referência à original"
        boolean dados_demonstrativos "Flag de teste"
        datetime created_at "UTC"
        datetime updated_at "UTC"
    }

    IMAGENS {
        string id PK "UUIDv4"
        string ocorrencia_id FK "UUID da ocorrência"
        string nome_arquivo_original "Arquivo salvo no disco"
        string nome_arquivo_anotada "Arquivo com Bounding Boxes"
        string caminho_relativo_original "uploads/originais/..."
        string caminho_relativo_anotada "uploads/anotadas/..."
        integer tamanho_bytes "Tamanho do arquivo"
        string mime_type "image/jpeg | image/png"
        string hash_sha256 "Integridade e deduplicação"
        datetime created_at "UTC"
    }

    RESULTADOS_IA {
        string id PK "UUIDv4"
        string ocorrencia_id FK "UUID da ocorrência"
        boolean buraco_detectado "True se quantidade > 0"
        integer quantidade_detectada "Qtd de caixas"
        float confianca_media "Score médio [0, 1]"
        float area_relativa_total_pct "% da imagem ocupada"
        string classificacao_visual "Severa | Moderada | Leve | Sem Buraco"
        float tempo_processamento_ms "Latência da inferência"
        string status_processamento "SUCESSO | SEM_DETECCAO | FALHA"
        text detalhes_json "JSON com coordenadas xyxy"
        datetime created_at "UTC"
    }

    HISTORICO_STATUS {
        string id PK "UUIDv4"
        string ocorrencia_id FK "UUID da ocorrência"
        string status_anterior "Status antes da mudança"
        string status_novo "Novo status atribuído"
        text motivo_observacao "Justificativa técnica"
        string autor "Nome ou papel do operador"
        datetime created_at "UTC"
    }
```

---

## 2. DICIONÁRIO DE DADOS DETALHADO

### Tabela: `ocorrencias`
Centraliza a entidade raiz de cada solicitação cadastrada pelo cidadão.
- `id`: Chave primária em UUIDv4 (36 caracteres), imutável.
- `protocolo`: Identificador único voltado ao cidadão no formato padronizado `VIA-YYYYMMDD-XXXX`.
- `latitude` e `longitude`: Ponto geoespacial com precisão de 6 casas decimais.
- `indice_prioridade`: Valor computado pelo algoritmo de apoio à decisão (IPM), normalizado de 0 a 100.
- `possivel_duplicidade`: Sinalizador booleano computado via fórmula de Haversine em raio $\le 50$ metros.
- `dados_demonstrativos`: Sinalizador obrigatório pela FIAP para distinguir registros de teste de dados de homologação.

### Tabela: `imagens`
Armazena as referências seguras aos arquivos físicos armazenados em disco.
- Nunca armazena o binário da imagem como BLOB dentro do banco, prevenindo degradação de performance relacional.
- `hash_sha256`: Permite auditoria forense de integridade da evidência fotográfica.

### Tabela: `resultados_ia`
Registra a inferência gerada pelo modelo YOLOv8.
- `buraco_detectado`: Booleano determinístico que indica se houve ao menos uma detecção acima do limiar $\tau = 0.25$.
- `area_relativa_total_pct`: Percentual da área total da foto ocupado pelas caixas delimitadoras, base da severidade visual.
- `detalhes_json`: Preserva o vetor completo de caixas delimitadoras com coordenadas $[x_{\min}, y_{\min}, x_{\max}, y_{\max}]$.

### Tabela: `historico_status`
Garante rastreabilidade total (trilha de auditoria) de todas as transições de status da ocorrência, registrando data, autor e justificativa.
