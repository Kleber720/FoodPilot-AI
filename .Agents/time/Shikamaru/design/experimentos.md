# Experimentos

Experimento sem registro é opinião. O registro existe para que outra pessoa — inclusive você daqui a três semanas — consiga repetir a execução, comparar com as anteriores e saber por que o modelo escolhido foi escolhido.

## Linha de base primeiro

Nenhum modelo complexo entra sem uma base medida no mesmo split e na mesma métrica:

- regra simples de negócio, quando existir;
- média ou mediana do alvo, em regressão;
- classe majoritária ou taxa base, em classificação;
- modelo anterior em produção, quando houver.

A base responde "quanto de sinal o dado tem" e impede que um resultado medíocre pareça bom por falta de referência.

## Registro do experimento

Cada execução vira uma entrada em `docs/experimentos/` ou na ferramenta adotada pelo projeto (MLflow, Weights & Biases, equivalente). O registro mínimo:

- **ID e data**, com uma frase de hipótese: o que esta execução testa.
- **Snapshot dos dados** — data e hash ou identificador do dataset.
- **Features** — lista ou referência à versão do pipeline.
- **Modelo e hiperparâmetros** — biblioteca e versão.
- **Seed.**
- **Métrica de validação** — nome, valor e conjunto usado.
- **Custo** — tempo de treino, memória e tempo de inferência.
- **Conclusão** — o que muda na decisão.

Se o projeto não tiver ferramenta, um arquivo Markdown por experimento resolve. O que não resolve é confiar na memória.

## Disciplina

- **Uma mudança por experimento.** Mudar feature, modelo e hiperparâmetro juntos impede saber o que causou a diferença.
- **Hiperparâmetro se ajusta na validação.** O teste nunca participa da escolha; modelo escolhido pelo teste é modelo otimista.
- **Escolha pela média entre seeds, não pela melhor execução.** Rode pelo menos três seeds quando o custo permitir e registre a variação.
- **Complexidade se paga.** Um modelo mais caro só substitui o simples quando o ganho passa da variação esperada e o custo cabe no uso pretendido.
- **Validação temporal para uso no tempo.** Treine no passado, valide no futuro, e não embaralhe a ordem.

## Versionamento

Dados, código e ambiente andam juntos. Registre o commit ou a versão do código, o snapshot dos dados e as versões das bibliotecas. Sem os três, o experimento não é reproduzível, mesmo que o número esteja anotado.

## Decisão

Escolha difícil de reverter — família de modelo, métrica de aceite, origem dos dados, formato de entrega — merece um registro de decisão no formato de [decisões/modelo.md](decisoes/modelo.md). O experimento prova que a alternativa funciona; a decisão registra por que ela foi adotada.
