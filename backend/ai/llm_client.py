"""Cliente LLM desacoplado (Protocol) e implementação HTTP para o servidor Ollama local."""

import json
import re
from typing import Any, Protocol

import httpx

from backend.config import OllamaSettings, get_ollama_settings


class LLMUnavailableError(RuntimeError):
    """O servidor do LLM não respondeu: offline, timeout, erro HTTP ou modelo ausente."""


class LLMResponseError(ValueError):
    """O LLM respondeu, mas o conteúdo não é um JSON utilizável."""


class LLMClient(Protocol):
    """Contrato mínimo que qualquer provedor de LLM precisa cumprir."""

    model: str

    def generate_json(
        self, messages: list[dict[str, str]], schema: dict[str, Any]
    ) -> tuple[dict[str, Any], str]:
        """Envia as mensagens e devolve (JSON decodificado, texto bruto da resposta)."""
        ...

    def health(self) -> dict[str, Any]:
        """Devolve `{ollama_reachable, base_url, model, model_available}` sem levantar exceção."""
        ...


_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def parse_json_content(raw: str) -> dict[str, Any]:
    """Decodifica o conteúdo textual do modelo, tolerando bloco `<think>` e cercas de código."""
    cleaned = _THINK_BLOCK.sub("", raw or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    if not cleaned.startswith("{"):
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end > start:
            cleaned = cleaned[start : end + 1]
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMResponseError(f"Resposta do modelo não é JSON válido: {exc.msg}.") from exc
    if not isinstance(data, dict):
        raise LLMResponseError("Resposta do modelo não é um objeto JSON.")
    return data


def _model_matches(configured: str, available: str) -> bool:
    if configured == available:
        return True
    if ":" not in configured and available == f"{configured}:latest":
        return True
    return False


class OllamaClient:
    """Implementação de `LLMClient` sobre a API HTTP local do Ollama (`/api/chat`, `/api/tags`)."""

    def __init__(self, settings: OllamaSettings | None = None) -> None:
        self.settings = settings or get_ollama_settings()
        self.model = self.settings.model

    def generate_json(
        self, messages: list[dict[str, str]], schema: dict[str, Any]
    ) -> tuple[dict[str, Any], str]:
        body = {
            "model": self.settings.model,
            "messages": messages,
            "stream": False,
            "format": schema,
            "keep_alive": self.settings.keep_alive,
            "options": {
                "temperature": 0,
                "seed": self.settings.seed,
                "num_ctx": self.settings.num_ctx,
            },
        }
        try:
            with httpx.Client(timeout=self.settings.timeout_seconds) as client:
                response = client.post(f"{self.settings.base_url}/api/chat", json=body)
        except httpx.TimeoutException as exc:
            raise LLMUnavailableError(
                f"Tempo limite de {self.settings.timeout_seconds:.0f}s excedido aguardando o Ollama."
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMUnavailableError(
                f"Servidor Ollama inacessível em {self.settings.base_url}."
            ) from exc

        if response.status_code != 200:
            detail = ""
            try:
                detail = str(response.json().get("error", ""))
            except ValueError:
                detail = response.text[:200]
            raise LLMUnavailableError(
                f"Ollama respondeu HTTP {response.status_code}"
                + (f": {detail}" if detail else ".")
            )

        try:
            content = str(response.json()["message"]["content"])
        except (ValueError, KeyError, TypeError) as exc:
            raise LLMResponseError("Resposta do Ollama sem o campo `message.content`.") from exc

        return parse_json_content(content), content

    def health(self) -> dict[str, Any]:
        status: dict[str, Any] = {
            "ollama_reachable": False,
            "base_url": self.settings.base_url,
            "model": self.settings.model,
            "model_available": False,
        }
        try:
            with httpx.Client(timeout=self.settings.health_timeout_seconds) as client:
                response = client.get(f"{self.settings.base_url}/api/tags")
        except httpx.HTTPError:
            return status

        if response.status_code != 200:
            return status

        status["ollama_reachable"] = True
        try:
            models = response.json().get("models", [])
        except ValueError:
            return status

        names = {
            str(entry.get(key))
            for entry in models
            if isinstance(entry, dict)
            for key in ("name", "model")
            if entry.get(key)
        }
        status["model_available"] = any(_model_matches(self.settings.model, n) for n in names)
        return status
