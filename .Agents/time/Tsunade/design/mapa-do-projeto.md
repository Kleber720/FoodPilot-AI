# Mapa do projeto

O mapa é o primeiro artefato do time no projeto. Ele responde "onde eu estou e o que já existe" antes de qualquer entrega, e é o que impede quatro especialistas de redescobrir a mesma coisa em paralelo — ou de receber uma instrução sem saber onde ela se encaixa.

Vive em `docs/mapa-do-projeto.md`, escrito pela Tsunade no reconhecimento. É **raso e completo**: estrutura, comandos, estado, fontes da verdade, riscos. Não é documentação de código, não é contrato e não é README — ele aponta para eles.

| O mapa é | O mapa não é |
| --- | --- |
| onde ficam as coisas e como rodar | explicação de cada arquivo |
| o estado real do projeto | a lista de desejos do time |
| o índice das fontes da verdade | substituto do contrato ou do guia de domínio |
| o briefing que cada agente recebe | o plano da entrega |

## Modelo

````markdown
# Mapa do projeto — <nome>

**Atualizado em** AAAA-MM-DD · **Dono** Tsunade
**Escopo** <pasta ou repositório; o que está fora e não é deste projeto>

## Stack

<Linguagem, framework, banco e ferramentas, conforme `comum/stacks.md` ou a stack própria do projeto. Se for própria, link para a decisão registrada.>

## Como rodar

| Comando | O que faz | Verificado em |
| --- | --- | --- |
| `<comando>` | instalar / rodar / testar / migrar / buildar | AAAA-MM-DD, ou "a verificar" |

## Estrutura

<Árvore curta, uma linha por pasta relevante, com a responsabilidade de cada uma. Onde ficam as regras, os testes, a configuração e os artefatos.>

## Estado

- **Funciona:** <o que foi exercitado, com a evidência>
- **Pela metade:** <o que existe mas não completa o fluxo>
- **Quebrado:** <o que falha, com o sintoma>
- **Sem teste:** <onde a ausência de teste é risco conhecido>

## Fontes da verdade

| Fonte | Onde | Estado |
| --- | --- | --- |
| Contrato | `docs/contrato.md` | atualizado / desatualizado / não existe |
| Guia de domínio | `docs/dominio/` | |
| Decisões | `docs/decisoes/` | |
| Matriz de regras | `docs/matriz-de-regras.md` | |
| Data cards | `docs/dados/` | |
| Registros abertos | `problemas/` | <quantos por estado> |

## Riscos

<O que pode quebrar a próxima entrega: dependência frágil, ausência de teste em regra crítica, contrato ambíguo, ambiente que não sobe.>

## O que cada camada precisa saber

| Camada | Onde olhar | O que evitar |
| --- | --- | --- |
| Back-end | <pastas, contrato, guia de domínio> | <ex.: camada de infraestrutura que não deve ser tocada> |
| Front-end | <telas, componentes, tokens> | |
| Teste | <comando da suíte, matriz, fixtures> | |
| Dados | <fonte, schema, data card> | |

## Lacunas

<O que ficou sem mapear e por quê. O que falta e bloqueia vira registro em `problemas/`.>
````

## Regras

- **Atualize** quando a estrutura, os comandos ou o estado mudarem — na mesma entrega em que a mudança entrar.
- **Comando sem execução** é "a verificar", nunca "funciona".
- **Estado sem evidência** é impressão: diga o comando ou a requisição que provou.
- **Lacuna declarada** é melhor que mapa silencioso: o que ficou de fora fica dito.
- A partir do mapa, cada delegação leva o caminho dele e os arquivos que o especialista deve ler. Instrução sem mapa é ordem para explorar do zero.
