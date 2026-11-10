# Qualidade de dados

Dado não chega neutro: chega com contrato implícito, recorte que ninguém declarou e defeito que só aparece depois do modelo treinado. A recepção existe para transformar o contrato implícito em um data card explícito — e para devolver o que não serve antes de custar uma análise inteira.

## Contrato com a fonte

Antes de extrair, escreva o que a fonte promete:

- **Colunas e tipos.** Nome, tipo, unidade e obrigatoriedade de cada campo que a análise usa.
- **Chave e granularidade.** O que uma linha representa: um pedido, um evento, um dia por cliente? Sem isso, toda contagem pode estar errada.
- **Cobertura.** Período mínimo e máximo, fuso horário, frequência de atualização e atraso entre o fato e o registro.
- **Filtros de negócio.** Cancelado entra? Conta de teste entra? O que fica de fora muda o resultado.
- **Dono.** Quem responde pela fonte e por mudanças de esquema.

Contrato que não existe é contrato a confirmar com o Lee, não a deduzir de um `SELECT *`. Quando a confirmação não vier, abra registro em [problemas/](../../problemas/modelo.md).

## Extração

- Use acesso somente leitura. Credencial fica em variável de ambiente ou cofre, nunca no notebook, no repositório ou no chat.
- Congele um snapshot com a consulta, a data e o volume. Banco que muda entre execuções produz análise que não se reproduz, e o resultado de ontem não é o de hoje.
- Registre paginação, janela e limite da API. Recorte que muda entre execuções contamina treino e avaliação.
- Confira contra a fonte: contagem, período coberto e amostra de registros.

## Dimensões de qualidade

| Dimensão | O que verificar | Sinal de problema |
| --- | --- | --- |
| Completude | missing por coluna e por período | coluna vazia em um intervalo |
| Unicidade | duplicata por chave e por registro completo | contagem maior que a fonte |
| Validade | domínio, faixa, tipo e unidade | negativo onde não pode, data futura |
| Consistência | regra entre colunas, total contra detalhe | soma que não fecha |
| Atualidade | último registro contra hoje | atraso maior que o contrato |
| Volume | linhas por período e por segmento | queda ou salto sem explicação |

Nenhuma dimensão é óbvia: o defeito que importa é o que muda a decisão. Registre o que foi medido, o que passou e o que ficou sem verificação.

## Dado pessoal e uso permitido

- Identifique dado pessoal antes da primeira análise: nome, documento, contato, endereço e dado sensível.
- Anonimize ou pseudonimize antes de extrair para o ambiente de análise, quando a finalidade permitir.
- Registre no data card a licença, a base legal ou a autorização de uso e a restrição de compartilhamento.
- Amostra de conferência também é dado pessoal: não vai para relatório, chat nem issue.

## Data card

Crie `docs/dados/<fonte>.md` com:

- **Origem e dono** — sistema, contato responsável e caminho de acesso.
- **Contrato** — colunas, tipos, chave, granularidade, cobertura e filtros.
- **Extração** — consulta ou comando, data do snapshot e volume.
- **Qualidade** — o que foi medido em cada dimensão e o que falhou.
- **PII e tratamento** — o que existe, o que foi feito e o que não pode circular.
- **Uso permitido** — finalidade, licença e restrição.
- **Limitações** — o que o dado não cobre e o que não responde.
- **Histórico** — mudanças de contrato, com data.

Data card desatualizado é pior que data card ausente, porque parece confiável. Atualize na mesma entrega em que a extração ou o contrato mudar.

## Veredito

Três saídas, sempre com evidência:

- **Usável** — o contrato se sustenta e a qualidade atende à pergunta.
- **Usável com restrição** — diga qual: período, segmento, coluna que precisa de tratamento.
- **Devolvido** — o defeito impede a análise. Entregue o sintoma, a consulta que o revela e o comportamento esperado.

Não conserte o dado na fonte: correção de origem é do dono, com registro. O que você pode fazer é tratar no seu pipeline e registrar a transformação.

## Exemplo

Uma tabela de pedidos com volume 30% menor nos fins de semana parece queda de demanda, mas o job de atualização não roda no sábado. O data card registra a defasagem e o recorte declara o período; sem isso, o modelo aprende um padrão de calendário que é falha de extração, não comportamento do negócio.
