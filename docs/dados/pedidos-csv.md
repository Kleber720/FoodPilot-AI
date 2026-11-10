# Data Card — Dataset de Pedidos de Restaurante (`data/sample_orders.csv`)

**Fonte:** `data/sample_orders.csv` (Dataset Simulado de Referência — FoodPilot AI)  
**Dono:** Shikamaru (Dados) · **Contrato Alinhado com:** Lee (Back-end, [`docs/contrato.md`](../contrato.md) e [`docs/dominio/pedidos-e-metricas.md`](../dominio/pedidos-e-metricas.md))  
**Data do Snapshot:** 2026-11-09  
**Veredito de Qualidade:** **Usável** (100% aderente às regras `RN-01` a `RN-06`, sem valores ausentes, sem PII e com fechamento contábil exato).

---

## 1. Origem, Dono e Propósito

- **Origem:** Conjunto de dados sintético e determinístico construído para representar uma semana de operação comercial de uma hamburgueria artesanal (*FoodPilot Burger*) operando em três canais (`delivery`, `app`, `balcao`).
- **Dono:** Shikamaru (Especialista de Dados).
- **Caminho no Repositório:** [`data/sample_orders.csv`](../../data/sample_orders.csv)
- **Propósito:**
  1. Servir como fixture canônica de validação do motor determinístico em `pandas` (`data_pipeline/`), da persistência transacional SQLite (`backend/`) e da suíte de auditoria automatizada (`tests/`).
  2. Exercitar todos os casos operacionais exigidos pelo domínio: pedidos com múltiplos itens compartilhando o mesmo `order_id`, descontos promocionais na linha, pedidos concluídos (`completed`) e cancelados (`canceled`), distribuição completa na Curva ABC (`A`, `B`, `C`), atrasos de preparo (`prep_time_minutes > 30`) e anomalia crítica de cancelamento por canal (`cancellation_rate_pct > 10.0%`).

---

## 2. Contrato, Chave e Granularidade

- **Formato do Arquivo:** Texto CSV codificado em `UTF-8`, separado por vírgula (`,`), com ponto (`.`) como separador decimal e cabeçalho obrigatório na linha `1`.
- **Granularidade (Grão):** **Uma linha por item de pedido (`order_item`)**.
  - Um pedido comercial (`order_id`) pode conter **1 ou mais linhas** no CSV.
  - Exemplo no dataset: o pedido `ORD-001` possui 2 linhas (`Combo Burger Duplo Artesanal` e `Porcao Batata Rustica Trufada`), compondo um único pedido concluído (`valid_orders_count += 1`).
- **Chave Lógica:** Composta por `(order_id, item_name)` dentro do lote, sendo `order_id` o identificador agrupador do pedido.
- **Período Coberto:** `2026-11-01T18:10:00Z` a `2026-11-07T22:30:00Z` (UTC, formato ISO-8601).
- **Volume do Snapshot (`data/sample_orders.csv`):**
  - **Total de linhas de dados (`total_rows`):** `82` linhas (linhas `2` a `83` do arquivo CSV).
  - **Total de pedidos únicos (`order_id`):** `55` pedidos (`ORD-001` a `ORD-055`), sendo `50` concluídos (`completed`) e `5` cancelados (`canceled`).

---

## 3. Esquema e Dicionário das 10 Colunas Obrigatórias

