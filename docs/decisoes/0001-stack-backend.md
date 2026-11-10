# ADR 0001 — Adoção de Python 3.12+ (FastAPI + Pydantic + SQLAlchemy 2.x + Alembic + SQLite) no Back-end

**Data** — 2026-11-09  
**Estado** — Aceita  
**Autor** — Lee (Back-end)  
**Autorizado por** — Humano (registrado em [`entregas/0001-fundacao-contrato-e-metricas.md`](../../entregas/0001-fundacao-contrato-e-metricas.md))

### Contexto

O projeto **FoodPilot AI** consiste em uma aplicação 100% local de inteligência operacional e financeira para restaurantes, estruturada em três camadas principais na Entrega 0001:
1. **Camada de API e Persistência (`backend/`):** Recepção de arquivos CSV de pedidos via HTTP, validação, persistência transacional em banco de dados local SQLite e exposição de endpoints REST para consulta de lotes e métricas consolidadas.
2. **Camada de Inteligência Determinística de Dados (`data_pipeline/`):** Processamento em Python + `pandas` para validação de schema e tipos do CSV, cálculo determinístico de faturamento (bruto e líquido), ticket médio, curva ABC de produtos e detecção de desvios/gargalos operacionais — respeitando a invariante estrita de que o LLM local jamais realiza cálculos matemáticos.
3. **Camada de Apresentação (`frontend/` — entregas seguintes):** Dashboard web em React + TypeScript + Vite.

O briefing inicial do produto mencionou `Node.js + Express` como sugestão para a API REST, mantendo `Python + pandas` para o pipeline de dados. Contudo:
- A governança técnica do time em [`.Agents/comum/stacks.md`](../../.Agents/comum/stacks.md) fixa a stack de back-end do Lee em **Python 3.12+ com FastAPI, Pydantic, SQLAlchemy 2.x e Alembic**, com testes unificados em `pytest`.
- No ambiente Windows de execução local (`C:\Users\klebe\OneDrive\Documentos\ChatGPT\FoodPilot AI`), o interpretador `Python 3.14.5` encontra-se instalado e funcional (`C:\Users\klebe\AppData\Local\Programs\Python\Python314\python.exe`), enquanto os binários `node` e `npm` estão ausentes no `PATH`.
- Manter dois runtimes distintos no servidor (`Node.js` para HTTP e `Python` para `pandas`) exigiria comunicação interprocessos (IPC/sub-processos ou serialização intermediária em disco/stdout) a cada upload e cálculo de métricas, adicionando latência, fragilidade de parsing e complexidade operacional sem ganho de negócio.

A decisão foi escalada pela Tsunade ao humano e formalmente autorizada em `2026-11-09`.

### Opções consideradas

1. **Opção A — `Python 3.12+ (3.14.5) + FastAPI + Pydantic + SQLAlchemy 2.x + Alembic + SQLite` (Stack padrão do time):**
   - *Como atende aos requisitos:* Permite invocação direta em memória (in-process) das funções puras do módulo `data_pipeline/` (`pandas`) a partir dos casos de uso do `backend/`, validação rigorosa de contratos JSON via `Pydantic v2`, geração automática de OpenAPI e controle transacional de banco SQLite via `SQLAlchemy 2.x` + migrações versionadas com `Alembic`. Unifica toda a suíte de testes de dados, domínio e API em `pytest`.
   - *Custos e riscos:* Requer alinhamento explícito da assinatura de funções Python entre `backend/` (Lee) e `data_pipeline/` (Shikamaru), mitigado pela seção de Contrato de Interface Interna em `docs/contrato.md`.

2. **Opção B — `Node.js + Express + SQLite` invocando scripts `Python + pandas` via subprocesso:**
   - *Como atende aos requisitos:* Segue literalmente a menção inicial do briefing para a camada HTTP.
   - *Custos e riscos:*
     - Bloqueado no ambiente atual pela ausência de `node` e `npm` no host.
     - Introduz overhead e pontos de falha na ponte `child_process` entre Node.js e Python (tratamento de códigos de saída, encoding no Windows, serialização de erros de validação linha a linha do CSV).
     - Fragmenta a suíte de testes de servidor e de dados em duas ferramentas e dois gerenciadores de pacotes (`npm` e `pip`), violando [`.Agents/comum/stacks.md`](../../.Agents/comum/stacks.md).

### Decisão

Adotar **Python 3.12+ (executando em `Python 3.14.5`) com FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic e SQLite** como stack oficial do `backend/` do FoodPilot AI.

Com esta decisão:
- O módulo `backend/` expõe a API REST (`FastAPI`), gerencia o ciclo de vida transacional do banco SQLite local (`SQLAlchemy 2.x` + `Alembic`) e valida os schemas de entrada e saída (`Pydantic`).
- O módulo `data_pipeline/` (dono: Shikamaru) é importado diretamente como pacote Python nativo pelo `backend/`, recebendo o conteúdo do CSV e devolvendo estruturas tipadas determinísticas sem IPC.
- A suíte de testes em `tests/` (dono: Kakashi) executa integralmente sob `pytest` no mesmo ambiente virtual (`.venv`).

### Consequências e revisão

- **Benefícios esperados:**
  - Execução imediata e 100% verificável no ambiente local usando `Python 3.14.5`.
  - Chamada síncrona e atômica entre recepção do upload HTTP, validação/cálculo em `pandas` e persistência transacional no SQLite.
  - Garantias fortes de contrato entre `data_pipeline/`, `backend/` e `frontend/` via schemas Pydantic.
- **Custos aceitos:**
  - O contrato de integração interna entre `backend/` e `data_pipeline/` deve ser estritamente respeitado para evitar acoplamento indevido a DataFrames internos do `pandas` na camada de persistência.
- **Critérios para revisão futura:**
  - Caso o projeto evolua de aplicação local single-tenant para implantação distribuída de alta concorrência com múltiplos workers assíncronos e banco cliente-servidor, o motor de banco poderá migrar de SQLite para PostgreSQL (mantendo SQLAlchemy 2.x e Alembic) mediante nova decisão arquitetural.
