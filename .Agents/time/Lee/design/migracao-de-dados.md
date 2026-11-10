# Design de migração de dados

Descreva a transformação do estado atual para o estado desejado antes de implementar a migração.

- **Origem e destino.** Registre quais registros entram na migração, como os campos e identificadores são mapeados e qual contexto do domínio é responsável pelos dados. Explicite as relações e regras de negócio que precisam ser preservadas.
- **Dados legados.** Defina o tratamento de registros com valores ausentes, duplicados ou incompatíveis. Quando a conversão depender de uma decisão de negócio, registre o caso e confirme a regra antes de transformar esses registros.
- **Transição.** Escolha entre uma mudança em uma etapa e uma transição gradual conforme volume, bloqueios e tolerância a interrupção. Se houver escrita concorrente, indique qual estrutura é a fonte de verdade em cada etapa e como as alterações feitas durante a cópia chegam ao destino. Consulte [evolução em produção](arquitetura.md#evolução-em-produção) para a convivência entre versões.
- **Critérios de conclusão.** Defina quais registros devem existir no destino, quais exceções são aceitáveis e como conferir as relações e regras preservadas. Se houver uma estrutura antiga, registre a condição para desativá-la.
