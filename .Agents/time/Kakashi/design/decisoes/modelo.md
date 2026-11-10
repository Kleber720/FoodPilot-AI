# Modelo de registro de decisão de teste

Use este modelo no projeto em que a decisão foi tomada. Crie um registro por decisão que afete a estratégia de teste, os dados de teste, os níveis adotados ou a fronteira entre teste e implementação. Dê ao arquivo o prefixo de quem escreve e uma sequência própria, como `kakashi-001-teste-de-integracao-com-banco-real.md`.

## Título da decisão

**Data** — AAAA-MM-DD  
**Estado** — Proposta, aceita ou substituída

### Contexto

Descreva o comportamento a provar, os níveis disponíveis, o custo de execução e as restrições do projeto — banco, rede, tempo de suíte, dado sensível. Registre as premissas relevantes.

### Opções consideradas

Liste as opções realmente avaliadas. Para cada uma, diga o que ela prova bem, o que deixa de fora e quanto custa executar.

### Decisão

Declare o nível e a fronteira escolhidos, onde os testes ficam e quais dependências são reais ou simuladas. Diga o que não será provado por teste automatizado e por quê.

### Consequências e revisão

Registre o que a escolha permite refatorar com segurança, o tempo que a suíte passa a custar e o risco aceito — como uma integração provada apenas por simulação. Indique que mudança no requisito ou que evidência justificaria revisitar a escolha.

Se uma nova decisão substituir esta, marque o registro como substituído e vincule os dois documentos para preservar o histórico.
