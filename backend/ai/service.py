"""Serviço de orquestração do Agente de Recomendações com retry e fallback determinístico (RN-07 a RN-10)."""

from collections.abc import Mapping
import logging
from typing import Any

from backend.ai.grounding import validate_recommendations
from backend.ai.llm_client import LLMClient, LLMResponseError, LLMUnavailableError
from backend.ai.prompts import (
    PROMPT_VERSION,
    RECOMMENDATION_JSON_SCHEMA,
    build_system_prompt,
    build_user_message,
)
from data_pipeline.insights import build_fact_sheet, build_fallback_recommendations

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Coordena a geração de recomendações executivas a partir dos cálculos analíticos,
    garantindo ancoragem factual, validação estrita, tentativa de correção e fallback determinístico.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def generate_recommendations(
        self,
        metrics: Mapping[str, Any],
    ) -> tuple[list[dict[str, Any]], str, str | None, str, list[str]]:
        """
        Orquestra o ciclo completo de geração das 3 recomendações.

        Retorna:
            (recommendations, source, model, prompt_version, warnings)
        """
        facts = build_fact_sheet(metrics)
        warnings: list[str] = []

        system_prompt = build_system_prompt()
        initial_user_msg = build_user_message(facts)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": initial_user_msg},
        ]

        try:
            # 1. Primeira tentativa de geração via LLM
            raw_payload, _raw_text = self.llm_client.generate_json(
                messages=messages,
                schema=RECOMMENDATION_JSON_SCHEMA,
            )
            is_valid, errors, sanitized = validate_recommendations(raw_payload, facts)

            if is_valid:
                return sanitized, "llm", self.llm_client.model, PROMPT_VERSION, []

            logger.warning(
                "Primeira tentativa de recomendação pelo LLM falhou na validação de fatos: %s. Iniciando retry corretivo.",
                errors,
            )

            # 2. Retry corretivo único com explicação das violações
            retry_user_msg = build_user_message(facts, corrective_notes=errors)
            retry_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": retry_user_msg},
            ]

            retry_payload, _retry_text = self.llm_client.generate_json(
                messages=retry_messages,
                schema=RECOMMENDATION_JSON_SCHEMA,
            )
            retry_valid, retry_errors, retry_sanitized = validate_recommendations(
                retry_payload, facts
            )

            if retry_valid:
                return (
                    retry_sanitized,
                    "llm",
                    self.llm_client.model,
                    PROMPT_VERSION,
                    ["Recomendações corrigidas com sucesso via retry na segunda tentativa após auditoria."],
                )

            # Se o retry também falhou na auditoria, ativa fallback determinístico (RN-09)
            fallback_reason = (
                "IA gerou recomendações não ancoradas na Ficha de Fatos após retry corretivo: "
                + "; ".join(retry_errors)
            )
            logger.warning("%s. Acionando fallback determinístico.", fallback_reason)
            fallback_recs = build_fallback_recommendations(metrics, facts)
            return (
                fallback_recs,
                "deterministic_fallback",
                None,
                PROMPT_VERSION,
                [fallback_reason],
            )

        except (LLMUnavailableError, LLMResponseError) as exc:
            # LLM offline, timeout ou formato ininteligível -> fallback determinístico seguro (RN-09)
            fallback_reason = f"Serviço de IA indisponível ou resposta inválida ({type(exc).__name__}): {exc}"
            logger.info("%s. Utilizando fallback determinístico.", fallback_reason)
            fallback_recs = build_fallback_recommendations(metrics, facts)
            return (
                fallback_recs,
                "deterministic_fallback",
                None,
                PROMPT_VERSION,
                [fallback_reason],
            )
        except Exception as exc:
            # Qualquer exceção imprevista ativa o fallback com registro
            logger.exception("Erro inesperado na geração de recomendações. Acionando fallback determinístico.")
            fallback_recs = build_fallback_recommendations(metrics, facts)
            return (
                fallback_recs,
                "deterministic_fallback",
                None,
                PROMPT_VERSION,
                [f"Erro inesperado no pipeline de IA: {exc}"],
            )
