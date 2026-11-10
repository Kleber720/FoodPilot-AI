# Matriz de Regras de Negócio e Verificação — FoodPilot AI

**Atualizado em:** 2026-11-09  
**Donos:** Lee (Back-end), Shikamaru (Dados) e Kakashi (Testes/Prova)  
**Entregas Cobertas:** 0001, 0002 e 0003 (`RN-01` a `RN-10`)

Esta matriz rastreia todas as regras de negócio verificáveis e invariantes do FoodPilot AI, vinculando a especificação de contrato/domínio à camada que a implementa e aos testes automatizados que a provam.

| ID | Regra | Fonte (Contrato/Domínio) | Camada | Teste que prova (a preencher pelo Kakashi) | Estado |
| --- | --- | --- | --- | --- | --- |
| `RN-01` | **Validação de schema, tipos e domínio do CSV de pedidos:** exige as 10 colunas obrigatórias (`order_id`, `timestamp`, `item_name`, `category`, `quantity`, `unit_price`, `discount`, `prep_time_minutes`, `status`, `channel`), arquivo não vazio, `quantity >= 1` (inteiro), `unit_price > 0`, `0 <= discount <= quantity * unit_price`, `prep_time_minutes >= 0`, `status` em `{"completed", "canceled"}`, `channel` em `{"balcao", "delivery", "app"}` e consistência de `status`/`channel` por `order_id`. Retorna `400 Bad Request` se nenhum arquivo for enviado ou `422 Unprocessable Entity` com lista `errors` (`row`, `column`, `message`) se o CSV for inválido. | [`docs/contrato.md`](contrato.md) (§2.2, §3), [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (§2, `RN-01`) e [`docs/dados/pedidos-csv.md`](dados/pedidos-csv.md) (§3) | `data_pipeline/validator.py` + `backend/main.py` | `tests/test_validator_rn01.py` (`test_rn01_valid_sample_csv_returns_typed_dataframe`, `test_rn01_valid_boundary_values_zero_discount_zero_prep_and_full_discount`, `test_rn01_rejects_empty_csv_file`, `test_rn01_rejects_header_only_without_data_rows`, `test_rn01_rejects_missing_required_columns`, `test_rn01_rejects_empty_or_null_values_in_required_fields`, `test_rn01_rejects_invalid_quantity`, `test_rn01_rejects_non_positive_unit_price`, `test_rn01_rejects_negative_or_excessive_discount`, `test_rn01_rejects_negative_prep_time_minutes`, `test_rn01_rejects_invalid_status_enum`, `test_rn01_rejects_invalid_channel_enum`, `test_rn01_rejects_intra_order_inconsistency_for_status_and_channel`, `test_rn01_collects_multiple_errors_across_rows_without_truncating`) | Provada por testes automatizados (Etapa 4) |
| `RN-02` | **Atomicidade de rejeição sem gravar no banco:** qualquer falha de validação (`RN-01`) em qualquer linha do CSV impede a gravação parcial no SQLite (`0` registros inseridos em `uploads` e `order_items`). Quando válido, o lote e todos os seus itens são persistidos na mesma transação. | [`docs/contrato.md`](contrato.md) (§2.2) e [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (§3, `RN-02`) | `backend/main.py` + `backend/models.py` (SQLAlchemy + SQLite) | `tests/test_api_and_atomicity_rn02.py` (`test_api_health_endpoint_returns_200_ok`, `test_rn02_upload_without_file_or_empty_filename_returns_400_bad_request`, `test_rn02_atomicity_rejects_mixed_valid_and_invalid_csv_without_partial_sqlite_writes`, `test_rn02_valid_upload_persists_atomically_and_serves_metrics_end_to_end`, `test_api_get_metrics_for_nonexistent_upload_returns_404_not_found`) | Provada por testes automatizados (Etapa 4) |
| `RN-03` | **Cálculo determinístico de Faturamento Bruto, Descontos, Faturamento Líquido e Perda por Cancelamento:** `gross_revenue = round(sum(quantity * unit_price), 2)` apenas para `status == "completed"`; `discount_total = round(sum(discount), 2)` apenas para `status == "completed"`; `net_revenue = round(gross_revenue - discount_total, 2)`; itens `canceled` são estritamente excluídos do faturamento e contabilizados apenas em `canceled_revenue_loss`. | [`docs/contrato.md`](contrato.md) (§2.2, §2.4, §3), [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (`RN-03`) e [`docs/dados/pedidos-csv.md`](dados/pedidos-csv.md) (§5.1) | `data_pipeline/metrics.py` (`pandas`) + `backend/main.py` | `tests/test_metrics_rn03_to_rn06.py` (`test_rn03_canonical_dataset_financial_metrics`, `test_rn03_canceled_orders_never_contaminate_revenue_or_discounts`, `test_rn03_only_canceled_orders_returns_zero_revenues`) e `tests/test_api_and_atomicity_rn02.py::test_rn02_valid_upload_persists_atomically_and_serves_metrics_end_to_end` | Provada por testes automatizados (Etapa 4) |
| `RN-04` | **Cálculo de Ticket Médio por `order_id` único concluído:** `valid_orders_count` conta valores distintos de `order_id` com `status == "completed"` (múltiplos itens de um mesmo pedido contam como 1 pedido); `average_ticket_gross = round(gross_revenue / valid_orders_count, 2)` e `average_ticket_net = round(net_revenue / valid_orders_count, 2)` (`0.0` quando `valid_orders_count == 0`). | [`docs/contrato.md`](contrato.md) (§2.2, §2.4, §3), [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (`RN-04`) e [`docs/dados/pedidos-csv.md`](dados/pedidos-csv.md) (§5.1) | `data_pipeline/metrics.py` (`pandas`) + `backend/main.py` | `tests/test_metrics_rn03_to_rn06.py` (`test_rn04_canonical_dataset_average_ticket_and_order_counts`, `test_rn04_multi_item_order_counts_as_single_order_in_denominator`, `test_rn04_zero_valid_orders_returns_zero_ticket_without_division_error`) e `tests/test_api_and_atomicity_rn02.py::test_rn02_valid_upload_persists_atomically_and_serves_metrics_end_to_end` | Provada por testes automatizados (Etapa 4) |
| `RN-05` | **Cálculo, ordenação e classificação da Curva ABC:** agrupa itens de pedidos `completed` por `item_name`, ordena por `revenue` decrescente (desempate por `item_name` crescente), calcula `revenue_share_pct` e `cumulative_share_pct` (fechando em `100.0%` no último item) e classifica em `"A"` (`cumulative_share_pct <= 80.0` ou primeiro item da lista), `"B"` (`80.0 < cumulative_share_pct <= 95.0`) e `"C"` (`> 95.0`). | [`docs/contrato.md`](contrato.md) (§2.4, §3), [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (`RN-05`) e [`docs/dados/pedidos-csv.md`](dados/pedidos-csv.md) (§5.2) | `data_pipeline/metrics.py` (`pandas`) + `backend/main.py` | `tests/test_metrics_rn03_to_rn06.py` (`test_rn05_canonical_dataset_abc_curve_classification_and_ordering`, `test_rn05_tie_breaking_by_item_name_ascending_and_excludes_canceled_items`, `test_rn05_single_leader_above_80_pct_still_gets_class_a`) | Provada por testes automatizados (Etapa 4) |
| `RN-06` | **Identificação determinística de gargalos e desvios operacionais:** identifica atrasos de preparo em itens `completed` com `prep_time_minutes > 30` (contagem de pedidos/itens atrasados e agregação por categoria), calcula taxa de cancelamento por canal (`canceled_orders_count / total_orders_count * 100`) e perda por item cancelado, e gera alertas em `anomalies` quando há itens com `prep_time_minutes > 30` ou canais com `cancellation_rate_pct > 10.0%`. | [`docs/contrato.md`](contrato.md) (§2.4, §3), [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (`RN-06`) e [`docs/dados/pedidos-csv.md`](dados/pedidos-csv.md) (§5.3) | `data_pipeline/metrics.py` (`pandas`) + `backend/main.py` | `tests/test_metrics_rn03_to_rn06.py` (`test_rn06_canonical_dataset_bottlenecks_anomalies_and_breakdowns`, `test_rn06_boundary_conditions_prep_time_30_and_cancellation_rate_10`) | Provada por testes automatizados (Etapa 4) |
| `RN-07` | **Construção determinística da Ficha de Fatos (`Fact Sheet`):** `build_fact_sheet(metrics)` transforma o resultado de `calculate_metrics` em uma lista ordenada e pura de fatos atômicos (`fact_id`, `category`, `label`, `value`, `unit`, `formatted`), incluindo os limiares operacionais (`thr.prep_time_minutes = 30.0`, `thr.cancellation_rate_pct = 10.0`), fatos financeiros (`fin.*`), gargalos (`bot.*`), canais (`chan.*`), categorias (`cat.*`) e Curva ABC (`abc.*`). | [`docs/contrato.md`](contrato.md) (§3.2) e [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (`RN-07`) | `data_pipeline/insights.py` | *A preencher pelo Kakashi na Etapa 5* | Especificada (Etapa 1 — Entrega 0003) |
| `RN-08` | **Aterramento numérico estrito e anti-alucinação (`Grounding`):** `validate_recommendations(payload, facts)` exige exatamente 3 recomendações com `rank` único (`1`, `2`, `3`), valida que todo `fact_id` citado em `evidence[]` existe na ficha de fatos, audita que todo número presente nos textos (`title`, `diagnosis`, `action`, `expected_impact`) corresponde a um fato (tolerância `±0.01`, aceitando formatos pt-BR e US) e sobrescreve `evidence[].value`, `label` e `unit` pelos valores oficiais do fato. | [`docs/contrato.md`](contrato.md) (§2.6) e [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (`RN-08`) | `backend/ai/grounding.py` + `backend/ai/service.py` | *A preencher pelo Kakashi na Etapa 5* | Especificada (Etapa 1 — Entrega 0003) |
| `RN-09` | **Degradação graciosa e fallback determinístico de recomendações:** quando o Ollama está offline, excede o timeout (`90s`) ou produz 2 respostas inválidas consecutivas (após 1 retry corretivo), o sistema aciona `build_fallback_recommendations`, retorna `201 Created` (nunca `5xx`) com `source = "deterministic_fallback"`, `model = null` e registra o motivo em `warnings[]`. | [`docs/contrato.md`](contrato.md) (§2.5, §2.6, §3.2) e [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (`RN-09`) | `data_pipeline/insights.py` + `backend/ai/service.py` + `backend/main.py` | *A preencher pelo Kakashi na Etapa 5* | Especificada (Etapa 1 — Entrega 0003) |
| `RN-10` | **Estrutura, ordenação, persistência e consulta das 3 recomendações:** persiste cada execução na tabela `recommendation_runs` no SQLite (migração `0002_recommendations.py`), expõe `GET /api/v1/ai/status` (`200 OK`), `POST /api/v1/uploads/{upload_id}/recommendations` (`201 Created` ou `404 Not Found`) e `GET /api/v1/uploads/{upload_id}/recommendations` (`200 OK` com a execução mais recente ou `404 Not Found`). | [`docs/contrato.md`](contrato.md) (§2.5, §2.6, §2.7) e [`docs/dominio/pedidos-e-metricas.md`](dominio/pedidos-e-metricas.md) (`RN-10`) | `backend/models.py` + `backend/alembic/versions/0002_recommendations.py` + `backend/main.py` | *A preencher pelo Kakashi na Etapa 5* | Especificada (Etapa 1 — Entrega 0003) |

---

## Detalhamento Matemático das Regras em `data_pipeline/` (Etapa 2 — Shikamaru)

### 1. Fórmulas Determinísticas (`RN-03` e `RN-04`)

Seja $D$ o conjunto de linhas validadas do CSV, $D_{\text{comp}} = \{r \in D \mid r.\text{status} = \text{"completed"}\}$ e $D_{\text{canc}} = \{r \in D \mid r.\text{status} = \text{"canceled"}\}$:

- **Faturamento Bruto (`gross_revenue`):**
  $$\text{gross\_revenue} = \text{round}\left(\sum_{r \in D_{\text{comp}}} (r.\text{quantity} \times r.\text{unit\_price}),\ 2\right)$$
- **Total de Descontos (`discount_total`):**
  $$\text{discount\_total} = \text{round}\left(\sum_{r \in D_{\text{comp}}} r.\text{discount},\ 2\right)$$
- **Faturamento Líquido (`net_revenue`):**
  $$\text{net\_revenue} = \text{round}\left(\text{gross\_revenue} - \text{discount\_total},\ 2\right)$$
- **Perda por Cancelamento (`canceled_revenue_loss`):**
  $$\text{canceled\_revenue\_loss} = \text{round}\left(\sum_{r \in D_{\text{canc}}} (r.\text{quantity} \times r.\text{unit\_price}),\ 2\right)$$
- **Pedidos Concluídos e Cancelados Únicos (`valid_orders_count`, `canceled_orders_count`):**
  $$\text{valid\_orders\_count} = \left|\{r.\text{order\_id} \mid r \in D_{\text{comp}}\}\right|, \quad \text{canceled\_orders\_count} = \left|\{r.\text{order\_id} \mid r \in D_{\text{canc}}\}\right|$$
- **Ticket Médio Bruto e Líquido (`average_ticket_gross`, `average_ticket_net`):**
  $$\text{average\_ticket\_gross} = \begin{cases} \text{round}\left(\dfrac{\text{gross\_revenue}}{\text{valid\_orders\_count}},\ 2\right) & \text{se } \text{valid\_orders\_count} > 0 \\ 0.0 & \text{caso contrário} \end{cases}$$
  $$\text{average\_ticket\_net} = \begin{cases} \text{round}\left(\dfrac{\text{net\_revenue}}{\text{valid\_orders\_count}},\ 2\right) & \text{se } \text{valid\_orders\_count} > 0 \\ 0.0 & \text{caso contrário} \end{cases}$$

### 2. Fórmulas da Curva ABC (`RN-05`)

Para cada produto distinto $p$ em $D_{\text{comp}}$, ordenado por $\text{revenue}_p$ decrescente e $\text{item\_name}_p$ crescente ($k = 0, 1, \dots, m-1$):

- $\text{revenue}_k = \text{round}\left(\sum_{r \in D_{\text{comp}}, r.\text{item\_name}=p_k} (r.\text{quantity} \times r.\text{unit\_price}),\ 2\right)$
- $\text{revenue\_share\_pct}_k = \text{round}\left(\frac{\text{revenue}_k}{\text{gross\_revenue}} \times 100.0,\ 2\right)$
- $\text{cumulative\_share\_pct}_k = \begin{cases} 100.0 & \text{se } k = m - 1 \\ \text{round}\left(\frac{\sum_{j=0}^{k} \text{revenue}_j}{\text{gross\_revenue}} \times 100.0,\ 2\right) & \text{se } k < m - 1 \end{cases}$
- Classificação $\text{abc\_class}_k$:
  - `"A"` se $k = 0$ ou $\text{cumulative\_share\_pct}_k \le 80.0$
  - `"B"` se $k > 0$ e $80.0 < \text{cumulative\_share\_pct}_k \le 95.0$
  - `"C"` se $k > 0$ e $\text{cumulative\_share\_pct}_k > 95.0$

### 3. Fórmulas de Gargalos e Anomalias (`RN-06`)

- **Atrasos de Preparo:** $D_{\text{delay}} = \{r \in D_{\text{comp}} \mid r.\text{prep\_time\_minutes} > 30.0\}$
  - $\text{delayed\_items\_count} = |D_{\text{delay}}|$
  - $\text{delayed\_orders\_count} = |\{r.\text{order\_id} \mid r \in D_{\text{delay}}\}|$
  - Anomalia `high_prep_time` por categoria em $D_{\text{delay}}$: `severity = "critical"` se `avg_prep_time_minutes > 45.0` ou `delayed_items_count >= 5`; caso contrário `"warning"`.
- **Taxa de Cancelamento por Canal $c$:**
  - $\text{cancellation\_rate\_pct}_c = \text{round}\left(\frac{\text{canceled\_orders\_count}_c}{\text{total\_orders\_count}_c} \times 100.0,\ 2\right)$
  - Anomalia `high_cancellation_rate` acionada quando $\text{cancellation\_rate\_pct}_c > 10.0$: `severity = "critical"` se $\text{cancellation\_rate\_pct}_c \ge 20.0$; caso contrário `"warning"`.

### 4. Valores de Referência para Auditoria em `data/sample_orders.csv`

| Indicador / Regra | Valor Esperado Exato |
| --- | --- |
| `total_rows` | `82` |
| `valid_orders_count` / `canceled_orders_count` | `50` / `5` |
| `gross_revenue` / `discount_total` / `net_revenue` (`RN-03`) | `5000.0` / `250.0` / `4750.0` |
| `canceled_revenue_loss` (`RN-03`) | `514.0` |
| `average_ticket_gross` / `average_ticket_net` (`RN-04`) | `100.0` / `95.0` |
| `top_abc_item` (`RN-05`) | `"Combo Burger Duplo Artesanal"` (`revenue = 2000.0`, `40.0%`) |
| Classes `abc_curve` (`RN-05`) | Classe `A`: 3 itens (`79.2%` acum.); Classe `B`: 2 itens (`94.5%` acum.); Classe `C`: 3 itens (`100.0%` acum.) |
| `delayed_orders_count` / `delayed_items_count` (`RN-06`) | `5` pedidos / `6` itens (`average_prep_time_minutes = 18.55`, `max_prep_time_minutes = 46.0`) |
| `canceled_by_channel` (`RN-06`) | `delivery`: `20.0%` (`4/20`, perda `474.0`); `app`: `5.0%` (`1/20`, perda `40.0`); `balcao`: `0.0%` (`0/15`, perda `0.0`) |
| `anomalies` (`RN-06`) | 3 anomalias: `high_prep_time` em `Burgers` (`warning`, `39.0`), `high_prep_time` em `Combos` (`warning`, `40.0`), `high_cancellation_rate` em `delivery` (`critical`, `20.0`) |
