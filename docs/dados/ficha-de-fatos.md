# Ficha de Fatos (Fact Sheet) — Catálogo de Métricas e Ancoragem Factual

> **Status:** Ativo • **Versão:** 1.0.0 • **Contrato:** Seção 3.2 de [`docs/contrato.md`](../contrato.md)  
> **Regras Vinculadas:** RN-07 (Ficha de Fatos Determinística), RN-08 (Auditoria Anti-Alucinação), RN-09 (Fallback Determinístico)

---

## 1. Visão Geral e Princípio de Grounding

A **Ficha de Fatos** é a única fonte da verdade permitida para a camada de Inteligência Artificial do **FoodPilot AI**. Ela traduz a saída multidimensional de `calculate_metrics(df)` em uma lista linear, imutável e determinística de fatos atômicos, onde cada número do restaurante recebe um identificador único (`fact_id`), categoria, rótulo legível, valor normalizado e unidade oficial.

### Por que a Ficha de Fatos existe?
1. **Zero Confiança em Cálculos de LLMs:** Modelos de linguagem frequentemente erram contas aritméticas, arredondamentos e somatórios. No FoodPilot AI, todo cálculo é realizado exclusivamente por `pandas` na camada analítica.
2. **Auditoria Rigorosa Anti-Alucinação:** O agente de IA só tem autorização para correlacionar e contextualizar fatos. Qualquer número citado em diagnósticos ou ações é confrontado diretamente com os valores cadastrados na ficha.
3. **Reescrita Sanitizada:** Valores exibidos ao usuário na interface são extraídos deterministicamente da ficha de fatos, impedindo que pequenas variações textuais geradas pelo modelo poluam as métricas do restaurante.

---

## 2. Estrutura Canônica de um Fato

Cada fato gerado por `build_fact_sheet(metrics)` possui a seguinte tipagem:

```typescript
interface Fact {
  fact_id: string;        // Identificador canônico hierárquico (ex: "fin.gross_revenue")
  category: string;       // Agrupamento semântico ("financials", "bottlenecks", etc.)
  label: string;          // Descrição legível em português do indicador
  value: number;          // Valor numérico primitivo (float com 2 casas ou int)
  unit: string;           // "BRL", "%", "min" ou "count"
  formatted: string;      // Formatação padrão para humanos (ex: "R$ 4.789,50")
}
```

---

## 3. Catálogo de Identificadores Canônicos (`fact_id`)

### 3.1 Limiares Operacionais (`threshold`)
| `fact_id` | Rótulo | Unidade | Descrição |
| :--- | :--- | :--- | :--- |
| `thr.prep_time_minutes` | Limite de tempo de preparo | `min` | Limiar tolerado antes de considerar atraso (default: 45 min) |
| `thr.cancellation_rate_pct` | Limite tolerado de taxa de cancelamento | `%` | Limiar tolerado para alertas de cancelamento (default: 5.0%) |

### 3.2 Indicadores Financeiros e Contagens Globais (`financials`)
| `fact_id` | Rótulo | Unidade | Descrição |
| :--- | :--- | :--- | :--- |
| `fin.total_rows` | Total de registros processados | `count` | Linhas totais do lote CSV |
| `fin.valid_orders_count` | Pedidos válidos concluídos | `count` | Pedidos com status 'COMPLETED' |
| `fin.canceled_orders_count` | Pedidos cancelados | `count` | Pedidos com status 'CANCELED' |
| `fin.gross_revenue` | Faturamento bruto realizado | `BRL` | Soma bruta dos pedidos válidos |
| `fin.discount_total` | Total de descontos concedidos | `BRL` | Descontos em pedidos válidos |
| `fin.net_revenue` | Faturamento líquido realizado | `BRL` | Faturamento bruto menos descontos |
| `fin.average_ticket_gross` | Ticket médio bruto | `BRL` | Bruto dividido por pedidos válidos |
| `fin.average_ticket_net` | Ticket médio líquido | `BRL` | Líquido dividido por pedidos válidos |
| `fin.canceled_revenue_loss` | Perda estimada por cancelamentos | `BRL` | Faturamento que deixou de entrar |

### 3.3 Gargalos Operacionais e Cozinha (`bottlenecks`)
| `fact_id` | Rótulo | Unidade | Descrição |
| :--- | :--- | :--- | :--- |
| `bot.delayed_orders_count` | Pedidos com atraso de preparo | `count` | Pedidos válidos com preparo > limiar |
| `bot.delayed_items_count` | Itens com preparo acima do limite | `count` | Itens de pedidos atrasados |
| `bot.average_prep_time_minutes` | Tempo médio geral de preparo | `min` | Média ponderada de preparo dos válidos |
| `bot.max_prep_time_minutes` | Tempo máximo registrado de preparo | `min` | Maior tempo de preparo registrado |

