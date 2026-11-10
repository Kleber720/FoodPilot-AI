/**
 * Contratos TypeScript espelhando estritamente `docs/contrato.md` (v1.1.0 — Entregas 0001 a 0003).
 * Nenhuma métrica financeira, operacional ou evidência de IA deve ser recalculada no cliente.
 */

export type ABCClass = 'A' | 'B' | 'C';

export type AnomalySeverity = 'warning' | 'critical';

export type SalesChannel = 'balcao' | 'delivery' | 'app';

export type RecommendationSource = 'ollama' | 'llm' | 'deterministic_fallback';

export type RecommendationTheme =
  | 'delivery'
  | 'prep_time'
  | 'mix_products'
  | 'cancelamento'
  | 'operacao'
  | 'mix'
  | 'receita';

export type EvidenceUnit = 'BRL' | '%' | 'min' | 'count';

/** Resposta de `GET /api/v1/health` (§2.1) */
export interface HealthResponse {
  status: string;
}

/** Item individual de erro de validação de CSV (§1 / §2.2) */
export interface ValidationErrorItem {
  row: number | null;
  column: string | null;
  message: string;
}

/** Envelope padrão de erro de validação `400` / `422` (§1 / §2.2) */
export interface ValidationErrorResponse {
  detail: string;
  errors: ValidationErrorItem[];
}

/** Resumo executivo das métricas financeiras do lote (§2.2 / §2.3) */
export interface SummaryMetrics {
  gross_revenue: number;
  discount_total: number;
  net_revenue: number;
  average_ticket_gross: number;
  average_ticket_net: number;
  canceled_revenue_loss: number;
  top_abc_item: string | null;
}

/** Metadados e resumo de um lote CSV processado (`POST /api/v1/uploads` e item de `GET /api/v1/uploads`) */
export interface UploadItem {
  upload_id: string;
  filename: string;
  created_at: string;
  total_rows: number;
  valid_orders_count: number;
  canceled_orders_count: number;
  summary_metrics: SummaryMetrics;
}

/** Resposta de listagem de lotes (`GET /api/v1/uploads` — §2.3) */
export interface UploadListResponse {
  items: UploadItem[];
  total: number;
}

/** Indicadores financeiros consolidados do lote (`RN-03`, `RN-04` — §2.4) */
export interface FinancialMetrics {
  gross_revenue: number;
  discount_total: number;
  net_revenue: number;
  valid_orders_count: number;
  canceled_orders_count: number;
  canceled_revenue_loss: number;
  average_ticket_gross: number;
  average_ticket_net: number;
}

/** Item classificado na Curva ABC de produtos (`RN-05` — §2.4) */
export interface ABCCurveItem {
  item_name: string;
  category: string;
  quantity_sold: number;
  revenue: number;
  revenue_share_pct: number;
  cumulative_share_pct: number;
  abc_class: ABCClass;
}

/** Agregação de atrasos de preparo por categoria (`RN-06` — §2.4) */
export interface DelayedCategoryItem {
  category: string;
  delayed_items_count: number;
  avg_prep_time_minutes: number;
}

/** Taxa e perda de cancelamento por canal (`RN-06` — §2.4) */
export interface CanceledChannelItem {
  channel: string;
  canceled_orders_count: number;
  total_orders_count: number;
  cancellation_rate_pct: number;
  canceled_revenue_loss: number;
}

/** Ocorrências e perda de cancelamento por item do cardápio (`RN-06` — §2.4) */
export interface CanceledItemMetric {
  item_name: string;
  category: string;
  canceled_quantity: number;
  canceled_revenue_loss: number;
}

/** Alerta determinístico de anomalia operacional (`RN-06` — §2.4) */
export interface AnomalyItem {
  type: string;
  severity: AnomalySeverity;
  dimension: string;
  description: string;
  metric_value: number;
  threshold_value: number;
}

/** Diagnóstico determinístico de gargalos operacionais e cancelamentos (`RN-06` — §2.4) */
export interface BottlenecksReport {
  prep_time_threshold_minutes: number;
  delayed_orders_count: number;
  delayed_items_count: number;
  average_prep_time_minutes: number;
  max_prep_time_minutes: number;
  delayed_by_category: DelayedCategoryItem[];
  canceled_by_channel: CanceledChannelItem[];
  canceled_by_item: CanceledItemMetric[];
  anomalies: AnomalyItem[];
}

/** Desempenho de vendas concluídas por canal (§2.4) */
export interface ChannelBreakdownItem {
  channel: string;
  valid_orders_count: number;
  quantity_sold: number;
  gross_revenue: number;
  discount_total: number;
  net_revenue: number;
  revenue_share_pct: number;
  average_ticket_net: number;
}

/** Desempenho de vendas concluídas por categoria (§2.4) */
export interface CategoryBreakdownItem {
  category: string;
  quantity_sold: number;
  gross_revenue: number;
  discount_total: number;
  net_revenue: number;
  revenue_share_pct: number;
  average_prep_time_minutes: number;
}

/** Relatório analítico completo do lote (`GET /api/v1/uploads/{upload_id}/metrics` — §2.4) */
export interface UploadMetricsResponse {
  upload_id: string;
  filename: string;
  created_at: string;
  total_rows: number;
  financials: FinancialMetrics;
  abc_curve: ABCCurveItem[];
  bottlenecks: BottlenecksReport;
  by_channel: ChannelBreakdownItem[];
  by_category: CategoryBreakdownItem[];
}

/** Status do servidor local Ollama e disponibilidade do modelo (`GET /api/v1/ai/status` — §2.5) */
export interface AiStatusResponse {
  ollama_reachable: boolean;
  base_url: string;
  model: string;
  model_available: boolean;
}

/** Fato atômico que comprova uma recomendação (`RN-07`, `RN-08` — §2.6) */
export interface EvidenceItem {
  fact_id: string;
  label: string;
  value: number;
  unit: EvidenceUnit;
}

/** Recomendação estruturada e fundamentada em fatos (`RN-08`, `RN-10` — §2.6) */
export interface RecommendationItem {
  rank: number;
  title: string;
  theme: RecommendationTheme;
  diagnosis: string;
  action: string;
  expected_impact: string;
  evidence: EvidenceItem[];
}

/** Resposta de geração ou consulta de recomendações (`POST` e `GET /api/v1/uploads/{upload_id}/recommendations` — §2.6, §2.7) */
export interface RecommendationsResponse {
  run_id?: string;
  upload_id: string;
  generated_at: string;
  source: RecommendationSource;
  model: string | null;
  prompt_version: string;
  warnings: string[];
  recommendations: RecommendationItem[];
}

/** Resposta do relatório executivo consolidado (`GET /api/v1/uploads/{upload_id}/report` — §2.8) */
export interface ExecutiveReportResponse {
  upload_id: string;
  filename: string;
  generated_at: string;
  financials: FinancialMetrics;
  top_abc_items: ABCCurveItem[];
  anomalies: AnomalyItem[];
  recommendations: RecommendationItem[];
  recommendations_source: RecommendationSource;
  report_markdown: string;
}

