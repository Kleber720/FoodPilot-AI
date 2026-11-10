---
name: registrar-problema
description: Registra na pasta problemas/ um problema que exige correção de outra pessoa — outra camada, ou a regra que o Kakashi revelou com um teste — quando o comportamento encontrado não pode ser corrigido dentro do próprio escopo.
---

# Registrar um problema entre camadas

O registro substitui o aviso no retorno. Ele é o artefato que o agente de TDD vai triar, delegar e verificar, e por isso precisa de evidência e de comportamento esperado, não de opinião.

## Quando registrar

Registre quando o trabalho esbarrar em algo que pertence à outra camada:

- a resposta ou a ausência de resposta da API impede o fluxo da tela;
- falta um campo, um filtro, um estado ou um erro que o front-end precisa tratar;
- o front-end envia dados fora do contrato, chama rota inexistente ou ignora um erro previsto;
- uma operação legítima recebe acesso negado ou um recurso de outra conta aparece.

Não use a pasta para:

- defeito dentro da própria camada — corrija e siga a skill da tarefa. A exceção é o Kakashi: a regra que ele revelou com um teste entra como `tipo: devolutiva`, porque a correção é de quem escreveu o código;
- entrega de trabalho pronto, comandos, contratos ou resultados de verificação — isso continua no retorno ao coordenador;
- dúvida que se resolve lendo o contrato ou a documentação do projeto.

## Antes de escrever

1. Confirme que o problema não está no seu lado. Reproduza, leia o contrato documentado e verifique a versão em uso antes de atribuir a falha à outra camada.
2. Isole o ponto de integração: qual rota, componente, arquivo ou fluxo. Separe o que você observou do que você supõe ser a causa.
3. Descreva o comportamento necessário, não a implementação do outro lado. "A listagem filtrada precisa devolver a contagem total do filtro" é um problema; "adicione o campo `total` no agregado" é uma decisão que cabe ao responsável.
4. Confira se o item já está no escopo da entrega em curso, no plano em `entregas/`. Se estiver, informe o coordenador em vez de abrir: registro do que já está planejado vira duplicata na fila.

## Escrever o registro

1. Copie o [modelo](../../../problemas/modelo.md) para `problemas/<autor>-NNNN-<slug>.md`, com o próximo número livre do **seu** prefixo e um slug curto do sintoma.
2. Preencha o cabeçalho — com `projeto` igual ao do plano de entrega — e as seções até **Hipótese de causa**. Deixe **Critério de verificação**, **Triagem**, **Correção** e **Verificação final** vazias: elas pertencem a quem tria, corrige e verifica.
3. Ajuste a severidade pelo impacto, não pelo esforço: `critica` bloqueia um fluxo em produção, `alta` bloqueia a entrega em andamento, `media` tem contorno aceitável, `baixa` é incômodo conhecido.
4. Use dados sintéticos ou anonimizados. Não copie credenciais, tokens nem dados de clientes para o arquivo.

## Depois de registrar

1. No retorno ao coordenador — ou no chat, quando você for usado direto — informe apenas o número e o título do registro, para o time saber que ele existe. Não repita o conteúdo: o detalhe está no arquivo.
2. Continue a parte da tarefa que ainda pode ser entregue com o contrato atual.
3. Se precisar de um contorno temporário no seu lado para não travar a entrega, registre no arquivo o que foi feito e por que ele deve ser removido quando a correção chegar.

## Se você é o Kakashi

O registro nasce de um teste que falha. Marque `tipo: devolutiva`, preencha **Evidência** com o caso mínimo e a saída do teste e **Devolutiva** com a regra esperada e o comportamento necessário. Na triagem, preencha **Critério de verificação** e delegue; **Correção** e **Verificação final** continuam com quem corrige e quem verifica.

## Se a triagem apontar para a sua camada

Corrija dentro do seu escopo, preencha **Correção** com o que mudou e como você verificou, e mova o estado para `corrigido`. Não feche o registro: quem não fez a correção é quem verifica.

## Estados

| Estado | Quem move para ele |
| --- | --- |
| `aberto` | quem abriu o registro |
| `em-triagem` | agente de TDD, ao começar a avaliação |
| `devolvido` | agente de TDD, quando falta evidência ou o problema não procede como descrito |
| `delegado` | agente de TDD, ao apontar o responsável e o critério de verificação |
| `corrigido` | agente responsável, com a correção e a verificação registradas |
| `verificado` | agente de TDD ou quem abriu, após conferir a correção |
| `descartado` | agente de TDD, quando o problema não procede ou não é desta camada |

A Tsunade, coordenadora, **lê** a fila e decide a ordem de ataque; não move estado, não preenche triagem e não altera evidência. No máximo, uma linha no Histórico. Por isso ela não abre registro: devolve ao dono, que abre com a evidência que ela viu.

## Limites

- Não edite a evidência nem o sintoma escritos por outro autor. Acrescente uma linha no **Histórico** e argumente ali.
- O registro não autoriza mexer na outra camada: o [AGENTS.md da Sakura](../../../Sakura/AGENTS.md) continua valendo, e o Lee segue responsável pelo servidor, pelas APIs, pelas regras de negócio do servidor, pelo banco e pelas migrações.
- Registro não substitui README, e README não substitui registro. A criação e a edição de READMEs continuam com a Tsunade.
