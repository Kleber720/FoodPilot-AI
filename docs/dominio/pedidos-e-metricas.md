# Guia de Domínio — Pedidos e Métricas Operacionais/Financeiras

**Contexto Delimitado:** Processamento de Vendas, Desempenho de Cardápio e Diagnóstico Operacional  
**Dono:** Lee (Back-end)  
**Atualizado em:** 2026-11-09  

Este guia documenta a linguagem ubíqua, as invariantes e as regras de negócio determinísticas do **FoodPilot AI** que governam a validação de lotes CSV (`data_pipeline/`), a persistência transacional (`backend/`) e a auditoria de testes (`tests/`).

---

## 1. Termos (Linguagem Ubíqua)

| Termo no Negócio | Identificador no Código/Contrato | Definição Exata | Sinônimos Rejeitados / Ambiguidades Resolvidas |
| --- | --- | --- | --- |
| **Lote de Upload** | `upload` / `upload_id` | Conjunto atômico de registros de vendas importado a partir de um único arquivo CSV enviado pelo operador do restaurante. | Não chamar de `batch_job` ou `import_session` na API pública. |
| **Item de Pedido (Linha do CSV)** | `order_item` / `row` | Cada linha de dados do arquivo CSV. Representa um produto específico (`item_name`), sua quantidade (`quantity`), preço unitário (`unit_price`) e desconto na linha (`discount`) dentro de um pedido (`order_id`). | **Ambiguidade resolvida:** Uma linha do CSV **não** é necessariamente um pedido inteiro; múltiplos itens comprados juntos compartilham o mesmo `order_id` em linhas distintas. |
| **Pedido** | `order` / `order_id` | Transação comercial identificada por um `order_id` único dentro do lote. Pode conter 1 ou mais linhas (`order_item`). | Não confundir contagem de linhas (`total_rows`) com contagem de pedidos (`valid_orders_count` + `canceled_orders_count`). |
| **Pedido Concluído (Válido)** | `status == "completed"` | Pedido finalizado e entregue ao cliente. Apenas itens com `status == "completed"` entram no cálculo de faturamento, ticket médio, curva ABC e tempo de preparo. | Rejeitados: `paid`, `delivered`, `done`, `active`. |
| **Pedido Cancelado** | `status == "canceled"` | Pedido abortado antes ou durante o preparo/entrega. Não compõe faturamento nem curva ABC; compõe exclusivamente métricas de perda (`canceled_revenue_loss`) e taxa de cancelamento. | Rejeitados: `cancelled` (com dois L), `refunded`, `void`. |
| **Canal de Venda** | `channel` | Origem do pedido, restrita estritamente aos valores `"balcao"`, `"delivery"` ou `"app"`. | Rejeitados: `ifood`, `presencial`, `loja`, `takeaway`. |
| **Faturamento Bruto** | `gross_revenue` | Soma exata de `quantity * unit_price` de todas as linhas com `status == "completed"`. | Não subtrai `discount` e não inclui itens `canceled`. |
| **Total de Descontos** | `discount_total` | Soma exata da coluna `discount` de todas as linhas com `status == "completed"`. | `discount` na linha é o valor monetário total de desconto aplicado àquela linha (e não percentual nem desconto unitário multiplicado por `quantity`). |
| **Faturamento Líquido** | `net_revenue` | `gross_revenue - discount_total` considerando apenas linhas com `status == "completed"`. | Nunca pode ser calculado sobre pedidos cancelados. |
| **Perda por Cancelamento** | `canceled_revenue_loss` | Soma exata de `quantity * unit_price` de todas as linhas com `status == "canceled"`. | Não entra em `gross_revenue` nem em `net_revenue`. |
| **Ticket Médio Bruto / Líquido** | `average_ticket_gross` / `average_ticket_net` | Razão entre o faturamento (`gross_revenue` ou `net_revenue`) e a quantidade de **pedidos concluídos únicos** (`valid_orders_count`). | **Ambiguidade resolvida:** O denominador é o número de `order_id` distintos com `status == "completed"`, e **nunca** o número de linhas (`total_rows`) nem a soma de `quantity`. |
| **Curva ABC (Pareto)** | `abc_curve` | Classificação dos produtos vendidos (`status == "completed"`) em ordem decrescente de receita bruta (`revenue`), divididos nas classes `"A"` (até 80% da receita acumulada), `"B"` (acima de 80% até 95%) e `"C"` (acima de 95%). | A ordenação é por `revenue` bruto do item, não por `quantity_sold`. |
| **Gargalo Operacional** | `bottlenecks` | Desvio determinístico de operação medido por atraso de preparo (`prep_time_minutes > 30` em itens `completed`) ou concentração de cancelamentos por canal/item. | Não depende de inferência de LLM. |
| **Ficha de Fatos (Fact Sheet)** | `fact_sheet` / `fact_id` | Lista ordenada e pura de fatos numéricos atômicos extraída exclusivamente de `calculate_metrics` por `build_fact_sheet`, onde cada número possui um identificador estável (`fact_id`), unidade (`BRL`, `%`, `min`, `count`), rótulo e valor arredondado. | **Ambiguidade resolvida:** O LLM jamais recebe o CSV bruto; recebe apenas a ficha de fatos já calculada pelo `pandas`. |
| **Evidência Aterrada** | `evidence` | Vínculo explícito entre uma recomendação e um ou mais fatos da ficha (`fact_id`, `label`, `value`, `unit`). O valor numérico (`value`) é sempre injetado pelo back-end a partir da ficha de fatos oficial, e nunca confiado ao output bruto do LLM. | Rejeitados: citações livres sem `fact_id` ou evidências com `value` divergente do fato. |
| **Recomendação Fundamentada** | `recommendation` / `recommendation_run` | Orientação prática estruturada (`rank`, `title`, `theme`, `diagnosis`, `action`, `expected_impact`, `evidence`) validada pelo motor de aterramento e persistida na tabela `recommendation_runs` para um `upload_id`. | Sempre em conjunto exato de 3 recomendações (`rank` `1`, `2`, `3`). |
| **Fallback Determinístico** | `deterministic_fallback` | Conjunto de 3 recomendações construído por regras determinísticas em Python (`build_fallback_recommendations`) acionado automaticamente quando o servidor Ollama está inacessível, excede o timeout ou falha na validação de aterramento após 1 nova tentativa. | Nunca mascarar como `"llm"`; o campo `source` deve indicar `"deterministic_fallback"` e `warnings[]` deve explicar o motivo. |

