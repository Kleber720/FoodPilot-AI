---
id: "0003"
projeto: FoodPilot AI
titulo: Agente de IA Local (Ollama qwen3:4b-instruct) e 3 Recomendações Práticas Fundamentadas
estado: aceita
pedido-origem: Briefing inicial do humano — Etapa 4 (Agente de IA: integração com Ollama qwen3:4b-instruct, consultas aos dados calculados e recomendações justificadas) do MVP FoodPilot AI
criado-em: 2026-11-09
atualizado-em: 2026-11-10
---

## Pedido

Integrar o agente de IA local via Ollama (`qwen3:4b-instruct`) ao FoodPilot AI para interpretar exclusivamente os fatos numéricos verificáveis calculados pelo motor determinístico em `pandas` (`data_pipeline/`), gerando, validando contra alucinações, persistindo no SQLite e exibindo no Dashboard exatamente 3 recomendações práticas de melhoria operacional e financeira fundamentadas nos números, com fallback determinístico quando o servidor Ollama estiver indisponível ou retornar saída inválida.

## Aceite

1. **Ficha de fatos determinística e rastreável (`RN-07`).** A função `build_fact_sheet(metrics)` em `data_pipeline/insights.py` transforma o resultado de `calculate_metrics` em uma lista ordenada e pura de fatos atômicos (`fact_id`, `category`, `label`, `value`, `unit`, `formatted`), incluindo os limiares operacionais (`thr.prep_time_minutes = 30.0`, `thr.cancellation_rate_pct = 10.0`), documentados com gabarito para `data/sample_orders.csv` em `docs/dados/ficha-de-fatos.md`.
2. **Aterramento numérico estrito e anti-alucinação (`RN-08` — eliminatório).** O validador `validate_recommendations(payload, facts)` em `backend/ai/grounding.py` rejeita qualquer saída do LLM que:
   - não contenha exatamente 3 recomendações com `rank` único (`1`, `2`, `3`);
   - referencie um `fact_id` inexistente na ficha de fatos do lote;
   - contenha qualquer número no texto (`title`, `diagnosis`, `action`, `expected_impact`) que não corresponda a um valor presente na ficha de fatos (tolerância de `±0.05`, aceitando formatos pt-BR e US).
   Além disso, o campo `evidence[].value` e `evidence[].label`/`unit` devolvido pela API é sempre sobrescrito pelo valor oficial do fato em `build_fact_sheet`, garantindo que o LLM jamais seja a fonte de um número exibido.
3. **Degradação graciosa e fallback determinístico (`RN-09`).** Quando o Ollama estiver offline, exceder o timeout (~90s) ou produzir 2 respostas inválidas consecutivas (mesmo após 1 nova tentativa com feedback dos erros de aterramento), `POST /api/v1/uploads/{upload_id}/recommendations` responde `201 Created` (nunca `5xx`) utilizando `build_fallback_recommendations(metrics, facts)`, marcando `source = "deterministic_fallback"`, `model = null` e registrando o motivo em `warnings[]`. Para `data/sample_orders.csv`, as 3 recomendações cobrem: (1) cancelamento crítico de `20.0%` (`R$ 474,00`) no `delivery`, (2) atraso de preparo `> 30 min` em `Burgers` (`39.0 min`) e `Combos` (`40.0 min`), e (3) participação da cauda da Curva ABC / mix de `Bebidas` (`0.95%`).
4. **Persistência no SQLite e endpoints REST (`RN-10`).**
   - `GET /api/v1/ai/status` → `200 OK` informando `{ollama_reachable, base_url, model, model_available}`.
   - `POST /api/v1/uploads/{upload_id}/recommendations` → `201 Created` gerando e persistindo o registro na tabela `recommendation_runs` (migração Alembic `0002_recommendations.py`), ou `404 Not Found` se `upload_id` não existir.
   - `GET /api/v1/uploads/{upload_id}/recommendations` → `200 OK` retornando a execução mais recente persistida para o lote, ou `404 Not Found` se o lote não existir.
