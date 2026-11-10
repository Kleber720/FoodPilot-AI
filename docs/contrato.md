# Contrato da API e de Integração Interna — FoodPilot AI

**Versão:** 1.2.0 (Entrega 0004)  
**Atualizado em:** 2026-11-10  
**Dono:** Lee (Back-end)  
**Estado:** Congelado para as Entregas 0001, 0002, 0003 e 0004  

Este documento é a fonte da verdade para os contratos HTTP REST expostos pelo `backend/` (consumidos pelo `frontend/` e auditados por `tests/`) e para o contrato de interface interna Python entre `backend/` (Lee) e `data_pipeline/` (Shikamaru).

---

## 1. Convenções Gerais da API HTTP

- **URL Base Local:** `http://localhost:8000`
- **Prefixo de Versão:** `/api/v1`
- **Formato de Resposta:** `application/json; charset=utf-8`
- **Autenticação e Acesso:** Aplicação 100% local (*single-tenant* em ambiente desktop/servidor local). Não há exigência de cabeçalho de autenticação (`Authorization`) na Entrega 0001.
- **Formato de Datas/Timestamps:** ISO-8601 em UTC (ex.: `"2026-11-09T18:30:00Z"`).
- **Arredondamento Numérico:** Todos os valores monetários (`gross_revenue`, `discount_total`, `net_revenue`, `canceled_revenue_loss`, `average_ticket_gross`, `average_ticket_net`, `revenue`) e percentuais/médias (`revenue_share_pct`, `cumulative_share_pct`, `cancellation_rate_pct`, `average_prep_time_minutes`) são números de ponto flutuante (`float`) arredondados em **2 casas decimais** (`round(val, 2)`).
- **Invariante Anti-Alucinação:** Nenhum campo numérico retornado nos endpoints abaixo é produzido ou modificado por LLM. Todos os números vêm exclusivamente do motor determinístico em `pandas` (`data_pipeline/`).

### Formato Padrão de Erro

Qualquer resposta de erro (`400`, `404`, `422`, `500`) devolve um objeto JSON com a chave `detail` (`str`) e, no caso de erros de validação de dados/CSV (`400` ou `422`), a lista `errors`:

```json
{
  "detail": "Falha na validação do arquivo CSV enviado.",
  "errors": [
    {
      "row": 4,
      "column": "unit_price",
      "message": "Valor numérico deve ser estritamente maior que zero (recebido: -15.0)."
    }
  ]
}
```

- `row` (`int | null`): Número da linha no arquivo CSV (1-indexed considerando o cabeçalho como linha 1, logo a primeira linha de dados é `2`), ou `null` quando o erro for estrutural do arquivo (ex.: arquivo vazio ou coluna obrigatória ausente no cabeçalho).
- `column` (`str | null`): Nome da coluna afetada, ou `null` quando o erro se aplicar ao arquivo como um todo.
- `message` (`str`): Mensagem descritiva em português detalhando a violação da regra.

---

## 2. Endpoints REST (Entrega 0001)

### 2.1. Verificação de Saúde do Serviço (`GET /api/v1/health`)

- **Objetivo:** Verificar disponibilidade do servidor FastAPI local.
- **Consumidores:** Front-end (Sakura), scripts de diagnóstico e suíte de testes (Kakashi).
- **Método e Rota:** `GET /api/v1/health`
- **Entradas:** Nenhuma.
- **Resposta de Sucesso (`200 OK`):**

```json
{
  "status": "ok"
}
```

---

### 2.2. Upload e Processamento de Lote CSV (`POST /api/v1/uploads`)

- **Objetivo:** Receber um arquivo CSV de pedidos de restaurante, validar integralmente seu schema e regras de negócio via `data_pipeline`, persistir de forma atômica o lote e seus itens de pedido no SQLite e devolver o resumo imediato do processamento.
- **Consumidores:** Front-end (Sakura) e suíte de testes de integração (Kakashi).
- **Método e Rota:** `POST /api/v1/uploads`
- **Content-Type de Entrada:** `multipart/form-data`
- **Campos de Entrada:**

| Campo | Tipo | Obrigatório | Descrição e Limites |
| --- | --- | --- | --- |
| `file` | Arquivo (`UploadFile`) | Sim | Arquivo texto CSV codificado em `UTF-8` (com ou sem BOM) separado por vírgula (`,`), contendo o cabeçalho com as 10 colunas obrigatórias de pedidos e ao menos 1 linha de dados. |

- **Comportamento Transacional e Idempotência:**
  - Cada chamada bem-sucedida gera um novo registro de lote com `upload_id` único (UUID v4) e persiste todas as linhas do CSV associadas a esse `upload_id` na mesma transação SQLite.
  - **Atomicidade (`RN-02`):** Se qualquer linha ou coluna do CSV violar as regras de validação (`RN-01`), **nenhum** registro (nem o lote em `uploads`, nem linhas em `order_items`) é gravado no SQLite.

- **Resposta de Sucesso (`201 Created`):**

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `upload_id` | `str` (UUID v4) | Identificador único do lote processado. |
| `filename` | `str` | Nome original do arquivo enviado. |
| `created_at` | `str` (ISO-8601) | Data/hora UTC de criação do registro. |
| `total_rows` | `int` | Total de linhas de itens de pedido presentes no CSV. |
| `valid_orders_count` | `int` | Quantidade de `order_id` únicos com `status == "completed"`. |
| `canceled_orders_count` | `int` | Quantidade de `order_id` únicos com `status == "canceled"`. |
| `summary_metrics` | `object` | Resumo executivo das métricas financeiras do lote (detalhado abaixo). |
| `summary_metrics.gross_revenue` | `float` | Soma de `quantity * unit_price` dos itens com `status == "completed"`. |
| `summary_metrics.discount_total` | `float` | Soma de `discount` dos itens com `status == "completed"`. |
| `summary_metrics.net_revenue` | `float` | `gross_revenue - discount_total` dos itens com `status == "completed"`. |
| `summary_metrics.average_ticket_gross` | `float` | `gross_revenue / valid_orders_count` (`0.0` se `valid_orders_count == 0`). |
| `summary_metrics.average_ticket_net` | `float` | `net_revenue / valid_orders_count` (`0.0` se `valid_orders_count == 0`). |
| `summary_metrics.canceled_revenue_loss` | `float` | Soma de `quantity * unit_price` dos itens com `status == "canceled"`. |
| `summary_metrics.top_abc_item` | `str \| null` | Nome (`item_name`) do produto nº 1 da Curva ABC no lote, ou `null` se não houver pedidos concluídos. |

