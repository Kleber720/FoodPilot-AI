---
name: criar-backend
description: Criar um serviço de back-end do zero e entregar o primeiro fluxo de negócio funcionando pela interface que seus consumidores vão usar.
---

# Criar um back-end

## Antes de escrever código

1. Identifique quem vai consumir o back-end, quais fluxos conhecidos ele precisa suportar e qual será a primeira entrega.
2. Desenhe a arquitetura de alto nível do back-end como um todo. Delimite responsabilidades, interfaces, fluxo de dados, persistência, integrações e limites de acesso. Modele o domínio com os termos do negócio, identifique onde cada modelo é válido e registre as regras que precisam ser preservadas. Considere a execução do serviço e as falhas das dependências. Use o guia de [arquitetura e DDD](../../design/arquitetura.md). Registre termos e regras no [guia de domínio](../../design/dominio.md), que vive em `docs/dominio/`.
3. Registre no projeto um esboço curto com as decisões que orientam a primeira implementação, as premissas que afetam essas decisões e as questões ainda em aberto. Se faltar uma definição que mude o contrato público, a propriedade dos dados ou o controle de acesso, esclareça esse ponto antes de implementar a parte afetada.

## Implementar e verificar

1. Use o esboço para recortar o primeiro fluxo de negócio e definir os dados e permissões que ele exige.
2. Siga a stack do time ([`comum/stacks.md`](../../../comum/stacks.md)) e as convenções do projeto: Python com FastAPI, SQLAlchemy e Alembic, salvo se o projeto já tiver stack própria. A stack não é escolha sua; trocar é decisão de produto.
3. Antes de implementar o fluxo, defina entradas, respostas e erros da interface. Para APIs, use o guia de [contratos de API](../../design/contratos-api.md). Modele os dados e suas restrições. Se houver banco de dados, inclua a migração inicial.
4. Implemente o fluxo desde a entrada até a regra de negócio e a persistência, quando necessária. Organize o código por responsabilidade de negócio, mantenha as regras de domínio independentes de detalhes de infraestrutura e aplique padrões táticos de DDD conforme a complexidade das regras. Valide as entradas e aplique autenticação e autorização conforme as regras do projeto. Se o pedido envolver front-end, entregue a parte de back-end que puder ser feita de forma independente e documente o contrato para a integração.
5. Para integrações externas, defina limites de tempo e o comportamento em caso de falha. Se uma operação de escrita puder ser repetida, defina se o serviço deve rejeitar a duplicata ou reaproveitar o resultado anterior. Registre contexto suficiente para investigar erros, preservando credenciais e dados sensíveis.
6. Reúna para o repasse técnico os comandos para instalar dependências, configurar e iniciar o serviço, aplicar migrações e rodar os testes. Entregue essas informações no chat ou no retorno ao coordenador. A criação e a edição do README cabem à Tsunade. Use valores fictícios nos exemplos de configuração.
7. Em ambiente limpo de teste, siga as instruções de inicialização. Exercite o fluxo principal pela interface que o consumidor vai usar, uma entrada inválida e, quando aplicável, uma tentativa de acesso sem permissão. Se houver isolamento entre contas, verifique também o acesso a um recurso de outra conta.

Informe as verificações executadas, os resultados e as pendências. Se faltar uma verificação essencial, descreva a entrega como parcialmente validada.
