---
name: investigar-falha-dados
description: Investiga degradação de métrica, drift, viés ou resultado inexplicável de um modelo ou pipeline de dados e verifica a correção no cenário que apresentou a falha.
---

# Investigar falha de dados

1. Registre o sintoma: métrica que caiu, número absurdo, predição fora de faixa ou execução que falhou. Anote quando começou, em qual período ou segmento e qual o impacto.
2. Separe as três causas possíveis antes de mexer em qualquer coisa: o dado mudou (fonte, esquema, volume, drift, sazonalidade), o código mudou (feature, split, hiperparâmetro, versão de biblioteca) ou o ambiente mudou (seed, memória, dependência).
3. Compare a execução atual com a última saudável usando o snapshot registrado: contagem, distribuição, taxa de missing e métrica por segmento.
4. Teste uma hipótese por vez com evidência — consulta, gráfico ou execução controlada. Diferencie causa confirmada de suspeita.
5. Só então corrija o pipeline. Não ajuste o modelo para esconder sintoma de dado: se a causa é a fonte, abra registro para o dono e siga com o que ainda pode ser entregue.
6. Verifique a correção no mesmo cenário que falhou, com a mesma métrica e o mesmo recorte, e confira o que a mudança pode ter afetado.
7. Registre o que aprendeu: o sinal que deveria ter alertado antes e o limiar que faltava monitorar. O [guia de monitoramento](../../design/monitoramento.md) ajuda a definir os sinais e os limiares.

Informe: o sintoma, a causa confirmada, a evidência, a correção e o resultado da verificação. O que não puder ser confirmado fica dito como hipótese.
