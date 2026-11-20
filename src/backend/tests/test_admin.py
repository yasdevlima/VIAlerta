from app.models.ocorrencia import Ocorrencia

def test_atualizar_status_ocorrencia(client, db_session):
    # Cria uma ocorrência diretamente no banco de teste
    ocorrencia = Ocorrencia(
        protocolo="VIA-20261119-TESTE1",
        descricao="Teste admin",
        status="PENDENTE",
        latitude=-23.5505,
        longitude=-46.6333,
        endereco="Rua Direita, 50",
        bairro="Centro",
        cidade="São Paulo"
    )
    db_session.add(ocorrencia)
    db_session.commit()
    db_session.refresh(ocorrencia)

    # Atualiza status para EM_ANDAMENTO
    payload = {
        "novo_status": "EM_ANDAMENTO",
        "motivo_observacao": "Equipe de triagem despachada",
        "autor": "Fiscal SP-01"
    }
    response = client.patch(f"/api/admin/ocorrencias/{ocorrencia.id}/status", json=payload)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "EM_ANDAMENTO"
    assert len(res_json["historico"]) >= 1
    assert res_json["historico"][0]["status_novo"] == "EM_ANDAMENTO"

def test_atualizar_status_invalido(client, db_session):
    ocorrencia = Ocorrencia(
        protocolo="VIA-20261119-TESTE2",
        status="PENDENTE",
        latitude=-23.5505,
        longitude=-46.6333,
        endereco="Rua Direita, 50",
        bairro="Centro",
        cidade="São Paulo"
    )
    db_session.add(ocorrencia)
    db_session.commit()

    payload = {"novo_status": "STATUS_INVENTADO"}
    response = client.patch(f"/api/admin/ocorrencias/{ocorrencia.id}/status", json=payload)
    assert response.status_code == 400

def test_obter_dashboard_e_mapa(client):
    # Endpoint do Dashboard
    res_dash = client.get("/api/admin/dashboard")
    assert res_dash.status_code == 200
    dash_json = res_dash.json()
    assert "total_ocorrencias" in dash_json
    assert "taxa_deteccao_pct" in dash_json
    assert "distribuicao_bairros" in dash_json

    # Endpoint do Mapa
    res_mapa = client.get("/api/admin/mapa")
    assert res_mapa.status_code == 200
    assert isinstance(res_mapa.json(), list)
