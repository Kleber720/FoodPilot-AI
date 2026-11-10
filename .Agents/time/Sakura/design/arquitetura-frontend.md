# Arquitetura de front-end

Antes de codar uma interface nova, desenhe o front-end considerando as telas e os fluxos conhecidos. Dê mais detalhe às decisões que afetam a próxima entrega e registre as questões futuras que podem mudar a estrutura, o contrato consumido ou a integração.

## O que o esboço deve mostrar

- **Limites e consumidores.** Identifique quem usa a interface, quais telas e fluxos existem e quais APIs cada um consome. Diga o que está fora do escopo do front-end.
- **Estrutura.** Mostre como o código se organiza e por qual responsabilidade de negócio, não por tipo de arquivo. Indique onde ficam as telas, os componentes reutilizáveis, o estado e a camada que fala com a API.
- **Estado.** Diga onde cada informação vive: estado local do componente, estado de servidor (dado remoto e seu cache) ou estado compartilhado pela aplicação. Registre quem pode alterá-lo.
- **Integração.** Descreva como o front consome o contrato: onde está o cliente de API, como os tipos do contrato entram no código e como o erro chega à tela. O contrato é do back-end; o front não o redefine nem completa o que falta nele.

## Estrutura na prática

- Agrupe por responsabilidade de negócio e mantenha explícitos os contratos entre as pastas. Uma área não deve importar o interior de outra.
- Separe os componentes de apresentação, que recebem dados e eventos por props, dos que orquestram dados e efeitos. Extraia um componente quando ele tiver uma responsabilidade clara ou quando houver repetição real, não por precaução.
- Prefira composição a props booleanas que trocam o comportamento inteiro. Se um componente acumula condicionais de variante, avalie quebrá-lo ou mover a variação para o estilo.
- Tenha um único ponto de acesso à API. Requisição espalhada pelo componente espalha também o tratamento de erro, o autenticador e a URL base.
- Mantenha o estado o mais próximo possível de quem o usa. Suba para contexto ou store quando houver consumidores distantes e um requisito concreto, não por conveniência.
- Não guarde em estado o que é derivável de props ou de outro estado.

## Integração com o back-end

- Importe os tipos do contrato de uma definição única e traduza o modelo da API em modelo de tela quando os significados forem diferentes.
- Trate timeout, falha de rede e erro de negócio como situações distintas, com estado de tela próprio. Use o guia de [estados e erros](estados-e-erros.md).
- Nunca coloque segredo, chave privada ou regra de autorização no código do front. A interface pode esconder uma ação, mas quem autoriza é o servidor.
- Se a tela precisar de um dado, um filtro ou uma distinção de erro que o contrato não oferece, abra um registro em [problemas/](../../problemas/modelo.md) seguindo a skill [registrar-problema](../../comum/skills/registrar-problema/SKILL.md). Não invente o dado no cliente nem deduza regra do servidor.

## Como escolher a estrutura

Use a estrutura mais simples que atenda aos requisitos conhecidos. Uma tela de cadastro pode ser um formulário direto, sem camada de estado. Introduza cache, estado global, roteamento ou uma biblioteca adicional quando houver um requisito concreto que justifique o custo de manutenção. Registre qual requisito motivou a escolha e o que ela muda na verificação e na evolução.

Um diagrama pequeno ou alguns parágrafos bastam se mostrarem as telas, o caminho do dado e quem consome o quê.

## Verificação

- Teste o comportamento que o usuário percebe: o fluxo principal, os estados de carregamento, vazio e erro e o envio de formulário. Evite teste preso a detalhe de implementação.
- Verifique a integração contra a resposta real do contrato, não contra uma suposição sobre ela.
- Rode as verificações disponíveis do projeto, como lint, checagem de tipos, testes ou build.
- Registre as metas de desempenho e de acessibilidade que o produto precisa atingir e como cada uma será verificada. Para acessibilidade, use o guia de [acessibilidade](acessibilidade.md).

## Registro de decisões

Para decisões com impacto duradouro ou difíceis de reverter — biblioteca de estado, estratégia de estilização, estrutura de rotas, adoção de framework — registre o requisito que motivou a escolha, as opções realmente consideradas, a decisão e suas consequências. Use o [modelo de registro de decisão](decisoes/modelo.md).

## Referências

- [React — documentação oficial](https://react.dev)
- [MDN Web Docs](https://developer.mozilla.org)
