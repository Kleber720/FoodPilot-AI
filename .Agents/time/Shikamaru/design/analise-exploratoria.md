# Análise exploratória

Explorar não é coleção de gráficos: é o conjunto de perguntas que decide se o dado sustenta o modelo e quais suspeitas precisam morrer antes do treino. Cada figura responde a uma pergunta escrita; cada conclusão cita o recorte e o tamanho da amostra.

## Ordem

1. **Pergunta e decisão.** O que a análise vai decidir e quem usa a resposta.
2. **Alvo.** Distribuição, balanceamento, cauda, período e o que significa cada valor.
3. **Features.** Distribuição, missing, categorias raras, outliers, unidade e cobertura.
4. **Tempo.** Cobertura, sazonalidade, mudança de comportamento no período.
5. **Segmentos.** O comportamento muda por conta, região, canal, produto? Segmento pequeno não sustenta conclusão.
6. **Relações.** Correlação e cruzamento com o alvo, com cautela.
7. **Vazamento.** Antes de qualquer métrica.
8. **Plano de modelagem.** Tipo de problema, unidade de previsão, alvo, horizonte e métrica candidata.

## Vazamento

Vazamento é a falha que faz o modelo parecer ótimo e falhar em produção. Procure antes de celebrar qualquer número.

| Tipo | Como aparece |
| --- | --- |
| Pós-evento | feature registrada depois do alvo, como data de cancelamento para prever cancelamento |
| Identidade | ID, e-mail ou hash que separam treino e teste sem generalizar |
| Duplicata | mesmo registro em treino e teste, ou linha por evento sem deduplicar |
| Agregação com o alvo | média do grupo calculada incluindo a própria linha |
| Seleção | base só com quem já converteu, e o modelo "prevê" conversão |
| Temporal | split aleatório em série temporal, com o futuro no treino |
| Target encoding | alvo da própria linha usado no encoding da categoria |

O teste do "prevê demais": uma feature isolada com AUC acima de 0,95 em problema difícil é suspeita até prova em contrário. Olhe o dicionário, a data de criação da coluna e a consulta que a gerou. Feature que não puder ser justificada pelo momento da previsão sai, mesmo que derrube a métrica.

## Relações e armadilhas

- Correlação não indica causa, e correlação alta entre features esconde redundância.
- Média sem distribuição esconde cauda e bimodalidade.
- Agregação por período esconde mudança de composição: a média caiu porque o mix mudou.
- Segmento com poucas observações produz diferença que parece efeito e é ruído.
- Tendência no tempo pode virar regra espúria: o modelo aprende "época do ano" no lugar do comportamento.

## Figuras

- Título, eixos com unidade, escala honesta e o tamanho da amostra visível.
- Distribuição antes da média; caixa ou violino ao lado do histograma quando a cauda importa.
- Sem eixo truncado para dramatizar e sem gráfico de pizza para comparar muitos grupos.
- Uma figura por pergunta. Se o gráfico precisa de três parágrafos para ser entendido, a pergunta ainda não está clara.

## Hipóteses

Registre as que sobreviveram e as que morreram, com a evidência. Hipótese descartada evita retrabalho na etapa seguinte e documenta por que o plano mudou.

## Limites e plano

Termine dizendo o que o dado não responde por falta de volume, cobertura ou seleção. Se o volume não sustenta o tipo de modelo, diga antes de treinar.

O plano fecha a exploração: classificação, regressão, ranking, agrupamento ou série temporal; unidade de previsão; alvo; horizonte; métrica candidata e critério de aceite provisório. Avance para a [preparação](preparacao-e-vazamento.md) com o vazamento resolvido ou com a lista do que vai sair.
