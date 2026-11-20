# GOVERNANÇA, SEGURANÇA E PROTEÇÃO DE DADOS — VIAALERTA

O **ViaAlerta** foi concebido sob a perspectiva *Privacy by Design* e em estrita consonância com a Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018).

---

## 1. PRINCÍPIOS DE PRIVACIDADE E MINIMIZAÇÃO DE DADOS

1. **Minimização da Coleta (Art. 6º, III, LGPD):**
   - O cidadão **não precisa cadastrar CPF, RG, telefone ou endereço residencial** para registrar uma ocorrência ou consultar o protocolo.
   - Apenas a fotografia da via pública, a coordenada do problema e um relato opcional são coletados.
2. **Anonimização no Painel Público:**
   - As consultas por protocolo exibem exclusivamente os dados da via e o status técnico do reparo, sem qualquer metadado pessoal de quem realizou o upload.
3. **Limpeza e Sanitização de Metadados:**
   - O pipeline de processamento de imagens decodifica a imagem com OpenCV/Pillow, descartando potenciais metadados sensíveis embutidos em tags EXIF (como modelo do celular ou número de série do sensor).

---

## 2. SEGURANÇA DA INFORMAÇÃO E PROTEÇÃO DE UPLOADS

1. **Validação Estrita de MIME-Type:**
   - Somente os formatos `image/jpeg`, `image/png` e `image/webp` são aceitos. Executáveis, scripts (`.py`, `.js`, `.sh`) ou arquivos com extensões forjadas são bloqueados na camada de entrada com código HTTP 400.
2. **Limitação Volumétrica de Carga:**
   - O payload de cada upload é limitado a 10MB (`MAX_IMAGE_SIZE_BYTES = 10485760`), mitigando ataques de Negação de Serviço (DoS) por esgotamento de disco ou memória RAM.
3. **Prevenção de Path Traversal:**
   - Os nomes de arquivos originais fornecidos pelo cliente são totalmente ignorados para fins de gravação em disco.
   - Cada arquivo recebe um identificador UUIDv4 único (`file_id = uuid.uuid4().hex`) gerado pelo servidor, impedindo navegações relativas (`../../`).
4. **Armazenamento de Credenciais:**
   - Nenhuma chave secreta, token ou credencial é gravada diretamente no código-fonte. Todas as configurações utilizam variáveis de ambiente gerenciadas via Pydantic Settings e arquivo `.env`.

---

## 3. AUDITORIA E RASTREABILIDADE

- Cada ocorrência possui registro imutável de `created_at` e `updated_at` sincronizados em UTC.
- A integridade do arquivo original é assegurada pelo cálculo do hash SHA-256 no momento do upload.
- Qualquer alteração administrativa de status gera um novo registro na tabela `historico_status`, com registro de autor, data/hora e justificativa operacional.