---

## 2. Schema e Colunas Obrigatórias do CSV

Todo arquivo CSV submetido ao sistema deve conter exatamente as **10 colunas obrigatórias** abaixo no cabeçalho (case-sensitive, separadas por vírgula `,`):

| # | Coluna | Tipo Lógico | Restrições de Domínio |
| --- | --- | --- | --- |
| 1 | `order_id` | `str` | Obrigatório, não vazio após `strip()`. Identifica o pedido ao qual o item pertence. |
| 2 | `timestamp` | `str` (ISO-8601 / Data-Hora) | Obrigatório, conversível para data/hora válida (ex.: `2026-11-01T19:15:00` ou `2026-11-01 19:15:00`). |
| 3 | `item_name` | `str` | Obrigatório, não vazio após `strip()`. Nome comercial do produto. |
| 4 | `category` | `str` | Obrigatório, não vazio após `strip()`. Categoria do cardápio (ex.: `Burgers`, `Bebidas`). |
| 5 | `quantity` | `int` | Obrigatório, número inteiro estritamente positivo (`quantity >= 1`). Valores decimais não inteiros (ex.: `1.5`), zero ou negativos são rejeitados. |
| 6 | `unit_price` | `float` | Obrigatório, numérico estritamente positivo (`unit_price > 0.0`). Zero ou negativo são rejeitados. |
| 7 | `discount` | `float` | Obrigatório, numérico não-negativo (`discount >= 0.0`) e menor ou igual ao subtotal da linha (`discount <= quantity * unit_price`). |
| 8 | `prep_time_minutes` | `float` | Obrigatório, numérico não-negativo (`prep_time_minutes >= 0.0`). |
| 9 | `status` | `str` (Enum) | Obrigatório. Valores permitidos: `"completed"` ou `"canceled"`. |
| 10 | `channel` | `str` (Enum) | Obrigatório. Valores permitidos: `"balcao"`, `"delivery"` ou `"app"`. |

