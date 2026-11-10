"""Schemas Pydantic v2 para validação de contratos de entrada e saída da API REST."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Resposta do endpoint GET /api/v1/health."""

    status: str = "ok"


class ValidationErrorItem(BaseModel):
    """Item individual de erro de validação de CSV (linha/coluna)."""

    row: int | None = None
    column: str | None = None
    message: str


class ValidationErrorResponse(BaseModel):
    """Formato padrão de erro estruturado (400 / 422)."""

    detail: str
    errors: list[ValidationErrorItem] = Field(default_factory=list)


class SummaryMetricsSchema(BaseModel):
    """Resumo executivo das métricas financeiras retornado no registro do upload."""

    gross_revenue: float
    discount_total: float
    net_revenue: float
    average_ticket_gross: float
    average_ticket_net: float
    canceled_revenue_loss: float
    top_abc_item: str | None = None


class UploadResponseSchema(BaseModel):
    """Metadados e resumo de um lote CSV processado (POST /api/v1/uploads e item de listagem)."""

    model_config = ConfigDict(from_attributes=True)

    upload_id: str
    filename: str
    created_at: str
    total_rows: int
    valid_orders_count: int
    canceled_orders_count: int
    summary_metrics: SummaryMetricsSchema


class UploadListResponseSchema(BaseModel):
    """Resposta da listagem de uploads realizados (GET /api/v1/uploads)."""

    items: list[UploadResponseSchema]
    total: int


class FinancialsSchema(BaseModel):
    """Indicadores financeiros consolidados do lote."""

    gross_revenue: float
    discount_total: float
    net_revenue: float
    valid_orders_count: int
    canceled_orders_count: int
    canceled_revenue_loss: float
    average_ticket_gross: float
    average_ticket_net: float


class ABCCurveItemSchema(BaseModel):
    """Item classificado na Curva ABC de produtos."""

    item_name: str
    category: str
    quantity_sold: int
    revenue: float
    revenue_share_pct: float
    cumulative_share_pct: float
    abc_class: Literal["A", "B", "C"]


class DelayedByCategorySchema(BaseModel):
    """Agregação de atrasos de preparo por categoria."""

    category: str
    delayed_items_count: int
    avg_prep_time_minutes: float


class CanceledByChannelSchema(BaseModel):
    """Métricas de cancelamento agregadas por canal."""

    channel: str
    canceled_orders_count: int
    total_orders_count: int
    cancellation_rate_pct: float
    canceled_revenue_loss: float


class CanceledByItemSchema(BaseModel):
    """Métricas de cancelamento agregadas por item do cardápio."""

    item_name: str
    category: str
    canceled_quantity: int
    canceled_revenue_loss: float


class AnomalySchema(BaseModel):
    """Alerta determinístico de anomalia operacional."""

    type: str
    severity: Literal["warning", "critical"]
    dimension: str
    description: str
    metric_value: float
    threshold_value: float


class BottlenecksSchema(BaseModel):
    """Diagnóstico completo de gargalos operacionais e cancelamentos."""

    prep_time_threshold_minutes: int
    delayed_orders_count: int
    delayed_items_count: int
    average_prep_time_minutes: float
    max_prep_time_minutes: float
    delayed_by_category: list[DelayedByCategorySchema]
    canceled_by_channel: list[CanceledByChannelSchema]
    canceled_by_item: list[CanceledByItemSchema]
    anomalies: list[AnomalySchema]


class ByChannelSchema(BaseModel):
    """Desempenho de vendas concluídas por canal."""

    channel: str
    valid_orders_count: int
    quantity_sold: int
    gross_revenue: float
    discount_total: float
    net_revenue: float
    revenue_share_pct: float
    average_ticket_net: float


class ByCategorySchema(BaseModel):
    """Desempenho de vendas concluídas por categoria."""

    category: str
    quantity_sold: int
    gross_revenue: float
    discount_total: float
    net_revenue: float
    revenue_share_pct: float
    average_prep_time_minutes: float


class UploadMetricsResponseSchema(BaseModel):
    """Relatório analítico completo e auditável de um lote (GET /api/v1/uploads/{upload_id}/metrics)."""

    upload_id: str
    filename: str
    created_at: str
    total_rows: int
    financials: FinancialsSchema
    abc_curve: list[ABCCurveItemSchema]
    bottlenecks: BottlenecksSchema
    by_channel: list[ByChannelSchema]
    by_category: list[ByCategorySchema]


class AiStatusSchema(BaseModel):
    """Status operacional do serviço de IA local (GET /api/v1/ai/status)."""

    ollama_reachable: bool
    base_url: str
    model: str
    model_available: bool


class EvidenceSchema(BaseModel):
    """Evidência atômica vinculada a um fato da Ficha de Fatos (RN-07)."""

    fact_id: str
    label: str
    value: float | int
    unit: str


class RecommendationSchema(BaseModel):
    """Recomendação executiva prioritária ancorada em fatos (RN-07, RN-08, RN-09)."""

    rank: int
    title: str
    theme: Literal[
        "cancelamento",
        "operacao",
        "mix",
        "receita",
        "delivery",
        "prep_time",
        "mix_products",
    ]
    diagnosis: str
    action: str
    expected_impact: str
    evidence: list[EvidenceSchema]


class RecommendationsResponseSchema(BaseModel):
    """Resposta com as 3 recomendações geradas/recuperadas de um lote (RN-10)."""

    run_id: str
    upload_id: str
    generated_at: str
    source: Literal["llm", "deterministic_fallback", "ollama"]
    model: str | None = None
    prompt_version: str
    recommendations: list[RecommendationSchema]
    warnings: list[str] = Field(default_factory=list)


class ExecutiveReportResponseSchema(BaseModel):
    """Relatório executivo consolidado do restaurante pronto para exportação (Entrega 0004)."""

    upload_id: str
    filename: str
    generated_at: str
    financials: FinancialsSchema
    top_abc_items: list[ABCCurveItemSchema]
    anomalies: list[AnomalySchema]
    recommendations: list[RecommendationSchema]
    recommendations_source: Literal["llm", "deterministic_fallback", "ollama"]
    report_markdown: str


