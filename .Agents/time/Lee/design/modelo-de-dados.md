# Modelo de dados

Antes de definir o esquema de persistência, descreva quais dados os fluxos do projeto precisam guardar, consultar e alterar. Use a linguagem do contexto de negócio e registre as escolhas que afetam a integridade, o acesso ou a evolução dos dados.

## Identidade, relações e responsabilidade

- Para cada conjunto de dados, identifique o contexto responsável, a fonte de verdade e quais módulos ou serviços podem ler ou escrever. Quando houver isolamento entre contas ou organizações, mostre como a propriedade do registro é representada e preservada.
- Defina os identificadores, as relações, a cardinalidade e o que acontece com os registros relacionados quando um deles é excluído. Registre se um campo é obrigatório e em qual escopo um valor precisa ser único.
- Separe as regras de negócio que o domínio deve aplicar das garantias que a persistência pode reforçar. Quando o armazenamento permitir, use restrições para proteger unicidade e integridade referencial. Se operações simultâneas puderem violar uma regra, defina como a escrita preserva essa regra sob concorrência.

## Consultas e ciclo de vida

- Parta das consultas que o serviço realmente fará. Registre os filtros, a ordenação e o volume esperado dos fluxos críticos. Quando houver necessidade de um índice, indique qual consulta ou restrição ele sustenta e avalie o custo adicional nas escritas.
- Quando o projeto exigir retenção, exclusão ou anonimização, defina por quanto tempo os dados ficam disponíveis, o que dispara a mudança e quais registros relacionados são afetados.
- Ao evoluir um modelo com registros existentes, use o [guia de migração de dados](migracao-de-dados.md) para descrever a transformação e os critérios de conclusão.

## Exemplo

Em uma API de tarefas privadas, cada tarefa pertence a uma conta. O modelo deve mostrar como essa relação é preservada, como o serviço restringe a listagem à conta autorizada e qual consulta precisa sustentar a ordenação da lista. Se essa consulta justificar um índice, registre os campos usados no filtro e na ordenação.
