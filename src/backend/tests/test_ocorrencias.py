import io
from PIL import Image
from app.core.config import settings

def test_criar_ocorrencia_com_imagem_valida(client):
    # Cria imagem de teste em memória
    img_byte_arr = io.BytesIO()
    sample_path = settings.ROOT_DATA_DIR / "samples" / "buraco_sample_1.jpg"
    if sample_path.exists():
        with open(sample_path, "rb") as f:
            img_bytes = f.read()
    else:
        test_img = Image.new("RGB", (300, 300), color=(128, 128, 128))
        test_img.save(img_byte_arr, format="JPEG")
        img_bytes = img_byte_arr.getvalue()

    files = {
        "foto": ("pothole.jpg", img_bytes, "image/jpeg")
    }
    data = {
        "latitude": "-23.5614",
        "longitude": "-46.6559",
        "endereco": "Avenida Paulista, 1578",
        "bairro": "Bela Vista",
        "descricao": "Buraco no asfalto em frente ao MASP",
        "cidade": "São Paulo"
    }

    response = client.post("/api/ocorrencias", data=data, files=files)
    assert response.status_code == 201
    res_json = response.json()
    assert "protocolo" in res_json
    assert res_json["protocolo"].startswith("VIA-")
    assert res_json["status"] == "PENDENTE"
    assert "indice_prioridade" in res_json
    assert "classificacao_visual" in res_json

    # Consulta pelo protocolo gerado
    proto = res_json["protocolo"]
    get_res = client.get(f"/api/ocorrencias/{proto}")
    assert get_res.status_code == 200
    get_json = get_res.json()
    assert get_json["protocolo"] == proto
    assert get_json["endereco"] == "Avenida Paulista, 1578"
    assert get_json["imagem"] is not None
    assert get_json["resultado_ia"] is not None

def test_criar_ocorrencia_formato_invalido(client):
    files = {
        "foto": ("documento.txt", b"Texto de teste nao eh imagem", "text/plain")
    }
    data = {
        "latitude": "-23.5614",
        "longitude": "-46.6559",
        "endereco": "Avenida Paulista, 100",
        "bairro": "Bela Vista"
    }

    response = client.post("/api/ocorrencias", data=data, files=files)
    assert response.status_code == 400
    assert "inválido" in response.json()["detail"].lower()

def test_consultar_protocolo_inexistente(client):
    response = client.get("/api/ocorrencias/VIA-99999999-INEXISTENTE")
    assert response.status_code == 404
