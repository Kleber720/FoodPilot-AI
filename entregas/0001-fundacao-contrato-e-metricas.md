---
id: "0001"
projeto: FoodPilot AI
titulo: Fundação arquitetural, contrato de API/CSV, persistência SQLite e motor determinístico de métricas em pandas
estado: aceita
pedido-origem: Briefing inicial do humano — Etapas 1 (Estrutura e arquitetura) e 2 (Dados e inteligência de negócio) do MVP FoodPilot AI
criado-em: 2026-11-09
atualizado-em: 2026-11-09
---

## Pedido

Construir a fundação arquitetural do FoodPilot AI (contratos, banco de dados local SQLite e API de upload/consulta) e o pipeline determinístico em Python + pandas que importa um arquivo CSV de pedidos de restaurante, valida sua integridade e calcula faturamento total, ticket médio, curva ABC de produtos e desvios/gargalos operacionais sem depender de IA para cálculos numéricos.

## Aceite

1. **Contrato e especificação de dados congelados antes do código.** Os arquivos `docs/contrato.md` (endpoints REST, códigos HTTP, schemas de requisição/resposta JSON), `docs/dominio/pedidos-e-metricas.md`, `docs/dados/pedidos-csv.md` (data card com colunas obrigatórias, tipos, regras de rejeição e dataset simulado de referência) e `docs/matriz-de-regras.md` existem e estão alinhados entre back-end e dados.
2. **Importação de CSV válido e persistência no SQLite.** Ao enviar um arquivo CSV válido com pedidos simulados para o endpoint de upload (`POST /api/v1/uploads`), a API responde `201 Created` (ou `200 OK` conforme contrato), grava os metadados do lote e os pedidos no banco SQLite local e retorna o identificador do processamento junto com o resumo de linhas processadas.
3. **Rejeição determinística de CSV inválido ou corrompido.** Ao enviar um arquivo vazio, sem colunas obrigatórias ou com valores numéricos negativos/inválidos que violem as regras do data card, a API responde `422 Unprocessable Entity` (ou `400 Bad Request` conforme contrato) com a lista estruturada de erros por coluna/linha e não contamina o banco SQLite com dados parciais.
4. **Cálculo determinístico auditável (Faturamento, Ticket Médio, Curva ABC e Gargalos) (eliminatório).** Dado o dataset CSV de referência (`data/sample_orders.csv`), o motor em `pandas` e o endpoint `GET /api/v1/uploads/{id}/metrics` devolvem JSON exatamente igual aos valores matemáticos esperados:
   - Faturamento bruto/líquido igual à soma exata de `quantity * unit_price` dos pedidos válidos;
   - Ticket médio igual a `faturamento_total / total_pedidos_validos`;
   - Classificação da Curva ABC ordenada por participação acumulada no faturamento (`A` até ~80%, `B` até ~95%, `C` restante) com soma percentual igual a 100%;
   - Identificação determinística de desvios e gargalos (ex.: atrasos de preparo acima do limiar ou concentração de cancelamentos por item/horário/canal).
   Qualquer divergência numérica ou uso de LLM para calcular estatísticas reprova a entrega de imediato.
5. **Suíte de testes automatizados passando.** A execução de `.venv\Scripts\python.exe -m pytest` passa integralmente com 100% dos testes de unidade do motor `pandas` e de integração dos endpoints/SQLite verdes.

## Etapas

| # | Etapa | Dono | Sai | Depende de |
| --- | --- | --- | --- | --- |
| 1 | Definição do contrato da API, guia de domínio e decisão de stack | Lee | `docs/contrato.md`, `docs/dominio/pedidos-e-metricas.md`, `docs/decisoes/0001-stack-backend.md` e estrutura inicial de `docs/matriz-de-regras.md` | Autorização de stack pelo humano |
| 2 | Especificação do Data Card do CSV, dataset simulado e motor determinístico em `pandas` | Shikamaru | `docs/dados/pedidos-csv.md`, `data/sample_orders.csv`, módulo `data_pipeline/` (validação de CSV, faturamento, ticket médio, curva ABC, gargalos) e regras numéricas em `docs/matriz-de-regras.md` | Etapa 1 (`docs/contrato.md` congelado) |
| 3 | Persistência SQLite, migrações e endpoints REST de upload e leitura de métricas | Lee | `backend/` (FastAPI + Pydantic + SQLAlchemy 2.x + Alembic), banco SQLite configurado e integração com `data_pipeline/` | Etapas 1 e 2 |
| 4 | Auditoria de regras, testes de borda e prova de conformidade do contrato e cálculos | Kakashi | Suíte de verificação em `tests/`, validação da `docs/matriz-de-regras.md` e parecer de prova (ou abertura de registros em `problemas/` se houver falha) | Etapas 2 e 3 |

## Portões obrigatórios

- **Contrato congelado antes da implementação (`docs/contrato.md`):** Nem Shikamaru nem Sakura acoplam formatos de saída antes de o Lee publicar os schemas de entrada/saída.
- **Determinismo matemático e invariante anti-alucinação:** Nenhum cálculo de faturamento, ticket médio, curva ABC ou desvio pode passar por modelo generativo; tudo deve ser provado por asserções exatas em `pytest` sobre o `pandas`.
- **Atomicidade no upload de CSV:** Falha na validação do CSV não pode deixar registros órfãos no SQLite.
- **Execução real da suíte (`pytest`):** Nenhuma etapa é dada como pronta sem o comando real executado no ambiente local com código de saída `0`.