**Exemplo de Resposta (`201 Created`):**

```json
{
  "upload_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "filename": "sample_orders.csv",
  "created_at": "2026-11-09T18:30:00Z",
  "total_rows": 25,
  "valid_orders_count": 15,
  "canceled_orders_count": 3,
  "summary_metrics": {
    "gross_revenue": 1850.5,
    "discount_total": 95.0,
    "net_revenue": 1755.5,
    "average_ticket_gross": 123.37,
    "average_ticket_net": 117.03,
    "canceled_revenue_loss": 210.0,
    "top_abc_item": "Hambúrguer Artesanal Duplo"
  }
}
```

- **Respostas de Erro:**
  - **`400 Bad Request`:** Quando a requisição não envia o campo `file` ou envia `file` com nome de arquivo vazio.
    ```json
    {
      "detail": "Nenhum arquivo CSV foi enviado no campo 'file'.",
      "errors": []
    }
    ```
  - **`422 Unprocessable Entity`:** Quando o arquivo CSV está vazio (0 bytes ou apenas cabeçalho sem linhas de dados), falha na decodificação UTF-8 / formatação CSV, não possui uma ou mais colunas obrigatórias ou contém valores inválidos em qualquer linha (`RN-01`).
    ```json
    {
      "detail": "Arquivo CSV inválido: foram encontrados erros de validação.",
      "errors": [
        {
          "row": null,
          "column": "prep_time_minutes",
          "message": "Coluna obrigatória 'prep_time_minutes' ausente no cabeçalho do CSV."
        }
      ]
    }
    ```

---

### 2.3. Listagem de Uploads Realizados (`GET /api/v1/uploads`)

- **Objetivo:** Listar os lotes de CSV já importados e persistidos no banco SQLite local.
- **Consumidores:** Front-end (Sakura) para seleção de histórico de lotes e suíte de testes (Kakashi).
- **Método e Rota:** `GET /api/v1/uploads`
- **Entradas:** Nenhuma.
- **Ordenação Padrão:** Ordenado por `created_at` decrescente (do upload mais recente para o mais antigo).
- **Resposta de Sucesso (`200 OK`):**
  Retorna um objeto contendo `items` (lista de lotes com a mesma estrutura do retorno de `POST /api/v1/uploads`) e `total` (`int` com o número total de lotes). Quando não houver uploads cadastrados, retorna `{"items": [], "total": 0}`.

**Exemplo de Resposta (`200 OK`):**

```json
{
  "items": [
    {
      "upload_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "filename": "sample_orders.csv",
      "created_at": "2026-11-09T18:30:00Z",
      "total_rows": 25,
      "valid_orders_count": 15,
      "canceled_orders_count": 3,
      "summary_metrics": {
        "gross_revenue": 1850.5,
        "discount_total": 95.0,
        "net_revenue": 1755.5,
        "average_ticket_gross": 123.37,
        "average_ticket_net": 117.03,
        "canceled_revenue_loss": 210.0,
        "top_abc_item": "Hambúrguer Artesanal Duplo"
      }
    }
  ],
  "total": 1
}
```

---

### 2.4. Consulta de Métricas Determinísticas do Lote (`GET /api/v1/uploads/{upload_id}/metrics`)

- **Objetivo:** Retornar o relatório analítico completo, determinístico e auditável de um lote específico, incluindo indicadores financeiros, Curva ABC de produtos, gargalos operacionais e quebras por canal e por categoria.
- **Consumidores:** Front-end (Sakura) para renderização do Dashboard, camada de IA local Ollama (na Entrega 0003) e suíte de testes (Kakashi).
- **Método e Rota:** `GET /api/v1/uploads/{upload_id}/metrics`
- **Parâmetros de Rota:**
  - `upload_id` (`str`, obrigatório): Identificador único do upload.
- **Resposta de Sucesso (`200 OK`):**

#### Estrutura de Campos do Payload de Métricas

