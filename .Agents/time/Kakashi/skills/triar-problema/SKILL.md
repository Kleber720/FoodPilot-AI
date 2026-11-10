---
name: triar-problema
description: Avaliar um registro aberto em problemas/, decidir se procede, identificar a camada responsável e delegar com critério de verificação objetivo.
---

# Triar um problema

O ciclo completo está no [fluxo de trabalho](../../design/fluxo-de-trabalho.md); esta skill cobre a decisão de triagem.

1. Leia o registro inteiro e mova o estado para `em-triagem`, com a data no **Histórico**. Confira o cabeçalho contra o [modelo de registro](../../../problemas/modelo.md).
2. Verifique se há **Comportamento observado** com evidência e **Comportamento esperado** escrito como comportamento, não como implementação da outra camada. Faltando um dos dois, mova para `devolvido` dizendo o que falta. Não complete a evidência pelo autor.
3. Reproduza por conta própria, pelo ponto de integração informado. Confirme se o problema está na camada declarada em `camada-origem` e se não é defeito do lado de quem abriu.
4. Preencha **Critério de verificação** com a prova objetiva: comando ou requisição, dados sintéticos e resposta esperada. O critério precisa ser executável por outra pessoa, sem interpretar.
5. Decida: `delegado` com `camada-correcao` e `delegado-para` preenchidos; `descartado` quando não procede ou não é desta camada, com o motivo; `devolvido` quando falta prova. Ajuste a severidade pelo impacto real, não pelo esforço — e, se ela mudar em relação à do autor, registre a mudança e o motivo no **Histórico**.
6. Quando o defeito estiver na própria camada de quem entregou e tiver sido revelado por teste, marque `tipo: devolutiva` e preencha **Devolutiva** com a regra esperada e o teste que falha. A correção continua com quem escreveu o código.

No retorno, informe apenas o número, o estado e o responsável. O detalhe fica no arquivo.
