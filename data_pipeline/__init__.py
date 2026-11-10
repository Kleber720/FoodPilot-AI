"""Interface pública do pacote determinístico de dados `data_pipeline` do FoodPilot AI."""

from data_pipeline.exceptions import CSVValidationError
from data_pipeline.insights import (
    build_fact_sheet,
    build_fallback_recommendations,
)
from data_pipeline.metrics import (
    CANCELLATION_RATE_THRESHOLD_PCT,
    PREP_TIME_THRESHOLD_MINUTES,
    calculate_metrics,
)
from data_pipeline.validator import (
    REQUIRED_COLUMNS,
    VALID_CHANNELS,
    VALID_STATUSES,
    validate_and_parse_csv,
)

__all__ = [
    "CSVValidationError",
    "validate_and_parse_csv",
    "calculate_metrics",
    "build_fact_sheet",
    "build_fallback_recommendations",
    "REQUIRED_COLUMNS",
    "VALID_STATUSES",
    "VALID_CHANNELS",
    "PREP_TIME_THRESHOLD_MINUTES",
    "CANCELLATION_RATE_THRESHOLD_PCT",
]
