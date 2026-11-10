---
id: "0002"
projeto: FoodPilot AI
titulo: Dashboard Profissional e Upload Web em React + TypeScript + Vite
estado: aceita
pedido-origem: Briefing inicial do humano — Etapa 3 (Dashboard profissional: indicadores financeiros, gráficos, filtros e relatórios) do MVP FoodPilot AI
criado-em: 2026-11-09
atualizado-em: 2026-11-09
---

## Pedido

Construir a aplicação web de front-end (`frontend/`) em React + TypeScript + Vite que consome o contrato congelado da Entrega 0001 (`docs/contrato.md`), permitindo ao operador de restaurante enviar arquivos CSV de pedidos, alternar entre lotes importados e visualizar o dashboard executivo com KPIs financeiros, gráficos e tabelas da Curva ABC, quebras por canal e categoria, filtros interativos e painel de gargalos/anomalias operacionais.

## Aceite

1. **Upload de CSV e tratamento completo de estados (`POST /api/v1/uploads`).** A interface permite selecionar e enviar um arquivo `.csv` via `multipart/form-data` (campo `file`), exibe estado de carregamento durante o envio, atualiza automaticamente a lista de lotes e o dashboard ativo quando a API responde `201 Created`, e exibe de forma clara e estruturada a tabela de erros por linha e coluna (`row`, `column`, `message`) quando a API devolve `422 Unprocessable Entity` ou `400 Bad Request`.
2. **Listagem e seleção de lotes (`GET /api/v1/uploads`).** A interface carrega o histórico de lotes importados (`items`, `total`), exibe um estado vazio orientativo quando `total == 0` e permite alternar entre lotes cadastrados disparando `GET /api/v1/uploads/{upload_id}/metrics`.
3. **Dashboard de KPIs Financeiros, Canal e Categoria (eliminatório: sem recálculo no cliente).** Os cartões executivos e gráficos exibem fielmente os valores retornados em `financials` (`gross_revenue`, `discount_total`, `net_revenue`, `average_ticket_gross`, `average_ticket_net`, `valid_orders_count`, `canceled_orders_count`, `canceled_revenue_loss`), `by_channel` (`balcao`, `delivery`, `app`) e `by_category`, com formatação monetária BRL (`R$`), percentuais e filtros interativos de visualização por canal e categoria, sem jamais recalcular KPIs financeiros no navegador.
4. **Visualização da Curva ABC e Painel de Gargalos/Anomalias.** O dashboard apresenta:
   - Gráfico visual de Pareto/barras e tabela ordenada da `abc_curve` com filtro por classe (`Todas`, `A`, `B`, `C`), destacando participação individual (`revenue_share_pct`) e acumulada (`cumulative_share_pct`);
   - Painel de gargalos (`bottlenecks`) exibindo atrasos de preparo (`delayed_orders_count`, `delayed_items_count`, `average_prep_time_minutes`, `max_prep_time_minutes`, `delayed_by_category`), cancelamentos por canal/item (`canceled_by_channel`, `canceled_by_item`) e alertas de `anomalies` diferenciados visualmente e semanticamente por `severity` (`warning` e `critical`).
5. **Sistema de Design, Acessibilidade e Testes de Comportamento de Interface.** A aplicação utiliza CSS com tokens de design definidos (`frontend/src/styles/tokens.css`), marcação HTML semântica acessível (`aria-live`, `role="alert"`, `role="status"`, labels explícitos e foco visível para teclado) e inclui suíte de testes de comportamento da interface em `frontend/src/__tests__/` (Vitest + Testing Library) cobrindo estado vazio, upload bem-sucedido, exibição de erros 422 por linha/coluna, renderização dos KPIs/Curva ABC/Gargalos e filtros interativos.

## Etapas

| # | Etapa | Dono | Sai | Depende de |
| --- | --- | --- | --- | --- |
| 1 | Arquitetura de front-end, sistema de design (tokens CSS), componentes do Dashboard, integração HTTP com `docs/contrato.md` e suíte de testes Vitest + Testing Library | Sakura | `frontend/` (`package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/styles/tokens.css`, `src/types/api.ts`, `src/services/api.ts`, componentes de Upload, KPIs, Curva ABC, Gargalos, Filtros e `src/__tests__/`) + `docs/frontend/design-e-arquitetura.md` | Entrega 0001 (`docs/contrato.md` congelado) |
| 2 | Auditoria independente de fronteira de escopo, aderência contratual `frontend/` ↔ `docs/contrato.md` e verificação de integridade da suíte | Kakashi | Relatório de auditoria da Entrega 0002, validação estática/contratual dos schemas e testes de front-end e reexecução da suíte `pytest` de servidor (`53 passed`) | Etapa 1 |

## Portões obrigatórios

- **Aderência estrita ao contrato (`docs/contrato.md`):** Todos os nomes de campos, rotas (`/api/v1/health`, `/api/v1/uploads`, `/api/v1/uploads/{upload_id}/metrics`) e códigos de status (`200`, `201`, `400`, `404`, `422`) em `frontend/src/types/api.ts` e `frontend/src/services/api.ts` devem refletir exatamente `docs/contrato.md`.
- **Proibição de recálculo financeiro no front-end:** O navegador apenas formata e filtra para exibição os dados já calculados pelo `data_pipeline/` e entregues pelo `backend/`.
- **Isolamento de fronteira de código:** A Sakura edita exclusivamente `frontend/` e `docs/frontend/`; nenhuma linha de `backend/`, `data_pipeline/` ou `tests/` de servidor pode ser alterada.