| # | Coluna | Tipo (`pandas` / Python) | Unidade | Obrigatória | Regras de Domínio e Validação (`RN-01`) |
| --- | --- | --- | --- | --- | --- |
| 1 | `order_id` | `str` | — | Sim | Identificador não vazio após `strip()`. Todas as linhas com mesmo `order_id` devem ter o mesmo `status` e o mesmo `channel`. |
| 2 | `timestamp` | `str` (ISO-8601) | Data/Hora UTC | Sim | String conversível para data/hora válida (ex.: `2026-11-01T18:10:00Z`). Números puros ou datas inválidas são rejeitados. |
| 3 | `item_name` | `str` | — | Sim | Nome comercial do item no cardápio, não vazio após `strip()`. |
| 4 | `category` | `str` | — | Sim | Categoria do cardápio (`Combos`, `Burgers`, `Porcoes`, `Sobremesas`, `Bebidas`), não vazia após `strip()`. |
| 5 | `quantity` | `int64` / `int` | Unidades | Sim | Inteiro estritamente positivo (`quantity >= 1`). Valores `<= 0` ou decimais (ex.: `1.5`) são rejeitados. |
| 6 | `unit_price` | `float64` / `float` | BRL (`R$`) | Sim | Valor monetário unitário estritamente positivo (`unit_price > 0.0`). Zero ou negativo são rejeitados. |
| 7 | `discount` | `float64` / `float` | BRL (`R$`) | Sim | Desconto monetário total aplicado na linha (`0.0 <= discount <= quantity * unit_price`). |
| 8 | `prep_time_minutes` | `float64` / `float` | Minutos (`min`) | Sim | Tempo de preparo na cozinha, não-negativo (`prep_time_minutes >= 0.0`). |
| 9 | `status` | `str` (Enum) | — | Sim | Estado final do pedido. Valores permitidos: `"completed"` ou `"canceled"`. |
| 10 | `channel` | `str` (Enum) | — | Sim | Canal de origem do pedido. Valores permitidos: `"balcao"`, `"delivery"` ou `"app"`. |

---

## 4. Dimensões de Qualidade Medidas no Snapshot

| Dimensão | Medição em `data/sample_orders.csv` | Resultado |
| --- | --- | --- |
| **Completude** | Contagem de nulos/vazios nas 10 colunas ao longo das 82 linhas | `0` valores ausentes (100% completo). |
| **Unicidade e Grão** | 55 `order_id` distintos distribuídos em 82 linhas de itens (27 pedidos com 2 itens e 28 pedidos com 1 item) | Sem duplicatas acidentais; grão de `order_item` preservado. |
| **Validade** | Checagem de tipos, faixas (`quantity >= 1`, `unit_price > 0`, `0 <= discount <= subtotal`, `prep_time_minutes >= 0`) e enums (`status`, `channel`) | 100% das 82 linhas aprovadas em `validate_and_parse_csv`. |
| **Consistência Intra-Pedido** | Verificação de unicidade de `status` e `channel` por `order_id` | `0` divergências (cada `order_id` possui exatamente 1 `status` e 1 `channel`). |
| **Consistência Contábil** | `gross_revenue (5000.0) - discount_total (250.0) == net_revenue (4750.0)` e soma de `revenue` da Curva ABC == `5000.0` (`100.0%`) | Fechamento exato sem resíduo de arredondamento. |

---

## 5. Valores Matemáticos Exatos de Referência (`data/sample_orders.csv`)

Comando que reproduz todos os números abaixo a partir da raiz do projeto:

```powershell
.venv\Scripts\python.exe -c "import json, pathlib; from data_pipeline import validate_and_parse_csv, calculate_metrics; df = validate_and_parse_csv(pathlib.Path('data/sample_orders.csv').read_bytes()); print(json.dumps(calculate_metrics(df), indent=2, ensure_ascii=False))"
```

### 5.1. Indicadores Financeiros e de Volume (`financials` e `summary_metrics`)

