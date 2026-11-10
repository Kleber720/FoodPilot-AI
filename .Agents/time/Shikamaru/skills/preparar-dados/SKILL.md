---
name: preparar-dados
description: Transforma o conjunto bruto em features reproduzíveis, com o split definido antes de qualquer ajuste e sem vazamento entre treino e avaliação.
---

# Preparar dados

1. Defina o split antes de qualquer transformação: treino, validação e teste. Em dado temporal, separe por tempo — o futuro não treina o passado. Com entidade repetida (mesmo cliente, mesma loja, mesmo equipamento), separe por grupo, nunca por linha. O [guia de preparação e vazamento](../../design/preparacao-e-vazamento.md) detalha as estratégias de split e as transformações.
2. Congele o split em arquivo ou função versionada. Split diferente a cada execução invalida a comparação entre experimentos.
3. Faça a limpeza com justificativa registrada: duplicata (remover ou manter e por quê), missing (remover linha, imputar ou criar indicador), outlier (manter, capar ou remover) e tipo ou unidade.
4. Construa as features: encoding, escala, agregação por janela, variável derivada. Todo ajuste — média, mediana, vocabulário, target encoding — é feito só no treino e aplicado nos demais conjuntos. Target encoding usa validação cruzada interna, nunca o alvo da própria linha.
5. Elimine o vazamento da lista da exploração, uma a uma. Nenhuma feature pode depender de informação posterior ao momento da previsão; o que não puder ser provado, sai.
6. Monte o pipeline: script ou módulo executável do bruto ao dataset de treino, com seed, ordem determinística e dependências registradas. O que existe só em célula de notebook não é entrega.
7. Registre a linhagem no data card: de onde veio cada dataset derivado e qual transformação o gerou.
8. Rode o pipeline do zero e compare com a versão anterior: contagem, distribuição e taxa de missing. Confirme que o teste não foi tocado.

Informe: o split, as transformações, o que saiu e por quê e o comando que reproduz o pipeline. Se o dado não sustentar o plano, devolva antes de treinar.
