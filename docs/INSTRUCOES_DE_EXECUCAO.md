# INSTRUÇÕES DE EXECUÇÃO — VIAALERTA

Este guia apresenta o passo a passo completo para executar a plataforma **ViaAlerta** localmente no ambiente de avaliação.

---

## 1. PRÉ-REQUISITOS

- **Python:** Versão 3.10 ou 3.11 recomendada (instalado no sistema).
- **Node.js:** Versão 18 ou superior (LTS) e gerenciador `npm`.
- **Git:** Para controle de versão e submissão ao repositório.

---

## 2. ESTRUTURA DOS DIRETÓRIOS

O projeto está centralizado na estrutura acadêmica oficial da FIAP:
```
ViaAlerta/
└── 2TIAO/
    └── GLOBAL-SOLUTION-2/
        ├── data/
        │   ├── models/ (pothole_yolov8.pt)
        │   └── samples/
        ├── docs/
        ├── notebooks/
        └── src/
            ├── backend/
            └── frontend/
```

---

## 3. INICIALIZAÇÃO DO BACKEND (API & INTELIGÊNCIA ARTIFICIAL)

1. Abra um terminal na pasta do backend:
   ```bash
   cd ViaAlerta/2TIAO/GLOBAL-SOLUTION-2/src/backend
   ```

2. Crie e ative um ambiente virtual (recomendado):
   ```bash
   # No Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Verifique a presença do arquivo de pesos da IA:
   - Os pesos pré-treinados do modelo YOLOv8 estão localizados em `ViaAlerta/2TIAO/GLOBAL-SOLUTION-2/data/models/pothole_yolov8.pt`.

5. Inicie a API com Uvicorn:
   ```bash
   python run.py
   # Ou via uvicorn diretamente:
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

6. A API estará disponível em:
   - **Endpoint Raiz:** `http://localhost:8000/`
   - **Documentação Swagger:** `http://localhost:8000/docs`
   - **Documentação ReDoc:** `http://localhost:8000/redoc`

---

## 4. INICIALIZAÇÃO DO FRONTEND (REACT + VITE + TAILWIND)

1. Abra um segundo terminal na pasta do frontend:
   ```bash
   cd ViaAlerta/2TIAO/GLOBAL-SOLUTION-2/src/frontend
   ```

2. Instale os pacotes npm:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

4. Acesse a aplicação no seu navegador:
   - **URL Local:** `http://localhost:3000`

---

## 5. EXECUÇÃO DA BATERIA DE TESTES AUTOMATIZADOS

Para rodar os testes unitários e de integração do backend:
```bash
cd ViaAlerta/2TIAO/GLOBAL-SOLUTION-2/src/backend
pytest -v
```

Todos os 12 testes do pipeline serão executados, validando:
- Inferência real da IA em imagem com buraco;
- Tratamento de vias limpas e arquivos corrompidos;
- Validação geodésica (Haversine) e cálculo de duplicidades;
- Cálculo do Índice de Prioridade de Manutenção (IPM);
- Cadastro de ocorrência, sanitização e consulta por protocolo;
- Atualização de status e trilha de auditoria.

---

## 6. INSTRUÇÕES PARA PUBLICAÇÃO NO REPOSITÓRIO PRIVADO DO GITHUB

> ⚠️ **ATENÇÃO ÀS DIRETRIZES DA FIAP:**  
> O repositório final **NUNCA DEVE SER TORNADO PÚBLICO**. Ele deve ser estritamente privado e compartilhado com o usuário oficial da tutoria: **`fiap-tutoria`**.

### Passo a Passo no Terminal:

1. Acesse seu perfil no GitHub e crie um **novo repositório privado** com o nome do projeto (ex: `ViaAlerta-GS-2026`).
2. No seu computador, abra o terminal na raiz do projeto (`ViaAlerta`):
   ```bash
   cd ViaAlerta
   git init
   git add .
   git commit -m "feat: entrega completa Global Solution 2026.2 ViaAlerta"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/ViaAlerta-GS-2026.git
   git push -u origin main
   ```
3. No GitHub, acesse a aba **Settings** do seu repositório recém-criado.
4. Clique em **Collaborators** no menu lateral esquerdo.
5. Clique em **Add people** e convide a conta: **`fiap-tutoria`**.
6. Verifique se o convite foi enviado com sucesso.
