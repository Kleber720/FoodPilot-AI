---
name: treinar-modelo
description: Treina um modelo de machine learning clássico a partir de uma linha de base, com semente, versões e dados congelados, e registra o experimento para que outra pessoa consiga repetir.
---

# Treinar modelo

1. Meça a linha de base antes do modelo: regra simples de negócio, média ou mediana, modelo anterior. Mesma métrica, mesmo split, mesma unidade de avaliação. O [guia de experimentos](../../design/experimentos.md) detalha o registro e a disciplina de comparação.
2. Comece pelo modelo simples e só aumente a complexidade quando ela superar a linha de base por uma margem que importe para o negócio. Registre a razão da escolha.
3. Ajuste hiperparâmetros na validação; o teste fica intocado até a avaliação.
4. Registre cada execução — id, data, snapshot dos dados, features, hiperparâmetros, seed, versão das bibliotecas, métrica e resultado — em `docs/experimentos/` ou na ferramenta que o projeto adotar. Experimento sem registro é opinião.
5. Fixe a semente e a ordem de amostragem. Se o resultado muda muito com a seed, isso é informação: reduza a variância em vez de escolher a seed sortuda.
6. Meça o custo: tempo de treino, memória e tempo de inferência. Modelo que não cabe no uso pretendido não é entrega.
7. Use validação cruzada quando o volume for pequeno e validação temporal quando o uso for prever o futuro. Nunca escolha o modelo pelo resultado no teste.

Informe: a linha de base, o modelo escolhido, a métrica de validação, o custo e o id do experimento. Não declare sucesso — a decisão é da avaliação.
