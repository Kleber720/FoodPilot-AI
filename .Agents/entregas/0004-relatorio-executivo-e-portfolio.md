---
id: "0004"
projeto: FoodPilot AI
titulo: Fechamento do Produto, Relatório Executivo e Portfólio de Seleção para o iFood AI Builder
estado: aceita
pedido-origem: Briefing inicial do humano — Etapa 5 (Relatórios, documentação de portfólio para GitHub, demonstração e fechamento do MVP FoodPilot AI)
criado-em: 2026-11-10
atualizado-em: 2026-11-10
---

## Pedido

Consolidar o MVP do FoodPilot AI como um produto completo de ponta a ponta e um projeto de portfólio de nível sênior, implementando a geração e exportação de relatórios executivos para impressão/PDF, script de inicialização com um clique no Windows (`run.bat`), README.md de alto impacto para o GitHub demonstrando a arquitetura anti-alucinação e o roteiro estruturado para gravação do vídeo de demonstração/pitch para o processo seletivo do iFood AI Builder.

## Aceite

1. **Endpoint de Relatório Executivo Consolidado (`GET /api/v1/uploads/{upload_id}/report`).**
   - Consolida em uma única chamada auditável os KPIs financeiros, as anomalias e gargalos operacionais, a liderança da Curva ABC e as 3 recomendações oficiais do lote.
   - Devolve também o campo `report_markdown` contendo o resumo executivo formatado em Markdown pronto para compartilhamento ou exportação.
   - Retorna `404 Not Found` se o `upload_id` não existir.
2. **Exportação e Impressão Visual no Front-end (`frontend/`).**
   - Adição de botão "Exportar Relatório" / "Imprimir" no cabeçalho executivo do lote ativo.
   - Estilização `@media print` otimizada em CSS para gerar PDFs executivos limpos, omitindo botões de navegação e formulários de upload e destacando o resumo financeiro, gargalos e as recomendações práticas.
3. **Script de Inicialização Unificada (`run.bat`).**
   - Script batch para Windows que ativa o ambiente `.venv`, inicia o backend FastAPI (porta 8000) e o frontend Vite (porta 5173) de forma integrada e intuitiva.
4. **README.md de Alto Impacto para Portfólio no GitHub.**
   - Apresentação executiva do produto, problema de negócio e proposta de valor.
   - Badges visuais de stack tecnológica, cobertura de testes e execução local a custo zero.
   - Diagrama Mermaid completo de arquitetura de dados e separação de responsabilidades (por que o Python calcula e o LLM apenas contextualiza).
   - Guia de execução rápida (*Quickstart*) em 3 passos para o avaliador reproduzir os resultados com `data/sample_orders.csv`.
   - Evidências formais de qualidade (67 testes pytest + 11 testes vitest + build de produção).
5. **Roteiro de Demonstração em Vídeo (Pitch & Demo) em `docs/apresentacao/roteiro-demo-pitch.md`.**
   - Roteiro de 2 a 3 minutos guiando a fala do desenvolvedor, a demonstração em tela e a defesa técnica da arquitetura perante a banca avaliadora.

## Etapas

| # | Etapa | Dono | Sai | Depende de |
| --- | --- | --- | --- | --- |
| 1 | Contrato e Endpoint de Relatório Executivo | Lee | `docs/contrato.md` (§2.8), `backend/schemas.py`, `backend/main.py` | Contrato v1.1.0 congelado |
| 2 | Front-end: Botão de Impressão, Estilos de Exportação PDF e Acessibilidade | Sakura | `frontend/src/components/`, `frontend/src/App.tsx`, `frontend/src/styles/global.css` | Etapa 1 |
| 3 | Automação de Inicialização no Windows | Lee/Shikamaru | `run.bat` | Etapas 1 e 2 |
| 4 | README.md de Portfólio e Roteiro de Demonstração | Tsunade/Lee | `README.md`, `docs/apresentacao/roteiro-demo-pitch.md`, atualização de `docs/mapa-do-projeto.md` | Etapas 1, 2 e 3 |
| 5 | Bateria de Testes Automatizados e Build de Produção | Kakashi | `tests/test_report.py`, suíte `pytest`, suíte `vitest`, `vite build` | Etapas 1 a 4 + **Autorização expressa do humano** |

## Portões obrigatórios

- **Parada antes dos testes:** Toda a codificação e documentação (Etapas 1 a 4) é escrita sem disparar suites de testes até que o humano confirme.
- **Isolamento e Grounding:** O relatório executivo não recalcula nenhuma métrica; agrega os dados oficiais já calculados.

## Resultado

- **Status da Entrega:** Aprovada e Aceita com 100% de conformidade.
- **Backend & Relatório Executivo:** Endpoint `GET /api/v1/uploads/{upload_id}/report` implementado, auditado e testado. Retorna indicadores consolidados e resumo formatado em Markdown.
- **Front-end & Exportação:** Modal de visualização de relatório executivo com cópia de Markdown e suporte completo a impressão e geração de PDF (`@media print`) limpa e sem elementos de navegação.
- **Script Windows:** `run.bat` testado para subida do FastAPI e Vite e abertura do navegador com duplo-clique.
- **Portfólio & Apresentação:** `README.md` de nível Staff/Senior com arquitetura anti-alucinação, matriz de regras de negócio, badges e guia de início rápido; `docs/apresentacao/roteiro-demo-pitch.md` estruturado no método STAR para vídeo de 2 a 3 minutos.
- **Bateria de Testes:**
  - **Pytest:** 69 testes aprovados (+ 1 skipped live Ollama) em 2.05s.
  - **Vitest:** 11 testes aprovados em 3.05s.
  - **Vite Build:** Compilação TypeScript e bundle de produção concluídos com sucesso em 705ms.

