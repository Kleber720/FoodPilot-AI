---
name: refatorar-frontend
description: Reorganiza a estrutura interna do front-end preservando comportamento, aparência e contratos. Use quando o objetivo for mudar a estrutura, não a tela.
---

# Refatorar o front-end

## Antes de tocar

1. **Congele o comportamento.** Anote ou execute o que a tela faz hoje: fluxo, estados, teclado, responsividade. Sem linha de base, "não mudou nada" é opinião.
2. Mapeie o que não pode mudar: os consumidores dos componentes, os contratos de integração, os tokens usados e as telas que dependem do trecho. Consumidor fora da tela é risco que você não mede.
3. Se o trecho não tem teste, escreva um que congele o comportamento atual antes de mudar — inclusive o estranho. Teste de caracterização não julga; registra.
4. Nomeie o alvo em uma frase: qual estrutura você quer e por que a atual atrapalha a próxima entrega. Sem alvo, refatoração vira reescrita.

## Durante

- Um passo por vez, pequeno o bastante para reverter sozinho. Verifique entre os passos.
- Não misture com mudança de comportamento nem com recurso novo: se aparecer defeito, pare e abra registro.
- Não troque framework, biblioteca de estado, roteamento nem contrato de API. Isso é decisão registrada, não refatoração.
- Preserve a interface pública dos componentes; se a assinatura mudar, atualize todos os consumidores no mesmo passo.

## Depois

- Compare com a linha de base: mesmos fluxos, mesmos estados, mesma aparência, teclado e responsividade intactos.
- Rode as verificações do projeto — lint, tipos, teste, build — e informe o resultado.
- Diga o ganho concreto: o que ficou mais fácil de mudar. "Código mais limpo" não é ganho.

Informe o que foi reestruturado, a comparação com a linha de base e o que ficou de fora de propósito.
