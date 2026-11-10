---
name: migrar-dados
description: Preparar e validar migrações de esquema, conversões de registros ou preenchimentos retroativos de dados em um back-end.
---

# Migrar dados

1. Inspecione o esquema atual, as migrações anteriores e os registros afetados. Identifique quais restrições e relações precisam ser preservadas.
2. Defina a ordem entre migração e deploy. Se versões antigas e novas do serviço puderem coexistir, teste ambas com o esquema intermediário.
3. Defina como retomar ou recuperar a operação se ela falhar no meio. Para mudanças irreversíveis, descreva como recuperar os dados antes da execução. Quando a operação admitir nova tentativa, verifique o efeito da reexecução sobre dados já processados.
4. Ensaie pelo comando de migração do projeto em um ambiente de teste com dados representativos, sintéticos ou anonimizados. Verifique o estado dos registros depois da execução e confira as restrições afetadas.
5. Execute em produção somente com autorização explícita para essa execução.

Informe a ordem de execução, a forma de recuperação, as verificações realizadas e as pendências. Se faltar uma verificação essencial, descreva a migração como parcialmente validada.
