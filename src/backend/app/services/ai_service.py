import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO

from app.core.config import settings

logger = logging.getLogger(__name__)

class PotholeDetectionService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PotholeDetectionService, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        model_path = settings.MODEL_PATH
        if model_path.exists():
            logger.info(f"Carregando modelo YOLOv8 real de: {model_path}")
            try:
                self._model = YOLO(str(model_path))
                logger.info(f"Modelo carregado com sucesso. Classes: {self._model.names}")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo YOLOv8: {e}")
                self._model = None
        else:
            logger.warning(f"Arquivo de pesos não encontrado em {model_path}. Tentando inicializar YOLOv8 padrão.")
            try:
                self._model = YOLO("yolov8n.pt")
            except Exception as e:
                logger.error(f"Erro ao carregar fallback YOLO: {e}")
                self._model = None

    def process_image(self, image_path: Path, output_annotated_path: Path) -> Dict[str, Any]:
        """
        Executa inferência real de visão computacional na imagem fornecida.
        Gera a imagem anotada com caixas delimitadoras e calcula métricas.
        """
        start_time = time.time()
        
        # Validação de integridade do arquivo
        try:
            with Image.open(image_path) as img:
                img.verify()
            
            # Recarrega para obter dimensões
            with Image.open(image_path) as img:
                width, height = img.size
        except Exception as e:
            logger.error(f"Falha ao validar imagem: {e}")
            return {
                "buraco_detectado": False,
                "quantidade_detectada": 0,
                "confianca_media": 0.0,
                "area_relativa_total_pct": 0.0,
                "classificacao_visual": "Falha no Processamento",
                "tempo_processamento_ms": round((time.time() - start_time) * 1000, 2),
                "status_processamento": "FALHA",
                "detalhes": [],
                "caminho_anotada": None
            }

        # Carrega com OpenCV para desenhar anotações
        cv_img = cv2.imread(str(image_path))
        if cv_img is None:
            return {
                "buraco_detectado": False,
                "quantidade_detectada": 0,
                "confianca_media": 0.0,
                "area_relativa_total_pct": 0.0,
                "classificacao_visual": "Falha no Processamento",
                "tempo_processamento_ms": round((time.time() - start_time) * 1000, 2),
                "status_processamento": "FALHA",
                "detalhes": [],
                "caminho_anotada": None
            }

        if self._model is None:
            self._load_model()

        if self._model is None:
            return {
                "buraco_detectado": False,
                "quantidade_detectada": 0,
                "confianca_media": 0.0,
                "area_relativa_total_pct": 0.0,
                "classificacao_visual": "Sem Modelo Disponível",
                "tempo_processamento_ms": round((time.time() - start_time) * 1000, 2),
                "status_processamento": "FALHA",
                "detalhes": [],
                "caminho_anotada": None
            }

        # Executa a predição real
        results = self._model.predict(source=str(image_path), conf=0.25, save=False, verbose=False)
        result = results[0]
        boxes = result.boxes

        num_detections = len(boxes)
        detalhes: List[Dict[str, Any]] = []
        confiancas: List[float] = []
        total_area_pixels = width * height
        soma_area_boxes = 0.0

        for box in boxes:
            xyxy = box.xyxy[0].tolist() # [xmin, ymin, xmax, ymax]
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = self._model.names.get(cls_id, "Buraco / Pothole")
            
            box_w = max(0.0, xyxy[2] - xyxy[0])
            box_h = max(0.0, xyxy[3] - xyxy[1])
            box_area = box_w * box_h
            area_pct = round((box_area / total_area_pixels) * 100, 2)
            
            soma_area_boxes += box_area
            confiancas.append(conf)

            detalhes.append({
                "classe": cls_name,
                "confianca": round(conf, 4),
                "box_xyxy": [round(coord, 1) for coord in xyxy],
                "area_pct": area_pct
            })

            # Desenha bounding box na imagem
            x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
            
            # Cor vibrante de alerta: Laranja/Vermelho (BGR: 0, 120, 255)
            cv2.rectangle(cv_img, (x1, y1), (x2, y2), (0, 100, 255), 3)
            
            # Rótulo com fundo para legibilidade
            label = f"Buraco: {int(conf * 100)}% ({area_pct}% area)"
            (w_txt, h_txt), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            cv2.rectangle(cv_img, (x1, max(0, y1 - 24)), (x1 + w_txt + 10, max(0, y1)), (0, 100, 255), -1)
            cv2.putText(cv_img, label, (x1 + 5, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        area_relativa_total_pct = round((soma_area_boxes / total_area_pixels) * 100, 2)
        confianca_media = round(float(np.mean(confiancas)), 4) if confiancas else 0.0

        # Classificação visual explicável baseada na evidência geométrica da imagem
        if num_detections == 0:
            buraco_detectado = False
            classificacao_visual = "Sem Buraco Identificado"
            status_processamento = "SEM_DETECCAO"
        else:
            buraco_detectado = True
            status_processamento = "SUCESSO"
            # Critérios transparentes:
            if area_relativa_total_pct >= 10.0 or num_detections >= 3:
                classificacao_visual = "Severa"
            elif area_relativa_total_pct >= 3.5 or num_detections >= 2:
                classificacao_visual = "Moderada"
            else:
                classificacao_visual = "Leve"

        # Salva imagem anotada se houver detecção ou gera cópia para exibição
        cv2.imwrite(str(output_annotated_path), cv_img)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "buraco_detectado": buraco_detectado,
            "quantidade_detectada": num_detections,
            "confianca_media": confianca_media,
            "area_relativa_total_pct": area_relativa_total_pct,
            "classificacao_visual": classificacao_visual,
            "tempo_processamento_ms": elapsed_ms,
            "status_processamento": status_processamento,
            "detalhes": detalhes,
            "caminho_anotada": str(output_annotated_path)
        }

pothole_service = PotholeDetectionService()
