# DOCUMENTAÇÃO DAS APIS REST — VIAALERTA

A API do **ViaAlerta** segue a convenção RESTful, retornando payloads estruturados no formato JSON e códigos de status HTTP semânticos.

- **URL Base:** `http://localhost:8000/api`
- **Swagger UI Interativo:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 1. ENDPOINTS DE OCORRÊNCIAS

### 1.1. Criar Ocorrência
- **Método:** `POST`
- **Rota:** `/api/ocorrencias`
- **Content-Type:** `multipart/form-data`
- **Descrição:** Recebe a fotografia da via pública, coordenadas geográficas e metadados. Dispara o pipeline de IA, calcula o IPM, verifica duplicidades e persiste a ocorrência.

#### Parâmetros de Formulário:
| Campo | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `foto` | Arquivo (Binary) | Sim | Imagem JPG, PNG ou WEBP (máx 10MB) |
| `latitude` | Float | Sim | Latitude geográfica em graus decimais (ex: -23.5614) |
| `longitude` | Float | Sim | Longitude geográfica em graus decimais (ex: -46.6559) |
| `endereco` | String | Sim | Logradouro e número aproximado |
| `bairro` | String | Sim | Bairro da ocorrência |
| `descricao` | String | Não | Observações e detalhes adicionais fornecidos pelo cidadão |
| `cidade` | String | Não | Cidade (padrão: "São Paulo") |

#### Resposta de Sucesso (HTTP 201 Created):
```json
{
  "protocolo": "VIA-20261119-A3F91",
  "id": "e9b2781b-f72b-4029-9a2d-20ec871c548a",
  "status": "PENDENTE",
  "mensagem": "Ocorrência registrada e analisada com sucesso!",
  "indice_prioridade": 74.2,
  "possivel_duplicidade": false,
  "buraco_detectado": true,
  "quantidade_detectada": 2,
  "classificacao_visual": "Moderada",
  "created_at": "2026-11-19T09:20:00Z"
}
```

---

### 1.2. Consultar Ocorrência por Protocolo
- **Método:** `GET`
- **Rota:** `/api/ocorrencias/{protocolo}`
- **Descrição:** Permite que qualquer cidadão acompanhe o andamento de seu chamado e veja as detecções da IA.

#### Exemplo de Requisição:
`GET /api/ocorrencias/VIA-20261119-A3F91`

#### Resposta de Sucesso (HTTP 200 OK):
```json
{
  "id": "e9b2781b-f72b-4029-9a2d-20ec871c548a",
  "protocolo": "VIA-20261119-A3F91",
  "descricao": "Buraco na faixa da direita próximo ao ponto de ônibus",
  "status": "PENDENTE",
  "latitude": -23.5614,
  "longitude": -46.6559,
  "endereco": "Avenida Paulista, 1578",
  "bairro": "Bela Vista",
  "cidade": "São Paulo",
  "indice_prioridade": 74.2,
  "possivel_duplicidade": false,
  "ocorrencia_referencia_id": null,
  "dados_demonstrativos": false,
  "created_at": "2026-11-19T09:20:00Z",
  "updated_at": "2026-11-19T09:20:00Z",
  "imagem": {
    "id": "7849e7cf-961e-4509-9fc6-9e6e44b5840d",
    "nome_arquivo_original": "e9b2781b_original.jpg",
    "nome_arquivo_anotada": "e9b2781b_anotada.jpg",
    "url_original": "/uploads/originais/e9b2781b_original.jpg",
    "url_anotada": "/uploads/anotadas/e9b2781b_anotada.jpg",
    "tamanho_bytes": 145280,
    "mime_type": "image/jpeg",
    "created_at": "2026-11-19T09:20:00Z"
  },
  "resultado_ia": {
    "id": "0df62734-d028-4e89-80ba-3bbf27694f92",
    "buraco_detectado": true,
    "quantidade_detectada": 2,
    "confianca_media": 0.825,
    "area_relativa_total_pct": 6.8,
    "classificacao_visual": "Moderada",
    "tempo_processamento_ms": 3120.4,
    "status_processamento": "SUCESSO",
    "detalhes": [
      {
        "classe": "Buraco / Pothole",
        "confianca": 0.88,
        "box_xyxy": [120.5, 230.1, 280.4, 390.2],
        "area_pct": 4.1
      }
    ],
    "created_at": "2026-11-19T09:20:00Z"
  },
  "historico": [
    {
      "id": "3c023d85-11ea-42ce-9252-9b2f4a13e2e5",
      "status_anterior": null,
      "status_novo": "PENDENTE",
      "motivo_observacao": "Ocorrência registrada pelo cidadão e processada por IA",
      "autor": "Sistema ViaAlerta",
      "created_at": "2026-11-19T09:20:00Z"
    }
  ]
}
```

