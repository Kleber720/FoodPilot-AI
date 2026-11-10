"""Teste de integração real com o servidor local Ollama (marcado com @pytest.mark.ollama_live)."""

import pytest

from backend.ai.llm_client import OllamaClient
from backend.ai.prompts import (
    RECOMMENDATION_JSON_SCHEMA,
    build_system_prompt,
    build_user_message,
)
from backend.ai.service import RecommendationService
from data_pipeline import calculate_metrics, validate_and_parse_csv


@pytest.mark.ollama_live
def test_ollama_live_connectivity_and_generation(sample_csv_path):
    """
    Testa a conectividade real com o Ollama em `http://localhost:11434`.
    Se o servidor não estiver respondendo, pula o teste de forma graciosa sem quebrar a pipeline.
    """
    client = OllamaClient()
    health = client.health()

    if not health.get("ollama_reachable", False):
        pytest.skip(
            f"Servidor Ollama inacessível em {client.settings.base_url}. Teste ao vivo pulado."
        )

    if not health.get("model_available", False):
        pytest.skip(
            f"Modelo '{client.settings.model}' não encontrado no Ollama. Execute 'ollama pull {client.settings.model}'."
        )

    # Executa geração real contra o modelo local
    raw_bytes = sample_csv_path.read_bytes()
    df = validate_and_parse_csv(raw_bytes)
    metrics = calculate_metrics(df)

    service = RecommendationService(client)
    recs, source, model, prompt_version, warnings = service.generate_recommendations(metrics)

    assert source in {"llm", "deterministic_fallback"}
    assert len(recs) == 3
    ranks = [r["rank"] for r in recs]
    assert ranks == [1, 2, 3]