| Métrica | Campo no JSON | Valor Exato | Memória de Cálculo |
| --- | --- | --- | --- |
| Total de Linhas do CSV | `total_rows` | `82` | 74 linhas `completed` + 8 linhas `canceled` |
| Pedidos Concluídos Únicos | `valid_orders_count` | `50` | `ORD-001` a `ORD-050` (`status == "completed"`) |
| Pedidos Cancelados Únicos | `canceled_orders_count` | `5` | `ORD-051` a `ORD-055` (`status == "canceled"`) |
| Faturamento Bruto | `gross_revenue` | `5000.0` | Soma de `quantity * unit_price` das 74 linhas `completed` |
| Total de Descontos | `discount_total` | `250.0` | Soma de `discount` das 74 linhas `completed` |
| Faturamento Líquido | `net_revenue` | `4750.0` | `5000.0 - 250.0` |
| Ticket Médio Bruto | `average_ticket_gross` | `100.0` | `5000.0 / 50` pedidos concluídos |
| Ticket Médio Líquido | `average_ticket_net` | `95.0` | `4750.0 / 50` pedidos concluídos |
| Perda por Cancelamento | `canceled_revenue_loss` | `514.0` | Soma de `quantity * unit_price` das 8 linhas `canceled` |
| Produto Top 1 Curva ABC | `top_abc_item` | `"Combo Burger Duplo Artesanal"` | Maior `revenue` bruto (`2000.0`, `40.0%`) |

### 5.2. Curva ABC de Produtos (`abc_curve` — `RN-05`)

Considera apenas linhas com `status == "completed"`:

| Posição | `item_name` | `category` | `quantity_sold` | `revenue` | `revenue_share_pct` | `cumulative_share_pct` | `abc_class` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `Combo Burger Duplo Artesanal` | `Combos` | `25` | `2000.0` | `40.0` | `40.0` | `A` |
| 2 | `Burger Trilogia Defumado` | `Burgers` | `24` | `1200.0` | `24.0` | `64.0` | `A` |
| 3 | `Smash Bacon Duplo` | `Burgers` | `19` | `760.0` | `15.2` | `79.2` | `A` |
| 4 | `Porcao Batata Rustica Trufada` | `Porcoes` | `14` | `490.0` | `9.8` | `89.0` | `B` |
| 5 | `Milkshake Pistache Artesanal` | `Sobremesas` | `11` | `275.0` | `5.5` | `94.5` | `B` |
| 6 | `Onion Rings Crocante` | `Porcoes` | `6` | `150.0` | `3.0` | `97.5` | `C` |
| 7 | `Brownie Belga com Sorvete` | `Sobremesas` | `4` | `80.0` | `1.6` | `99.1` | `C` |
| 8 | `Refrigerante Lata 350ml` | `Bebidas` | `5` | `45.0` | `0.9` | `100.0` | `C` |

### 5.3. Gargalos Operacionais e Anomalias (`bottlenecks` — `RN-06`)

- **Parâmetros e Médias Globais de Preparo (`status == "completed"`):**
  - `prep_time_threshold_minutes`: `30`
  - `delayed_orders_count`: `5` (`ORD-002`, `ORD-005`, `ORD-009`, `ORD-014`, `ORD-022` — nota: `ORD-005` possui 2 itens atrasados e `ORD-019` tem `prep_time_minutes == 30.0`, que não configura atraso pois a regra exige `> 30`)
  - `delayed_items_count`: `6`
  - `average_prep_time_minutes`: `18.55`
  - `max_prep_time_minutes`: `46.0`

- **Atrasos por Categoria (`delayed_by_category`):**

| `category` | `delayed_items_count` | `avg_prep_time_minutes` | Tempos Individuais (`> 30 min`) |
| --- | --- | --- | --- |
| `Burgers` | `4` | `39.0` | `35.0`, `38.0`, `41.0`, `42.0` |
| `Combos` | `2` | `40.0` | `34.0`, `46.0` |

- **Cancelamentos por Canal (`canceled_by_channel`):**

| `channel` | `canceled_orders_count` | `total_orders_count` | `cancellation_rate_pct` | `canceled_revenue_loss` |
| --- | --- | --- | --- | --- |
| `delivery` | `4` | `20` | `20.0` | `474.0` |
| `app` | `1` | `20` | `5.0` | `40.0` |
| `balcao` | `0` | `15` | `0.0` | `0.0` |

- **Cancelamentos por Item (`canceled_by_item`):**

