"""Testes do serviço de recomendações com dublê de LLM (FakeLLMClient), retry e fallback (RN-07 a RN-10)."""

from pathlib import Path
from typing import Any

from backend.ai.llm_client import LLMResponseError, LLMUnavailableError
from backend.ai.service import RecommendationService
from data_pipeline import calculate_metrics, validate_and_parse_csv


class FakeLLMClient:
    """Dublê configurável de LLM para testes unitários e de integração determinísticos sem rede."""

    def __init__(
        self,
        responses: list[dict[str, Any] | Exception] | None = None,
        model: str = "qwen3:4b-instruct",
        reachable: bool = True,
        model_available: bool = True,
    ) -> None:
        self.responses = list(responses or [])
        self.model = model
        self.reachable = reachable
        self.model_available = model_available
        self.calls_count = 0
        self.received_messages: list[list[dict[str, str]]] = []

    def generate_json(
        self, messages: list[dict[str, str]], schema: dict[str, Any]
    ) -> tuple[dict[str, Any], str]:
        self.calls_count += 1
        self.received_messages.append(messages)

        if not self.responses:
            raise LLMUnavailableError("Sem respostas configuradas no FakeLLMClient.")

        resp = self.responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp, "{}"

    def health(self) -> dict[str, Any]:
        return {
            "ollama_reachable": self.reachable,
            "base_url": "http://localhost:11434",
            "model": self.model,
            "model_available": self.model_available,
        }


def _get_sample_metrics(sample_csv_path: Path):
    raw_bytes = sample_csv_path.read_bytes()
    df = validate_and_parse_csv(raw_bytes)
    return calculate_metrics(df)


def test_service_successful_generation_turn_one(sample_csv_path: Path):
    """Quando o LLM responde um JSON válido de primeira, devolve as recomendações higienizadas."""
    metrics = _get_sample_metrics(sample_csv_path)

    valid_payload = {
        "recommendations": [
            {
                "rank": 1,
                "title": "Ajuste Delivery",
                "theme": "delivery",
                "diagnosis": "Delivery com cancelamento de 20.0%.",
                "action": "Ajustar operação.",
                "expected_impact": "Diminuir perda de 474.00.",
                "evidence": [
                    {"fact_id": "chan.delivery.cancellation_rate_pct", "label": "Taxa", "value": 20.0, "unit": "%"}
                ],
            },
            {
                "rank": 2,
                "title": "Atrasos Cozinha",
                "theme": "prep_time",
                "diagnosis": "5 pedidos atrasados acima de 30 min.",
                "action": "Treinar equipe.",
                "expected_impact": "Reduzir média de 18.55 min.",
                "evidence": [
                    {"fact_id": "bot.delayed_orders_count", "label": "Atrasados", "value": 5, "unit": "count"}
                ],
            },
            {
                "rank": 3,
                "title": "Cardápio e Preços",
                "theme": "mix_products",
                "diagnosis": "Faturamento líquido de 4750.0.",
                "action": "Revisar preços.",
                "expected_impact": "Subir faturamento bruto acima de 5000.0.",
                "evidence": [
                    {"fact_id": "fin.gross_revenue", "label": "Bruto", "value": 5000.0, "unit": "BRL"}
                ],
            },
        ]
    }

    client = FakeLLMClient(responses=[valid_payload])
    service = RecommendationService(client)

    recs, source, model, prompt_version, warnings = service.generate_recommendations(metrics)

    assert source == "llm"
    assert model == "qwen3:4b-instruct"
    assert prompt_version == "rec-v1"
    assert len(recs) == 3
    assert len(warnings) == 0
    assert client.calls_count == 1


def test_service_successful_generation_on_retry(sample_csv_path: Path):
    """Quando o LLM falha no 1º turno com fato inventado mas corrige no retry, aceita a resposta corrigida."""
    metrics = _get_sample_metrics(sample_csv_path)

    invalid_payload = {
        "recommendations": [
            {
                "rank": 1,
                "title": "Inválido",
                "theme": "delivery",
                "diagnosis": "Sem fato",
                "action": "Sem ação",
                "expected_impact": "Sem impacto",
                "evidence": [{"fact_id": "fact_inexistente", "label": "X", "value": 1, "unit": "count"}],
            },
            {"rank": 2, "title": "T2", "theme": "prep_time", "diagnosis": "D2", "action": "A2", "expected_impact": "E2", "evidence": []},
            {"rank": 3, "title": "T3", "theme": "mix_products", "diagnosis": "D3", "action": "A3", "expected_impact": "E3", "evidence": []},
        ]
    }

    valid_payload = {
        "recommendations": [
            {
                "rank": 1,
                "title": "Corrigido Delivery",
                "theme": "delivery",
                "diagnosis": "Taxa de 20.0%.",
                "action": "Ação correta.",
                "expected_impact": "Impacto.",
                "evidence": [
                    {"fact_id": "chan.delivery.cancellation_rate_pct", "label": "Taxa", "value": 20.0, "unit": "%"}
                ],
            },
            {
                "rank": 2,
                "title": "Corrigido Cozinha",
                "theme": "prep_time",
                "diagnosis": "Tempo médio de 18.55 min.",
                "action": "Ação preparo.",
                "expected_impact": "Menos atrasos.",
                "evidence": [
                    {"fact_id": "bot.average_prep_time_minutes", "label": "Tempo Médio", "value": 18.55, "unit": "min"}
                ],
            },
            {
                "rank": 3,
                "title": "Corrigido Mix",
                "theme": "mix_products",
                "diagnosis": "Total bruto de 5000.0.",
                "action": "Ação cardápio.",
                "expected_impact": "Mais margem.",
                "evidence": [
                    {"fact_id": "fin.gross_revenue", "label": "Bruto", "value": 5000.0, "unit": "BRL"}
                ],
            },
        ]
    }

    client = FakeLLMClient(responses=[invalid_payload, valid_payload])
    service = RecommendationService(client)

    recs, source, model, prompt_version, warnings = service.generate_recommendations(metrics)

    assert source == "llm"
    assert len(recs) == 3
    assert client.calls_count == 2
    assert len(warnings) == 1
    assert "retry" in warnings[0].lower()


def test_service_triggers_fallback_when_retry_fails(sample_csv_path: Path):
    """Quando o LLM falha tanto no 1º turno quanto no retry, ativa o fallback determinístico (RN-09)."""
    metrics = _get_sample_metrics(sample_csv_path)

    invalid_payload = {
        "recommendations": [
            {"rank": 1, "title": "Inválido", "theme": "delivery", "diagnosis": "D", "action": "A", "expected_impact": "E", "evidence": []}
        ]
    }

    client = FakeLLMClient(responses=[invalid_payload, invalid_payload])
    service = RecommendationService(client)

    recs, source, model, prompt_version, warnings = service.generate_recommendations(metrics)

    assert source == "deterministic_fallback"
    assert model is None
    assert len(recs) == 3
    assert len(warnings) == 1
    assert client.calls_count == 2


def test_service_triggers_fallback_when_ollama_offline(sample_csv_path: Path):
    """Quando o Ollama está offline ou dá timeout, ativa o fallback determinístico de forma transparente."""
    metrics = _get_sample_metrics(sample_csv_path)

    client = FakeLLMClient(responses=[LLMUnavailableError("Ollama offline em http://localhost:11434")])
    service = RecommendationService(client)

    recs, source, model, prompt_version, warnings = service.generate_recommendations(metrics)

    assert source == "deterministic_fallback"
    assert model is None
    assert len(recs) == 3
    assert len(warnings) == 1
    assert "LLMUnavailableError" in warnings[0]
