"""Testes de integração para as rotas de IA e Recomendações (RN-07 a RN-10 — §2.5, §2.6, §2.7)."""

from pathlib import Path

from backend.main import app, get_llm_client
from backend.models import RecommendationRun
from tests.conftest import SyncASGIClient
from tests.test_ai_service import FakeLLMClient


def test_get_ai_status(client: SyncASGIClient):
    """GET /api/v1/ai/status retorna o status operacional do LLM."""
    fake = FakeLLMClient(reachable=True, model_available=True)
    app.dependency_overrides[get_llm_client] = lambda: fake
    try:
        response = client.get("/api/v1/ai/status")
        assert response.status_code == 200
        body = response.json()
        assert body["ollama_reachable"] is True
        assert body["model"] == "qwen3:4b-instruct"
        assert body["model_available"] is True
    finally:
        app.dependency_overrides.pop(get_llm_client, None)


def test_generate_and_get_recommendations_flow(
    client: SyncASGIClient,
    sample_csv_bytes: bytes,
    db_session,
):
    """POST e GET /api/v1/uploads/{id}/recommendations geram, persistem no SQLite e recuperam."""
    # 1. Faz o upload do arquivo CSV primeiro
    upload_res = client.post(
        "/api/v1/uploads",
        files={"file": ("sample_orders.csv", sample_csv_bytes, "text/csv")},
    )
    assert upload_res.status_code == 201
    upload_id = upload_res.json()["upload_id"]

    # 2. Configura FakeLLMClient com fallback ou payload direto
    fake = FakeLLMClient(responses=[])  # Sem respostas -> fallback determinístico seguro
    app.dependency_overrides[get_llm_client] = lambda: fake

    try:
        # POST: Gera recomendações
        post_res = client.post(f"/api/v1/uploads/{upload_id}/recommendations")
        assert post_res.status_code == 201
        post_body = post_res.json()

        assert post_body["run_id"]
        assert post_body["upload_id"] == upload_id
        assert post_body["source"] == "deterministic_fallback"
        assert len(post_body["recommendations"]) == 3
        ranks = [r["rank"] for r in post_body["recommendations"]]
        assert ranks == [1, 2, 3]

        # Verifica persistência no SQLite
        persisted = (
            db_session.query(RecommendationRun)
            .filter_by(upload_id=upload_id)
            .first()
        )
        assert persisted is not None
        assert persisted.source == "deterministic_fallback"
        assert len(persisted.recommendations) == 3

        # GET: Recupera a execução previamente persistida
        get_res = client.get(f"/api/v1/uploads/{upload_id}/recommendations")
        assert get_res.status_code == 200
        get_body = get_res.json()
        assert get_body["upload_id"] == upload_id
        assert get_body["source"] == "deterministic_fallback"
        assert len(get_body["recommendations"]) == 3
        assert get_body["recommendations"][0]["title"] == post_body["recommendations"][0]["title"]

    finally:
        app.dependency_overrides.pop(get_llm_client, None)


def test_recommendations_not_found(client: SyncASGIClient):
    """Rotas de recomendações retornam 404 para upload_id inexistente."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    post_res = client.post(f"/api/v1/uploads/{fake_id}/recommendations")
    assert post_res.status_code == 404
    assert f"Upload '{fake_id}' não encontrado." in post_res.json()["detail"]

    get_res = client.get(f"/api/v1/uploads/{fake_id}/recommendations")
    assert get_res.status_code == 404
    assert f"Upload '{fake_id}' não encontrado." in get_res.json()["detail"]
