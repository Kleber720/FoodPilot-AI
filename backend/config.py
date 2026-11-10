"""Configuração de execução do back-end lida de variáveis de ambiente (ADR 0002)."""

import os
from dataclasses import dataclass

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "qwen3:4b-instruct"
DEFAULT_OLLAMA_TIMEOUT_SECONDS = 90.0
DEFAULT_OLLAMA_HEALTH_TIMEOUT_SECONDS = 3.0
DEFAULT_OLLAMA_SEED = 42
DEFAULT_OLLAMA_NUM_CTX = 8192
DEFAULT_OLLAMA_KEEP_ALIVE = "10m"


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class OllamaSettings:
    """Parâmetros de conexão e geração do servidor Ollama local."""

    base_url: str
    model: str
    timeout_seconds: float
    health_timeout_seconds: float
    seed: int
    num_ctx: int
    keep_alive: str


def get_ollama_settings() -> OllamaSettings:
    """Lê as variáveis `OLLAMA_*` do ambiente, com os padrões definidos no ADR 0002."""
    base_url = (os.getenv("OLLAMA_BASE_URL") or DEFAULT_OLLAMA_BASE_URL).strip().rstrip("/")
    model = (os.getenv("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL).strip()
    return OllamaSettings(
        base_url=base_url,
        model=model,
        timeout_seconds=_env_float("OLLAMA_TIMEOUT_SECONDS", DEFAULT_OLLAMA_TIMEOUT_SECONDS),
        health_timeout_seconds=_env_float(
            "OLLAMA_HEALTH_TIMEOUT_SECONDS", DEFAULT_OLLAMA_HEALTH_TIMEOUT_SECONDS
        ),
        seed=_env_int("OLLAMA_SEED", DEFAULT_OLLAMA_SEED),
        num_ctx=_env_int("OLLAMA_NUM_CTX", DEFAULT_OLLAMA_NUM_CTX),
        keep_alive=(os.getenv("OLLAMA_KEEP_ALIVE") or DEFAULT_OLLAMA_KEEP_ALIVE).strip(),
    )
