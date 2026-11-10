---
name: investigar-falha-frontend
description: Investiga falhas de renderização ou interação e regressões visuais observadas no front-end. Use quando a tarefa começa por um defeito ou sintoma a diagnosticar.
---

# Investigar falha no front-end

1. Reproduza a falha pelo fluxo afetado. Registre os passos, o resultado observado e o esperado, além do navegador, do tamanho da tela ou do estado inicial quando forem relevantes. Para regressões visuais, procure a referência ou o padrão anterior.
2. Isole a causa com evidências da interface. Conforme o sintoma, examine o DOM, os estilos computados, o console, o estado dos componentes e as requisições e respostas observáveis no navegador. Compare a integração com o contrato documentado da API, use o guia de [estados e erros](../../design/estados-e-erros.md) para distinguir erro do servidor, falha de rede e estado que a tela não tratou, e diferencie causa confirmada de hipótese.
3. Corrija somente o que estiver no front-end, conforme o [AGENTS.md da Sakura](../../AGENTS.md). Se a evidência apontar para o back-end, abra um registro em [problemas/](../../../problemas/modelo.md) seguindo a skill [registrar-problema](../../../comum/skills/registrar-problema/SKILL.md), com os passos de reprodução, o ponto de integração, o resultado esperado, o observado e a evidência relevante. Remova credenciais e dados sensíveis dos registros.
4. Repita a reprodução original após corrigir e verifique os fluxos diretamente afetados. Informe o resultado e qualquer limitação de reprodução ou verificação.
