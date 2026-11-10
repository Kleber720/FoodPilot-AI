---
name: evoluir-sistema-de-design
description: Evolui tokens, estilos e componentes compartilhados da interface. Use quando a mudança deve valer para várias telas ou quando a tarefa pede uma alteração no sistema de design.
---

# Evoluir o sistema de design

1. Antes de codar, localize os tokens, estilos, componentes e referências visuais do projeto. Mapeie as variantes e as telas consumidoras. Quando o projeto não tem sistema de design, é esta skill que cria o núcleo inicial — antes de qualquer tela nova.
2. Defina quais tokens, componentes, variantes e estados precisam mudar, seguindo o guia de [sistema de design](../../design/sistema-de-design.md). Reaproveite os padrões existentes e adicione uma variante ou um token quando houver uma necessidade compartilhada. Identifique quais consumidores devem migrar e preserve o comportamento dos demais.
3. Aplique a mudança às definições compartilhadas do front-end e aos consumidores previstos. Siga o [AGENTS.md da Sakura](../../AGENTS.md) e mantenha a alteração restrita à interface. Se houver uma dependência do servidor, abra um registro em [problemas/](../../../problemas/modelo.md) seguindo a skill [registrar-problema](../../../comum/skills/registrar-problema/SKILL.md).
4. Confira componentes e telas representativas em tamanhos diferentes. Quando aplicável, verifique variantes, temas, estados de interação, contraste e foco por teclado conforme o guia de [acessibilidade](../../design/acessibilidade.md). Informe os consumidores atualizados e as verificações realizadas.