---

### 1.3. Listar Ocorrências com Filtros
- **Método:** `GET`
- **Rota:** `/api/ocorrencias`
- **Query Params:**
  - `status`: `PENDENTE`, `EM_ANALISE`, `PROGRAMADA`, `EM_ANDAMENTO`, `CONCLUIDA`, `REJEITADA`
  - `bairro`: Filtro parcial por nome do bairro
  - `buraco_detectado`: `true` ou `false`
  - `possivel_duplicidade`: `true` ou `false`
  - `limit`: Padrão 50 (máx 200)
  - `offset`: Padrão 0

---

## 2. ENDPOINTS ADMINISTRATIVOS E DE GESTÃO

### 2.1. Indicadores do Dashboard
- **Método:** `GET`
- **Rota:** `/api/admin/dashboard`
- **Descrição:** Retorna agregados em tempo real calculados sobre a base de dados.

#### Exemplo de Resposta (HTTP 200 OK):
```json
{
  "total_ocorrencias": 18,
  "total_buracos_detectados_ia": 16,
  "taxa_deteccao_pct": 88.9,
  "ocorrencias_pendentes": 8,
  "ocorrencias_em_andamento": 5,
  "ocorrencias_concluidas": 4,
  "ocorrencias_outros_status": 1,
  "total_possiveis_duplicidades": 2,
  "distribuicao_bairros": {
    "Pinheiros": 5,
    "Bela Vista": 4,
    "Vila Mariana": 3,
    "Centro": 3
  },
  "distribuicao_severidade": {
    "Severa": 7,
    "Moderada": 6,
    "Leve": 3,
    "Sem Buraco Identificado": 2
  },
  "tempo_medio_resolucao_dias": 3.8,
  "aviso_dados_demonstrativos": "A plataforma inclui registros de teste identificados com flag demonstrativa para validação de layout e fluxos acadêmicos."
}
```

---

### 2.2. Pontos Geográficos do Mapa
- **Método:** `GET`
- **Rota:** `/api/admin/mapa`
- **Query Params:** `status` (opcional)
- **Descrição:** Retorna lista compacta de coordenadas e metadados para renderização no Leaflet.

---

### 2.3. Atualizar Status da Ocorrência
- **Método:** `PATCH`
- **Rota:** `/api/admin/ocorrencias/{id}/status`
- **Body JSON:**
```json
{
  "novo_status": "EM_ANDAMENTO",
  "motivo_observacao": "Equipe de pavimentação mobilizada para o local",
  "autor": "Engenheiro Fiscal - Regional Centro"
}
```
- **Resposta:** Objeto completo da ocorrência atualizada com novo item registrado no histórico de auditoria.

---

### 2.4. Semear Base Demonstrativa
- **Método:** `POST`
- **Rota:** `/api/admin/seed-demo`
- **Descrição:** Insere dados simulados com localizações reais em São Paulo para homologação das visualizações cartográficas e gráficos, sinalizando formalmente `dados_demonstrativos = true`.
