# Avaliação do Lee — API de tarefas privadas

## Preparação

Use um projeto de teste vazio. Envie ao Lee somente o pedido abaixo. Reserve os critérios para quem vai avaliar a entrega.

## Pedido para o Lee

> Crie do zero o back-end de uma API de tarefas privadas. Cada conta deve conseguir criar, listar e consultar suas próprias tarefas. Cada tarefa precisa de um título obrigatório. Use persistência e informe como iniciar o serviço localmente e acessar a API com duas contas de teste. Use a stack do time.

## Critérios de aprovação

1. **Arquitetura antes do código.** O primeiro esboço identifica os consumidores, as responsabilidades, o caminho dos dados, a propriedade da tarefa e onde a autorização será verificada. Observe a ordem durante a execução.
2. **Execução reproduzível.** Em ambiente limpo, siga as instruções entregues para iniciar o serviço, preparar a persistência e autenticar duas contas de teste. Use o contrato entregue para fazer as chamadas. Confira que o serviço é em Python, conforme a stack do time.
3. **Fluxo principal.** Crie uma tarefa válida com cada conta. Confirme que cada conta lista e consulta sua própria tarefa. Reinicie o serviço mantendo o armazenamento e confirme que as tarefas persistem.
4. **Validação.** Tente criar uma tarefa sem título. Confira se a API devolve o erro descrito no contrato e se o registro inválido ficou fora da listagem.
5. **Isolamento.** Autenticado como a conta A, tente consultar pelo ID a tarefa da conta B. Confira a resposta prevista no contrato e confirme que ela não revela dados da tarefa. A listagem da conta A também deve omitir a tarefa da conta B.
6. **Escopo e evidências.** A entrega se limita ao back-end e ao contrato de integração. Confira que o Lee deixou o README a cargo da Tsunade e informou no retorno o que verificou, os resultados e eventuais pendências.

## Resultado

Marque cada critério como passou, falhou ou ficou sem verificação. Registre a evidência ou o bloqueio ao lado do resultado. Considere o cenário aprovado quando todos os critérios passarem.
