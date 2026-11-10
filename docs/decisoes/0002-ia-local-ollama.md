# ADR 0002 — Integração do Agente de IA Local (Ollama `qwen3:4b-instruct`), Aterramento por Ficha de Fatos, Fallback Determinístico e Persistência em SQLite

**Data** — 2026-11-09  
**Estado** — Aceita  
**Autor** — Lee (Back-end)  
**Autorizado por** — Humano (registrado em [`entregas/0003-agente-ia-local-e-recomendacoes.md`](../../entregas/0003-agente-ia-local-e-recomendacoes.md))

### Contexto

Na **Entrega 0003**, o **FoodPilot AI** passa a oferecer ao operador do restaurante **3 recomendações práticas de melhoria operacional e financeira** geradas a partir dos indicadores determinísticos já calculados pelo módulo `data_pipeline/` (`RN-03` a `RN-06`).

Quatro restrições arquiteturais e de produto pesam sobre o desenho desta camada:
1. **Invariante eliminatória de não-alucinação financeira (`RN-08`):** O modelo generativo local (`qwen3:4b-instruct` via Ollama) jamais pode calcular faturamento, ticket médio, percentuais da Curva ABC ou taxas de cancelamento por conta própria, nem inventar números no texto das recomendações.
2. **Operação 100% local e resiliência offline (`RN-09`):** A aplicação roda na máquina do usuário sem dependência de APIs pagas em nuvem. Como o servidor Ollama (`http://localhost:11434`) pode estar desligado, sem o modelo baixado ou sofrer latência de carga inicial (*cold start* em GPU local), a aplicação não pode falhar com erro `5xx` nem deixar o Dashboard sem diagnóstico.
3. **Testabilidade determinística em ambiente isolado (sandbox Windows):** A suíte automatizada (`pytest` e `vitest`) precisa provar todas as regras de aterramento, retry, fallback e persistência sem depender de rede externa ou do processo Ollama rodando em segundo plano, reservando o teste contra o servidor real para um portão explícito (`@pytest.mark.ollama_live`).
4. **Rastreabilidade e reaproveitamento (Entrega 0004):** As recomendações geradas para um lote (`upload_id`) precisam ser armazenadas com metadados de auditoria (`source`, `model`, `prompt_version`, `warnings`) para consulta imediata ao reabrir o lote e para futura exportação de relatórios executivos.

As decisões de produto correspondentes foram escaladas pela Tsunade e formalmente autorizadas pelo humano em `2026-11-09`.

### Opções consideradas

1. **Opção A — Arquitetura Aterrada em Ficha de Fatos (`Fact Sheet`) + `OllamaClient` Síncrono (`httpx`) + Validador de Aterramento com 1 Retry + Fallback Determinístico + Persistência SQLite (`recommendation_runs`):**
   - *Como atende aos requisitos:*
     - `data_pipeline/insights.py` (Shikamaru) transforma o dicionário de `calculate_metrics` em uma lista pura de fatos atômicos (`build_fact_sheet`), onde cada número possui um `fact_id` estável (ex.: `fin.net_revenue`, `chan.delivery.cancellation_rate_pct`, `thr.prep_time_minutes`).
     - `backend/ai/` (Lee) define um protocolo `LLMClient` e a implementação `OllamaClient` usando `httpx` (chamada síncrona `POST /api/chat` com `stream=False`, `format` contendo o JSON Schema estrito, `temperature=0.0`, `seed=42` e timeout configurável padrão de `90.0s`).
     - `validate_recommendations` (`backend/ai/grounding.py`) audita a saída do LLM exigindo exatamente 3 recomendações (`rank` 1, 2, 3), validando a existência de cada `fact_id` citado em `evidence[]`, extraindo todos os números presentes nos campos textuais (`title`, `diagnosis`, `action`, `expected_impact`) e exigindo correspondência com valores da ficha de fatos (tolerância `±0.01`), além de sobrescrever `evidence[].value`, `label` e `unit` pelos valores oficiais do fato.
     - Se a 1ª resposta do LLM falhar na validação, o serviço realiza **1 nova tentativa** injetando a lista de erros no prompt. Se falhar novamente ou se o Ollama estiver inacessível/timeout (`LLMUnavailableError`), o serviço aciona `build_fallback_recommendations` (`source = "deterministic_fallback"`), registrando o motivo em `warnings[]` e respondendo `201 Created`.
     - O resultado é gravado na tabela `recommendation_runs` no SQLite (migração Alembic `0002_recommendations.py`).
   - *Custos e riscos:* Exige regex e normalização cuidadosa de números pt-BR/US no validador de aterramento e inclusão dos limiares (`30` min e `10%`) como fatos explícitos na ficha para não gerar falsos positivos.

