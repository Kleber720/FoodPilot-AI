---
name: receber-dados
description: Recebe um conjunto de dados do banco ou da API do projeto, confere contrato, esquema, chave, granularidade e qualidade antes de qualquer análise, e registra origem e limitações em um data card.
---

# Receber dados

## Antes de extrair

1. Identifique a fonte: esquema e tabela ou visão do banco, ou rota e versão da API. Confirme com quem mantém a fonte — normalmente o Lee — o contrato: colunas, tipos, chave, granularidade, período coberto e frequência de atualização. Contrato ausente ou divergente vira registro em [problemas/](../../../problemas/modelo.md), não suposição. O [guia de qualidade de dados](../../design/qualidade-de-dados.md) detalha o contrato, as dimensões e o data card.
2. Defina o recorte antes de rodar a consulta: período, filtros de negócio e volume esperado. Recorte maior não compensa recorte errado.
3. Peça acesso somente leitura. Não copie credenciais para script, notebook, repositório nem chat; use variável de ambiente ou o mecanismo do projeto.
4. Trate dado pessoal antes de qualquer coisa: identifique PII, aplique a anonimização ou pseudonimização que o projeto exigir e registre o que foi feito.

## Extrair

5. Congele a extração em um snapshot com data e consulta registradas. O banco muda entre duas execuções; análise sem snapshot não é reproduzível.
6. Salve no projeto a consulta exata e o comando de extração. Paginação, janela de tempo e limite da API fazem parte do recorte: sem eles, o volume muda sem aviso.
7. Confira a extração contra a fonte: contagem, período mínimo e máximo e uma amostra de registros. Divergência de volume é sintoma, não detalhe.

## Perfilar

8. Compare o esquema real com o esperado: coluna faltando, tipo trocado, nulo onde não deveria haver, unidade diferente.
9. Verifique chave e granularidade: uma linha por quê? A duplicata é de registro ou de evento legítimo?
10. Meça qualidade por coluna: missing, cardinalidade, valores impossíveis (negativo, data futura, categoria fora do domínio) e distribuição truncada.
11. Dê o veredito: usável; usável com restrição, dizendo qual; ou devolvido, com o defeito e a evidência.

## Data card

12. Crie `docs/dados/<fonte>.md` com origem e dono, contrato, consulta de extração, período e volume, esquema, qualidade, PII e tratamento, licença e uso permitido, limitações e data do snapshot.
13. Atualize o data card sempre que a extração ou o contrato mudar.

No retorno ao coordenador — ou no chat, quando você for usado direto — informe: a fonte, o recorte, o volume, o veredito e o caminho do data card. Se o dado veio errado, informe o número do registro aberto e siga com o que ainda é possível entregar.
