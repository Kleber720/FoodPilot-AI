---
name: alterar-api
description: Criar endpoints em um serviço existente ou alterar o contrato, a validação, as permissões ou o comportamento de uma API de back-end.
---

# Alterar uma API

1. Localize a rota, o contrato, os consumidores identificáveis e os testes relevantes. Confira o comportamento atual antes de alterar a interface.
   Se a mudança afetar regras de negócio, identifique o módulo responsável e as regras que precisam continuar válidas. Preserve os limites e as dependências existentes. Atualize o [guia de domínio](../../design/dominio.md) quando o comportamento da regra mudar. Consulte o guia de [arquitetura e DDD](../../design/arquitetura.md).
2. Preserve a compatibilidade com os consumidores, salvo quando a tarefa pedir uma quebra explícita. Defina a mudança no contrato público antes de implementar e descreva o impacto para os consumidores. Use o guia de [contratos de API](../../design/contratos-api.md).
3. Verifique validação de entrada, autenticação e autorização conforme a mudança. Quando houver recursos privados, confira a autorização para o recurso solicitado e teste se outra conta ou organização é impedida de ler ou alterar o registro ao trocar seu identificador na requisição.
4. Verifique o fluxo de sucesso, as falhas afetadas e o comportamento anterior que precisa ser preservado, pela interface usada pelo consumidor. Por exemplo, ao adicionar um filtro opcional a uma listagem paginada, verifique o resultado filtrado e a paginação quando o filtro for omitido.

Use dados sintéticos ou anonimizados nos testes e preserve credenciais e dados sensíveis em logs e exemplos. Informe as verificações executadas, os resultados e as pendências. Se faltar uma verificação essencial, descreva a entrega como parcialmente validada.
