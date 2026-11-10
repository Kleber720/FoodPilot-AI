# Relatório e entrega

A entrega é um artefato, não uma mensagem no chat. Ela precisa sobreviver sem você: outra pessoa lê o relatório, reproduz o número, encontra os dados devolvidos e entende o que o modelo faz e não faz.

## Relatório

Estrutura mínima:

1. **Pergunta** — o que foi pedido e qual decisão a entrega apoia.
2. **Dados** — fonte, recorte, período e caminho do data card.
3. **Método** — pipeline, features, modelo e validação, em nível suficiente para reproduzir.
4. **Resultado** — métrica, conjunto de avaliação, tamanho da amostra e comparação com a linha de base.
5. **Erro** — onde o modelo erra e o que isso custa.
6. **Limitações** — cobertura, período, segmento ausente, viés conhecido, o que não foi medido.
7. **Recomendação** — entrega, restrição ou próximo passo.

Cada número tem origem: o comando ou o experimento que o produziu. Número que não se reproduz sai do relatório.

## Figuras

- Título, eixos com unidade, escala honesta, período e tamanho da amostra.
- Sem eixo truncado para dramatizar, sem pizza para comparar muitos grupos.
- Distribuição antes da média; incerteza quando a conclusão depende de diferença pequena.
- Uma figura por pergunta, não uma figura por variável.

## Devolver dados

Devolver dado ao banco ou à API é operação de escrita: tem contrato, dono e verificação.

- Combine o destino com o Lee, que responde pelo banco e pela API. Use o contrato existente; schema, tabela ou coluna nova é mudança do Lee, com registro e decisão — não do seu script.
- Defina formato, colunas, tipos, chave, granularidade e período da entrega.
- Use chave de idempotência por execução: reenviar a mesma entrega não pode duplicar registro.
- Nunca sobrescreva a fonte. Correção de origem é registro para o dono.
- Verifique o que gravou: contagem, soma de uma coluna de controle e uma amostra lida de volta do destino. Gravação sem leitura de conferência é suposição.
- Registre no relatório o que foi gravado, onde e com qual identificador de execução.

## Artefato do modelo

- Formato e versão (pickle, joblib, ONNX ou equivalente), com o comando que reproduz o treino.
- Entrada e saída esperadas: colunas, tipos, ordem e faixa de valores.
- Seed e versões das bibliotecas.
- Modelo servido por outro serviço é handoff com contrato para o Lee: ele implementa a API, você entrega o artefato e o comportamento esperado.

## Verificação final

- Rode o comando de reprodução em ambiente limpo e compare com o número entregue.
- Releia o relatório contra as saídas do código: nenhum número digitado à mão sem conferência.
- Confira que a amostra de dados devolvida lida de volta bate com a contagem.

## No retorno

Informe: o que foi entregue, onde, o comando de reprodução, os números principais com o conjunto de avaliação, as limitações e as pendências. Se faltar uma verificação essencial, descreva a entrega como parcialmente validada.

README continua com a Tsunade; o relatório e o data card são artefatos de dados, não substituem README.
