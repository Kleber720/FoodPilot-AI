# Modelo de registro de problema

Use este modelo para abrir um registro que exige correção de outra pessoa: um problema entre camadas (`tipo: problema`) ou uma regra que o Kakashi revelou com um teste (`tipo: devolutiva`). Copie o bloco abaixo para `problemas/<autor>-NNNN-<slug>.md`, com o prefixo do autor em minúsculas (`lee`, `sakura`, `kakashi`, `shikamaru`), o próximo número livre do seu prefixo e um slug curto em kebab-case. O arquivo é o registro oficial; o retorno serve apenas para avisar que ele existe.

Preencha `projeto` com o nome do projeto, o mesmo usado em `entregas/`: é por ele que a fila e o relatório separam os times quando houver mais de um.

Preencha as seções até **Hipótese de causa**. **Devolutiva** pertence ao Kakashi, quando o registro nasce de um teste. **Critério de verificação**, **Triagem**, **Correção** e **Verificação final** pertencem a quem tria, quem corrige e quem verifica, nessa ordem.

````markdown
---
id: "<autor>-0001"
projeto: <nome do projeto>
titulo: <sintoma em uma frase>
status: aberto
tipo: <problema | devolutiva>
camada-origem: <frontend | backend | dados>
camada-correcao: <frontend | backend | dados | nao-sei>
autor: <Sakura | Lee | Kakashi | Shikamaru>
delegado-para:
severidade: <critica | alta | media | baixa>
criado-em: AAAA-MM-DD
atualizado-em: AAAA-MM-DD
ponto-de-integracao: <rota, componente, arquivo ou fluxo>
---

## Sintoma

<O que acontece, em uma frase, sem propor solução.>

## Impacto

<Quem é afetado, em qual fluxo e o que deixa de funcionar. Diga se bloqueia a entrega.>

## Passos para reproduzir

1. <passo>
2. <passo>

## Comportamento observado

<O que aconteceu de fato, com dados sintéticos.>

## Comportamento esperado

<O que o consumidor precisa receber ou fazer. Descreva o comportamento, não a implementação da outra camada.>

## Evidência

<Requisição e resposta, trecho de código, mensagem de erro ou descrição da tela. Sem credenciais nem dados sensíveis.>

## Hipótese de causa

<Marque como hipótese e diga o que a sustenta. Se não houver, escreva "não identificada".>

## Critério de verificação

<!-- Preenchido na triagem: a prova objetiva de que o problema foi resolvido. -->

## Triagem

<!-- Preenchido pelo agente de TDD: procede, camada responsável, delegação ou devolução. -->

## Devolutiva

<!-- Preenchido pelo Kakashi quando o registro nasce de um teste: a regra esperada, o teste que falha e o comportamento necessário. É o pedido de correção entregue a quem escreveu o código. -->

## Correção

<!-- Preenchido pelo agente responsável: o que mudou e como ele verificou. -->

## Verificação final

<!-- Preenchido por quem não fez a correção: resultado e data. -->

## Histórico

- AAAA-MM-DD — <autor>: registro aberto.
````