---

## 3. Invariantes do Domínio

1. **Invariante de Determinismo e Anti-Alucinação:** Nenhum indicador financeiro, percentual de curva ABC, contagem de pedidos ou detecção de gargalo pode ser gerado, estimado ou alterado por modelo de linguagem (LLM). O cálculo em `pandas` é a única fonte numérica.
2. **Invariante de Atomicidade de Lote (`RN-02`):** Um lote CSV é aceito por inteiro ou rejeitado por inteiro. Não existe importação parcial de CSV com linhas válidas e linhas descartadas silenciosamente.
3. **Invariante de Segregação de Cancelados (`RN-03`):** Itens com `status == "canceled"` jamais somam em `gross_revenue`, `discount_total`, `net_revenue`, `abc_curve`, `by_channel` ou `by_category`.
4. **Invariante de Consistência Intra-Pedido:** Todas as linhas que compartilham o mesmo `order_id` dentro de um mesmo CSV devem possuir o mesmo `status` e o mesmo `channel`. Caso um mesmo `order_id` apareça com `status` ou `channel` divergentes em linhas distintas do mesmo arquivo, o arquivo é rejeitado na validação (`RN-01`).
5. **Invariante de Fechamento Contábil:** Para qualquer lote com `valid_orders_count > 0`:
   - `round(gross_revenue - discount_total, 2) == net_revenue`
   - A soma de `revenue` de todos os itens em `abc_curve` é igual a `gross_revenue` (com tolerância máxima de arredondamento de `±0.01`).
   - O `cumulative_share_pct` do último item da `abc_curve` é exatamente `100.0`.
6. **Invariante de Aterramento Estrito de Recomendações (`RN-07`, `RN-08`):** Nenhuma recomendação é aceita ou persistida se citar um `fact_id` inexistente na ficha de fatos do lote ou se contiver qualquer número nos campos textuais (`title`, `diagnosis`, `action`, `expected_impact`) que não corresponda a um fato da ficha (tolerância `±0.01`). Além disso, `evidence[].value`, `evidence[].label` e `evidence[].unit` são sempre sobrescritos pelos valores oficiais de `build_fact_sheet`.
7. **Invariante de Degradação Graciosa sem Erro 5xx (`RN-09`):** Falhas de conectividade, timeout ou alucinação persistente do modelo local Ollama nunca produzem respostas HTTP `5xx`; o serviço entrega o fallback determinístico (`source = "deterministic_fallback"`) com transparência total em `warnings[]`.

---

## 4. Regras de Negócio Verificáveis

### RN-01 — Validação Estrutural e de Domínio do CSV de Pedidos

- **Termo:** Lote de Upload (`upload`) e Item de Pedido (`order_item`).
- **Válido:** Arquivo texto UTF-8 não vazio, contendo as 10 colunas obrigatórias no cabeçalho e ao menos 1 linha de dados, onde todas as linhas respeitam os tipos, domínios (`status` em `{"completed", "canceled"}`, `channel` em `{"balcao", "delivery", "app"}`), limites numéricos (`quantity >= 1`, `unit_price > 0`, `0 <= discount <= quantity * unit_price`, `prep_time_minutes >= 0`) e consistência intra-pedido (`order_id` com `status` e `channel` únicos).
- **Exceção:**
  - Arquivo ausente na requisição HTTP devolve `400 Bad Request`.
  - Arquivo com 0 bytes, apenas cabeçalho sem linhas de dados, coluna obrigatória faltante, valor nulo/vazio, tipo incompatível, número negativo/inválido ou `status`/`channel` fora do domínio levanta `CSVValidationError` no pipeline e devolve `422 Unprocessable Entity` na API com a lista detalhada `errors` (`row`, `column`, `message`).
