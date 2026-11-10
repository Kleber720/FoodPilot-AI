---
name: entregar-resultados
description: Entrega o resultado da análise ou do modelo — relatório, dataset tratado, predições ou artefato — no formato que o projeto pedir, com números rastreáveis e verificação do que foi devolvido.
---

# Entregar resultados

## Definir a entrega

1. Confirme o pedido: relatório, dataset tratado, features, predições ou artefato do modelo. Entregue o que foi pedido, não o que é mais fácil mostrar.
2. Combine o destino com quem é dono dele. Devolução de dados ao banco ou à API segue o contrato e a autorização do Lee; schema, tabela ou coluna nova é mudança do Lee, com registro — não do seu script.
3. Defina o contrato da entrega: formato, colunas, tipos, chave, granularidade, período e como identificar uma execução. O [guia de relatório e entrega](../../design/relatorio-e-entrega.md) detalha a estrutura, a devolução de dados e o artefato.

## Relatório

4. Estruture: pergunta, dados (fonte e data card), método, resultado com métrica e conjunto de avaliação, análise de erro, limitações e recomendação.
5. Dê origem a cada número: o comando ou o experimento que o produziu. Número que não se reproduz sai do relatório.
6. Faça as figuras com matplotlib: título, eixos com unidade, tamanho de amostra, escala honesta e período. Sem eixo truncado para dramatizar e sem média sem distribuição.
7. Deixe a limitação no relatório, não só no chat: cobertura, período, segmento ausente, viés conhecido e o que não foi medido.

## Devolver dados

8. Escreva no destino combinado com chave de idempotência: reenviar a mesma execução não pode duplicar registro.
9. Nunca sobrescreva a fonte. Se o dado de origem precisa de correção, isso é registro para o dono da fonte.
10. Verifique o que gravou: contagem, soma de uma coluna de controle e uma amostra lida de volta do destino. Gravação sem leitura de conferência é suposição.

## Artefato do modelo

11. Registre formato, versão, entrada e saída esperadas, seed e o comando que reproduz o treino. Modelo servido por outro serviço exige handoff com contrato para o Lee.
12. Antes de encerrar, rode o comando de reprodução em ambiente limpo e confira se o resultado bate com o entregue.

No retorno ao coordenador — ou no chat, quando você for usado direto: o que foi entregue, onde, o comando de reprodução, os números principais, as limitações e as pendências. Se faltar uma verificação essencial, descreva a entrega como parcialmente validada.
