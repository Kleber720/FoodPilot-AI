---
name: fechar-entrega
description: Confere a entrega contra o aceite e os portões declarados, consolida o resultado em uma resposta única ao humano e só declara pronto o que tem evidência.
---

# Fechar uma entrega

1. **Percorra o aceite critério por critério.** Para cada um: passou, falhou ou ficou sem verificação, com a evidência do dono ao lado. Sem evidência, não passou.
2. **Confira os portões declarados no plano.** A prova do Kakashi está aberta e cobre o que foi entregue; o README existe e corresponde ao que saiu. A execução em ambiente limpo é dele: você confere a evidência e não reexecuta. Portão que não foi exercitado é pendência, não aprovação — e entrega sem avaliação independente fecha como parcial, nunca como aceita.
3. **Confira o escopo no diff, não no relato.** Mudança que atravessou a fronteira — Sakura no servidor, teste enfraquecido, código do Lee alterado por outro — reprova a entrega, mesmo que o resto passe.
4. **Separe o que falhou do que não deu para verificar.** Falha volta como registro para o dono. Falta de ambiente ou de integração não é falha nem aprovação: é entrega parcialmente validada, com o motivo.
5. **Consolide em uma resposta.** Ao humano, um texto só: o que saiu com a prova, o que ficou parcial, os registros abertos ou movimentados, a decisão que falta e o próximo passo. Não cole quatro relatos; diga o que eles significam juntos.
6. **Não reescreva o relatório de ninguém.** Resuma e aponte o arquivo. Corrigir o relato alheio apaga a evidência de que o resultado não foi o esperado.
7. **Não declare pronto o que não viu.** "Parcialmente validado" é um resultado aceitável; "pronto" sem verificação não é.

## Saída

Uma entrega termina em um dos quatro: **aceita**, **parcial**, **bloqueada** ou **devolvida**. Em todos, o humano sabe o que falta e quem é o próximo.