### 3.4 Desempenho por Canal (`channel.<slug>`)
Para cada canal registrado (`delivery`, `salao`, `takeaway`):
- `channel.<slug>.valid_orders`: Contagem de pedidos válidos do canal (`count`)
- `channel.<slug>.gross_revenue`: Faturamento bruto do canal (`BRL`)
- `channel.<slug>.net_revenue`: Faturamento líquido do canal (`BRL`)
- `channel.<slug>.revenue_share_pct`: Participação percentual no faturamento total (`%`)
- `channel.<slug>.average_ticket_net`: Ticket médio líquido do canal (`BRL`)
- `channel.<slug>.canceled_orders`: Total de pedidos cancelados no canal (`count`)
- `channel.<slug>.cancellation_rate_pct`: Taxa de cancelamento do canal (`%`)
- `channel.<slug>.canceled_revenue_loss`: Perda financeira com cancelamentos no canal (`BRL`)

### 3.5 Desempenho por Categoria (`category.<slug>`)
Para cada categoria de produtos:
- `cat.<slug>.quantity_sold`: Unidades vendidas em pedidos válidos (`count`)
- `cat.<slug>.gross_revenue`: Faturamento bruto da categoria (`BRL`)
- `cat.<slug>.net_revenue`: Faturamento líquido da categoria (`BRL`)
- `cat.<slug>.revenue_share_pct`: Participação percentual no faturamento (`%`)
- `cat.<slug>.avg_prep_time_minutes`: Tempo médio de preparo na categoria (`min`)
- `cat.<slug>.delayed_items_count`: Quantidade de itens atrasados na categoria (`count`)

### 3.6 Curva ABC de Produtos (`abc.<slug>`)
Para os produtos classificados no lote:
- `abc.<slug>.class`: Classe ABC atribuída (`A`, `B` ou `C`)
- `abc.<slug>.revenue`: Faturamento gerado pelo item (`BRL`)
- `abc.<slug>.revenue_share_pct`: Participação individual no faturamento (`%`)
- `abc.<slug>.quantity_sold`: Unidades comercializadas (`count`)

---

## 4. Gabarito de Fatos da Amostra Padrão (`data/sample_orders.csv`)

Ao processar o arquivo de referência com 100 linhas:

| `fact_id` | Rótulo Oficial | Valor | Unidade | Formatado |
| :--- | :--- | :--- | :--- | :--- |
| `fin.total_rows` | Total de registros processados | `100` | `count` | `100` |
| `fin.valid_orders_count` | Pedidos válidos concluídos | `84` | `count` | `84` |
| `fin.canceled_orders_count` | Pedidos cancelados | `16` | `count` | `16` |
| `fin.gross_revenue` | Faturamento bruto realizado | `4789.50` | `BRL` | `R$ 4.789,50` |
| `fin.discount_total` | Total de descontos concedidos | `240.00` | `BRL` | `R$ 240,00` |
| `fin.net_revenue` | Faturamento líquido realizado | `4549.50` | `BRL` | `R$ 4.549,50` |
| `fin.average_ticket_gross` | Ticket médio bruto | `57.02` | `BRL` | `R$ 57,02` |
| `fin.average_ticket_net` | Ticket médio líquido | `54.16` | `BRL` | `R$ 54,16` |
| `fin.canceled_revenue_loss` | Perda estimada por cancelamentos | `864.00` | `BRL` | `R$ 864,00` |
| `bot.delayed_orders_count` | Pedidos com atraso de preparo | `18` | `count` | `18` |
| `bot.delayed_items_count` | Itens com preparo acima do limite | `22` | `count` | `22` |
| `bot.average_prep_time_minutes` | Tempo médio geral de preparo | `34.50` | `min` | `34.50 min` |
| `bot.max_prep_time_minutes` | Tempo máximo registrado de preparo | `58.00` | `min` | `58.00 min` |
| `channel.delivery.canceled_orders` | Cancelamentos no canal Delivery | `12` | `count` | `12` |
| `channel.delivery.cancellation_rate_pct` | Taxa de cancelamento no Delivery | `18.75` | `%` | `18.75%` |
| `channel.delivery.canceled_revenue_loss` | Perda por cancelamento no Delivery | `648.00` | `BRL` | `R$ 648,00` |

---

## 5. Auditoria e Sanitização em Execução

Quando o LLM gera o payload de recomendações:
1. `validate_recommendations` percorre cada `evidence.fact_id` e busca no índice gerado por `build_fact_sheet`. Se o ID não existir, a recomendação é rejeitada.
2. Os campos `evidence[].value`, `label` e `unit` são **sobrescritos** pelos valores oficiais da Ficha de Fatos.
3. Se o texto livre contiver números que não estejam na ficha (com tolerância de 0.05), a auditoria acusa erro e dispara o retry corretivo.
4. Caso a segunda tentativa persista em erro, o sistema ativa imediatamente o fallback determinístico (`build_fallback_recommendations`), garantindo 100% de confiabilidade ao usuário.
