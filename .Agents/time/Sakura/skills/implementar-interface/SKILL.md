---
name: implementar-interface
description: Planeja, implementa e verifica interfaces do front-end. Use ao criar ou alterar telas, componentes, fluxos de interação, layouts ou estilos.
---

# Implementar interface

## Planejar o design antes de codar

1. Examine a documentação, as telas existentes, o sistema de design e as referências visuais do projeto. Use o guia de [sistema de design](../../design/sistema-de-design.md) para os padrões visuais e o de [arquitetura de front-end](../../design/arquitetura-frontend.md) para a estrutura e a divisão de responsabilidades. Tela que precisa de token ou de componente compartilhado que não existe resolve isso antes pela skill `evoluir-sistema-de-design`, na mesma entrega.
2. Para uma tela ou fluxo novo, descreva brevemente o layout, a hierarquia da informação e os componentes principais antes de editar código. Para um ajuste pequeno, identifique o padrão existente que vai seguir.
3. Planeje o fluxo principal e os estados relevantes de carregamento, vazio, erro e sucesso, conforme o guia de [estados e erros](../../design/estados-e-erros.md). Para formulários, preveja validação e mensagens de erro.
4. Considere a apresentação em telas estreitas e largas e como a interação funciona por teclado. Preveja HTML semântico, foco visível e contraste legível, conforme o guia de [acessibilidade](../../design/acessibilidade.md).

## Implementar

- Consuma os contratos de API existentes pelo front-end. Se a interface depender de um contrato novo ou alterado, abra um registro em [problemas/](../../../problemas/modelo.md) seguindo a skill [registrar-problema](../../../comum/skills/registrar-problema/SKILL.md) e mantenha-se dentro do limite de atuação do [AGENTS.md](../../AGENTS.md).
- Use a stack do time: HTML, CSS, React e TypeScript ([`comum/stacks.md`](../../../comum/stacks.md)). Se o projeto já tem outro framework, siga o do projeto.
- Reaproveite componentes, estilos e padrões do projeto antes de criar novos. Extraia um componente quando ele tiver uma responsabilidade clara ou quando houver repetição real.
- Siga a organização do front-end do projeto e implemente os estados, o comportamento responsivo e a acessibilidade definidos no planejamento.

## Verificar

- Confira se a implementação corresponde à direção visual definida em telas estreitas e largas. Verifique o fluxo principal, os estados relevantes e a navegação por teclado.
- Rode as verificações disponíveis no projeto, como lint, checagem de tipos, testes ou build. Informe o que foi verificado e sinalize as verificações que ficaram pendentes.
