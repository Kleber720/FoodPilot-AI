---
name: testar-regra-de-negocio
description: Provar com testes uma função ou regra de negócio entregue pelo Lee, derivando os casos do contrato e do domínio, com o teste vermelho antes do verde.
---

# Testar uma regra de negócio

1. Localize a regra antes do código: contrato, [guia de domínio](../../../Lee/design/dominio.md) do Lee (o artefato vive em `docs/dominio/`) e [matriz de regras](../../design/matriz-de-regras.md). Escreva em uma frase o comportamento esperado, com o termo do negócio. Se o contrato não disser o que acontece no caso que você precisa provar, não suponha: abra a devolutiva.
2. Liste os casos antes de escrever: caminho válido, cada entrada inválida, os limites, o acesso negado de outra conta ou organização, a repetição da escrita e o estado persistido depois da operação. A [estratégia de testes](../../design/estrategia-de-testes.md) indica o nível.
3. Escreva o teste no nível mais baixo que ainda exercite o comportamento, na estrutura e nos nomes do guia de [arquitetura de testes](../../design/arquitetura-de-testes.md). Verifique o que o consumidor recebe, não a chamada interna. Monte os dados conforme o guia de [dados de teste](../../design/dados-de-teste.md).
4. Rode e confirme o vermelho pelo motivo certo — falha de asserção, não de importação, fixture ou digitação. Teste que passa de primeira não mede a regra: ajuste antes de seguir.
5. Confirme o verde com a implementação existente, sem alterar o código de produção — a única exceção é a quebra deliberada do passo 6. Se continuar vermelho porque a regra não existe ou diverge, abra a devolutiva com o teste que falha e o comportamento esperado, e siga para a próxima regra.
6. Para regra crítica — acesso, dinheiro, perda de dado — faça a sanidade: quebre a regra de propósito, rode a suíte e confirme que o teste falha. Restaure no mesmo passo e prove que o diff voltou ao original. Mutação esquecida no código é pior que lacuna: o diff dela precisa aparecer no relato.
7. Atualize a [matriz de regras](../../design/matriz-de-regras.md) com a linha da regra e as situações cobertas.

Informe a regra, o teste, a saída do vermelho e do verde, a prova de que a mutação foi restaurada e o que ficou sem cobertura. Não informe "testado" sem a saída que prova.
