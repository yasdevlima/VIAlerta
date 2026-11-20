from pathlib import Path
from PIL import Image
import numpy as np

from app.services.ai_service import pothole_service
from app.core.config import settings

def test_ai_inference_with_pothole_sample(tmp_path):
    # Usa a amostra real de buraco baixada
    sample_pothole = settings.ROOT_DATA_DIR / "samples" / "buraco_sample_1.jpg"
    assert sample_pothole.exists(), f"Amostra não encontrada em {sample_pothole}"

    out_annotated = tmp_path / "anotada_teste.jpg"
    result = pothole_service.process_image(sample_pothole, out_annotated)

    assert result["status_processamento"] == "SUCESSO"
    assert result["buraco_detectado"] is True
    assert result["quantidade_detectada"] >= 1
    assert result["confianca_media"] > 0.20
    assert result["area_relativa_total_pct"] > 0.0
    assert result["classificacao_visual"] in ["Severa", "Moderada", "Leve"]
    assert out_annotated.exists()

def test_ai_inference_without_pothole(tmp_path):
    # Cria imagem artificial sem buraco (cinza sólida com linha branca)
    clean_img_path = tmp_path / "asfalto_perfeito.jpg"
    img = Image.new("RGB", (640, 480), color=(100, 100, 100))
    img.save(clean_img_path)

    out_annotated = tmp_path / "anotada_limpa.jpg"
    result = pothole_service.process_image(clean_img_path, out_annotated)

    assert result["status_processamento"] == "SEM_DETECCAO"
    assert result["buraco_detectado"] is False
    assert result["quantidade_detectada"] == 0
    assert result["classificacao_visual"] == "Sem Buraco Identificado"

def test_ai_corrupted_image_handling(tmp_path):
    # Cria arquivo corrompido com extensão .jpg mas bytes inválidos
    corrupted_path = tmp_path / "corrompida.jpg"
    corrupted_path.write_bytes(b"INVALID_HEADER_NOT_A_JPEG_FILE")

    out_annotated = tmp_path / "anotada_err.jpg"
    result = pothole_service.process_image(corrupted_path, out_annotated)

    assert result["status_processamento"] == "FALHA"
    assert result["buraco_detectado"] is False
    assert result["classificacao_visual"] == "Falha no Processamento"
