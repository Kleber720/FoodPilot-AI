# Estados e erros

Toda tela que depende de dado remoto ou de ação do usuário tem mais de um estado. Planeje os quatro antes de implementar: carregando, vazio, erro e sucesso. Estado não planejado vira tela em branco na mão do usuário.

## Os quatro estados

- **Carregando.** Preserve o layout: esqueleto com a forma do conteúdo evita salto quando o dado chega. Prefira indicador no lugar do conteúdo a bloquear a tela inteira. Em ação de escrita, mostre o estado no próprio botão e impeça reenvio.
- **Vazio.** Diferencie "ainda não há nada" (com o próximo passo) de "o filtro não encontrou nada" (com como limpar o filtro) e de "sem permissão" (com a explicação). Um texto só para os três confunde.
- **Erro.** Diga o que aconteceu e o que fazer. Preserve o que o usuário digitou. Ofereça nova tentativa quando a falha for transitória.
- **Sucesso.** Confirme a ação quando o efeito não é óbvio na tela, sem exigir um clique a mais.

## Tradução do erro do contrato

Parta do que o contrato documenta e traduza em ação, não em código:

| Situação no contrato | O que a tela faz |
| --- | --- |
| Entrada inválida (400, 422) | Mostra a mensagem junto ao campo e mantém os dados preenchidos |
| Não autenticado (401) | Encaminha para autenticar sem perder o contexto |
| Sem permissão (403) | Explica a restrição e oferece a saída possível |
| Não encontrado (404) | Mostra a ausência com caminho de volta, não erro genérico |
| Conflito (409) | Mostra o estado atual e pede a decisão: recarregar ou sobrescrever |
| Falha transitória, 5xx ou timeout | Mensagem de instabilidade com nova tentativa, preservando os dados |
| Falha de rede | Diferencie do erro do servidor e permita tentar de novo |

Não exiba a mensagem crua do servidor nem detalhe interno ao usuário. Mapeie para texto do produto e registre o original só onde a investigação precisa dele.

## Formulários

- Valide no envio e, quando houver feedback útil, ao sair do campo. Não valide a cada tecla em campo que o usuário ainda está preenchendo.
- Mensagem junto ao campo e ligada a ele, conforme o guia de [acessibilidade](acessibilidade.md).
- Mantenha os valores no erro, exceto o que for sensível.
- Tenha estado de envio explícito e libere o botão ao terminar, inclusive em falha.
- Se a escrita puder ser reenviada e o contrato tiver chave de idempotência, use-a. Sem isso, não reenvie automaticamente operação que cria ou altera.

## Quando o estado depende de um contrato que não existe

Se a tela precisa distinguir uma situação que o contrato não permite distinguir — falta um código de erro, um campo ou um filtro — não invente a distinção no cliente nem deduza regra do servidor. Abra um registro em [problemas/](../../problemas/modelo.md) seguindo a skill [registrar-problema](../../comum/skills/registrar-problema/SKILL.md) e entregue a parte da tela que já funciona com o contrato atual.
