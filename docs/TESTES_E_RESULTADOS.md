# TESTES E EVIDÊNCIAS DE VALIDAÇÃO — VIAALERTA

Este documento consolida a suíte de testes automatizados e as evidências reais de execução do sistema **ViaAlerta**, em conformidade com as diretrizes da Global Solution 2026.2 da FIAP.

> **Regra de Conformidade:** Todos os testes documentados foram efetivamente executados no ambiente local de desenvolvimento com o framework `pytest`. Nenhum resultado foi simulado ou inferido.

---

## 1. RESUMO GERAL DA SUÍTE DE TESTES

- **Ambiente de Testes:** Windows x64 • Python 3.11.9 • Pytest 9.2.0 • Ultralytics 8.4.215
- **Total de Testes Executados:** 12
- **Aprovados (Passed):** 12 (100%)
- **Falhas (Failed):** 0
- **Tempo de Execução:** 23.73 segundos

---

## 2. DETALHAMENTO DOS TESTES POR MÓDULO

### 2.1. Testes de Visão Computacional e Inteligência Artificial (`tests/test_ai_service.py`)
| Teste | Objetivo | Evidência / Resultado | Status |
| :--- | :--- | :--- | :--- |
| `test_ai_inference_with_pothole_sample` | Valida a inferência do modelo YOLOv8 real sobre fotografia com buraco viário (`buraco_sample_1.jpg`). | O modelo gerou bounding box com confiança > 25%, calculou área relativa e atribuiu classificação visual com sucesso. | **PASSED** |
| `test_ai_inference_without_pothole` | Valida o comportamento do modelo diante de uma via sem buracos (asfalto íntegro). | O modelo retornou 0 caixas delimitadoras e status `SEM_DETECCAO` com classificação visual "Sem Buraco Identificado". | **PASSED** |
| `test_ai_corrupted_image_handling` | Valida o tratamento robusto de arquivos de imagem corrompidos ou malformados. | O serviço capturou a falha sem interrupção do processo, retornando status `FALHA` e 0 detecções. | **PASSED** |

### 2.2. Testes de Ocorrências e API REST (`tests/test_ocorrencias.py`)
| Teste | Objetivo | Evidência / Resultado | Status |
| :--- | :--- | :--- | :--- |
| `test_criar_ocorrencia_com_imagem_valida` | Cadastra ocorrência com imagem real, coordenadas e descrição. | Retornou HTTP 201, gerou protocolo no padrão `VIA-YYYYMMDD-XXXX` e persistiu relacionamentos no banco. | **PASSED** |
| `test_criar_ocorrencia_formato_invalido` | Tenta upload de arquivo não-imagem (`.txt`). | Bloqueado na validação de entrada retornando HTTP 400 Bad Request com mensagem explicativa. | **PASSED** |
| `test_consultar_protocolo_inexistente` | Consulta protocolo aleatório não existente. | Retornou HTTP 404 Not Found sem expor dados internos do banco. | **PASSED** |

### 2.3. Testes de Priorização e Deduplicação (`tests/test_priority_and_dedup.py`)
| Teste | Objetivo | Evidência / Resultado | Status |
| :--- | :--- | :--- | :--- |
| `test_haversine_known_distance` | Valida o cálculo geodésico da distância entre dois pontos conhecidos em SP. | Distância calculada coerente com a geodésia real (~2.2 km entre MASP e Copan). | **PASSED** |
| `test_deduplication_detection` | Avalia sinalização de duplicidade para coordenadas a menos de 50 metros e a mais de 2 km. | Identificou corretamente duplicidade a 15 metros (`possivel_duplicidade = True`) e rejeitou a 2 km. | **PASSED** |
| `test_priority_index_calculation` | Valida a pontuação do IPM para cenários severos e cenários de baixo impacto. | Ocorrência severa próxima a hospital obteve pontuação substancialmente superior à ocorrência sem buraco. | **PASSED** |

### 2.4. Testes Administrativos e Dashboard (`tests/test_admin.py`)
| Teste | Objetivo | Evidência / Resultado | Status |
| :--- | :--- | :--- | :--- |
| `test_atualizar_status_ocorrencia` | Modifica status para `EM_ANDAMENTO` com justificativa e autor. | Retornou HTTP 200 e gravou entrada correspondente na tabela de histórico de auditoria. | **PASSED** |
| `test_atualizar_status_invalido` | Tenta atribuir status não existente no enum do sistema. | Bloqueado retornando HTTP 400 Bad Request. | **PASSED** |
| `test_obter_dashboard_e_mapa` | Consulta métricas agregadas do dashboard e vetor de pontos do mapa. | Retornou HTTP 200 com métricas agregadas consistentes e array de pontos geoespaciais. | **PASSED** |

---

## 3. LOG REAL DA EXECUÇÃO DO PYTEST

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\yasmi\.gemini\antigravity\scratch\ViaAlerta\2TIAO\GLOBAL-SOLUTION-2\src\backend
collected 12 items

tests/test_admin.py::test_atualizar_status_ocorrencia PASSED             [  8%]
tests/test_admin.py::test_atualizar_status_invalido PASSED               [ 16%]
tests/test_admin.py::test_obter_dashboard_e_mapa PASSED                  [ 25%]
tests/test_ai_service.py::test_ai_inference_with_pothole_sample PASSED   [ 33%]
tests/test_ai_service.py::test_ai_inference_without_pothole PASSED       [ 41%]
tests/test_ai_service.py::test_ai_corrupted_image_handling PASSED        [ 50%]
tests/test_ocorrencias.py::test_criar_ocorrencia_com_imagem_valida PASSED [ 58%]
tests/test_ocorrencias.py::test_criar_ocorrencia_formato_invalido PASSED [ 66%]
tests/test_ocorrencias.py::test_consultar_protocolo_inexistente PASSED   [ 75%]
tests/test_priority_and_dedup.py::test_haversine_known_distance PASSED   [ 83%]
tests/test_priority_and_dedup.py::test_deduplication_detection PASSED    [ 91%]
tests/test_priority_and_dedup.py::test_priority_index_calculation PASSED [100%]

======================= 12 passed, 6 warnings in 23.73s =======================
```
