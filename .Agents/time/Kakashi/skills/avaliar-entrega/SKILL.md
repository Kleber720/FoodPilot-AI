---
name: avaliar-entrega
description: Avaliar uma entrega de ponta a ponta contra um cenário de aprovação, em ambiente limpo, sem usar o código para decidir se o critério passou.
---

# Avaliar uma entrega

O cenário é o **Aceite** do plano da entrega em [`entregas/`](../../../entregas/modelo.md): avalie contra os critérios que estão lá, não contra critérios que você inventa. O formato do resultado segue o [modelo de avaliação](../../design/modelo-de-avaliacao.md).

1. Use um ambiente ou projeto limpo e siga apenas as instruções entregues — o README e o plano da entrega —: instalar, configurar, iniciar, migrar. Não aproveite estado de execuções anteriores.
2. Execute cada critério do cenário pela interface do consumidor, na ordem definida. Para API, use o contrato entregue; para tela, use o navegador. Não leia o código de produção para decidir o resultado.
3. Registre por critério: passou, falhou ou ficou sem verificação, com a evidência ao lado — comando, requisição, resposta, tela. Sem evidência, o critério não passou.
4. Separe falha de entrega de falha de instrução. Se o serviço não sobe porque o comando do chat está errado ou incompleto, a falha é do critério de execução reproduzível, não do comportamento.
5. Ao encontrar defeito de regra, abra a devolutiva com o caso mínimo que reproduz e siga os critérios que não dependem dele. Uma falha não interrompe a avaliação inteira.
6. Feche com o resultado de cada critério, o que não pôde ser verificado, o que ficou parcialmente validado e o que a entrega fez bem fora do cenário.

Não declare "testado e funcionando" sem a execução que prova. Se faltou ambiente ou integração, diga o que impediu.
