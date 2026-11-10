# Arquitetura de back-end

Antes de codar um back-end novo, desenhe o serviço considerando todos os fluxos conhecidos. Dê mais detalhe às decisões que afetam a primeira entrega e registre as questões futuras que podem mudar contratos, dados ou permissões.

## O que o esboço deve mostrar

- **Limites e consumidores.** Identifique as responsabilidades do back-end, quem o consome e quais sistemas externos participam de cada fluxo relevante. Para integração com o front-end, descreva a interface que ele vai consumir.
- **Responsabilidades internas.** Mostre onde entram as requisições ou eventos, onde ficam as regras de negócio e quais partes acessam dados ou sistemas externos. Indique o caminho do primeiro fluxo entre essas partes.
- **Dados e acesso.** Identifique onde cada dado é persistido, qual componente pode alterá-lo e quais usuários ou serviços podem acessá-lo. Registre onde as permissões serão verificadas.
- **Execução e falhas.** Indique como o serviço roda, quais dependências são essenciais e o que acontece se uma delas ficar indisponível. Para operações que podem ser repetidas, descreva como o serviço evita efeitos duplicados quando o fluxo exigir essa garantia.

Para detalhar identidade, relações, integridade e consultas, use o [guia de modelo de dados](modelo-de-dados.md).

## Requisitos de qualidade

- Identifique os fluxos com exigências de desempenho, disponibilidade ou recuperação. Para cada meta conhecida, registre o cenário, a medida e como ela será verificada. Para desempenho, inclua a carga esperada. Para recuperação, registre o tempo máximo de interrupção e a perda de dados aceitável quando esses limites forem relevantes.
- Defina o comportamento esperado quando uma dependência crítica falhar. Por exemplo, confirme se um pedido pode ser aceito como pendente enquanto o pagamento estiver indisponível ou se deve ser recusado. Registre como essa decisão afeta os estados do pedido, o contrato da API e a recuperação da operação.
- Quando uma meta desconhecida puder mudar a arquitetura, registre a pergunta em aberto e indique qual decisão depende da resposta.

## Modelar o negócio com DDD

- **Linguagem ubíqua.** Levante os termos, operações e regras com quem conhece o negócio. Use os mesmos nomes nos casos de uso, no código e nos testes dentro de cada contexto. Registre termos ambíguos e resolva os que afetam a primeira entrega.
- **Subdomínios e contextos delimitados.** Identifique as áreas do negócio e onde cada modelo é válido. Quando o mesmo termo tiver sentidos ou regras diferentes, avalie se os modelos precisam de contextos distintos. Registre quem é responsável pelas regras e pelos dados de cada contexto e como os contextos se comunicam. Um contexto pode ser um módulo dentro do mesmo serviço.
- **Consistência.** Identifique as invariantes, ou seja, as regras que devem continuar verdadeiras após uma operação. Use um agregado quando um conjunto de objetos precisar proteger invariantes em conjunto. A raiz controla as mudanças dentro desse limite. Entre agregados ou contextos, explicite quais garantias de consistência o fluxo exige e como a operação se recupera se falhar no meio.

## Traduzir o modelo em código

- **Módulos.** Agrupe o código por responsabilidade de negócio e mantenha explícitos os contratos entre módulos. Traduza dados entre contextos quando seus modelos tiverem significados diferentes.
- **Entrada e aplicação.** Controllers, handlers e outros adaptadores validam o formato da entrada e traduzem protocolos. Os casos de uso coordenam autorização, transações e chamadas ao domínio e às dependências.
- **Domínio e infraestrutura.** Coloque as decisões do negócio no domínio e mantenha o modelo independente de HTTP, banco, ORM e fornecedores externos. Quando precisar isolar uma dependência, defina o contrato junto ao código que precisa dele e implemente-o em um adaptador de infraestrutura. Essa é a base de portas e adaptadores.
- **Padrões táticos.** Use entidades quando a identidade acompanhar o objeto ao longo do tempo e objetos de valor quando o significado depender dos seus valores. Use um serviço de domínio para uma operação de negócio que envolve vários objetos e não pertence naturalmente a um deles. Use eventos de domínio quando outro fluxo precisar reagir a um fato do negócio.
- **Verificação.** Teste as invariantes do domínio sem depender de rede ou banco quando a regra puder ser exercitada isoladamente. Use testes de integração para os contratos, o comportamento transacional e as restrições que dependem da persistência.

## Como escolher a estrutura

Use a estrutura mais simples que atenda aos requisitos conhecidos. Um cadastro com validações simples pode seguir um fluxo direto. Aprofunde a modelagem nas áreas em que regras, mudanças de estado e consistência exigirem mais cuidado. Introduza filas, cache ou serviços separados quando houver um requisito concreto que justifique o custo operacional. Registre qual requisito motivou a escolha e o que ela muda na execução ou na recuperação de falhas.

Um diagrama pequeno ou alguns parágrafos bastam se mostrarem os componentes, o caminho dos dados e os limites de acesso. Atualize o esboço se a implementação mudar uma decisão registrada.

## Evolução em produção

- Identifique quais consumidores e versões do serviço precisam continuar funcionando durante mudanças em APIs, eventos e bancos de dados. Defina a ordem entre publicação de contratos, migração e implantação. Se versões puderem coexistir, verifique a compatibilidade em cada etapa intermediária.
- Defina quais sinais serão acompanhados após a implantação, como erros por operação, aumento de latência ou falhas de processamento. Registre o que levaria a interromper a implantação e como recuperar o serviço ou os dados. Para mudanças irreversíveis, defina a recuperação antes da execução.

## Registro de decisões arquiteturais

Para decisões com impacto duradouro ou difíceis de reverter, registre no projeto o requisito que motivou a escolha, as opções realmente consideradas, a decisão e suas consequências. Indique o que justificaria revisá-la, como uma nova meta de disponibilidade ou a necessidade de implantar um módulo de forma independente.

Use o [modelo de registro de decisão](decisoes/modelo.md).

## Referências

- [Domain-Driven Design Reference, Eric Evans](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)
- [Hexagonal Architecture, Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture)
