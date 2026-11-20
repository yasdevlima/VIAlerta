# LIMITAÇÕES IDENTIFICADAS E TRABALHOS FUTUROS — VIAALERTA

A transparência científica e técnica é um pilar central na metodologia de projetos da FIAP. Este documento detalha as limitações operacionais da versão atual do **ViaAlerta** e propõe um roteiro evolutivo.

---

## 1. LIMITAÇÕES IDENTIFICADAS

### 1.1. Limitações de Visão Computacional
1. **Ângulo de Captura e Profundidade Tridimensional:**
   - O modelo de visão computacional (YOLOv8) atua sobre imagens bidimensionais (RGB).
   - O tamanho da bounding box e a área relativa calculada dependem da distância e do ângulo em que o cidadão tirou a fotografia (efeito de perspectiva). Uma foto tirada a 30 cm do solo aparenta ocupar 40% da imagem, enquanto a mesma avaria capturada a 3 metros ocupa apenas 3%.
   - O modelo **não mede profundidade física (em centímetros) nem o volume cúbico** de massa asfáltica necessária para o reparo.
2. **Condições Climáticas e Iluminação Noturna:**
   - Fotografias tiradas à noite sob baixa iluminação ou sob chuva torrencial (quando o buraco fica submerso sob poça d'água e reflete o céu) apresentam queda na confiança estatística do modelo.
3. **Hardware de Inferência:**
   - Em servidores ou computadores pessoais sem GPU dedicada com CUDA, a inferência roda em CPU, com tempo médio de processamento entre 2 e 5 segundos por imagem.

### 1.2. Limitações de Integração Pública e Escopo
1. **Ausência de Integração Oficial com Prefeituras:**
   - A plataforma é uma ferramenta conceitual e funcional de **apoio à gestão urbana** desenvolvida para fins acadêmicos na Global Solution 2026.2.
   - Não existe convênio formal com prefeituras, e os chamados não são automaticamente despachados para serviços municipais (ex: 156 de São Paulo).
2. **Dados Sensíveis Geoespaciais:**
   - A proximidade de hospitais e escolas utiliza um conjunto de pontos de referência catalogados. A integração com bases completas de georreferenciamento público (como Geosampa ou OpenStreetMap Overpass API em tempo real) depende de limites de taxa e conexão estável.

---

## 2. TRABALHOS FUTUROS E EVOLUÇÃO DO SISTEMA

1. **Estimativa de Profundidade Monocular (Monocular Depth Estimation):**
   - Integrar modelos como *MiDaS* ou *Depth Anything* para estimar mapa de profundidade a partir de uma única fotografia, permitindo classificar buracos não apenas por largura superficial, mas por profundidade estimada.
2. **Detecção de Fraude e Reenvio:**
   - Aplicar modelos de *Image Similarity Search* (embeddings ResNet ou CLIP) para identificar quando uma foto baixada da internet ou reutilizada de outro local foi submetida indevidamente.
3. **Aplicativo Mobile PWA com Captura Orientada:**
   - Implementar guia de enquadramento na câmera do celular (overlay visual na tela recomendando ângulo de 45º e distância de 1.5 metro) para padronizar as imagens submetidas pela população.
4. **Exportação de Relatórios Gerenciais (PDF e CSV):**
   - Permitir que os fiscais municipais exportem relatórios de triagem filtrados por subprefeitura ou distrito para apoiar reuniões operacionais de pavimentação.
