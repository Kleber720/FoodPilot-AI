---
name: explorar-dados
description: Analisa distribuição, missing, relações, segmentos e riscos de vazamento de um conjunto de dados para decidir o que dá para modelar e o que precisa voltar para quem forneceu.
---

# Explorar dados

1. Escreva antes a pergunta que a análise responde e a decisão que ela apoia. Figura sem pergunta é decoração. O [guia de análise exploratória](../../design/analise-exploratoria.md) detalha a ordem, as armadilhas e a caça a vazamento.
2. Confirme o snapshot no data card e use sempre o mesmo recorte. Explorar um recorte e treinar em outro invalida o que foi aprendido.
3. Descreva o alvo primeiro: distribuição, balanceamento, cauda, período. Sem entender o alvo, a análise das features vira passeio.
4. Descreva as features: distribuição, missing, categorias raras, outliers e, quando houver tempo, cobertura e sazonalidade.
5. Procure relações: correlação e cruzamento com o alvo, com cautela. Correlação não indica causa, e categoria presente em um único período engana.
6. Caçe vazamento antes de qualquer modelagem: coluna gerada depois do evento, identificador que separa treino e teste, duplicata entre registros e agregação que inclui o próprio alvo. Se a feature sozinha "prevê" demais, é vazamento até prova em contrário.
7. Compare segmentos — conta, região, período, canal. Segmento pequeno demais não sustenta conclusão; diga o tamanho ao lado de cada diferença.
8. Registre as hipóteses que sobreviveram e as que morreram. Hipótese descartada também é resultado e evita retrabalho.
9. Diga o limite: o que o dado não responde por falta de volume, cobertura ou seleção.
10. Faça as figuras com matplotlib: título, eixos com unidade, tamanho de amostra e escala honesta.
11. Feche com o plano de modelagem: tipo de problema (classificação, regressão, ranking, agrupamento, série temporal), unidade de previsão, alvo e métrica candidata. Se o dado não sustentar o plano, devolva antes de treinar.

Informe: o que o dado permite, o que não permite, as suspeitas de vazamento e o plano proposto. Não avance para treino com vazamento em aberto — corrija na preparação ou devolva.