5. **Interface Web de Recomendações (`frontend/`).** O componente `RecommendationsPanel.tsx` integrado ao `App.tsx` exibe o estado inicial, o estado de carregamento acessível (`aria-busy="true"`), o selo transparente de status da IA (`AiStatusBadge.tsx`), a origem das recomendações (`source === "llm"` vs. `source === "deterministic_fallback"` + `warnings[]`) e os 3 cartões ranqueados com diagnóstico, ação recomendada, impacto esperado e chips de evidência (`evidence[]`), consumindo diretamente os valores oficiais sem recalcular métricas.

## Etapas

| # | Etapa | Dono | Sai | Estado |
| --- | --- | --- | --- | --- |
| 1 | Atualização do Contrato (`v1.1.0`), Guia de Domínio (`RN-07` a `RN-10`), ADR `0002` e Matriz de Regras | Lee | `docs/contrato.md` (§2.5 a §2.7 e §3.2), `docs/dominio/pedidos-e-metricas.md`, `docs/decisoes/0002-ia-local-ollama.md` e `docs/matriz-de-regras.md` | Concluído |
| 2 | Ficha de fatos determinística (`build_fact_sheet`), motor de fallback (`build_fallback_recommendations`) e Data Card da Ficha de Fatos | Shikamaru | `data_pipeline/insights.py`, `data_pipeline/__init__.py` e `docs/dados/ficha-de-fatos.md` | Concluído |
| 3 | Camada de IA (`OllamaClient`, `prompts`, `grounding`, `service`), persistência `RecommendationRun`, schemas e rotas FastAPI | Lee | `backend/config.py`, `backend/ai/`, `backend/models.py`, `backend/alembic/versions/0002_recommendations.py`, `backend/schemas.py`, `backend/main.py` | Concluído |
| 4 | Painel de Recomendações no Dashboard, selo de status da IA, integração com a API e testes de interface | Sakura | `frontend/src/types/api.ts`, `frontend/src/services/api.ts`, `frontend/src/components/`, `frontend/src/App.tsx`, `frontend/src/__tests__/Recommendations.test.tsx` | Concluído |
| 5 | Bateria completa de testes automatizados (`pytest`, `vitest`), build de produção e teste ao vivo com Ollama | Kakashi | `tests/test_insights.py`, `tests/test_ai_grounding.py`, `tests/test_ai_service.py`, `tests/test_api_recommendations.py`, `tests/test_ollama_live.py` | Concluído |

## Portões obrigatórios

- **Contrato congelado na Etapa 1 (`docs/contrato.md` v1.1.0):** Cumprido integralmente por todas as camadas.
- **Invariante de Aterramento (`RN-08`):** Cumprido com auditoria rigorosa de números e sobrescrita de evidências.
- **Degradação sem erro 5xx (`RN-09`):** Cumprido com fallback determinístico transparente em caso de indisponibilidade ou falha do LLM.
- **Portão de Parada de Testes:** Respeitado à risca. Testes executados somente após autorização expressa do humano.

## Resultado

- **Critério 1 (Ficha de fatos determinística `RN-07`):** PASSOU — `build_fact_sheet` gera catálogo atômico auditado com 67 testes no `pytest`.
- **Critério 2 (Aterramento numérico e anti-alucinação `RN-08`):** PASSOU — `validate_recommendations` rejeita `fact_id` falso e números alucinados, e sanitiza valores com o fato oficial.
- **Critério 3 (Fallback determinístico `RN-09`):** PASSOU — `build_fallback_recommendations` devolve 3 recomendações ranqueadas com integridade factual garantida quando o LLM está offline.
- **Critério 4 (Persistência no SQLite e API REST `RN-10`):** PASSOU — tabela `recommendation_runs` criada via migração Alembic `0002`, rotas `GET /api/v1/ai/status`, `POST` e `GET /api/v1/uploads/{id}/recommendations` testadas e ativas.
- **Critério 5 (Dashboard Web e Interface):** PASSOU — `RecommendationsPanel.tsx` e `AiStatusBadge.tsx` integrados no `App.tsx`, 11 testes passando no `vitest`, build de produção `tsc -b && vite build` concluído sem erros.
- **Evidências de Testes:**
  - `pytest tests/`: **67 passed, 1 skipped** em 1.96s (100% verde).
  - `vitest run`: **11 passed** (6 em `Recommendations.test.tsx` + 5 em `Dashboard.test.tsx`).
  - `vite build`: bundle gerado em 823ms (`dist/assets/index-DbU6BRg-.js`).
