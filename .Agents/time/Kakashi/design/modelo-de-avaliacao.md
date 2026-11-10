# Modelo de avaliação

Use este modelo para escrever o cenário que avalia um agente. O cenário é o roteiro de quem avalia: o pedido é enviado uma vez, sem dicas, e os critérios ficam só com quem corrige.

## Preparação

Descreva o projeto de teste, o que já existe nele e o que deve faltar. A ausência é parte do teste quando ela é o comportamento avaliado. Diga o que **não** pode ser contado ao agente.

## Pedido

O texto exato que será enviado, sem critério, dica ou correção embutida. Um pedido, uma vez.

## Critérios de aprovação

Cada critério precisa ser observável no resultado ou no diff, não na intenção declarada:

1. **Nome do critério.** O comportamento esperado e a evidência que o comprova.
2. **Nome do critério (eliminatório).** O que reprova de imediato, mesmo que o resto passe.

Marque como eliminatório o que quebra a razão de existir do agente — para o Kakashi, corrigir a regra que ele deveria devolver.

## Durante a execução

Registre as perguntas prováveis e a resposta neutra que devolve a decisão ao agente. A pergunta é dado de avaliação; a resposta não pode entregar o critério. Não impeça a falha: registre.

## Resultado

Uma linha por critério, com passou, falhou ou sem verificação e a evidência ao lado. Feche com o que o agente fez bem e o que errou fora dos critérios — é isso que orienta o ajuste do `AGENTS.md` e das skills.
