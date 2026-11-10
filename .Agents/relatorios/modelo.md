# Modelo de relatório do dia

O relatório é tirado dos arquivos — frontmatter dos registros em `problemas/`, planos em `entregas/`, resultados de verificação —, não da memória. O que não está no arquivo não vira linha. Salve em `relatorios/AAAA-MM-DD.md`.

````markdown
# Relatório — AAAA-MM-DD

## O que saiu

<Uma linha por entrega aceita: o critério que provou e a evidência.>

| Entrega | Critério que provou | Evidência |
| --- | --- | --- |
| <NNNN> | <critério> | <comando, arquivo ou registro> |

## Fila

<Abertos por estado e severidade.>

| Estado | critica | alta | media | baixa |
| --- | --- | --- | --- | --- |
| aberto | | | | |
| em-triagem | | | | |
| delegado | | | | |
| corrigido | | | | |

<Parados sem movimento: número, dono, dias.>

## O que travou

<Bloqueio, dono e o que destrava. Bloqueio sem dono é o item mais caro do dia.>

## Decisões do dia

<Uma linha cada, com link para o registro de decisão.>

## Precisa de decisão humana

<Escopo, contrato público, risco aceito — com a opção recomendada.>

## Ordem de amanhã

<A primeira entrega, o que ela depende e quem começa. Não é lista de desejos.>
````
