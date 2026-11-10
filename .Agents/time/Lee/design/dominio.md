# Guia de domínio

O contrato diz o que a API aceita e devolve. O guia de domínio diz o que a regra de negócio exige — inclusive o que o contrato não expressa. É a segunda fonte da verdade do time: o Kakashi deriva casos de teste dele, a Tsunade arbitra por ele, a Sakura lê para saber o que a tela pode assumir e o Shikamaru para saber o que o dado significa.

Regra que só existe no código é dívida: ou entra aqui, ou vira devolutiva. "Não estava escrito em lugar nenhum" não é desculpa para supor.

## Onde vive

`docs/dominio/<contexto>.md`, um arquivo por contexto delimitado. Projeto com um contexto só usa `docs/dominio/dominio.md`. Cada arquivo tem dono: o Lee. Atualizado na mesma entrega que muda a regra.

## O que registra

- **Termos.** A linguagem ubíqua: o termo, o que significa no negócio, os sinônimos rejeitados e os termos ambíguos já resolvidos. "Tarefa" e "item" não podem ser a mesma coisa em dois lugares.
- **Invariantes.** O que precisa continuar verdadeiro depois de qualquer operação, mesmo quando duas escritas concorrem.
- **Regras.** Uma frase por regra, com o caso válido, as exceções e o que acontece no limite. Regra com "depende" não está escrita.
- **O que o contrato não expressa.** Validação cruzada, transição de estado, permissão de negócio que não é papel da API, ordem de precedência entre regras.
- **Decisões de negócio.** Quem decidiu, quando, e o que muda no comportamento se a decisão mudar. Link para o registro de decisão quando houver.
- **Histórico.** Data e o que mudou.

## Como escrever

- Descreva comportamento, não implementação: "tarefa concluída não volta para pendente" é regra; "o service lança 409" é implementação.
- Nomeie pelo termo do negócio, o mesmo do código e do teste.
- Cada regra precisa ser verificável: se ninguém consegue dizer "passou" ou "falhou" olhando o comportamento, ainda não é regra.
- Regra que o time não sabe responder vira pergunta em aberto, não suposição escrita no arquivo.

## Exemplo

```markdown
### Regra — tarefa concluída não volta para pendente

- **Termo:** tarefa (unidade de trabalho de uma conta).
- **Válido:** criar, listar, concluir e reabrir tarefa ainda pendente.
- **Exceção:** reabrir tarefa concluída devolve 409 e mantém o estado.
- **Limite:** reabrir a mesma tarefa duas vezes devolve 409 nas duas.
- **Contrato:** documentado em `docs/contrato.md`, operação `PATCH /tarefas/{id}`.
- **Fonte:** pedido de 12/10, confirmado com o produto.
```

## Limites

- Não é README, não é contrato de API, não é o código, não é a matriz de regras. A matriz aponta qual teste protege a regra; o guia diz qual é a regra.
- Não copie o contrato nem repita a implementação: o que já está no contrato só entra aqui se o contrato não disser o suficiente.
- Guia desatualizado é pior que guia ausente: parece confiável e manda o teste provar a regra errada.