## Autorizações

- **[AUTORIZADO EM 2026-11-09] Confirmação da stack de Back-end (`.Agents/comum/stacks.md`):**
  - *Contexto:* O briefing inicial sugeriu `Node.js + Express` para o back-end ao lado de `Python + pandas` para dados. Porém, a regra de stack fixa do time em [`.Agents/comum/stacks.md`](../.Agents/comum/stacks.md) define **Python 3.12+ com FastAPI, Pydantic, SQLAlchemy 2.x e Alembic** para o Lee (Back-end) + **SQLite**.
  - *Decisão autorizada:* Seguir com a stack oficial do time (`Python 3.14.5 / FastAPI / Pydantic / SQLAlchemy 2.x / Alembic / SQLite`), integrando nativamente com o pipeline `pandas` do Shikamaru.
  - *Status:* Autorizado (Data: `2026-11-09` | Autorizado por: `Humano`).

## Fora de escopo

- Interface web em React + TypeScript + Vite, gráficos visuais e filtros interativos de tela (alocados na **Entrega 0002 — Dashboard Profissional e Upload Web** com a Sakura).
- Integração com o servidor local Ollama (`qwen3:4b-instruct`), engenharia de prompt das 3 recomendações acionáveis e chat contextual (alocados na **Entrega 0003 — Agente de IA Local Ollama e Recomendações Fundamentadas** com Shikamaru, Lee e Sakura).
- Geração/exportação de relatórios finais consolidados, alertas automatizados e fechamento do `README.md` de portfólio para o GitHub (alocados na **Entrega 0004 — Relatórios, Alertas, Prova Ponta a Ponta e Documentação de Portfólio**).

## Decisões

- [`docs/decisoes/0001-stack-backend.md`](../docs/decisoes/0001-stack-backend.md) — Adoção de `Python 3.12+ (3.14.5) + FastAPI + Pydantic v2 + SQLAlchemy 2.x + Alembic + SQLite` no back-end, unificando o runtime em memória com `data_pipeline/` (`pandas`) e `pytest`.

## Resultado

**Veredito da Entrega 0001:** **ACEITA** em `2026-11-09` (Tsunade).

| # | Critério de Aceite | Status | Evidência Verificada |
| --- | --- | --- | --- |
| 1 | **Contrato e especificação de dados congelados antes do código** | **PASSOU** | Publicados e alinhados: [`docs/contrato.md`](../docs/contrato.md), [`docs/dominio/pedidos-e-metricas.md`](../docs/dominio/pedidos-e-metricas.md), [`docs/dados/pedidos-csv.md`](../docs/dados/pedidos-csv.md), [`docs/matriz-de-regras.md`](../docs/matriz-de-regras.md) e [`docs/decisoes/0001-stack-backend.md`](../docs/decisoes/0001-stack-backend.md). |
| 2 | **Importação de CSV válido e persistência no SQLite** | **PASSOU** | Endpoint `POST /api/v1/uploads` (`backend/main.py`) retorna `201 Created`, persiste atomicamente nas tabelas `uploads` e `order_items` via SQLAlchemy 2.x + SQLite (migração `0001_initial_schema.py` validada em `alembic upgrade head`) e expõe consulta em `GET /api/v1/uploads`. Provado por `test_rn02_valid_upload_persists_atomically_and_serves_metrics_end_to_end`. |
| 3 | **Rejeição determinística de CSV inválido ou corrompido** | **PASSOU** | `POST /api/v1/uploads` retorna `400 Bad Request` quando o arquivo está ausente e `422 Unprocessable Entity` com lista `errors` (`row` 1-indexed, `column`, `message`) quando o CSV viola `RN-01`, mantendo `0` registros órfãos no SQLite (`RN-02`). Provado por 39 testes de validação em `tests/test_validator_rn01.py` e `test_rn02_atomicity_rejects_mixed_valid_and_invalid_csv_without_partial_sqlite_writes`. |
| 4 | **Cálculo determinístico auditável (Faturamento, Ticket Médio, Curva ABC e Gargalos) (eliminatório)** | **PASSOU** | Em `data/sample_orders.csv` (`82` linhas, `50` pedidos concluídos e `5` cancelados), `data_pipeline/metrics.py` e `GET /api/v1/uploads/{id}/metrics` devolvem exatidão matemática: `gross_revenue=5000.0`, `discount_total=250.0`, `net_revenue=4750.0`, `canceled_revenue_loss=514.0`, `average_ticket_gross=100.0`, `average_ticket_net=95.0`, Curva ABC com 3 itens `A` (`79.2%`), 2 itens `B` (`94.5%`) e 3 itens `C` (`100.0%`), `delayed_orders_count=5`, `delayed_items_count=6` e 3 anomalias determinísticas. Zero uso de LLM para cálculos. |
| 5 | **Suíte de testes automatizados passando** | **PASSOU** | `.venv\Scripts\python.exe -m pytest -v` executou **53 testes com 100% de aprovação em `0.79s`** (exit code `0`), incluindo prova de sanidade com quebra deliberada em `data_pipeline/metrics.py` (`7 failed` detectados imediatamente) e restauração limpa (`53 passed`). |
