"""Camada de IA local do FoodPilot AI: cliente LLM, prompts, ancoragem e serviço (Entrega 0003)."""

from backend.ai.grounding import validate_recommendations
from backend.ai.llm_client import (
    LLMClient,
    LLMResponseError,
    LLMUnavailableError,
    OllamaClient,
    parse_json_content,
)
from backend.ai.prompts import (
    PROMPT_VERSION,
    RECOMMENDATION_JSON_SCHEMA,
    build_system_prompt,
    build_user_message,
)
from backend.ai.service import RecommendationService

__all__ = [
    "LLMClient",
    "LLMResponseError",
    "LLMUnavailableError",
    "OllamaClient",
    "parse_json_content",
    "PROMPT_VERSION",
    "RECOMMENDATION_JSON_SCHEMA",
    "build_system_prompt",
    "build_user_message",
    "validate_recommendations",
    "RecommendationService",
]