| Caminho do Campo | Tipo | Descrição |
| --- | --- | --- |
| `upload_id` | `str` | Identificador do lote. |
| `filename` | `str` | Nome do arquivo CSV original. |
| `created_at` | `str` | Timestamp ISO-8601 UTC do upload. |
| `total_rows` | `int` | Total de linhas processadas no lote. |
| `financials` | `object` | Indicadores financeiros consolidados (`RN-03`, `RN-04`). |
| `financials.gross_revenue` | `float` | Faturamento bruto (`sum(quantity * unit_price)` apenas para `status == "completed"`). |
| `financials.discount_total` | `float` | Total de descontos concedidos (`sum(discount)` apenas para `status == "completed"`). |
| `financials.net_revenue` | `float` | Faturamento líquido (`gross_revenue - discount_total` apenas para `status == "completed"`). |
| `financials.valid_orders_count` | `int` | Contagem de `order_id` distintos com `status == "completed"`. |
| `financials.canceled_orders_count` | `int` | Contagem de `order_id` distintos com `status == "canceled"`. |
| `financials.canceled_revenue_loss` | `float` | Receita bruta perdida em cancelamentos (`sum(quantity * unit_price)` para `status == "canceled"`). |
| `financials.average_ticket_gross` | `float` | Ticket médio bruto por pedido concluído (`gross_revenue / valid_orders_count`). |
| `financials.average_ticket_net` | `float` | Ticket médio líquido por pedido concluído (`net_revenue / valid_orders_count`). |
| `abc_curve` | `list[object]` | Lista de produtos de pedidos `completed` ordenada por `revenue` decrescente e `item_name` crescente (`RN-05`). |
| `abc_curve[].item_name` | `str` | Nome do item do cardápio. |
| `abc_curve[].category` | `str` | Categoria principal associada ao item. |
| `abc_curve[].quantity_sold` | `int` | Soma de `quantity` vendida (`status == "completed"`). |
| `abc_curve[].revenue` | `float` | Faturamento bruto gerado pelo item (`sum(quantity * unit_price)` em pedidos `completed`). |
| `abc_curve[].revenue_share_pct` | `float` | Participação percentual do item no `gross_revenue` total (`0.0` a `100.0`). |
| `abc_curve[].cumulative_share_pct` | `float` | Participação percentual acumulada (`0.0` a `100.0`). |
| `abc_curve[].abc_class` | `str` | Classe ABC do item: `"A"`, `"B"` ou `"C"` conforme regra `RN-05`. |
| `bottlenecks` | `object` | Diagnóstico determinístico de gargalos operacionais e cancelamentos (`RN-06`). |
| `bottlenecks.prep_time_threshold_minutes` | `int` | Limiar configurado para atraso de preparo (fixo em `30` minutos). |
| `bottlenecks.delayed_orders_count` | `int` | Quantidade de `order_id` únicos com `status == "completed"` e `prep_time_minutes > 30`. |
| `bottlenecks.delayed_items_count` | `int` | Quantidade de linhas de itens com `status == "completed"` e `prep_time_minutes > 30`. |
| `bottlenecks.average_prep_time_minutes` | `float` | Tempo médio de preparo (em minutos) considerando as linhas com `status == "completed"`. |
| `bottlenecks.max_prep_time_minutes` | `float` | Maior tempo de preparo registrado entre as linhas com `status == "completed"`. |
| `bottlenecks.delayed_by_category` | `list[object]` | Categorias com itens atrasados (`prep_time_minutes > 30` e `status == "completed"`), ordenadas por `delayed_items_count` decrescente e `category` crescente. Campos: `category` (`str`), `delayed_items_count` (`int`), `avg_prep_time_minutes` (`float`). |
| `bottlenecks.canceled_by_channel` | `list[object]` | Taxa de cancelamento por canal (baseada em `order_id` únicos por canal), ordenada por `cancellation_rate_pct` decrescente e `channel` crescente. Campos: `channel` (`str`), `canceled_orders_count` (`int`), `total_orders_count` (`int`), `cancellation_rate_pct` (`float`), `canceled_revenue_loss` (`float`). |
| `bottlenecks.canceled_by_item` | `list[object]` | Itens com ocorrências de `status == "canceled"`, ordenados por `canceled_revenue_loss` decrescente e `item_name` crescente. Campos: `item_name` (`str`), `category` (`str`), `canceled_quantity` (`int`), `canceled_revenue_loss` (`float`). |
| `bottlenecks.anomalies` | `list[object]` | Alertas determinísticos acionados quando limiares operacionais são ultrapassados (`RN-06`). Campos: `type` (`str`), `severity` (`"warning"` \| `"critical"`), `dimension` (`str`), `description` (`str`), `metric_value` (`float`), `threshold_value` (`float`). |
| `by_channel` | `list[object]` | Desempenho de vendas concluídas (`status == "completed"`) por canal, ordenado por `net_revenue` decrescente e `channel` crescente. Campos: `channel` (`str`), `valid_orders_count` (`int`), `quantity_sold` (`int`), `gross_revenue` (`float`), `discount_total` (`float`), `net_revenue` (`float`), `revenue_share_pct` (`float`), `average_ticket_net` (`float`). |
| `by_category` | `list[object]` | Desempenho de vendas concluídas (`status == "completed"`) por categoria, ordenado por `net_revenue` decrescente e `category` crescente. Campos: `category` (`str`), `quantity_sold` (`int`), `gross_revenue` (`float`), `discount_total` (`float`), `net_revenue` (`float`), `revenue_share_pct` (`float`), `average_prep_time_minutes` (`float`). |

**Exemplo Completo de Resposta (`200 OK`):**

```json
{
  "upload_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "filename": "sample_orders.csv",
  "created_at": "2026-11-09T18:30:00Z",
  "total_rows": 25,
  "financials": {
    "gross_revenue": 1850.5,
    "discount_total": 95.0,
    "net_revenue": 1755.5,
    "valid_orders_count": 15,
    "canceled_orders_count": 3,
    "canceled_revenue_loss": 210.0,
    "average_ticket_gross": 123.37,
    "average_ticket_net": 117.03
  },
  "abc_curve": [
    {
      "item_name": "Hambúrguer Artesanal Duplo",
      "category": "Burgers",
      "quantity_sold": 22,
      "revenue": 1100.0,
      "revenue_share_pct": 59.44,
      "cumulative_share_pct": 59.44,
      "abc_class": "A"
    },
    {
      "item_name": "Combo Família",
      "category": "Combos",
      "quantity_sold": 4,
      "revenue": 380.0,
      "revenue_share_pct": 20.54,
      "cumulative_share_pct": 79.98,
      "abc_class": "A"
    },
    {
      "item_name": "Batata Rústica Grande",
      "category": "Acompanhamentos",
      "quantity_sold": 14,
      "revenue": 252.0,
      "revenue_share_pct": 13.62,
      "cumulative_share_pct": 93.6,
      "abc_class": "B"
    },
    {
      "item_name": "Refrigerante Lata",
      "category": "Bebidas",
      "quantity_sold": 15,
      "revenue": 118.5,
      "revenue_share_pct": 6.4,
      "cumulative_share_pct": 100.0,
      "abc_class": "C"
    }
  ],
  "bottlenecks": {
    "prep_time_threshold_minutes": 30,
    "delayed_orders_count": 3,
    "delayed_items_count": 4,
    "average_prep_time_minutes": 21.4,
    "max_prep_time_minutes": 45.0,
    "delayed_by_category": [
      {
        "category": "Burgers",
        "delayed_items_count": 3,
        "avg_prep_time_minutes": 38.33
      },
      {
        "category": "Combos",
        "delayed_items_count": 1,
        "avg_prep_time_minutes": 42.0
      }
    ],
    "canceled_by_channel": [
      {
        "channel": "delivery",
        "canceled_orders_count": 2,
        "total_orders_count": 8,
        "cancellation_rate_pct": 25.0,
        "canceled_revenue_loss": 150.0
      },
      {
        "channel": "app",
        "canceled_orders_count": 1,
        "total_orders_count": 6,
        "cancellation_rate_pct": 16.67,
        "canceled_revenue_loss": 60.0
      },
      {
        "channel": "balcao",
        "canceled_orders_count": 0,
        "total_orders_count": 4,
        "cancellation_rate_pct": 0.0,
        "canceled_revenue_loss": 0.0
      }
    ],
    "canceled_by_item": [
      {
        "item_name": "Hambúrguer Artesanal Duplo",
        "category": "Burgers",
        "canceled_quantity": 3,
        "canceled_revenue_loss": 150.0
      },
      {
        "item_name": "Batata Rústica Grande",
        "category": "Acompanhamentos",
        "canceled_quantity": 3,
        "canceled_revenue_loss": 60.0
      }
    ],
    "anomalies": [
      {
        "type": "high_prep_time",
        "severity": "warning",
        "dimension": "Burgers",
        "description": "3 itens na categoria 'Burgers' ultrapassaram o limite de 30 minutos de preparo.",
        "metric_value": 38.33,
        "threshold_value": 30.0
      },
      {
        "type": "high_cancellation_rate",
        "severity": "critical",
        "dimension": "delivery",
        "description": "Taxa de cancelamento no canal 'delivery' atingiu 25.0%, acima do limite tolerado de 10.0%.",
        "metric_value": 25.0,
        "threshold_value": 10.0
      }
    ]
  },
  "by_channel": [
    {
      "channel": "delivery",
      "valid_orders_count": 6,
      "quantity_sold": 24,
      "gross_revenue": 850.0,
      "discount_total": 50.0,
      "net_revenue": 800.0,
      "revenue_share_pct": 45.57,
      "average_ticket_net": 133.33
    },
    {
      "channel": "app",
      "valid_orders_count": 5,
      "quantity_sold": 19,
      "gross_revenue": 620.5,
      "discount_total": 35.0,
      "net_revenue": 585.5,
      "revenue_share_pct": 33.35,
      "average_ticket_net": 117.1
    },
    {
      "channel": "balcao",
      "valid_orders_count": 4,
      "quantity_sold": 12,
      "gross_revenue": 380.0,
      "discount_total": 10.0,
      "net_revenue": 370.0,
      "revenue_share_pct": 21.08,
      "average_ticket_net": 92.5
    }
  ],
  "by_category": [
    {
      "category": "Burgers",
      "quantity_sold": 22,
      "gross_revenue": 1100.0,
      "discount_total": 60.0,
      "net_revenue": 1040.0,
      "revenue_share_pct": 59.24,
      "average_prep_time_minutes": 26.5
    },
    {
      "category": "Combos",
      "quantity_sold": 4,
      "gross_revenue": 380.0,
      "discount_total": 25.0,
      "net_revenue": 355.0,
      "revenue_share_pct": 20.22,
      "average_prep_time_minutes": 31.0
    },
    {
      "category": "Acompanhamentos",
      "quantity_sold": 14,
      "gross_revenue": 252.0,
      "discount_total": 10.0,
      "net_revenue": 242.0,
      "revenue_share_pct": 13.79,
      "average_prep_time_minutes": 14.2
    },
    {
      "category": "Bebidas",
      "quantity_sold": 15,
      "gross_revenue": 118.5,
      "discount_total": 0.0,
      "net_revenue": 118.5,
      "revenue_share_pct": 6.75,
      "average_prep_time_minutes": 3.0
    }
  ]
}
```