- **Limite:** `discount == 0.0` e `prep_time_minutes == 0.0` são válidos; `discount == quantity * unit_price` (100% de desconto na linha) é válido; `unit_price == 0.0` ou `quantity == 0` são inválidos e rejeitam o arquivo.
- **Contrato:** `POST /api/v1/uploads` e `validate_and_parse_csv` em [`docs/contrato.md`](../contrato.md).

---

### RN-02 — Atomicidade Transacional na Rejeição de CSV Inválido

- **Termo:** Lote de Upload (`upload`).
- **Válido:** Quando `validate_and_parse_csv` conclui sem erros, o lote e todos os seus itens são gravados em uma única transação no SQLite.
- **Exceção:** Se o CSV contiver 99 linhas válidas e 1 linha inválida (ex.: na linha 100), o upload é integralmente recusado com `422 Unprocessable Entity` e o banco SQLite permanece inalterado (0 registros adicionados em `uploads` e 0 registros em `order_items`).
- **Limite:** Falhas de validação ocorrem em memória antes de abrir escrita no banco; caso ocorra falha de persistência durante o `commit`, a sessão executa `rollback` completo.
- **Contrato:** `POST /api/v1/uploads` em [`docs/contrato.md`](../contrato.md).

---

### RN-03 — Cálculo de Faturamento Bruto, Descontos, Faturamento Líquido e Perda por Cancelamento

- **Termo:** Faturamento Bruto (`gross_revenue`), Total de Descontos (`discount_total`), Faturamento Líquido (`net_revenue`) e Perda por Cancelamento (`canceled_revenue_loss`).
- **Válido:**
  - Filtrar linhas com `status == "completed"`:
    - `line_gross = quantity * unit_price`
    - `gross_revenue = round(sum(line_gross), 2)`
    - `discount_total = round(sum(discount), 2)`
    - `net_revenue = round(gross_revenue - discount_total, 2)`
  - Filtrar linhas com `status == "canceled"`:
    - `canceled_revenue_loss = round(sum(quantity * unit_price), 2)`
- **Exceção:** Linhas com `status == "canceled"` são estritamente ignoradas em `gross_revenue`, `discount_total` e `net_revenue`.
- **Limite:** Se o CSV contiver apenas pedidos com `status == "canceled"`, então `gross_revenue = 0.0`, `discount_total = 0.0` e `net_revenue = 0.0`.
- **Contrato:** `POST /api/v1/uploads` e `GET /api/v1/uploads/{upload_id}/metrics` em [`docs/contrato.md`](../contrato.md).

---

### RN-04 — Cálculo de Ticket Médio por Pedido Concluído Único (`order_id`)

- **Termo:** Ticket Médio Bruto (`average_ticket_gross`) e Ticket Médio Líquido (`average_ticket_net`).
- **Válido:**
  - `valid_orders_count` = contagem de valores distintos de `order_id` entre as linhas com `status == "completed"`.
  - `canceled_orders_count` = contagem de valores distintos de `order_id` entre as linhas com `status == "canceled"`.
  - `average_ticket_gross = round(gross_revenue / valid_orders_count, 2)`
  - `average_ticket_net = round(net_revenue / valid_orders_count, 2)`
- **Exceção:** Não dividir pelo número de linhas (`total_rows`) nem pela quantidade de itens vendidos (`sum(quantity)`). Um pedido com 3 itens (`3 linhas` com o mesmo `order_id`) conta como `1` pedido no denominador.
- **Limite:** Se `valid_orders_count == 0`, tanto `average_ticket_gross` quanto `average_ticket_net` retornam `0.0` (sem erro de divisão por zero). O mesmo vale por canal em `by_channel`.
- **Contrato:** `GET /api/v1/uploads/{upload_id}/metrics` em [`docs/contrato.md`](../contrato.md).