## Autorizações

- Stack de Front-end (`React + TypeScript + Vite + CSS com tokens do projeto + Vitest / Testing Library`) já definida como padrão fixo em [`.Agents/comum/stacks.md`](../.Agents/comum/stacks.md). Nenhuma exceção de stack solicitada.

## Fora de escopo

- Integração com o servidor local Ollama (`qwen3:4b-instruct`), geração das 3 recomendações acionáveis por IA e interface de recomendações/chat (alocados na **Entrega 0003 — Agente de IA Local Ollama e Recomendações Fundamentadas**).
- Exportação de relatórios consolidados finais, alertas automatizados de servidor e fechamento do `README.md` de portfólio (alocados na **Entrega 0004**).

## Decisões

- Documentação de arquitetura e tokens de design do front-end em `docs/frontend/design-e-arquitetura.md` (dono: Sakura).

## Resultado

**Veredito da Entrega 0002:** **ACEITA** em `2026-11-09` (Tsunade — todos os 5 critérios provados em auditoria contratual e em execução real com Node.js `v26.13.0`, Vitest `2.1.9` e Vite `6.4.6`).

| # | Critério de Aceite | Status | Evidência Verificada |
| --- | --- | --- | --- |
| 1 | **Upload de CSV e tratamento completo de estados (`POST /api/v1/uploads`)** | **PASSOU** | Implementado em [`frontend/src/components/UploadPanel.tsx`](../frontend/src/components/UploadPanel.tsx) e [`frontend/src/services/api.ts`](../frontend/src/services/api.ts) (`uploadOrdersCsv` com `FormData` campo `'file'`, estado `aria-busy`, atualização automática no `201 Created` e captura de `400`/`422` em `ApiValidationError` renderizando tabela `row`, `column`, `message`). Provado em runtime no Vitest (`Dashboard.test.tsx`: cenários 2 e 3). |
| 2 | **Listagem e seleção de lotes (`GET /api/v1/uploads`)** | **PASSOU** | Implementado em [`frontend/src/components/UploadHistorySelector.tsx`](../frontend/src/components/UploadHistorySelector.tsx) e [`frontend/src/App.tsx`](../frontend/src/App.tsx) (estado vazio orientativo quando `total === 0` e seletor acessível `<select>` disparando `GET /api/v1/uploads/{upload_id}/metrics`). Provado em runtime no Vitest (`Dashboard.test.tsx`: cenários 1 e 5). |
| 3 | **Dashboard de KPIs Financeiros, Canal e Categoria (eliminatório: sem recálculo no cliente)** | **PASSOU** | Auditado pelo Kakashi em [`FinancialKpiGrid.tsx`](../frontend/src/components/FinancialKpiGrid.tsx), [`ChannelAndCategorySection.tsx`](../frontend/src/components/ChannelAndCategorySection.tsx) e [`formatters.ts`](../frontend/src/utils/formatters.ts): 16 schemas Pydantic (`88 campos`) de `backend/schemas.py` batem 100% com [`frontend/src/types/api.ts`](../frontend/src/types/api.ts), **nenhum** componente realiza recálculo matemático no navegador e o Vitest comprova a renderização exata (`R$ 5.000,00`, `R$ 4.750,00`, `R$ 100,00`, `R$ 95,00`). |
| 4 | **Visualização da Curva ABC e Painel de Gargalos/Anomalias** | **PASSOU** | Implementado em [`AbcCurveSection.tsx`](../frontend/src/components/AbcCurveSection.tsx) (gráfico de Pareto + tabela + filtro `Todas`/`A`/`B`/`C`) e [`BottlenecksAndAnomaliesSection.tsx`](../frontend/src/components/BottlenecksAndAnomaliesSection.tsx) (KPIs de atraso `> 30 min`, tabelas `delayed_by_category`, `canceled_by_channel`, `canceled_by_item` e alertas `anomalies` por `severity: warning | critical`). Provado em runtime no Vitest (`Dashboard.test.tsx`: cenários 2 e 4). |
| 5 | **Sistema de Design, Acessibilidade e Testes de Comportamento de Interface** | **PASSOU** | Entregues [`docs/frontend/design-e-arquitetura.md`](../docs/frontend/design-e-arquitetura.md), [`tokens.css`](../frontend/src/styles/tokens.css), [`global.css`](../frontend/src/styles/global.css) e [`Dashboard.test.tsx`](../frontend/src/__tests__/Dashboard.test.tsx). Verificados em runtime: `npm.cmd --prefix frontend test` → **`5 passed (5)` em `862ms`** (exit code `0`); `npm.cmd --prefix frontend run build` (`tsc -b && vite build`) → **`✓ 35 modules transformed`, `✓ built in 658ms`** (exit code `0`); e `.venv\Scripts\python.exe -m pytest -v` → **`53 passed in 0.84s`** (exit code `0`). |
