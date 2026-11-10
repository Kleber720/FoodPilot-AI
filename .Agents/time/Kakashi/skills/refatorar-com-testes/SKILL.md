---
name: refatorar-com-testes
description: Reestruturar código já coberto por testes sem mudar comportamento, contrato nem escopo, mantendo a suíte verde entre os passos.
---

# Refatorar com testes

1. Confirme a suíte verde e guarde a saída como linha de base. Sem verde não há refatoração: há correção, e correção é do Lee.
2. Mapeie o trecho e seus consumidores. Se o trecho não tem teste, escreva um teste de caracterização que congele o comportamento atual antes de mudar, conforme a [refatoração segura](../../design/refatoracao-segura.md).
3. Nomeie o cheiro e a estrutura pretendida em uma frase. Defina o critério de parada.
4. Execute em passos pequenos, rodando a suíte entre eles. Reverta o passo no vermelho; não ajuste a asserção para acomodar o código.
5. Não altere contrato, schema, migração, dependência nem regra de negócio. Se a refatoração exigir mudança de comportamento, pare e abra a devolutiva para o Lee.
6. Se um passo revelar defeito, pare. Abra a devolutiva com a evidência e não conserte no meio da refatoração.
7. Ao final, compare com a linha de base: mesmos testes, mesmos resultados, nenhuma asserção enfraquecida. Informe o ganho concreto.

Informe o antes e o depois da suíte, o que mudou e o que ficou de fora de propósito.
