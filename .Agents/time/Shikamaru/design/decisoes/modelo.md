# Modelo de registro de decisão de dados

Use este modelo no projeto em que a decisão foi tomada. Crie um registro por decisão que afete a modelagem, a avaliação, a origem dos dados ou o formato de entrega, e que seja difícil de reverter. Dê ao arquivo o prefixo de quem escreve e uma sequência própria, como `shikamaru-001-usar-gradient-boosting-em-vez-de-regressao-logistica.md`.

## Título da decisão

**Data** — AAAA-MM-DD  
**Estado** — Proposta, aceita ou substituída

### Contexto

Descreva a pergunta do projeto, os requisitos que pesam na escolha — volume de dado, custo do erro, prazo, restrição de privacidade — e os fluxos ou consumidores afetados. Registre as premissas relevantes, como a qualidade da fonte e a disponibilidade do rótulo.

### Opções consideradas

Liste as opções realmente avaliadas. Resuma o que cada uma entrega em métrica, custo de treino e de operação, interpretabilidade e risco. Inclua a linha de base como opção: manter a regra simples é decisão legítima.

### Decisão

Declare o que foi escolhido, por que atende ao cenário e o que muda no pipeline, na avaliação ou na entrega. Registre a métrica de aceite e o conjunto em que ela foi medida.

### Consequências e revisão

Registre os benefícios esperados, os custos aceitos — tempo de treino, inferência, manutenção, dependência de biblioteca — e o que precisa ser verificado depois. Indique que mudança nos requisitos ou que evidência justificaria revisitar a escolha, como degradação em produção ou mudança de contrato na fonte.

Se uma nova decisão substituir esta, marque o registro como substituído e vincule os dois documentos para preservar o histórico.
