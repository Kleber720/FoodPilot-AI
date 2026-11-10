# Stack do time

A stack é fixa. Agente com stack livre produz código genérico: cada entrega escolhe uma biblioteca, cada projeto ganha um jeito, e o time perde o reaproveitamento, o comando previsível e a comparação entre entregas. A escolha de stack não é do especialista — é do time.

## Back-end — Lee

- **Linguagem:** Python 3.12+.
- **API:** FastAPI com Pydantic.
- **Persistência:** SQLAlchemy 2.x; migração com Alembic.
- **Teste:** pytest, na mesma suíte que o Kakashi roda.

## Front-end — Sakura

- **Stack:** React com TypeScript, build por Vite.
- **Estilo:** CSS com tokens do projeto; framework de UI novo exige decisão registrada.
- **Teste:** Vitest com Testing Library.

## Dados — Shikamaru

- **Base:** Python com pandas, numpy e matplotlib.
- **Sob demanda:** scikit-learn, polars, statsmodels, XGBoost e LightGBM entram quando o projeto pedir; a escolha vira registro de decisão.

## Banco de dados

- **O banco é o do projeto:** PostgreSQL, MySQL ou SQLite.
- As sintaxes são próximas, e a modelagem, o contrato e as regras não mudam com o motor. O dialeto e a ferramenta de migração seguem o que o projeto usa.
- Escreva SQL portável e isole a diferença de dialeto no adaptador, não na regra.
- Trocar de motor é decisão de produto, não de implementação.

## Regras

- **A stack do projeto vence este documento.** Se o projeto já tem stack própria, siga a dele e registre a exceção — nunca em silêncio.
- **Projeto sem stack definida começa neste padrão**, e a adoção vira registro de decisão no formato de `design/decisoes/modelo.md` de quem adotou.
- **Nenhum agente troca framework, biblioteca de teste ou banco por preferência.** Trocar é decisão de produto: a Tsunade escala ao humano.
- **Teste roda no comando que o projeto declara**, e esse comando entra no README pela Tsunade.

## Dependências e arquivos compartilhados

- **Dependência de back** (`pyproject.toml`, `requirements.txt`) é do Lee; **de front** (`package.json`, lockfile) é da Sakura. A stack separada elimina a disputa pelo mesmo arquivo.
- **Lockfile não se edita à mão:** quem precisa da dependência roda o instalador e commita o lockfile inteiro. Conflito resolve com reinstalação, não com escolha de linha.
- **Arquivo de infraestrutura** — `docker-compose`, `Dockerfile`, CI, `.env.example` — tem **um dono por entrega**, definido no plano. Quem precisa de mudança pede a quem está com a vez; se as duas camadas precisarem, a Tsunade serializa as etapas.
- **`.env.example` recebe a variável com valor fictício**; segredo nunca entra no repositório, e o valor real fica no ambiente de quem roda.
- **Conflito no mesmo arquivo, na mesma entrega**, é sintoma de plano mal recortado, não de azar: volta para a Tsunade antes de virar merge.