- **Respostas de Erro:**
  - **`404 Not Found`:** Quando `upload_id` não existe no banco SQLite.
    ```json
    {
      "detail": "Upload 'id-inexistente' não encontrado."
    }
    ```

---

### 2.5. Status do Agente de IA Local (`GET /api/v1/ai/status`)

- **Objetivo:** Informar ao Dashboard se o servidor local Ollama está acessível (`ollama_reachable`) e se o modelo configurado (`qwen3:4b-instruct` ou o definido em `OLLAMA_MODEL`) está disponível localmente (`model_available`), consultando `GET /api/tags` do Ollama com timeout curto.
- **Consumidores:** Front-end (Sakura — componente `AiStatusBadge` / `RecommendationsPanel`) e suíte de testes (Kakashi).
- **Método e Rota:** `GET /api/v1/ai/status`
- **Entradas:** Nenhuma.
- **Comportamento de Resiliência:** Mesmo quando o servidor Ollama está desligado ou inacessível, este endpoint **sempre retorna `200 OK`** com `"ollama_reachable": false` e `"model_available": false` (nunca retorna `5xx`).
- **Resposta de Sucesso (`200 OK`):**

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `ollama_reachable` | `bool` | `true` se o servidor Ollama respondeu em `base_url`; `false` em caso de falha de conexão ou timeout. |
| `base_url` | `str` | URL base configurada para o servidor Ollama (padrão `"http://localhost:11434"`). |
| `model` | `str` | Nome/tag do modelo configurado (padrão `"qwen3:4b-instruct"`). |
| `model_available` | `bool` | `true` se `ollama_reachable` for `true` e o modelo constar em `/api/tags` do Ollama; `false` caso contrário. |

**Exemplo de Resposta (`200 OK` — Ollama Online):**

```json
{
  "ollama_reachable": true,
  "base_url": "http://localhost:11434",
  "model": "qwen3:4b-instruct",
  "model_available": true
}
```

**Exemplo de Resposta (`200 OK` — Ollama Offline):**

```json
{
  "ollama_reachable": false,
  "base_url": "http://localhost:11434",
  "model": "qwen3:4b-instruct",
  "model_available": false
}
```

---

### 2.6. Geração e Persistência de Recomendações Fundamentadas (`POST /api/v1/uploads/{upload_id}/recommendations`)

- **Objetivo:** Gerar, validar contra alucinações numéricas (`RN-07`, `RN-08`), degradar graciosamente para o motor determinístico se necessário (`RN-09`), persistir no SQLite (`recommendation_runs`) e retornar exatamente **3 recomendações práticas ranqueadas** (`RN-10`) fundamentadas nos fatos do lote `upload_id`.
- **Consumidores:** Front-end (Sakura — botão de geração em `RecommendationsPanel`) e suíte de testes (Kakashi).
- **Método e Rota:** `POST /api/v1/uploads/{upload_id}/recommendations`
- **Parâmetros de Rota:**
  - `upload_id` (`str`, obrigatório): Identificador único do upload no SQLite.
- **Corpo da Requisição:** Nenhum.
- **Comportamento Síncrono, Validação de Aterramento e Degradação Graciosa:**
  1. Carrega os itens do lote `upload_id` do SQLite (ou retorna `404 Not Found` se `upload_id` não existir).
  2. Calcula as métricas determinísticas (`calculate_metrics`) e constrói a ficha de fatos (`build_fact_sheet`).
  3. Solicita ao LLM local (`OllamaClient`) um JSON estruturado contendo 3 recomendações que referenciem exclusivamente `fact_id` válidos da ficha de fatos.
  4. Audita a saída via `validate_recommendations(payload, facts)` (`RN-08`):
     - Se inválida na 1ª tentativa, realiza **1 nova tentativa (retry)** enviando a lista de erros de aterramento ao modelo.
     - Se válida (na 1ª ou 2ª tentativa), sobrescreve `evidence[].value`, `evidence[].label` e `evidence[].unit` com os valores oficiais da ficha de fatos e grava com `source = "llm"`.
  5. Caso o Ollama esteja offline/timeout (`LLMUnavailableError`) ou a 2ª tentativa também falhe na validação de aterramento (`RN-09`), aciona `build_fallback_recommendations(metrics, facts)`, define `source = "deterministic_fallback"`, `model = null`, preenche `warnings[]` com a razão técnica e responde `201 Created` (nunca `5xx`).
  6. Persiste o registro na tabela `recommendation_runs` em transação atômica no SQLite.

