---
name: relatorio-do-dia
description: Fecha o dia com o relatório tirado dos registros, planos e verificações — o que saiu com prova, a fila por estado e severidade, o que travou e a ordem de amanhã.
---

# Relatório do dia

O relatório segue o [modelo de relatório](../../../relatorios/modelo.md) e é salvo em `relatorios/AAAA-MM-DD.md`.

1. **Tire os números dos arquivos, não da memória.** Frontmatter dos registros em `problemas/`, planos em `entregas/`, resultados de verificação. Sem registro, não aconteceu: o que não está no arquivo não vira linha do relatório.
2. **Comece pelo que saiu.** Uma linha por entrega aceita, com o critério que provou e o comando. "Entreguei" sem prova não é saída.
3. **Mostre a fila.** Abertos por estado e severidade — por projeto, quando houver mais de um —, e os que envelheceram sem movimento, com dono e dias parado. É aqui que a duplicata e a dependência entre registros aparecem.
4. **Diga o que travou e por quê.** Bloqueio sem dono é o problema mais caro do dia: aponte quem cobrar.
5. **Registre as decisões do dia.** Uma linha cada, com link para o registro. Decisão não registrada volta amanhã.
6. **Peça a decisão humana.** O que só o humano pode decidir — escopo, contrato público, risco — separado do resto, com a opção que você recomenda.
7. **Feche com a ordem de amanhã.** Não uma lista de desejos: a primeira entrega, o que ela depende e quem começa.
8. **Fale em uma página.** O relatório é para decidir, não para arquivar tudo; o detalhe continua nos registros.

## Limites

- Não maquie número: parcial é parcial, bloqueado é bloqueado.
- Não inclua dado pessoal nem credencial.
- Não transforme o relatório em segunda cópia do registro: aponte o número.
