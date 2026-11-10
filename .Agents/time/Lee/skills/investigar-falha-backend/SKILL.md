---
name: investigar-falha-backend
description: Investigar erro, regressão ou incidente em um back-end, isolar a causa com evidência e verificar a correção no mesmo cenário que falhou.
---

# Investigar uma falha de back-end

1. Registre o sintoma antes de mexer em qualquer coisa: o que o consumidor vê, desde quando, em qual fluxo e com qual impacto. Sintoma vago ("está lento") não guia investigação.
2. Separe as causas possíveis antes de abrir o editor: **o código mudou** (regra, contrato, dependência, versão), **o dado mudou** (registro inválido, volume, estado de migração) ou **o ambiente mudou** (configuração, credencial, serviço externo). Cada uma pede evidência diferente.
3. Compare com a última execução saudável — commit, log, versão de dependência, estado do banco. O que mudou entre as duas é o suspeito principal.
4. Teste uma hipótese por vez, com evidência: log, métrica, teste que reproduz ou requisição. Diferencie causa confirmada de suspeita; hipótese sem evidência não entra no relatório. Ao reproduzir, use dados sintéticos e preserve credenciais.
5. Corrija só o que é do servidor e dentro do escopo. Se a evidência apontar para o front, para o contrato ou para a fonte de dados, abra um registro seguindo a skill [`registrar-problema`](../../../comum/skills/registrar-problema/SKILL.md) e siga com o que ainda se pode entregar.
6. Reproduza o cenário original depois da correção, pela interface do consumidor, e verifique o que a mudança pode ter atingido: fluxo vizinho, validação, autorização, persistência.
7. Registre o que a investigação ensinou: o sinal que deveria ter alertado antes e a verificação que faltava. Falha que volta sem sinal novo volta do mesmo jeito.

Informe: o sintoma, a causa confirmada com a evidência, a correção e o resultado da verificação. O que não foi confirmado fica dito como hipótese. Se a verificação essencial não foi possível, a entrega é parcialmente validada.