---

### RN-05 — Cálculo, Ordenação e Classificação da Curva ABC de Produtos

- **Termo:** Curva ABC (`abc_curve`).
- **Válido:**
  1. Considerar exclusivamente linhas com `status == "completed"`.
  2. Agrupar por `item_name` (utilizando a primeira `category` associada ao `item_name`, ou agrupando por `(item_name, category)` considerando que cada `item_name` pertence a uma categoria):
     - `quantity_sold = int(sum(quantity))`
     - `revenue = round(sum(quantity * unit_price), 2)`
  3. Ordenar os itens por `revenue` **decrescente** e, em caso de empate, por `item_name` **crescente** (ordem alfabética).
  4. Para cada item na lista ordenada:
     - `revenue_share_pct = round((revenue / gross_revenue) * 100.0, 2)`
     - `cumulative_revenue` = soma acumulada de `revenue` do primeiro item até o item atual.
     - `cumulative_share_pct = round((cumulative_revenue / gross_revenue) * 100.0, 2)`
  5. Atribuir `abc_class` segundo a faixa de `cumulative_share_pct`:
     - Se for o **primeiro item da lista (índice 0)** OU se `cumulative_share_pct <= 80.0` → `"A"`
     - Caso contrário, se `cumulative_share_pct <= 95.0` → `"B"`
     - Caso contrário (`cumulative_share_pct > 95.0`) → `"C"`
- **Exceção:** Produtos que só aparecem em pedidos `canceled` não entram na `abc_curve`.
- **Limite:**
  - Se um único produto concentrar sozinho `85.0%` do faturamento no topo do ranking (índice 0), ele recebe `abc_class = "A"` (regra de garantia de existência da Classe A no líder de faturamento).
  - Se `valid_orders_count == 0` (ou `gross_revenue == 0.0`), `abc_curve` retorna lista vazia `[]` e `top_abc_item` retorna `None`.
- **Contrato:** `GET /api/v1/uploads/{upload_id}/metrics` em [`docs/contrato.md`](../contrato.md).

---

### RN-06 — Identificação Determinística de Gargalos Operacionais e Anomalias

- **Termo:** Gargalo Operacional (`bottlenecks`).
- **Válido:**
  1. **Atrasos de Preparo (apenas linhas com `status == "completed"`):**
     - Limiar fixo: `prep_time_threshold_minutes = 30`.
     - Uma linha é considerada atrasada se `prep_time_minutes > 30` (estritamente maior que 30).
     - `delayed_items_count`: total de linhas com `status == "completed"` e `prep_time_minutes > 30`.
     - `delayed_orders_count`: total de `order_id` distintos entre as linhas com `status == "completed"` e `prep_time_minutes > 30`.
     - `average_prep_time_minutes`: `round(mean(prep_time_minutes), 2)` de **todas** as linhas com `status == "completed"` (`0.0` se não houver linhas concluídas).
     - `max_prep_time_minutes`: `round(max(prep_time_minutes), 2)` de **todas** as linhas com `status == "completed"` (`0.0` se não houver linhas concluídas).
     - `delayed_by_category`: agrupamento das linhas atrasadas (`status == "completed"` e `prep_time_minutes > 30`) por `category`, contendo `category`, `delayed_items_count` (contagem de linhas atrasadas na categoria) e `avg_prep_time_minutes` (`round(mean(prep_time_minutes), 2)` das linhas atrasadas da categoria), ordenado por `delayed_items_count` decrescente e `category` crescente.
  2. **Cancelamentos por Canal (`canceled_by_channel`):**
     - Para cada `channel` presente no lote CSV, calcular:
       - `total_orders_count`: quantidade de `order_id` distintos naquele `channel` (concluídos + cancelados).
       - `canceled_orders_count`: quantidade de `order_id` distintos com `status == "canceled"` naquele `channel`.
       - `cancellation_rate_pct`: `round((canceled_orders_count / total_orders_count) * 100.0, 2)`.
       - `canceled_revenue_loss`: `round(sum(quantity * unit_price), 2)` das linhas com `status == "canceled"` naquele `channel`.
     - Ordenar por `cancellation_rate_pct` decrescente e `channel` crescente.
  3. **Cancelamentos por Item (`canceled_by_item`):**
     - Filtrar linhas com `status == "canceled"`, agrupar por `item_name` (mantendo `category`), calculando `canceled_quantity = int(sum(quantity))` e `canceled_revenue_loss = round(sum(quantity * unit_price), 2)`.
     - Ordenar por `canceled_revenue_loss` decrescente e `item_name` crescente.
  4. **Geração Determinística de Anomalias (`anomalies`):**
     - Para cada item em `delayed_by_category`: adicionar anomalia com `type = "high_prep_time"`, `dimension = category`, `metric_value = avg_prep_time_minutes`, `threshold_value = 30.0`, `severity = "critical"` se `avg_prep_time_minutes > 45.0` ou `delayed_items_count >= 5`, senão `"warning"`, e `description` explicativa.
     - Para cada canal em `canceled_by_channel` com `cancellation_rate_pct > 10.0`: adicionar anomalia com `type = "high_cancellation_rate"`, `dimension = channel`, `metric_value = cancellation_rate_pct`, `threshold_value = 10.0`, `severity = "critical"` se `cancellation_rate_pct >= 20.0`, senão `"warning"`, e `description` explicativa.
