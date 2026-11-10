# Fluxo de trabalho

Este é o ciclo do Kakashi sobre uma entrega do Lee. As skills descrevem cada tarefa; aqui ficam a ordem, o que precisa estar pronto antes de avançar e para quem vai cada saída.

## Entradas

- **Entrega do Lee:** o que ele informou no chat, o contrato documentado, o guia de domínio (`docs/dominio/`) e o código no repositório. Regra que não está no contrato nem no guia de domínio é suposição: confirme ou devolva.
- **Registro em `problemas/`:** sintoma, evidência e comportamento esperado.
- **Cenário de avaliação:** quando a tarefa é conferir a entrega inteira, é o **Aceite** do plano em [`entregas/`](../../entregas/modelo.md). O resultado segue o formato do [modelo de avaliação](modelo-de-avaliacao.md).

## Sequência

1. **Ler a regra.** Contrato, guia de domínio e decisões registradas. Sem isso o teste nasce da implementação e não prova nada.
2. **Auditar o que já existe.** Inventário de regras e lacunas por risco — [auditar cobertura](../skills/auditar-cobertura-de-regras/SKILL.md) e [matriz de regras](matriz-de-regras.md).
3. **Provar o que falta.** Uma regra por vez, vermelho antes do verde — [testar regra](../skills/testar-regra-de-negocio/SKILL.md).
4. **Devolver o que falhar.** Regra ausente ou divergente vira devolutiva para o Lee; não se corrige aqui.
5. **Refatorar só com verde e sem devolutiva aberta no mesmo trecho.** Misturar correção e reestruturação tira a referência de comportamento — [refatorar com testes](../skills/refatorar-com-testes/SKILL.md) e [refatoração segura](refatoracao-segura.md).
6. **Atualizar a matriz** na mesma entrega que criou o teste.
7. **Relatar:** regras cobertas, comando e resultado, lacunas e registros.

Refatoração antes de teste é reescrita sem rede. Correção antes de devolutiva é o teste passando por construção.

## Portões

Uma entrega só é "coberta" quando:

- toda regra crítica tem teste que falha quando a regra é quebrada;
- nenhum teste foi enfraquecido, removido ou ignorado para ficar verde;
- a matriz está atualizada e as lacunas restantes estão ditas, com risco;
- as devolutivas geradas estão abertas, com critério de verificação executável;
- a suíte roda do zero, em ambiente limpo, com o comando informado.

Portão que não passou é dito como pendência. Não se declara coberto o que não foi exercitado.

## Handoffs

| Situação | Vai para |
| --- | --- |
| regra ausente, errada ou fora do contrato | Lee, com `tipo: devolutiva` |
| comportamento de front-end fora do contrato | Sakura, com `tipo: problema` |
| contrato precisa mudar | Lee, decisão dele, com registro de decisão |
| correção registrada como `corrigido` | volta para verificação |
| dúvida que o contrato não responde | o autor do pedido, não uma suposição |

## Estados do registro

O ciclo usa os estados do [modelo de registro](../../problemas/modelo.md): `aberto` → `em-triagem` → `delegado` → `corrigido` → `verificado`, com `devolvido` e `descartado` nos casos sem evidência ou sem procedência. Quem move cada estado está na skill [registrar-problema](../../comum/skills/registrar-problema/SKILL.md).

## Quando não há como verificar

Falta ambiente, integração ou dado? Registre a limitação e entregue o que foi provado. Simulação não substitui a verificação que o critério exige, e a entrega fica como parcialmente validada.
