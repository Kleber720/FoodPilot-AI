# Refatoração segura

Refatorar é mudar a estrutura sem mudar o comportamento. O teste é o que define "sem mudar o comportamento": se a suíte não cobre o trecho, a primeira tarefa é cobrir, não reestruturar.

## Antes de tocar

1. Confirme a suíte verde e guarde a saída. É a linha de base.
2. Localize os consumidores do código: quem chama a função, quem lê o tipo, quem depende do formato. Consumidor fora da suíte é risco que você não mede.
3. Se o trecho não tem teste, escreva um teste de caracterização que registre o comportamento atual — inclusive o estranho — antes de mudar. Caracterização não julga: congela o que existe.
4. Nomeie o cheiro e a estrutura pretendida em uma frase. Sem alvo claro, a refatoração vira reescrita.

## Durante os passos

- Um passo por vez, pequeno o suficiente para ser revertido sozinho.
- Rode a suíte entre os passos. Vermelho significa reverter o passo, não ajustar o teste.
- Não misture refatoração com correção de comportamento nem com recurso novo. Se precisar dos dois, entregue o registro do defeito primeiro.
- Não troque dependência, framework, versão, schema, migração nem contrato público. Isso não é refatoração.
- Preserve a interface pública. Se a mudança de assinatura for inevitável, atualize todos os consumidores no mesmo passo e confirme a suíte verde.
- Pare quando o alvo foi alcançado. Refatoração sem critério de parada vira churn.

## Cheiros que valem a pena

Função longa com mais de um motivo para mudar; regra de negócio presa no controller ou na consulta; a mesma regra duplicada em dois pontos; dependência de infraestrutura dentro do domínio; estado mutável compartilhado; condicional aninhada que esconde uma tabela de decisão; nome que não diz o que a regra faz.

Cheiro sem impacto no custo de mudar não é prioridade. Refatore o que atrapalha a próxima entrega.

## Depois

- Suíte verde com a mesma cobertura de comportamento, e os testes que já existiam **sem alteração de asserção**.
- Compare a saída antes e depois: os mesmos testes, os mesmos resultados.
- Informe o ganho concreto — o que ficou mais fácil de mudar — e não apenas "código mais limpo".
- Se um passo revelou defeito de comportamento, pare a refatoração e abra a devolutiva. Não conserte no meio.
