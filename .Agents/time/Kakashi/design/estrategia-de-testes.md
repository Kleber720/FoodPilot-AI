# Estratégia de testes

Um teste existe para provar um comportamento que o negócio exige, não para cobrir linha. Antes de escrever, responda qual regra o teste protege e qual mudança no código deveria fazê-lo falhar. Se a resposta for "nenhuma", o teste não serve.

## Onde testar

| Nível | Use para | Não use para |
| --- | --- | --- |
| Unidade | regra de domínio pura: cálculo, validação, transição de estado, decisão de permissão | banco, HTTP, fila |
| Integração | persistência, transação, restrição única, migração aplicada, autorização com o registro real | formato de tela |
| Contrato | entrada e saída, status, erro documentado, paginação, idempotência | regra interna |
| Ponta a ponta | fluxo do consumidor em ambiente limpo, com o serviço iniciado como as instruções mandam | detalhe de implementação |

Prove no nível mais baixo que ainda exercita o comportamento. Regra de domínio testada só por HTTP esconde qual regra quebrou; integração testada com mock não prova que a integração funciona.

## Derivar os casos da regra

Parta do contrato e do domínio, não do código. Para cada regra, liste:

- o caminho válido mínimo;
- cada entrada inválida que o contrato documenta e a que ele não documenta;
- os limites: vazio, zero, negativo, maior valor aceito, texto no tamanho máximo, lista vazia e lista no limite de página;
- a autorização: recurso de outra conta ou organização, requisição sem credencial, credencial sem permissão;
- a repetição: escrita reenviada, chave de idempotência reutilizada, execução após falha parcial;
- o estado depois da operação: o que ficou persistido e o que não pode ter sido criado.

Regra sem caso de limite e sem caso de acesso negado está meio testada. A [matriz de regras](matriz-de-regras.md) mostra o que já existe e o que falta.

## Escrever o teste

- Nomeie pelo comportamento: `nao_lista_tarefa_de_outra_conta`, não `teste_listagem_2`.
- Um motivo de falha por teste. Vários `assert` convivem quando descrevem o mesmo comportamento.
- Verifique o que o consumidor recebe, não como o código chegou lá. Asserção sobre chamada interna prende a implementação e quebra na refatoração.
- Use dados sintéticos e explícitos no próprio teste, ou uma fixture nomeada. Nada que dependa do banco de produção ou de execução anterior.
- Prepare o estado no início e limpe ao final, sem depender da ordem da suíte. Teste que só passa depois de outro é falha intermitente esperando acontecer.
- Congele tempo e geração de identificadores quando a regra depender deles.
- Mock serve para isolar a fronteira externa, não para substituir o objeto que se quer provar.

## Vermelho antes de verde

1. Rode o teste novo e confirme que ele falha. Leia a falha: erro de importação, fixture ausente ou digitação não é vermelho válido.
2. Só então confirme o verde com a implementação existente.
3. Se ficou vermelho porque a regra não existe ou está errada, não implemente. Devolva com a evidência da falha.

## Sanidade por mutação

Para regra crítica — acesso a recurso de outra conta, dinheiro, perda de dado — quebre a regra de propósito no código local, rode a suíte e confirme que o teste falha. Restaure e confirme que o diff voltou ao original. Teste que passa com a regra quebrada é lacuna disfarçada, não cobertura.

## Tempo e intermitência

Suíte intermitente destrói a confiança que justifica a refatoração. Teste instável não é silenciado nem quarentenado em silêncio: registre o sintoma, isole a causa e corrija o teste ou a dependência que ele assume. Mantenha a suíte que roda a cada mudança abaixo do tempo que o time aceita esperar; o que for lento e não for regra de negócio roda em alvo separado.