- **Limite:** `prep_time_minutes == 30.0` **não** é atraso (a condição é `> 30.0`). `cancellation_rate_pct == 10.0` **não** dispara anomalia de cancelamento (a condição é `> 10.0`).
- **Contrato:** `GET /api/v1/uploads/{upload_id}/metrics` em [`docs/contrato.md`](../contrato.md).

---

### RN-07 — Construção Determinística da Ficha de Fatos (`Fact Sheet`)

- **Termo:** Ficha de Fatos (`fact_sheet` / `fact_id`).
- **Válido:**
  - A função pura `build_fact_sheet(metrics)` em `data_pipeline/insights.py` recebe o dicionário de `calculate_metrics` e devolve uma lista determinística de fatos atômicos (`fact_id`, `category`, `label`, `value`, `unit`, `formatted`).
  - Inclui obrigatoriamente os fatos de limiar operacional (`thr.prep_time_minutes = 30.0` e `thr.cancellation_rate_pct = 10.0`), os fatos financeiros (`fin.*`), gargalos globais e por categoria (`bot.*`), cancelamentos por canal (`chan.<channel>.*`), desempenho por canal (`chan.<channel>.*`), desempenho por categoria (`cat.<category>.*`) e Curva ABC (`abc.*`).
  - Todos os valores em ponto flutuante são arredondados em 2 casas decimais e todas as contagens são inteiros nativos (`int`).
- **Exceção:** Nenhum fato pode ser criado a partir de fonte externa a `calculate_metrics`.
- **Limite:** Duas chamadas consecutivas a `build_fact_sheet(metrics)` com o mesmo dicionário de entrada retornam exatamente a mesma lista na mesma ordem.
- **Contrato:** Seção 3.2 de [`docs/contrato.md`](../contrato.md).

---

### RN-08 — Aterramento Numérico Estrito e Anti-Alucinação (`Grounding`)