- **Resposta de Sucesso (`201 Created`):**

| Caminho do Campo | Tipo | Descrição |
| --- | --- | --- |
| `run_id` | `str` (UUID v4) | Identificador único desta execução de recomendações. |
| `upload_id` | `str` (UUID v4) | Identificador do lote analisado. |
| `generated_at` | `str` (ISO-8601) | Data/hora UTC da geração. |
| `source` | `"llm"` \| `"deterministic_fallback"` | Origem das recomendações entregues (`"llm"` quando aprovadas no validador de aterramento; `"deterministic_fallback"` quando geradas pelo motor de contingência). |
| `model` | `str \| null` | Nome do modelo LLM utilizado (ex.: `"qwen3:4b-instruct"`) quando `source == "llm"`, ou `null` quando `source == "deterministic_fallback"`. |
| `prompt_version` | `str` | Versão do prompt e contrato de aterramento utilizado (fixo em `"rec-v1"`). |
| `warnings` | `list[str]` | Lista de avisos operacionais. Vazia (`[]`) quando `source == "llm"` na 1ª tentativa; contém a justificativa quando houve retry ou fallback determinístico. |
| `recommendations` | `list[object]` | Lista contendo **exatamente 3 recomendações**, ordenadas por `rank` crescente (`1`, `2`, `3`). |
| `recommendations[].rank` | `int` | Prioridade da recomendação: `1`, `2` ou `3` (sem repetição). |
| `recommendations[].title` | `str` | Título curto e executivo da recomendação. |
| `recommendations[].theme` | `"cancelamento"` \| `"operacao"` \| `"mix"` \| `"receita"` | Tema principal da recomendação. |
| `recommendations[].diagnosis` | `str` | Diagnóstico explicativo fundamentado apenas nos números da ficha de fatos. |
| `recommendations[].action` | `str` | Ação prática recomendada para o operador do restaurante. |
| `recommendations[].expected_impact` | `str` | Impacto operacional ou financeiro esperado, referenciando métricas existentes na ficha de fatos. |
| `recommendations[].evidence` | `list[object]` | Lista não vazia (mínimo 1 item) de fatos que comprovam a recomendação. |
| `recommendations[].evidence[].fact_id` | `str` | Identificador estável do fato na ficha de fatos (ex.: `"chan.delivery.cancellation_rate_pct"`). |
| `recommendations[].evidence[].label` | `str` | Rótulo legível em português do fato (preenchido a partir da ficha de fatos). |
| `recommendations[].evidence[].value` | `float \| int` | Valor numérico oficial do fato (sempre sobrescrito a partir da ficha de fatos). |
| `recommendations[].evidence[].unit` | `"BRL"` \| `"%"` \| `"min"` \| `"count"` | Unidade de medida oficial do fato. |

**Exemplo de Resposta (`201 Created` para `data/sample_orders.csv`):**

```json
{
  "run_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "upload_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "generated_at": "2026-11-09T21:30:00Z",
  "source": "llm",
  "model": "qwen3:4b-instruct",
  "prompt_version": "rec-v1",
  "warnings": [],
  "recommendations": [
    {
      "rank": 1,
      "title": "Conter cancelamentos críticos no canal delivery",
      "theme": "cancelamento",
      "diagnosis": "O canal delivery apresenta taxa de cancelamento de 20.0% (acima do limite tolerado de 10.0%), gerando perda de R$ 474,00 em 4 pedidos cancelados.",
      "action": "Revisar o SLA de confirmação e expedição dos pedidos de delivery e alinhar disponibilidade de itens líderes antes do pico noturno.",
      "expected_impact": "Reduzir a perda por cancelamentos no delivery, hoje em R$ 474,00 de um total de R$ 514,00 perdidos no lote.",
      "evidence": [
        {
          "fact_id": "chan.delivery.cancellation_rate_pct",
          "label": "Taxa de cancelamento no canal delivery",
          "value": 20.0,
          "unit": "%"
        },
        {
          "fact_id": "chan.delivery.canceled_revenue_loss",
          "label": "Perda por cancelamento no canal delivery",
          "value": 474.0,
          "unit": "BRL"
        },
        {
          "fact_id": "thr.cancellation_rate_pct",
          "label": "Limite tolerado de taxa de cancelamento",
          "value": 10.0,
          "unit": "%"
        }
      ]
    },
    {
      "rank": 2,
      "title": "Eliminar gargalo de tempo de preparo na chapa e montagem",
      "theme": "operacao",
      "diagnosis": "Foram registrados 6 itens atrasados em 5 pedidos concluídos acima do limite de 30.0 minutos, concentrados em Burgers (4 itens com média de 39.0 min) e Combos (2 itens com média de 40.0 min).",
      "action": "Pré-porcionar insumos das categorias Burgers e Combos e balancear a fila da cozinha quando o tempo de preparo superar 30.0 minutos.",
      "expected_impact": "Aproximar as categorias críticas da média global de preparo de 18.55 minutos e reduzir o pico máximo de 46.0 minutos.",
      "evidence": [
        {
          "fact_id": "bot.delay_cat.Burgers.avg_prep_time_minutes",
          "label": "Tempo médio dos itens atrasados em Burgers",
          "value": 39.0,
          "unit": "min"
        },
        {
          "fact_id": "bot.delay_cat.Combos.avg_prep_time_minutes",
          "label": "Tempo médio dos itens atrasados em Combos",
          "value": 40.0,
          "unit": "min"
        },
        {
          "fact_id": "thr.prep_time_minutes",
          "label": "Limite de tempo de preparo",
          "value": 30.0,
          "unit": "min"
        }
      ]
    },
    {
      "rank": 3,
      "title": "Estimular venda cruzada para elevar a participação de Bebidas e itens Classe C",
      "theme": "mix",
      "diagnosis": "A categoria Bebidas representa apenas 0.95% da receita líquida (R$ 45,00), enquanto 3 itens do cardápio encontram-se na Classe C da Curva ABC.",
      "action": "Oferecer sugestão automática de Refrigerante Lata 350ml e sobremesas no checkout dos canais app e delivery junto aos itens Classe A.",
      "expected_impact": "Elevar o ticket médio líquido atual de R$ 95,00 aproveitando a tração dos 50 pedidos concluídos.",
      "evidence": [
        {
          "fact_id": "cat.Bebidas.revenue_share_pct",
          "label": "Participação na receita líquida da categoria Bebidas",
          "value": 0.95,
          "unit": "%"
        },
        {
          "fact_id": "cat.Bebidas.net_revenue",
          "label": "Receita líquida da categoria Bebidas",
          "value": 45.0,
          "unit": "BRL"
        },
        {
          "fact_id": "fin.average_ticket_net",
          "label": "Ticket médio líquido",
          "value": 95.0,
          "unit": "BRL"
        }
      ]
    }
  ]
}
```

