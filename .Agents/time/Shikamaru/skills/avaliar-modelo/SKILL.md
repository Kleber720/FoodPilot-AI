---
name: avaliar-modelo
description: Mede o modelo contra a linha de base e contra o critério do projeto, com holdout, análise de erro e limitações explícitas, e decide se ele pode ser entregue.
---

# Avaliar modelo

1. Escolha a métrica pelo custo do erro, antes de ver o resultado. Em alvo desbalanceado, acurácia engana: use precision, recall, F1, PR-AUC ou ROC-AUC conforme a decisão. Em regressão, MAE ou RMSE conforme a penalidade que o negócio aceita. Quando a decisão usa probabilidade, avalie calibração. O [guia de avaliação](../../design/avaliacao.md) detalha a métrica por tipo de problema, a análise de erro e o critério de aceite.
2. Use o teste uma vez. Se precisou mexer no modelo depois, refaça o split ou use validação cruzada; o teste que já foi visto deixou de ser teste.
3. Compare com a linha de base no mesmo conjunto e considere a variação esperada — bootstrap, múltiplas seeds ou validação cruzada. Diferença dentro da variação não é melhora.
4. Analise o erro: matriz de confusão, erro por segmento e piores casos. Onde o erro se concentra? Quem é prejudicado quando ele erra?
5. Verifique estabilidade: validação temporal, sensibilidade a seed e a hiperparâmetro, comportamento em período ou segmento fora do treino.
6. Se o dado envolve pessoas, avalie a disparidade dos erros entre grupos e registre o resultado mesmo quando desfavorável.
7. Combine com o projeto o critério de aceite antes do veredito: métrica mínima, limite de erro aceitável, restrição de escopo. Sem critério, "bom" é opinião.
8. Dê o veredito explícito: entrega; entrega com restrição, dizendo qual (limiar, segmento, volume mínimo); ou não entrega, com o motivo e o próximo passo.

Informe: a métrica no teste, a comparação com a base, a análise de erro, as limitações e o veredito. O número informado é o que o código produziu — sem arredondar para cima nem escolher o resultado mais favorável.
