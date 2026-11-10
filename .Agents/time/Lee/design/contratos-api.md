# Contratos de API

Use a especificação adotada pelo projeto como referência e mantenha os exemplos e o comportamento observado da API alinhados com ela. Use os termos do negócio do contexto responsável pela operação e traduza o modelo interno em campos e comportamentos que os consumidores possam usar.

## O que especificar por operação

- **Identificação e efeito.** Registre o objetivo, os consumidores, o método e a rota ou o equivalente no protocolo adotado. Descreva o efeito esperado e, se a execução for assíncrona, diferencie o aceite da conclusão e indique como consultar o resultado.
- **Entradas.** Defina campos, tipos, formatos, valores permitidos e limites. Diferencie campos obrigatórios, opcionais, omitidos e nulos quando essa distinção mudar o comportamento. Explique valores padrão, filtros e ordenação.
- **Respostas.** Documente os estados de sucesso, o formato dos dados e um exemplo com valores fictícios. Em listagens, defina a ordenação padrão, como pedir a próxima página e quais limites de tamanho se aplicam.
- **Erros.** Use o formato de erro do projeto. Documente o status ou código que o consumidor pode tratar para entrada inválida, falta de acesso, recurso ausente ou conflito de negócio, conforme a operação. Inclua a ação esperada do consumidor quando couber e mantenha detalhes internos e dados sensíveis fora da resposta.
- **Acesso.** Especifique como autenticar, quais permissões são exigidas e quem pode ler ou alterar cada recurso. Em APIs com dados privados, defina a resposta esperada para tentativas de acesso a recursos de outra conta ou organização.
- **Novas tentativas e repetição de escritas.** Documente quais falhas permitem uma nova tentativa e, quando aplicável, quanto tempo o consumidor deve aguardar. Se uma escrita puder ser reenviada após falha ou perda de resposta, descreva o resultado esperado da repetição. Quando houver chave de idempotência, especifique como enviá-la, por quanto tempo ela vale e qual resposta o consumidor recebe se reutilizar a chave com dados diferentes.

## Evolução do contrato

Antes de mudar um contrato em uso, identifique os consumidores afetados e confira o comportamento que eles já utilizam. Avalie alterações de tipo, obrigatoriedade, valores padrão, ordenação, permissões e erros. Para uma quebra autorizada, descreva como os consumidores vão migrar e quais versões precisam coexistir durante a transição.