- **Respostas de Erro:**
  - **`404 Not Found`:** Quando `upload_id` não existe no banco SQLite.
    ```json
    {
      "detail": "Upload 'id-inexistente' não encontrado."
    }
    ```

---

### 2.7. Consulta da Última Recomendação Gerada (`GET /api/v1/uploads/{upload_id}/recommendations`)

- **Objetivo:** Retornar a última execução de recomendações (`recommendation_runs`) já persistida para o lote `upload_id` (ordenada por `generated_at` decrescente), permitindo que o Dashboard recarregue imediatamente as recomendações ao alternar entre lotes sem acionar novamente o modelo.
- **Consumidores:** Front-end (Sakura) ao selecionar um lote e suíte de testes (Kakashi).
- **Método e Rota:** `GET /api/v1/uploads/{upload_id}/recommendations`
- **Parâmetros de Rota:**
  - `upload_id` (`str`, obrigatório): Identificador único do upload.
- **Resposta de Sucesso (`200 OK`):**
  - Retorna exatamente o mesmo schema JSON documentado em `POST /api/v1/uploads/{upload_id}/recommendations` (§2.6).
- **Respostas de Erro:**
  - **`404 Not Found` (Upload inexistente):**
    ```json
    {
      "detail": "Upload 'id-inexistente' não encontrado."
    }
    ```
  - **`404 Not Found` (Upload existe, mas nenhuma recomendação foi gerada ainda):**
    ```json
    {
      "detail": "Nenhuma recomendação gerada para o upload 'f47ac10b-58cc-4372-a567-0e02b2c3d479'."
    }
    ```

---

### 2.8. Relatório Executivo Consolidado (`GET /api/v1/uploads/{upload_id}/report`)

- **Objetivo:** Fornecer uma visão executiva consolidada e pronta para exportação/impressão contendo o sumário financeiro, anomalias críticas, produtos líderes e as 3 recomendações oficiais do agente de IA com texto formatado em Markdown executivo.
- **Consumidores:** Front-end (Sakura — botão "Exportar Relatório" / "Imprimir"), script de exportação e avaliadores técnicos.
- **Método e Rota:** `GET /api/v1/uploads/{upload_id}/report`
- **Parâmetros de Rota:**
  - `upload_id` (`str`, obrigatório): Identificador único do upload.
- **Resposta de Sucesso (`200 OK`):**

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `upload_id` | `str` | Identificador do lote analisado. |
| `filename` | `str` | Nome do arquivo CSV de origem. |
| `generated_at` | `str` | Timestamp ISO-8601 da emissão do relatório. |
| `financials` | `FinancialsSchema` | Indicadores financeiros consolidados. |
| `top_abc_items` | `list[ABCCurveItemSchema]` | Itens classificados na Classe A (principais geradores de faturamento). |
| `anomalies` | `list[AnomalySchema]` | Anomalias operacionais detectadas no lote. |
| `recommendations` | `list[RecommendationSchema]` | As 3 recomendações práticas auditadas do lote. |
| `recommendations_source` | `str` | `"llm"` ou `"deterministic_fallback"`. |
| `report_markdown` | `str` | Texto executivo formatado em Markdown pronto para compartilhamento ou exportação. |

- **Respostas de Erro:**
  - **`404 Not Found`:** Quando `upload_id` não existe no banco SQLite.
    ```json
    {
      "detail": "Upload 'id-inexistente' não encontrado."
    }
    ```


---

## 3. Contrato de Interface Interna Python (`data_pipeline` ↔ `backend`)

### 3.1. Validação de CSV e Cálculo de Métricas (Entrega 0001)

Para garantir integração direta em memória entre `data_pipeline/` (dono: Shikamaru) e `backend/` (dono: Lee), o pacote `data_pipeline` expõe em `data_pipeline/__init__.py` os seguintes símbolos públicos:

