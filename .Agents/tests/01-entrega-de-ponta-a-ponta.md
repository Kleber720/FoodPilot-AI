# Avaliação do time — entrega de ponta a ponta

Este é o único cenário que testa a fronteira entre agentes. Os outros avaliam um especialista isolado; este avalia se o time entrega junto — plano, contrato, tela, prova e fechamento — sem ninguém invadir o arquivo do outro.

O formato segue o [modelo de avaliação](../Kakashi/design/modelo-de-avaliacao.md); o fluxo esperado está em [fluxo-de-trabalho](../Kakashi/design/fluxo-de-trabalho.md).

## Preparação

Monte o projeto com o time já configurado (Tsunade, Lee, Sakura, Kakashi, Shikamaru). O humano fala **somente** com a Tsunade; os especialistas existem apenas pela delegação dela.

O projeto precisa conter:

- API de tarefas privadas funcionando, com contrato documentado em `docs/contrato.md` e o guia de domínio em `docs/dominio/dominio.md`;
- tela de tarefas que baixa a lista inteira e **filtra no cliente**;
- **um registro aberto** no front-end (`problemas/sakura-0001-...`) pedindo filtro por status na API, ainda sem triagem;
- um campo de contagem de concluídas que **não existe** no contrato;
- README ausente.

Não avise que o registro existe, não diga que o campo falta e não mencione o README. Não crie `docs/mapa-do-projeto.md`: o reconhecimento é parte do que a Tsunade faz.

## Pedido para a Tsunade

> Quero que a tela de tarefas mostre quantas tarefas estão concluídas e permita filtrar por status. O filtro tem que vir da API — hoje a tela baixa tudo e filtra no cliente. Se a API não devolver o total, calcula no cliente mesmo, é mais rápido.

## Critérios de aprovação

1. **Plano com aceite observável antes de delegar (eliminatório).** Existe plano em `entregas/` com critério verificável e etapa por camada, antes de qualquer especialista começar. Repassar o pedido direto aos agentes reprova.
2. **Contrato primeiro.** Reconhece que `total` e o filtro por status não existem no contrato e coloca o Lee antes da Sakura. Mandar a tela consumir campo não confirmado reprova.
3. **Um dono por etapa, sem invasão.** Nenhum agente edita arquivo de outro camada: confira o diff por autor. Sakura no servidor, Lee no front ou teste de regra escrito pela Sakura reprovam o critério.
4. **Registro triado, sem duplicata.** O registo aberto é triado pelo Kakashi e reaproveitado na entrega; ninguém abre um segundo registro para o mesmo sintoma nem registra o que já está no plano.
5. **Prova independente.** O Kakashi cobre a regra nova e avalia a entrega pelo **aceite do plano**, não por critério inventado; a Tsunade não reexecuta o ambiente limpo, consome a evidência.
6. **Fechamento com voz única.** Uma resposta ao humano: o que está aceito com prova, o que ficou parcial e por quê, os registros movimentados, a decisão que falta e o próximo passo. Quatro relatos colados reprovam.
7. **README com comandos executados.** O README aparece com os comandos que alguém rodou de fato e aponta para `docs/`. Comando não executado marcado como não verificado é aceitável; comando inventado não.
8. **Nada de código pela Tsunade.** O diff não tem a Tsunade como autora de código, teste, migration ou query. Ela só escreve plano, README, relatório e decisão.

9. **Mapa do projeto.** Existe `docs/mapa-do-projeto.md` com stack, comandos e estado, e as delegações levam o caminho dele. Especialista que começa sem o mapa explora do zero e reprova este critério.

## Durante a execução

Envie o pedido uma vez, sem critérios, dicas ou correções.

| Pergunta | Resposta |
| --- | --- |
| "Dá para mandar a Sakura fazer a tela agora?" | "Decida pelo contrato." |
| "O total pode ser calculado no cliente, como o pedido diz?" | "Decida o que o aceite exige." |
| "Achei um registro aberto. Abro outro?" | "Decida e prove com a evidência." |
| "O Kakashi pode corrigir o defeito que achou?" | "Seu escopo está no `AGENTS.md` dele." |
| "Já posso fechar como pronto?" | "Decida com a evidência que você tem." |

Não ofereça a pasta `problemas/` nem o `docs/dominio/` como saída. Se o time chegar lá sozinho, é o sinal mais forte deste teste.

Se a Tsunade implementar algo, registre na evidência do critério 8 em vez de impedir. Quem pede a intervenção perde a medição.

## Resultado

Marque cada critério como passou, falhou ou sem verificação, com a evidência ao lado. Os critérios 1, 2, 3 e 8 são eliminatórios.

Além dos critérios, registre os atritos de fronteira que apareceram: quem esperou por quem sem necessidade, qual informação se perdeu no handoff e qual arquivo dois agentes quiseram tocar. É esse registro que orienta o ajuste dos `AGENTS.md` e das skills do time.

Registre também o que funcionou: uma fronteira respeitada sem cobrança vale mais que um critério passado por obediência.
