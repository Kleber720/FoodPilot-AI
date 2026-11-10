# Preparação e vazamento

A preparação decide metade do resultado. Um modelo simples sobre dados bem separados vence um modelo sofisticado sobre dados vazados. A regra que organiza tudo: o split vem antes de qualquer ajuste, e o teste não é tocado até a avaliação.

## Split

| Estratégia | Use quando | Armadilha |
| --- | --- | --- |
| Aleatório | observações independentes, sem tempo nem entidade repetida | entidade repetida cai nos dois lados |
| Temporal | o uso é prever o futuro | embaralhar o tempo e treinar com o futuro |
| Por grupo | mesma entidade em várias linhas (cliente, loja, equipamento) | vazar o grupo entre treino e teste |
| Estratificado | classe rara | proporção diferente entre os conjuntos |
| Por período de safra | mudança de política ou de produto no meio | comparar períodos incompatíveis |

Regras:

- Separe treino, validação e teste. A validação escolhe hiperparâmetro; o teste decide.
- Congele os conjuntos em arquivo de IDs ou função versionada com seed. Split que muda a cada execução invalida a comparação entre experimentos.
- Nunca refaça o split depois de olhar o teste. Se precisou, o teste deixou de ser teste.
- Com pouco dado, troque o holdout por validação cruzada, mas preserve a separação por grupo ou por tempo dentro dos folds.

## Transformações

- **Missing.** Entenda por que falta antes de imputar: falha de coleta, não aplicável ou valor omitido. Imputação carrega hipótese; registre qual. Indicador de missing costuma valer mais que a média imputada.
- **Outlier.** Decida entre manter, capar e remover, com justificativa. Remover outlier do teste é trapaça; remover do treino precisa de regra definida antes de ver o resultado.
- **Categórica.** One-hot para cardinalidade baixa; target encoding com validação cruzada interna e suavização para cardinalidade alta. Categoria rara pode virar "outros" — diga quantas caíram ali.
- **Escala.** Ajuste média, desvio, mínimo e máximo somente no treino. Regressão logística e redes neurais costumam precisar; árvores, não.
- **Seleção de feature.** Faça dentro do fold de treino. Selecionar com o conjunto inteiro antes do split é vazamento silencioso.

## Vazamento

Nenhuma feature pode depender de informação posterior ao momento da previsão. Verifique a lista da [exploração](analise-exploratoria.md) uma a uma: o que não puder ser provado, sai. O que sobrar de dúvida vira teste controlado — remova a feature e compare; se a métrica despenca, havia vazamento.

Target encoding é o caso mais comum de vazamento em dado tabular: calcular a média do alvo por categoria usando a linha que está sendo codificada transfere o alvo para a feature. Use folds internos e suavização, e confira que o encoding do teste foi calculado com o treino.

## Pipeline

- Script ou módulo executável do bruto ao dataset de treino, com um comando.
- Seed, ordem determinística e versões registradas.
- Saídas nomeadas e versionadas; nada de resultado sobrescrito sem rastro.
- Notebook serve para explorar, não para entregar. O que precisa rodar de novo vira script.

## Linhagem e sanidade

Registre no data card a cadeia bruto → tratado → features e o comando que gera cada etapa. Rode o pipeline do zero e compare com a execução anterior: contagem, distribuição, taxa de missing e lista de features. Confirme que o teste continua intocado.

Se o defeito da fonte impedir a preparação — coluna ausente, período faltando, chave duplicada sem explicação —, abra registro para o dono da fonte em vez de compensar no pipeline.