| `item_name` | `category` | `canceled_quantity` | `canceled_revenue_loss` |
| --- | --- | --- | --- |
| `Combo Burger Duplo Artesanal` | `Combos` | `3` | `240.0` |
| `Burger Trilogia Defumado` | `Burgers` | `3` | `150.0` |
| `Smash Bacon Duplo` | `Burgers` | `2` | `80.0` |
| `Porcao Batata Rustica Trufada` | `Porcoes` | `1` | `35.0` |
| `Refrigerante Lata 350ml` | `Bebidas` | `1` | `9.0` |

- **Anomalias Detectadas (`anomalies`):**
  1. `type: "high_prep_time"` | `severity: "warning"` | `dimension: "Burgers"` | `metric_value: 39.0` | `threshold_value: 30.0` | `"4 itens na categoria 'Burgers' ultrapassaram o limite de 30 minutos de preparo."`
  2. `type: "high_prep_time"` | `severity: "warning"` | `dimension: "Combos"` | `metric_value: 40.0` | `threshold_value: 30.0` | `"2 itens na categoria 'Combos' ultrapassaram o limite de 30 minutos de preparo."`
  3. `type: "high_cancellation_rate"` | `severity: "critical"` | `dimension: "delivery"` | `metric_value: 20.0` | `threshold_value: 10.0` | `"Taxa de cancelamento no canal 'delivery' atingiu 20.0%, acima do limite tolerado de 10.0%."`

### 5.4. Desempenho por Canal (`by_channel`) e por Categoria (`by_category`)

- **Por Canal (`by_channel` — apenas `completed`):**

| `channel` | `valid_orders_count` | `quantity_sold` | `gross_revenue` | `discount_total` | `net_revenue` | `revenue_share_pct` | `average_ticket_net` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `delivery` | `16` | `43` | `2128.0` | `90.0` | `2038.0` | `42.91` | `127.38` |
| `app` | `19` | `41` | `1823.0` | `90.0` | `1733.0` | `36.48` | `91.21` |
| `balcao` | `15` | `24` | `1049.0` | `70.0` | `979.0` | `20.61` | `65.27` |

- **Por Categoria (`by_category` — apenas `completed`):**

| `category` | `quantity_sold` | `gross_revenue` | `discount_total` | `net_revenue` | `revenue_share_pct` | `average_prep_time_minutes` |
| --- | --- | --- | --- | --- | --- | --- |
| `Combos` | `25` | `2000.0` | `120.0` | `1880.0` | `39.58` | `26.88` |
| `Burgers` | `43` | `1960.0` | `85.0` | `1875.0` | `39.47` | `22.5` |
| `Porcoes` | `20` | `640.0` | `30.0` | `610.0` | `12.84` | `12.5` |
| `Sobremesas` | `15` | `355.0` | `15.0` | `340.0` | `7.16` | `6.89` |
| `Bebidas` | `5` | `45.0` | `0.0` | `45.0` | `0.95` | `2.0` |

---

## 6. PII, Tratamento, Licença e Limitações

- **PII (Dados Pessoais):** Inexistente. O dataset contém exclusivamente identificadores sintéticos de pedido (`ORD-001` a `ORD-055`), nomes de produtos do cardápio, valores financeiros e tempos operacionais. Nenhum nome de cliente, CPF, telefone ou endereço é coletado ou aceito no schema.
- **Uso Permitido:** Uso irrestrito para testes automatizados, demonstração de portfólio e validação de modelos determinísticos e prompts locais no projeto FoodPilot AI.
- **Limitações Conhecidas:**
  1. Os dados cobrem uma janela de 7 dias (`2026-11-01` a `2026-11-07`) e não modelam sazonalidade mensal/anual nem custos de insumos (CMV/margem de contribuição por ingrediente).
  2. O campo `prep_time_minutes` é informado na linha do item no CSV; em itens de um mesmo pedido que saem juntos da cozinha, cada linha registra o tempo daquele item específico.

---

## 7. Histórico

| Data | Entrega | Alteração | Autor |
| --- | --- | --- | --- |
| 2026-11-09 | 0001 | Criação do Data Card oficial e congelamento do snapshot `data/sample_orders.csv` (82 linhas, 55 pedidos). | Shikamaru |