```python
from typing import Any, Mapping, Sequence
import pandas as pd


class CSVValidationError(ValueError):
    """Exceção levantada quando o arquivo CSV falha na validação estrutural ou de domínio."""

    def __init__(self, detail: str, errors: list[dict[str, Any]]) -> None:
        super().__init__(detail)
        self.detail: str = detail
        self.errors: list[dict[str, Any]] = errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "detail": self.detail,
            "errors": self.errors,
        }


def validate_and_parse_csv(content: bytes | str) -> pd.DataFrame:
    """
    Valida o conteúdo bruto de um arquivo CSV de pedidos e retorna um DataFrame tipado.

    Regras:
    - Aceita `bytes` (decodificando em `utf-8-sig` / `utf-8`) ou `str`.
    - Se o conteúdo estiver vazio, sem cabeçalho, com colunas obrigatórias faltantes ou
      com qualquer linha inválida segundo RN-01, levanta `CSVValidationError` contendo
      `detail` (str) e `errors` (lista de dicts `{"row": int | None, "column": str | None, "message": str}`).
    - Não trunca na primeira linha inválida: coleta todos os erros de validação encontrados
      no arquivo para devolver feedback completo ao usuário no status HTTP 422.
    - Retorna um `pd.DataFrame` contendo as 10 colunas obrigatórias já limpas e convertidas:
      `order_id` (str), `timestamp` (str ISO-8601 ou datetime convertível), `item_name` (str),
      `category` (str), `quantity` (int), `unit_price` (float), `discount` (float),
      `prep_time_minutes` (float), `status` (str: 'completed' | 'canceled'),
      `channel` (str: 'balcao' | 'delivery' | 'app').
    """


def calculate_metrics(
    df_or_records: pd.DataFrame | Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """
    Calcula deterministicamente todas as métricas financeiras, curva ABC e gargalos.

    Entrada:
    - `df_or_records`: `pd.DataFrame` retornado por `validate_and_parse_csv` OU uma lista
      de dicionários/registros (`Sequence[Mapping[str, Any]]`) carregados do SQLite.

    Saída:
    - Retorna um `dict[str, Any]` contendo exclusivamente tipos nativos Python (`int`, `float`,
      `str`, `bool`, `None`, `list`, `dict` — sem escalares numpy como `np.float64`/`np.int64`)
      com a seguinte estrutura exata:
      {
          "total_rows": int,
          "valid_orders_count": int,
          "canceled_orders_count": int,
          "summary_metrics": {
              "gross_revenue": float,
              "discount_total": float,
              "net_revenue": float,
              "average_ticket_gross": float,
              "average_ticket_net": float,
              "canceled_revenue_loss": float,
              "top_abc_item": str | None,
          },
          "financials": {
              "gross_revenue": float,
              "discount_total": float,
              "net_revenue": float,
              "valid_orders_count": int,
              "canceled_orders_count": int,
              "canceled_revenue_loss": float,
              "average_ticket_gross": float,
              "average_ticket_net": float,
          },
          "abc_curve": [
              {
                  "item_name": str,
                  "category": str,
                  "quantity_sold": int,
                  "revenue": float,
                  "revenue_share_pct": float,
                  "cumulative_share_pct": float,
                  "abc_class": str,  # "A" | "B" | "C"
              },
              ...
          ],
          "bottlenecks": {
              "prep_time_threshold_minutes": int,  # 30
              "delayed_orders_count": int,
              "delayed_items_count": int,
              "average_prep_time_minutes": float,
              "max_prep_time_minutes": float,
              "delayed_by_category": [
                  {
                      "category": str,
                      "delayed_items_count": int,
                      "avg_prep_time_minutes": float,
                  },
                  ...
              ],
              "canceled_by_channel": [
                  {
                      "channel": str,
                      "canceled_orders_count": int,
                      "total_orders_count": int,
                      "cancellation_rate_pct": float,
                      "canceled_revenue_loss": float,
                  },
                  ...
              ],
              "canceled_by_item": [
                  {
                      "item_name": str,
                      "category": str,
                      "canceled_quantity": int,
                      "canceled_revenue_loss": float,
                  },
                  ...
              ],
              "anomalies": [
                  {
                      "type": str,          # "high_prep_time" | "high_cancellation_rate"
                      "severity": str,      # "warning" | "critical"
                      "dimension": str,     # nome da categoria ou canal afetado
                      "description": str,
                      "metric_value": float,
                      "threshold_value": float,
                  },
                  ...
              ],
          },
          "by_channel": [
              {
                  "channel": str,
                  "valid_orders_count": int,
                  "quantity_sold": int,
                  "gross_revenue": float,
                  "discount_total": float,
                  "net_revenue": float,
                  "revenue_share_pct": float,
                  "average_ticket_net": float,
              },
              ...
          ],
          "by_category": [
              {
                  "category": str,
                  "quantity_sold": int,
                  "gross_revenue": float,
                  "discount_total": float,
                  "net_revenue": float,
                  "revenue_share_pct": float,
                  "average_prep_time_minutes": float,
              },
              ...
          ],
      }
    """
```

---

### 3.2. Ficha de Fatos e Fallback Determinístico de Recomendações (Entrega 0003 — `data_pipeline/insights.py` ↔ `backend/ai/`)

Na Entrega 0003, o pacote `data_pipeline` (dono: Shikamaru) deve implementar `data_pipeline/insights.py` e reexportar em `data_pipeline/__init__.py` as funções `build_fact_sheet` e `build_fallback_recommendations`:

```python
from collections.abc import Mapping, Sequence
from typing import Any


def build_fact_sheet(metrics: Mapping[str, Any]) -> list[dict[str, Any]]:
    """
    Transforma o dicionário retornado por `calculate_metrics` em uma lista ordenada,
    pura e determinística de fatos atômicos rastreáveis por `fact_id` (RN-07).

    Estrutura de cada item retornado:
    {
        "fact_id": str,          # identificador único e estável (ex.: "fin.net_revenue")
        "category": str,         # "threshold" | "financials" | "bottlenecks" | "channel_cancellation" | "by_channel" | "by_category" | "abc_curve"
        "label": str,            # descrição legível em pt-BR
        "value": float | int,    # valor numérico exato (int para contagens, float arredondado em 2 casas para demais)
        "unit": str,             # "BRL" | "%" | "min" | "count"
        "formatted": str,        # representação textual formatada (ex.: "R$ 4750.00", "20.0%", "39.0 min", "50")
    }
    """


def build_fallback_recommendations(
    metrics: Mapping[str, Any],
    facts: Sequence[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Gera deterministicamente exatamente 3 recomendações práticas ranqueadas (ranks 1, 2, 3)
    a partir das métricas e da ficha de fatos, sem uso de LLM (RN-09, RN-10).

    Se `facts` for None, invoca `build_fact_sheet(metrics)` internamente.

    Estrutura de cada uma das 3 recomendações retornadas:
    {
        "rank": int,             # 1, 2 ou 3
        "title": str,
        "theme": str,            # "cancelamento" | "operacao" | "mix" | "receita"
        "diagnosis": str,        # texto contendo exclusivamente números presentes em `facts`
        "action": str,           # texto contendo exclusivamente números presentes em `facts`
        "expected_impact": str,  # texto contendo exclusivamente números presentes em `facts`
        "evidence": [
            {
                "fact_id": str,
                "label": str,
                "value": float | int,
                "unit": str,     # "BRL" | "%" | "min" | "count"
            },
            ...
        ],
    }
    """
```

#### Catálogo Obrigatório de `fact_id` Gerados por `build_fact_sheet(metrics)`

Para garantir interoperabilidade exata entre `data_pipeline/insights.py` (Shikamaru), `backend/ai/grounding.py` (Lee) e `tests/` (Kakashi), `build_fact_sheet` deve emitir os seguintes identificadores padronizados:

1. **Limiares Operacionais (`category = "threshold"`):**
   - `thr.prep_time_minutes` (`value`: `float(bottlenecks["prep_time_threshold_minutes"])` = `30.0`, `unit`: `"min"`, `label`: `"Limite de tempo de preparo"`)
   - `thr.cancellation_rate_pct` (`value`: `10.0`, `unit`: `"%"`, `label`: `"Limite tolerado de taxa de cancelamento"`)