- **Termo:** Evidência Aterrada (`evidence`) e Recomendação Fundamentada (`recommendation`).
- **Válido:**
  - O validador `validate_recommendations(payload, facts)` em `backend/ai/grounding.py` aprova o payload do LLM somente se todas as condições abaixo forem satisfeitas:
    1. O payload contém a lista `recommendations` com **exatamente 3 itens**;
    2. Os valores de `rank` são exatamente `[1, 2, 3]` (únicos) e `theme` pertence a `{"cancelamento", "operacao", "mix", "receita"}`;
    3. Os campos `title`, `diagnosis`, `action` e `expected_impact` são strings não vazias;
    4. Cada recomendação possui `evidence` como lista não vazia (`len(evidence) >= 1`) e todo `fact_id` citado existe no índice de `facts`;
    5. Todo número extraído dos textos (`title`, `diagnosis`, `action`, `expected_impact`) — após remover dos textos as ocorrências literais dos nomes de itens do cardápio (ex.: `"Refrigerante Lata 350ml"`, onde `350` faz parte do nome do produto) e aceitando formatos pt-BR (`R$ 474,00`, `4.750,00`, `20,0%`) e US (`474.0`, `4750.0`, `20.0%`) — corresponde a algum `value` presente em `facts` com tolerância máxima de `±0.01`, permitindo-se adicionalmente os inteiros estruturais `1`, `2` e `3` (referentes a `rank`/contagem de recomendações).
  - Quando aprovado, o validador **sobrescreve** `evidence[].value`, `evidence[].label` e `evidence[].unit` com os valores canônicos da ficha de fatos, garantindo que o LLM nunca seja a fonte do valor numérico exibido na interface.
- **Exceção:** Qualquer `fact_id` inexistente, número inventado no texto fora da ficha de fatos, lista de evidências vazia ou quantidade diferente de 3 recomendações reprova a saída com lista detalhada de erros de aterramento.
- **Limite:** Tolerância numérica de `±0.01` entre o número citado no texto e o `fact["value"]` (ex.: `0.95` aceita `0,95%`). Um número discrepante em `0.05` (ex.: citar `21.0%` quando a taxa real é `20.0%`) é rejeitado como alucinação.
- **Contrato:** Seção 2.6 de [`docs/contrato.md`](../contrato.md).

---

### RN-09 — Degradação Graciosa e Fallback Determinístico de Recomendações

- **Termo:** Fallback Determinístico (`deterministic_fallback`).
- **Válido:**
  - Durante `POST /api/v1/uploads/{upload_id}/recommendations`:
    1. Se a 1ª resposta do `LLMClient` falhar em `validate_recommendations`, o `RecommendationService` realiza **1 nova tentativa (retry)** fornecendo ao modelo a lista de erros de aterramento cometidos.
    2. Se a 2ª tentativa for aprovada, o resultado é retornado com `source = "llm"` e um aviso em `warnings[]` indicando que a resposta foi validada na 2ª tentativa.
    3. Se o `LLMClient` lançar `LLMUnavailableError` (servidor Ollama offline, falha de conexão ou timeout) ou se a 2ª tentativa também reprovar em `validate_recommendations`, o serviço aciona `build_fallback_recommendations(metrics, facts)` de `data_pipeline/insights.py`, retorna `201 Created` com `source = "deterministic_fallback"`, `model = None` e registra o motivo em `warnings[]`.
  - Para o dataset de referência (`data/sample_orders.csv`), `build_fallback_recommendations` gera deterministicamente 3 recomendações aterradas nos fatos:
    - **Rank 1 (`theme = "cancelamento"`):** Cancelamento crítico no canal `delivery` (`20.0%`, perda de `R$ 474,00` acima do limite de `10.0%`);
    - **Rank 2 (`theme = "operacao"`):** Atraso de preparo acima do limite de `30.0` minutos em `Burgers` (`4` itens, média `39.0` min) e `Combos` (`2` itens, média `40.0` min);
    - **Rank 3 (`theme = "mix"`):** Baixa participação da categoria `Bebidas` (`0.95%` da receita líquida, `R$ 45,00`) e cauda da Curva ABC (`3` itens na Classe C).
- **Exceção:** Indisponibilidade ou erro do LLM jamais retorna `500`, `502`, `503` ou `504` na rota de recomendações.
- **Limite:** As próprias recomendações geradas por `build_fallback_recommendations` devem passar integralmente por `validate_recommendations( { "recommendations": fallback }, facts )` com 0 erros.
- **Contrato:** Seções 2.5, 2.6 e 3.2 de [`docs/contrato.md`](../contrato.md).

