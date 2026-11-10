"""Exceções customizadas do pipeline determinístico de dados do FoodPilot AI."""

from typing import Any


class CSVValidationError(ValueError):
    """Exceção levantada quando o arquivo CSV falha na validação estrutural ou de domínio."""

    def __init__(self, detail: str, errors: list[dict[str, Any]]) -> None:
        super().__init__(detail)
        self.detail: str = detail
        self.errors: list[dict[str, Any]] = errors

    def to_dict(self) -> dict[str, Any]:
        """Converte a exceção para o formato padrão de erro do contrato HTTP 422/400."""
        return {
            "detail": self.detail,
            "errors": self.errors,
        }
