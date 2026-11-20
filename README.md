# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="./src/frontend/dist/assets/logo-fiap.png" 
       alt="FIAP - Faculdade de Informática e Administração Paulista" 
       width="40%">
</a>
</p>

<br>

# ViaAlerta — Inteligência Artificial aplicada à identificação e priorização de problemas na infraestrutura urbana

## Global Solution 2026.2 — CitizenTech: Tecnologia centrada no cidadão

## 👥 Integrantes: 
- <a href="#">[Yasmin Kauane Silva Lima]</a> (RM: [RM566645])
- <a href="#">[Marina Clara Constantino Ribeiro]</a> (RM: [RM568576])


## 🎓 Professores:

### Tutor(a)
- <a href="#">Leonardo Ruiz Orabona</a>
  
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

---

## 📌 Descrição da Solução

O **ViaAlerta** é uma plataforma inovadora de *CitizenTech* que utiliza Inteligência Artificial (Visão Computacional via **YOLOv8**), geoprocessamento e análise de dados para transformar registros fotográficos e geográficos enviados pela população em inteligência acionável para o monitoramento e priorização de reparos em buracos no asfalto.

A solução oferece:
1. **Área do Cidadão:** Interface intuitiva e responsiva para envio de foto da via pública, geolocalização exata em mapa interativo ou endereço, e geração de comprovante com protocolo único (`VIA-YYYYMMDD-XXXX`).
2. **Motor de Visão Computacional Real:** Rede neural YOLOv8 treinada sobre a base pública *Pothole Detection* para inferência em tempo real, delimitando bounding boxes nas fotos, mensurando a área visual ocupada e aferindo a confiança estatística da detecção.
3. **Mecanismo de Priorização Inteligente (IPM):** Fórmula transparente e explicável (0 a 100 pontos) que combina severidade visual da avaria, reincidência de relatos no mesmo trecho de via, tempo de espera e proximidade de polos sensíveis (hospitais e escolas).
4. **Deduplicação Geoespacial:** Algoritmo geodésico de Haversine que identifica e correlaciona ocorrências a menos de 50 metros e 30 dias de intervalo, sem descartar o chamado do cidadão.
5. **Dashboard Administrativo & Mapa:** Painel com indicadores em tempo real, gráficos de concentração por bairro e severidade (Recharts), mapa com marcadores dinâmicos (Leaflet/OpenStreetMap), comparativo lado a lado de fotos e trilha de auditoria para transição de status.

---

## 📁 Estrutura de Pastas do Projeto

Abaixo encontra-se a organização modular deste módulo de entrega:

* **`data/`** Contém os pesos pré-treinados do modelo YOLOv8 (`models/pothole_yolov8.pt`), amostras de validação fotográfica (`samples/`) e o arquivo de documentação e licença da base (`metadata_dataset.json`).
* **`docs/`** Documentação técnica e acadêmica exaustiva do projeto, incluindo:
  - `RELATORIO_ACADEMICO_VIAALERTA.pdf`: Documento acadêmico unificado com capa, introdução, desenvolvimento, resultados, ODS e referências.
  - `DOCUMENTACAO_TECNICA.md`: Detalhamento técnico aprofundado de todos os módulos.
  - `ARQUITETURA.md`: Diagramas e decisões arquiteturais.
  - `DOCUMENTACAO_API.md`: Especificação dos endpoints RESTful, parâmetros e payloads JSON.
  - `MODELAGEM_BANCO.md`: Diagrama ER e dicionário das tabelas.
  - `GOVERNANCA_DADOS.md`: Diretrizes de segurança, LGPD e sanitização de uploads.
  - `TESTES_E_RESULTADOS.md`: Relatório de execução e evidências dos testes automatizados (`pytest`).
  - `LIMITACOES_E_TRABALHOS_FUTUROS.md`: Transparência metodológica e roadmap evolutivo.
  - `FONTES_E_REFERENCIAS.md`: Referências bibliográficas no padrão acadêmico.
  - `INSTRUCOES_DE_EXECUCAO.md`: Manual passo a passo para execução e publicação privada.
* **`notebooks/`** Contém o caderno Jupyter `demonstracao_inferencia_ia.ipynb`, demonstrando o carregamento dos metadados, inicialização do modelo YOLOv8, inferência sobre imagem real e cálculo de severidade visual.
* **`src/`** Código-fonte completo e funcional:
  - `backend/`: API RESTful assíncrona desenvolvida em Python 3.11 com FastAPI, SQLAlchemy, Pydantic, serviços de IA, geodésia, priorização e suíte de testes com `pytest`.
  - `frontend/`: Aplicação SPA moderna em React 18, TypeScript, Tailwind CSS, Vite, Leaflet e Recharts.
* **`README.md`** Este guia introdutório e contextualizador da Global Solution.

---


### 💡 Decisões Técnicas

> 1. **Framework de IA:** Adoção do Ultralytics YOLOv8s pela maturidade, eficiência em inferência computacional em CPU e alta precisão para localização de objetos com bounding boxes.  
> 2. **Desacoplamento Arquitetural:** Separação estrita entre Frontend SPA (React + TypeScript) e Backend RESTful (FastAPI), garantindo que a interface possa evoluir de forma independente da camada de inferência e banco.  
> 3. **Cartografia Sem Chaves Proprietárias:** Uso de Leaflet com OpenStreetMap / CartoDB para viabilizar execução imediata sem necessidade de cadastrar cartões de crédito ou chaves de API pagas.  
> 4. **Explicabilidade Matemática do IPM:** O modelo não trata a confiança da IA como sinônimo de perigo físico; em vez disso, correlaciona área geométrica da avaria na foto com tempo de espera, reincidência e vizinhança de escolas e hospitais.

### 📋 Observações Gerais

* **Participação na Competição Global Solution:** [X] Sim, aceitamos participar / [ ] Não vamos participar.
* *Outras observações gerais:* A plataforma é uma ferramenta de apoio à gestão urbana participativa desenvolvida como prova de conceito para fins acadêmicos. Não possui vínculo operacional formal com órgãos governamentais específicos.

---

## 🚀 Como Executar o Código

### 1. Inicializando o Backend
```bash
cd 2TIAO/GLOBAL-SOLUTION-2/src/backend
pip install -r requirements.txt
python run.py
```
A API iniciará em `http://127.0.0.1:8000` (Swagger disponível em `/docs`).

### 2. Inicializando o Frontend
```bash
cd 2TIAO/GLOBAL-SOLUTION-2/src/frontend
npm install
npm run dev
```
A interface estará acessível no navegador em `http://localhost:3000`.

### 3. Executando os Testes Automatizados
```bash
cd 2TIAO/GLOBAL-SOLUTION-2/src/backend
pytest -v
```

---

## 📄 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