---

### RN-10 — Estrutura, Ordenação, Persistência e Consulta das Recomendações

- **Termo:** Recomendação Fundamentada (`recommendation_run`).
- **Válido:**
  - Toda geração bem-sucedida (`POST /api/v1/uploads/{upload_id}/recommendations`) persiste um registro na tabela `recommendation_runs` no SQLite vinculado a `uploads.upload_id` (`ON DELETE CASCADE`), contendo `run_id`, `upload_id`, `generated_at`, `source`, `model`, `prompt_version`, `warnings` e as 3 recomendações ordenadas por `rank` `1`, `2`, `3`.
  - `GET /api/v1/uploads/{upload_id}/recommendations` retorna `200 OK` com a execução mais recente (`generated_at` decrescente) daquele `upload_id`.
  - `GET /api/v1/ai/status` retorna `200 OK` informando `ollama_reachable`, `base_url`, `model` e `model_available`.
- **Exceção:**
  - Se `upload_id` não existir no SQLite, tanto `POST` quanto `GET` em `/api/v1/uploads/{upload_id}/recommendations` retornam `404 Not Found`.
  - Se `upload_id` existir, mas ainda não possuir nenhum registro em `recommendation_runs`, `GET /api/v1/uploads/{upload_id}/recommendations` retorna `404 Not Found`.
- **Limite:** Se `POST /api/v1/uploads/{upload_id}/recommendations` for chamado múltiplas vezes para o mesmo `upload_id`, cada chamada cria um novo `run_id` e o `GET` subsequente devolve sempre o mais recente.
- **Contrato:** Seções 2.5, 2.6 e 2.7 de [`docs/contrato.md`](../contrato.md).

---

## 5. Agregações Complementares (`by_channel` e `by_category`)

- **`by_channel`:**
  - Considera apenas linhas com `status == "completed"`.
  - Agrupa por `channel`:
    - `valid_orders_count`: `order_id` distintos concluídos no canal.
    - `quantity_sold`: `int(sum(quantity))`.
    - `gross_revenue`: `round(sum(quantity * unit_price), 2)`.
    - `discount_total`: `round(sum(discount), 2)`.
    - `net_revenue`: `round(gross_revenue - discount_total, 2)`.
    - `revenue_share_pct`: `round((net_revenue / total_net_revenue) * 100.0, 2)` (ou `0.0` se `total_net_revenue == 0`).
    - `average_ticket_net`: `round(net_revenue / valid_orders_count, 2)`.
  - Ordenado por `net_revenue` decrescente e `channel` crescente.

- **`by_category`:**
  - Considera apenas linhas com `status == "completed"`.
  - Agrupa por `category`:
    - `quantity_sold`: `int(sum(quantity))`.
    - `gross_revenue`: `round(sum(quantity * unit_price), 2)`.
    - `discount_total`: `round(sum(discount), 2)`.
    - `net_revenue`: `round(gross_revenue - discount_total, 2)`.
    - `revenue_share_pct`: `round((net_revenue / total_net_revenue) * 100.0, 2)` (ou `0.0` se `total_net_revenue == 0`).
    - `average_prep_time_minutes`: `round(mean(prep_time_minutes), 2)`.
  - Ordenado por `net_revenue` decrescente e `category` crescente.

---

## 6. Histórico

| Data | Entrega | Alteração | Autor |
| --- | --- | --- | --- |
| 2026-11-09 | 0001 | Criação inicial do guia de domínio com linguagem ubíqua, invariantes e regras `RN-01` a `RN-06`. | Lee |
| 2026-11-09 | 0003 | Inclusão dos termos de IA aterrada (`fact_sheet`, `evidence`, `recommendation_run`, `deterministic_fallback`), invariantes 6 e 7 e regras `RN-07` a `RN-10`. | Lee |
