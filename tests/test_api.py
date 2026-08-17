from fastapi.testclient import TestClient
from pontos.api import criar_app
from pontos.infraestrutura.memoria import RepositorioEmMemoria


def test_consulta_de_saldo_respeita_contrato_da_tela():
    cliente = TestClient(criar_app(RepositorioEmMemoria()))
    cliente.post("/compras", json={"compra_id": "v1", "cliente_id": 42, "valor": "150.00", "data": "2025-01-01"})
    resposta = cliente.get("/clientes/42/saldo?em=2025-01-02")
    assert resposta.status_code == 200
    assert resposta.json() == {"saldo": 150, "expirado": 0, "expira_em_30_dias": 0, "lotes": [{"compra_em": "2025-01-01", "pontos": 150, "expira_em": "2026-01-01", "status": "ativo"}]}


def test_compra_da_tela_funciona_sem_compra_id():
    cliente = TestClient(criar_app(RepositorioEmMemoria()))
    resposta = cliente.post("/compras", json={"cliente_id": 42, "valor": "10.99", "data": "2025-01-01"})
    assert resposta.status_code == 201
    assert resposta.json()["criada"] is True
