# Dados de teste

O dado sintético é parte do teste: precisa ser explícito, determinístico e descartável. Dado de produção, credencial real e registro que sobra de outra execução não entram na suíte.

## Regra do dado

- **Sintético ou anonimizado.** Nunca copie nome, e-mail, documento ou token real para teste, fixture ou log.
- **Explícito.** O valor que importa fica escrito no teste. Aleatório só quando a regra for sobre variação — e aí a semente é fixa.
- **Determinístico.** Congele relógio, identificador e ordenação. `agora()` sem injeção é a causa mais comum de teste intermitente.
- **Descartável.** Cada teste cria o que precisa e remove o que criou, ou roda em transação revertida. Nada depende de outra execução.

## Factories e fixtures

| Recurso | Use para |
| --- | --- |
| factory | variação: a mesma entidade com um campo diferente por teste |
| fixture nomeada | caso específico que precisa ser lido e reconhecido, como `tarefaDeOutraConta` |
| massa compartilhada | só quando inevitável; documente no suporte e trate como somente leitura |

A factory devolve o registro criado e aceita sobrescrita explícita: `criaTarefa({ concluida: true })`. O padrão da factory não pode esconder a regra que o teste prova.

## Isolamento entre contas

Toda regra de acesso precisa de dois lados: a conta dona e a conta alheia. Monte as duas no mesmo teste, com dados distinguíveis — títulos diferentes, não "tarefa 1" e "tarefa 1". Confira também que a conta alheia não vê o recurso na listagem, não só que o acesso direto falha.

## Casos que o dado precisa cobrir

- valores de fronteira: vazio, zero, negativo, máximo aceito, texto no limite;
- texto fora do comum: acento, emoji, direção de escrita diferente, espaço no início e no final;
- nulo e ausente, quando o contrato os distingue;
- dinheiro em centavos, nunca em ponto flutuante;
- falha de dependência: serviço fora, tempo esgotado, resposta parcial.

## Limpeza e segredos

- Remova o que criou, mesmo no caminho de falha. Teste que vaza registro contamina a próxima execução.
- Configure credenciais e endpoints por variável de ambiente, com valor fictício versionado em `.env.example`.
- Não imprima payload com token nem cabeçalho de autenticação na saída do teste.
