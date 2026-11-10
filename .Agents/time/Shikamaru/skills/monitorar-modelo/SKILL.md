---
name: monitorar-modelo
description: Define o monitoramento de um modelo em uso — sinais, janela de referência, limiares, dono do alerta e gatilho de retreino — e entrega o plano como artefato, sem servir em produção.
---

# Monitorar um modelo

O guia de [monitoramento](../../design/monitoramento.md) detalha os sinais, o drift e o retreino. Esta skill cobre a decisão e a entrega.

1. **Parta do uso, não da métrica.** Descubra se o rótulo chega, quando chega e com que atraso. Sem rótulo, escolha o proxy que avisa antes — taxa de aceite, correção manual, reclamação — e diga que ele não substitui a métrica.
2. **Fixe a janela de referência.** É o período usado no treino. A janela atual só significa algo comparada a ela.
3. **Escolha os sinais pelo que pode quebrar.** Volume e cobertura, esquema, distribuição das features, distribuição da predição, métrica real, custo e latência. Sinal sem ação esperada não entra.
4. **Separe drift de degradação.** Distribuição diferente não prova modelo pior: confirme se a métrica caiu antes de propor retreino. Retreinar por susto troca um modelo bom por um pior.
5. **Defina limiar com o time, não no incidente.** Cada alerta tem dono e ação: investigar, restringir escopo, retreinar ou desligar. Excesso de alerta treina todos a ignorar.
6. **Defina o gatilho de retreino antes do problema.** Gatilho, janela de histórico, critério de reavaliação com o mesmo rigor da avaliação original, e como voltar atrás.
7. **Entregue o plano como arquivo** — `docs/monitoramento/<modelo>.md` — com sinais, janelas, limiares, donos, ações e o que ainda não pode ser medido. Plano no chat não sobrevive.
8. **Handoff:** servir, alertar e instrumentar em produção é do Lee. Você entrega o plano, os sinais esperados e o comportamento de retreino; a implementação segue o contrato dele.

## Limites

- Não cria dashboard nem alerta sem dono nomeado.
- Não retreina por drift sem medir a métrica.
- Não escolhe proxy que esconde o erro: proxy serve para avisar, não para declarar sucesso.
- Modelo sem monitoramento não é entrega completa: é dívida declarada no relatório.
