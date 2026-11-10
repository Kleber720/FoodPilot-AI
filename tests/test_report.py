"""Testes de integração para o Relatório Executivo Consolidado (Entrega 0004 — §2.8)."""

from backend.main import app, get_llm_client
from tests.conftest import SyncASGIClient
from tests.test_ai_service import FakeLLMClient


def test_get_executive_report_success(
    client: SyncASGIClient,
    sample_csv_bytes: bytes,
):
    """GET /api/v1/uploads/{id}/report consolida métricas, Pareto, anomalias, IA e Markdown executivo."""
    # 1. Faz upload do arquivo CSV
    upload_res = client.post(
        "/api/v1/uploads",
        files={"file": ("sample_orders.csv", sample_csv_bytes, "text/csv")},
    )
    assert upload_res.status_code == 201
    upload_id = upload_res.json()["upload_id"]

    # 2. Configura dublê de LLM
    fake = FakeLLMClient(responses=[])  # Aciona fallback determinístico de contingência
    app.dependency_overrides[get_llm_client] = lambda: fake

    try:
        response = client.get(f"/api/v1/uploads/{upload_id}/report")
        assert response.status_code == 200
        body = response.json()

        # Metadados
        assert body["upload_id"] == upload_id
        assert body["filename"] == "sample_orders.csv"
        assert body["generated_at"]

        # Indicadores financeiros
        fin = body["financials"]
        assert fin["gross_revenue"] == 5000.0
        assert fin["net_revenue"] == 4750.0
        assert fin["valid_orders_count"] == 50

        # Curva ABC (Classe A)
        top_abc = body["top_abc_items"]
        assert isinstance(top_abc, list)
        assert len(top_abc) >= 1
        assert all(item["abc_class"] == "A" for item in top_abc)

        # Anomalias operacionais
        assert isinstance(body["anomalies"], list)

        # Recomendações
        recs = body["recommendations"]
        assert len(recs) == 3
        ranks = [r["rank"] for r in recs]
        assert ranks == [1, 2, 3]
        assert body["recommendations_source"] == "deterministic_fallback"

        # Markdown executivo formatado
        md = body["report_markdown"]
        assert md
        assert "# Relatório Executivo de Inteligência Operacional — FoodPilot AI" in md
        assert "Resumo Executivo e Indicadores Financeiros" in md
        assert "Liderança de Cardápio (Curva ABC — Classe A)" in md
        assert "Recomendações Práticas Fundamentadas em Fatos" in md
        assert f"Lote Analisado:** `{upload_id}`" in md

    finally:
        app.dependency_overrides.pop(get_llm_client, None)


def test_get_executive_report_not_found(client: SyncASGIClient):
    """GET /api/v1/uploads/{id}/report retorna 404 para upload inexistente."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/uploads/{fake_id}/report")
    assert response.status_code == 404
    assert f"Upload '{fake_id}' não encontrado." in response.json()["detail"]
