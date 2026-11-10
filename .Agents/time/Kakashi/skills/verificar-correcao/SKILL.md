---
name: verificar-correcao
description: Conferir de forma independente a correção registrada em problemas/ e fechar ou reabrir o registro.
---

# Verificar uma correção

1. Leia **Correção** e **Critério de verificação**. Se o critério não puder ser executado por outra pessoa sem interpretar, devolva antes de tentar. Reexecute você mesmo, sem reaproveitar a execução de quem corrigiu, sem confiar no relato e sem ajustar o critério para o que a correção faz.
2. Confira o diff dos testes: asserção enfraquecida, removida ou marcada como ignorada para passar reprova a correção, mesmo com a suíte verde.
3. Verifique o que a mudança pode atingir além do caso: fluxo principal, validação vizinha, acesso de outra conta, paginação e persistência, conforme a regra.
4. Se passou, mova para `verificado` e preencha **Verificação final** com comando, resultado e data. Se falhou, reabra com a evidência nova e uma linha no **Histórico**; não edite a correção de outro autor.
5. Se a correção mudou o contrato público sem registro de decisão, não feche: isso é do Lee e precisa do registro correspondente.

Informe o critério executado, o resultado e o estado final. Se não foi possível executar o critério, o registro não fecha.
