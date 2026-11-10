---
name: planejar-entrega
description: Transforma um pedido em plano de entrega com critério de aceite observável, etapas com dono único, dependências e portões, antes de qualquer especialista começar.
---

# Planejar uma entrega

O plano segue o [modelo de entrega](../../../entregas/modelo.md). Ele é o contrato entre você e o time: o que será aceito, em que ordem e com o que.

1. **Leia o pedido e o projeto.** Comece pelo [mapa do projeto](../../design/mapa-do-projeto.md) em `docs/mapa-do-projeto.md`; se ele não existir, faça o reconhecimento pela skill [`receber-projeto`](../receber-projeto/SKILL.md) antes de planejar. Contrato documentado, guia de domínio, registros abertos em `problemas/` e decisões registradas. Pedido que repete trabalho existente ou registro aberto volta com a referência, não com uma tarefa nova.
2. **Escreva o aceite em comportamento observável.** O que o consumidor faz quando está pronto e qual evidência prova. "Contador na tela bate com o total do banco" é aceite; "implementar contador" não é.
3. **Decomponha por camada, com dono único por etapa.** Backend para o Lee, tela para a Sakura, prova para o Kakashi, dado para o Shikamaru. Etapa sem dono não entra; etapa com dois donos é dividida.
4. **Marque as dependências.** Contrato que muda vem antes da tela e do dado. O que é independente roda em paralelo — declare o que é mock e o que é real, para ninguém esperar o que não vai chegar.
5. **Escolha os portões obrigatórios desta entrega.** Só os que ela exige: uma entrega de tela não precisa do isolamento entre contas provado; uma que mexe em autorização precisa. Diga qual portão e por quê.
6. **Diga o fora de escopo.** O que o pedido sugere mas não entra, para não ser cobrado depois.
7. **Salve o plano e delegue com o recorte.** Cada especialista recebe o aceite da sua etapa, a dependência, o que não é dele, o caminho do mapa do projeto e os arquivos que precisa ler. O plano inteiro fica no arquivo; o pedido cru não é repassado.
8. **Não delegue antes do aceite existir.** Sem critério, cada um define "pronto" do seu jeito e o aceite vira negociação no fim.

## Limites

- Pedido grande demais vira duas entregas, não uma entrega grande.
- Decisão de produto que aparecer no plano — mudar contrato público, cortar escopo — volta para o humano antes de virar etapa, e a autorização fica registrada em **Autorizações**, com data e escopo. Execução de migração em produção segue a mesma regra: sem autorização escrita, não executa.
- Você planeja o que será verificado; não planeja como o especialista implementa.
