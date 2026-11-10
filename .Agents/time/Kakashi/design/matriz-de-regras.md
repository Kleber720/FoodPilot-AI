# Matriz de regras

Use este modelo no projeto em que os testes estão sendo escritos. Crie `docs/matriz-de-regras.md` e mantenha uma linha por regra de negócio entregue. É o artefato que responde "o que ainda não está testado" sem obrigar a ler a suíte inteira.

## Como preencher

- **Regra** — o comportamento em uma frase, com o termo do negócio. "Tarefa de outra conta não aparece na listagem."
- **Fonte** — onde a regra está escrita: contrato, guia de domínio (`docs/dominio/`), decisão registrada ou pedido que originou a entrega. Regra sem fonte é suposição: confirme antes de testar.
- **Teste** — caminho e nome do teste que a protege. Vazio significa lacuna.
- **Nível** — unidade, integração, contrato ou ponta a ponta.
- **Situações** — marque o que já existe: válido, inválido, limite, acesso, repetição, persistência.
- **Lacuna** — o que falta e por quê, quando for o caso.

## Tabela

| Regra | Fonte | Teste | Nível | Válido | Inválido | Limite | Acesso | Repetição | Persistência | Lacuna |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tarefa de outra conta não aparece na listagem | contrato, listagem | `tests/listagem.test.ts` | integração | sim | — | sim | sim | — | sim | — |
| Tarefa sem título é rejeitada | contrato, criação | `tests/criacao.test.ts` | unidade | sim | sim | sim | — | — | — | falta caso de acesso negado |

## Manutenção

Atualize a matriz na mesma entrega que criou ou alterou o teste. Regra nova sem linha é regra que ninguém sabe que existe. Regra removida sai da matriz, com a remoção registrada no histórico do projeto.

Revise as lacunas por risco, não por ordem alfabética: acesso a dado de outra conta, dinheiro, perda de dado e fluxo que trava a entrega vêm primeiro. Cobertura de linha alta não compensa uma regra de acesso sem teste.
