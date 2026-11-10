# Arquitetura de testes

A suíte é código de produção do time: alguém vai lê-la na próxima mudança. Estrutura previsível vale mais que esperteza. Este guia responde onde o teste fica e como a suíte se organiza; o que provar e em que nível está na [estratégia de testes](estrategia-de-testes.md).

## Onde os testes ficam

- Espelhe o domínio, não o framework. Uma pasta por área de negócio quando a suíte crescer; um arquivo por assunto testado.
- O nome do arquivo descreve o assunto; o nome do teste descreve o comportamento: `tests/tarefas/isolamento.test.ts` com `nao_lista_tarefa_de_outra_conta`.
- Teste de contrato fica separado dos testes de regra, porque roda contra a API real e falha por motivo diferente.
- Suporte compartilhado — factories, fixtures, cliente HTTP autenticado, preparação de banco — fica em `tests/support/`, fora dos arquivos de teste.

## Alvos de execução

| Alvo | Contém | Quando roda |
| --- | --- | --- |
| rápido | unidade e contrato leve, sem I/O externo | a cada salvamento e no pre-commit |
| integração | banco, HTTP e autorização reais | a cada mudança e no CI |
| completo | integração mais ponta a ponta | antes de fechar a entrega |

O alvo que o time roda a cada mudança precisa ser confiável. Teste lento no alvo rápido ensina o time a ignorar a suíte.

## Helpers

- Helper que monta estado é bem-vindo: criar conta, autenticar, semear tarefa.
- Helper que esconde a asserção é proibido: `expectListingOk()` que engole status, forma e conteúdo transforma vários testes em um só, sem diagnóstico.
- Helper com efeito colateral diz isso no nome: `criaContaAutenticada`, não `setup`.
- Não compartilhe estado mutável entre testes. O helper devolve o que criou e o teste limpa.

## Banco e serviços

- Um teste, um estado próprio: transação revertida ao final ou banco efêmero por execução.
- Teste que exige ordem de execução é falha intermitente esperando acontecer.
- Paralelismo exige isolamento real — schema, banco ou tenant por worker. Sem isso, o alvo roda em série, e isso fica registrado.
- Serviço externo que não é o objeto do teste pode ser simulado, com o contrato do simulador registrado. O que se quer provar nunca é simulado.

## Quando o projeto não tem estrutura

Proponha a mínima que atende ao primeiro fluxo, registre a escolha em [decisões](decisoes/modelo.md) e não reorganize a suíte inteira de uma vez. Estrutura nasce do uso, não do gosto.
