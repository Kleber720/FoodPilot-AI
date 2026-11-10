# Monitoramento

Modelo entregue começa a envelhecer no dia seguinte. Monitorar é saber, antes do usuário, que o dado mudou, que a predição saiu da faixa ou que a métrica caiu — e ter critério para agir em vez de retreinar por susto.

## O que acompanhar

| Sinal | Por que importa | Como ver |
| --- | --- | --- |
| Volume e cobertura | extração quebrada ou recorte menor mudam a predição | contagem por período e por segmento |
| Esquema | coluna renomeada, tipo trocado, nulo novo | comparação com o contrato do data card |
| Distribuição das features | drift antes de a métrica cair | PSI, KS ou distância entre janelas |
| Distribuição da predição | modelo "achatando" ou disparando | média, faixa e taxa de positivo por período |
| Métrica real | o número que importa | quando o rótulo chega, comparar com a avaliação original |
| Custo e latência | modelo que não cabe na operação | tempo de inferência e volume processado |

Rótulo pode demorar. Enquanto ele não chega, acompanhe proxy: taxa de aceite, correção manual, reclamação. Proxy não substitui a métrica, mas avisa antes.

## Drift não é degradação

Dado diferente não significa modelo pior: a distribuição pode mudar e a relação com o alvo continuar. Antes de retreinar, confirme se a métrica caiu. Retreinar por drift sem medir pode trocar um modelo bom por um pior.

## Limiares e alerta

- Defina a janela de referência — o período usado no treino — e compare a janela atual com ela.
- Escolha limiares com o time, não no calor do incidente. Excesso de alerta treina todos a ignorar.
- Cada alerta tem dono e ação esperada: investigar, restringir escopo, retreinar ou desligar.
- Registre onde o monitoramento vive e como consultá-lo. Sem isso, o alerta é de quem estava de plantão.

## Retreino

Defina antes o gatilho, não depois do problema:

- **Gatilho** — métrica abaixo do critério de aceite, drift sustentado, mudança de negócio.
- **Janela** — quanto histórico entra no novo treino e por quê.
- **Reavaliação** — mesmo critério de aceite e mesmo rigor da avaliação original; experimento registrado como qualquer outro.
- **Publicação** — versão nova, comparação com a anterior e possibilidade de voltar.

## Quando investigar

Sinal que não fecha com o esperado vira investigação pela skill [investigar-falha-dados](../skills/investigar-falha-dados/SKILL.md): sintoma, causa confirmada, correção verificada no mesmo cenário. O que a investigação ensinar sobre sinal faltante volta para esta lista.
