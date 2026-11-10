---
name: auditar-cobertura-de-regras
description: Levantar as regras de negócio entregues e apontar quais estão sem teste, por risco, antes de considerar uma entrega coberta.
---

# Auditar a cobertura de regras

1. Monte o inventário das regras a partir do contrato, do guia de domínio, das decisões registradas e do pedido que originou a entrega. Não derive regra do código: código é a implementação, não a fonte.
2. Para cada regra, procure o teste que a protege pela leitura da suíte e pela busca do termo do negócio. Marque as situações cobertas: válido, inválido, limite, acesso, repetição, persistência.
3. Classifique as lacunas por risco, não por volume: acesso a recurso de outra conta, dinheiro, perda de dado e fluxo que bloqueia a entrega vêm primeiro. Cobertura de linha alta não compensa uma regra de acesso sem teste.
4. Prove o que afirma sobre as regras críticas: quebre a regra de propósito, rode a suíte e confirme que algo falha. Restaure no mesmo passo, confirme o diff limpo e registre a prova. Teste que passa com a regra quebrada é lacuna disfarçada.
5. Atualize a [matriz de regras](../../design/matriz-de-regras.md) e entregue a lista de lacunas classificada por risco. A ordem de ataque entre registros é da Tsunade; aqui o que você diz é o que é mais grave. Cada lacuna vira pedido de teste na skill `testar-regra-de-negocio`, ou devolutiva se a regra nem existir.

Informe quantas regras foram inventariadas, quantas têm teste, quais lacunas ficaram e o que você provou por quebra deliberada. Se uma regra não pôde ser testada, diga o motivo.