2. **Indicadores Financeiros e Contagens Globais (`category = "financials"`):**
   - `fin.total_rows` (`value`: `int(metrics["total_rows"])`, `unit`: `"count"`, `label`: `"Total de itens registrados no lote"`)
   - `fin.gross_revenue` (`value`: `float`, `unit`: `"BRL"`, `label`: `"Faturamento bruto"`)
   - `fin.discount_total` (`value`: `float`, `unit`: `"BRL"`, `label`: `"Total de descontos"`)
   - `fin.net_revenue` (`value`: `float`, `unit`: `"BRL"`, `label`: `"Faturamento líquido"`)
   - `fin.valid_orders_count` (`value`: `int`, `unit`: `"count"`, `label`: `"Pedidos concluídos"`)
   - `fin.canceled_orders_count` (`value`: `int`, `unit`: `"count"`, `label`: `"Pedidos cancelados"`)
   - `fin.canceled_revenue_loss` (`value`: `float`, `unit`: `"BRL"`, `label`: `"Perda total por cancelamentos"`)
   - `fin.average_ticket_gross` (`value`: `float`, `unit`: `"BRL"`, `label`: `"Ticket médio bruto"`)
   - `fin.average_ticket_net` (`value`: `float`, `unit`: `"BRL"`, `label`: `"Ticket médio líquido"`)
3. **Gargalos Globais e por Categoria (`category = "bottlenecks"`):**
   - `bot.delayed_orders_count` (`value`: `int`, `unit`: `"count"`, `label`: `"Pedidos concluídos com atraso de preparo"`)
   - `bot.delayed_items_count` (`value`: `int`, `unit`: `"count"`, `label`: `"Itens concluídos com preparo acima do limite"`)
   - `bot.average_prep_time_minutes` (`value`: `float`, `unit`: `"min"`, `label`: `"Tempo médio global de preparo"`)
   - `bot.max_prep_time_minutes` (`value`: `float`, `unit`: `"min"`, `label`: `"Tempo máximo de preparo registrado"`)
   - Para cada item `d` em `bottlenecks["delayed_by_category"]` (onde `<category>` é `d["category"]`):
     - `bot.delay_cat.<category>.delayed_items_count` (`value`: `int`, `unit`: `"count"`, `label`: `f"Itens atrasados em {category}"`)
     - `bot.delay_cat.<category>.avg_prep_time_minutes` (`value`: `float`, `unit`: `"min"`, `label`: `f"Tempo médio dos itens atrasados em {category}"`)
4. **Cancelamentos por Canal (`category = "channel_cancellation"`):**
   - Para cada item `c` em `bottlenecks["canceled_by_channel"]` (onde `<channel>` é `c["channel"]`):
     - `chan.<channel>.canceled_orders_count` (`value`: `int`, `unit`: `"count"`, `label`: `f"Pedidos cancelados no canal {channel}"`)
     - `chan.<channel>.total_orders_count` (`value`: `int`, `unit`: `"count"`, `label`: `f"Total de pedidos no canal {channel}"`)
     - `chan.<channel>.cancellation_rate_pct` (`value`: `float`, `unit`: `"%"`, `label`: `f"Taxa de cancelamento no canal {channel}"`)
     - `chan.<channel>.canceled_revenue_loss` (`value`: `float`, `unit`: `"BRL"`, `label`: `f"Perda por cancelamento no canal {channel}"`)
5. **Desempenho de Vendas Concluídas por Canal (`category = "by_channel"`):**
   - Para cada item `ch` em `by_channel` (onde `<channel>` é `ch["channel"]`):
     - `chan.<channel>.valid_orders_count` (`value`: `int`, `unit`: `"count"`, `label`: `f"Pedidos concluídos no canal {channel}"`)
     - `chan.<channel>.quantity_sold` (`value`: `int`, `unit`: `"count"`, `label`: `f"Unidades vendidas no canal {channel}"`)
     - `chan.<channel>.gross_revenue` (`value`: `float`, `unit`: `"BRL"`, `label`: `f"Receita bruta no canal {channel}"`)
     - `chan.<channel>.discount_total` (`value`: `float`, `unit`: `"BRL"`, `label`: `f"Descontos no canal {channel}"`)
     - `chan.<channel>.net_revenue` (`value`: `float`, `unit`: `"BRL"`, `label`: `f"Receita líquida no canal {channel}"`)
     - `chan.<channel>.revenue_share_pct` (`value`: `float`, `unit`: `"%"`, `label`: `f"Participação na receita líquida do canal {channel}"`)
     - `chan.<channel>.average_ticket_net` (`value`: `float`, `unit`: `"BRL"`, `label`: `f"Ticket médio líquido no canal {channel}"`)
6. **Desempenho de Vendas Concluídas por Categoria (`category = "by_category"`):**
   - Para cada item `cat` em `by_category` (onde `<category>` é `cat["category"]`):
     - `cat.<category>.quantity_sold` (`value`: `int`, `unit`: `"count"`, `label`: `f"Unidades vendidas na categoria {category}"`)
     - `cat.<category>.gross_revenue` (`value`: `float`, `unit`: `"BRL"`, `label`: `f"Receita bruta da categoria {category}"`)
     - `cat.<category>.discount_total` (`value`: `float`, `unit`: `"BRL"`, `label`: `f"Descontos da categoria {category}"`)
     - `cat.<category>.net_revenue` (`value`: `float`, `unit`: `"BRL"`, `label`: `f"Receita líquida da categoria {category}"`)
     - `cat.<category>.revenue_share_pct` (`value`: `float`, `unit`: `"%"`, `label`: `f"Participação na receita líquida da categoria {category}"`)
     - `cat.<category>.average_prep_time_minutes` (`value`: `float`, `unit`: `"min"`, `label`: `f"Tempo médio de preparo da categoria {category}"`)
7. **Curva ABC (`category = "abc_curve"`):**
   - Contagens por classe:
     - `abc.class_a.items_count` (`value`: `int`, `unit`: `"count"`, `label`: `"Quantidade de produtos na Classe A"`)
     - `abc.class_b.items_count` (`value`: `int`, `unit`: `"count"`, `label`: `"Quantidade de produtos na Classe B"`)
     - `abc.class_c.items_count` (`value`: `int`, `unit`: `"count"`, `label`: `"Quantidade de produtos na Classe C"`)
   - Para cada item na posição 1-indexed `<rank>` (`1..N`) de `abc_curve`:
     - `abc.rank<rank>.revenue` (`value`: `float`, `unit`: `"BRL"`, `label`: `f"Receita bruta ABC #{rank} ({item_name})"`)
     - `abc.rank<rank>.revenue_share_pct` (`value`: `float`, `unit`: `"%"`, `label`: `f"Participação na receita bruta ABC #{rank} ({item_name})"`)
     - `abc.rank<rank>.cumulative_share_pct` (`value`: `float`, `unit`: `"%"`, `label`: `f"Participação acumulada ABC #{rank} ({item_name})"`)
     - `abc.rank<rank>.quantity_sold` (`value`: `int`, `unit`: `"count"`, `label`: `f"Unidades vendidas ABC #{rank} ({item_name})"`)

