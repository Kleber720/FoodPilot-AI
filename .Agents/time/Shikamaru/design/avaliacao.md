# Avaliação

Avaliar é decidir, não colecionar métrica. A pergunta não é "quanto deu", é "esse número sustenta a entrega para o uso pretendido, com o custo de erro que o negócio aceita". Por isso a métrica e o critério de aceite são escolhidos antes de ver o resultado.

## Métrica pelo custo do erro

| Problema | Métrica principal | Cuidado |
| --- | --- | --- |
| Classificação binária | precision, recall ou F1 conforme o custo; PR-AUC em desbalanceado | acurácia engana com classe rara; ROC-AUC fica otimista |
| Classificação multiclasse | macro-F1 ou matriz de confusão | micro-F1 é dominado pela classe frequente |
| Regressão | MAE ou RMSE conforme a penalidade | MAPE explode perto de zero; RMSE pune o outlier |
| Ranking | NDCG, MAP@k ou precision@k | métrica alinhada ao que o consumidor vê |
| Série temporal | erro por horizonte, em backtest temporal | erro médio esconde o horizonte que importa |
| Agrupamento | silhouette com critério de negócio | métrica interna não prova utilidade |

Em alvo desbalanceado, escolha o limiar pelo custo: falso negativo e falso positivo raramente custam o mesmo. Relate precision e recall no limiar escolhido, não só a curva.

Quando a decisão usa probabilidade, avalie calibração — curva de confiabilidade e Brier. Probabilidade descalibrada decide mal mesmo com AUC alta.

## Validação

- O teste é usado uma vez. Reutilizou, precisa de novo split ou de validação cruzada para a nova decisão.
- Compare com a linha de base no mesmo conjunto e com a mesma métrica.
- Estime a variação: bootstrap, múltiplas seeds ou desvio entre folds. Diferença menor que a variação é ruído, não melhora.
- Em uso temporal, valide no futuro e reporte o desempenho por período, não só a média.

## Análise de erro

O número agregado esconde onde o modelo erra. Sempre olhe:

- **Matriz de confusão.** Qual erro domina e quanto ele custa.
- **Segmentos.** O erro se concentra em conta, região, canal, faixa de valor?
- **Piores casos.** Quais registros erram mais e o que têm em comum.
- **Custo assimétrico.** Errar para um lado pode ser aceitável; para o outro, não.

Erro concentrado em um segmento é restrição de escopo, não detalhe do relatório.

## Viés

Quando o dado envolve pessoas, compare a taxa de erro entre grupos e a representação de cada grupo no treino. Registre o resultado mesmo quando desfavorável. Variável proxy — CEP, escola, dispositivo — pode reproduzir discriminação sem que o grupo apareça explicitamente. Não remova a variável e declare resolvido: meça o efeito da remoção.

## Estabilidade

- **Tempo.** O desempenho se mantém no período seguinte ao treino?
- **Seed.** O resultado varia muito entre seeds? Modelo que só funciona em uma seed não está pronto.
- **Hiperparâmetro.** Pequena mudança derruba a métrica? Sinal de ajuste frágil.
- **Fora da distribuição.** Segmento novo ou período atípico quebra o modelo?

## Critério de aceite e veredito

Escreva com o projeto, antes do resultado: métrica mínima, limite de erro aceitável, restrição de escopo, volume mínimo. Sem critério, "bom" é opinião de quem olha o gráfico.

Depois, um veredito explícito:

- **Entrega** — atende ao critério no conjunto declarado.
- **Entrega com restrição** — diga qual: limiar mais conservador, segmento coberto, volume mínimo.
- **Não entrega** — motivo, o que faltou e o próximo passo.

A entrega segue para o [relatório e a devolução](relatorio-e-entrega.md).
