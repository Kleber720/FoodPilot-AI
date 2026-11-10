# Modelo de plano de entrega

Use este modelo para transformar um pedido em entrega: critério de aceite observável, etapas com dono único, dependências e portões. Copie o bloco para `entregas/NNNN-<slug>.md`, com o próximo número livre e um slug curto em kebab-case. O arquivo é o contrato da entrega; o retorno serve para avisar o que saiu.

O plano é escrito **antes** de qualquer especialista começar. Etapa sem aceite não entra.

````markdown
---
id: "0000"
projeto: <nome do projeto>
titulo: <entrega em uma frase>
estado: <planejada | em-andamento | em-aceite | aceita | parcial | bloqueada>
pedido-origem: <quem pediu e onde>
criado-em: AAAA-MM-DD
atualizado-em: AAAA-MM-DD
---

## Pedido

<O pedido como chegou, em uma frase. Sem tradução para solução.>

## Aceite

<O comportamento observável que prova a entrega pronta. Cada critério precisa de evidência: o que o consumidor faz, o que aparece, o que a API devolve. "Contador na tela bate com o total do banco" é aceite; "implementar contador" não é.>

1. **<critério>.** <evidência que o comprova.>
2. **<critério (eliminatório)>.** <o que reprova de imediato.>

## Etapas

| # | Etapa | Dono | Sai | Depende de |
| --- | --- | --- | --- | --- |
| 1 | <contrato / tela / prova / dado> | <agente> | <artefato entregue> | <etapa ou registro> |

## Portões obrigatórios

<Só os que esta entrega exige, com o motivo. Uma entrega de tela não precisa do isolamento entre contas provado; uma que mexe em autorização precisa.>

## Autorizações

<O que depende de aprovação do humano: execução de migração em produção, mudança de contrato público, corte de escopo, acesso a dado sensível. Registre a data, o que foi autorizado e por quem. Sem esta seção preenchida, a ação não acontece.>

## Fora de escopo

<O que o pedido sugere mas não entra — e que será cobrado se não estiver dito.>

## Decisões

<Link para o registro de decisão quando a escolha for difícil de reverter.>

## Resultado

<!-- Preenchido no fechamento: critério por critério, com passou, falhou ou sem verificação e a evidência ao lado. -->
````

## Exemplo de plano preenchido

````markdown
# Entrega 014 — filtro de tarefas concluídas

Aceite: a listagem filtrada não expõe tarefa de outra conta e a contagem reflete o filtro.
Ordem: contrato (Lee) → congelado → Sakura com mock em paralelo → Kakashi prova → release.
Depende de: 0007 (isolamento entre contas) — não começa antes.
Portões obrigatórios desta entrega: isolamento entre contas.
Fora de escopo: paginação.
````