2. **Opção B — Envio do JSON bruto de métricas ao Ollama sem validador de números no texto e retorno `503 Service Unavailable` quando offline:**
   - *Como atende aos requisitos:* Implementação mais curta na camada de back-end.
   - *Custos e riscos:* Modelos pequenos (`4B`) frequentemente arredondam ou recalculam somas de cabeça no texto livre, violando a invariante anti-alucinação; além disso, retornar `503` quando o Ollama não está ativo inutiliza a experiência da funcionalidade em máquinas sem o serviço iniciado.

3. **Opção C — Processamento assíncrono via fila de jobs (polling/WebSocket) e interface de chat aberto:**
   - *Como atende aos requisitos:* Evita conexões HTTP longas durante o *cold start* do modelo.
   - *Custos e riscos:* Adiciona complexidade desnecessária para um MVP local *single-user* e dificulta o aterramento determinístico em perguntas abertas fora do escopo autorizado.

### Decisão

Adotar a **Opção A**, estruturada nos seguintes pilares técnicos:

1. **Cliente HTTP e Configuração (`backend/config.py` e `backend/ai/llm_client.py`):**
   - Mover `httpx` para as dependências de runtime do projeto (`requirements.txt` e `pyproject.toml`).
   - Variáveis de ambiente com padrões seguros:
     - `OLLAMA_BASE_URL` = `"http://localhost:11434"`
     - `OLLAMA_MODEL` = `"qwen3:4b-instruct"`
     - `OLLAMA_TIMEOUT_SECONDS` = `90.0`
     - `OLLAMA_SEED` = `42`
   - Interface `LLMClient` (`typing.Protocol`) injetável via `Depends(get_llm_client)` no FastAPI, permitindo substituição limpa por `FakeLLMClient` nos testes automatizados.
2. **Contrato de Ficha de Fatos e Fallback (`data_pipeline/insights.py`):**
   - `build_fact_sheet(metrics)` gera todos os fatos verificáveis do lote, incluindo os fatos de limiar (`thr.prep_time_minutes = 30.0`, `thr.cancellation_rate_pct = 10.0`).
   - `build_fallback_recommendations(metrics, facts)` produz deterministicamente 3 recomendações ranqueadas usando apenas os fatos do lote.
3. **Validação de Aterramento, Retry Único e Degradação Graciosa (`backend/ai/grounding.py` e `backend/ai/service.py`):**
   - Versão de prompt congelada em `PROMPT_VERSION = "rec-v1"`.
   - Máximo de 2 tentativas contra o LLM (1 chamada inicial + 1 retry corretivo se `validate_recommendations` apontar violação).
   - Em caso de indisponibilidade (`LLMUnavailableError`) ou falha após a 2ª tentativa, retorno imediato do fallback determinístico com `source = "deterministic_fallback"`, `model = None` e explicação em `warnings[]`.
4. **Persistência Transacional (`backend/models.py` e `0002_recommendations.py`):**
   - Tabela `recommendation_runs` vinculada a `uploads.upload_id` (`ON DELETE CASCADE`), armazenando `run_id`, `upload_id`, `generated_at`, `source`, `model`, `prompt_version`, `warnings_json` e `recommendations_json`.

### Consequências e revisão

- **Benefícios esperados:**
  - Garantia matemática de que nenhum número alucinado pelo LLM chega ao Dashboard (`RN-08`).
  - Disponibilidade de 100% no endpoint `POST /api/v1/uploads/{upload_id}/recommendations` mesmo sem Ollama instalado, com total transparência na UI sobre a fonte (`llm` vs. `deterministic_fallback`).
  - Execução ultrarrápida da suíte de testes padrão via injeção de dependência (`get_llm_client`), isolando o teste real em `@pytest.mark.ollama_live`.
- **Custos aceitos:**
  - A chamada HTTP `POST /api/v1/uploads/{upload_id}/recommendations` pode aguardar até `90s` quando o Ollama está carregando o modelo na VRAM pela primeira vez (mitigado na UI por estado `aria-busy` e aviso explícito).
- **Critérios para revisão futura:**
  - Caso uma entrega futura adicione múltiplos usuários simultâneos ou chat interativo multi-turno, a execução síncrona poderá ser migrada para streaming SSE ou fila de tarefas mantendo o mesmo `RecommendationService` e `grounding.py`.
