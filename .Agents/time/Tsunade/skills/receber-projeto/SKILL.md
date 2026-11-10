---
name: receber-projeto
description: Recebe um projeto — pasta, repositório ou código existente —, mapeia estrutura, stack, comandos reais, estado, fontes da verdade e lacunas, e entrega o mapa que orienta o primeiro plano e as delegações.
---

# Receber um projeto

O mapa segue o [modelo do mapa](../../design/mapa-do-projeto.md) e vive em `docs/mapa-do-projeto.md`. Ele é o primeiro artefato do time no projeto: sem ele, cada especialista redescobre a mesma coisa e o plano nasce no escuro.

1. **Confirme o escopo.** Qual pasta ou repositório é o projeto, o que está dentro, o que está fora (outro serviço, outro repositório, ambiente de terceiro) e o que você pode ler. Projeto que começa no lugar errado contamina todo o resto.
2. **Leia raso e completo, não fundo.** Estrutura de pastas, configuração, dependências, README, docs, lista de testes e comandos. Não leia cada arquivo de código: profundidade é do especialista, e o mapa existe para dizer onde ele deve olhar.
3. **Descubra os comandos reais.** Como instalar, rodar, testar, migrar e buildar — e se algum funciona de fato. Comando que ninguém rodou não entra como verdade: entra como a verificar.
4. **Descreva o estado com evidência.** O que existe e funciona, o que está pela metade, o que está quebrado, o que não tem teste. "Parece ok" não é estado; "roda e responde 200" é.
5. **Localize as fontes da verdade.** Contrato, guia de domínio, decisões, registros abertos, matriz de regras, data cards. Para cada uma: existe, está atualizada ou falta? O que falta vira lacuna declarada — e, se bloquear trabalho, vira registro.
6. **Escreva o mapa** no modelo: identificação, stack, como rodar, estrutura, estado, fontes da verdade, riscos e o que cada camada precisa saber.
7. **Proponha as primeiras entregas.** O reconhecimento fecha com uma lista curta do que dá para fazer primeiro, o que depende do quê e o que precisa de decisão humana. Não é o plano completo: é o insumo dele.
8. **Delegue com o mapa.** Cada especialista recebe o caminho do mapa e os arquivos que deve ler, além do recorte da etapa. Instrução sem mapa é ordem para explorar do zero.

## Limites

- Você não conserta o projeto no reconhecimento: achado que exige correção vira registro ou entrega, não edição.
- O mapa não substitui contrato, guia de domínio nem README: ele aponta para eles.
- Mapa desatualizado é pior que mapa ausente: atualize quando a estrutura, os comandos ou o estado mudarem.
- Projeto grande não vira leitura infinita: se algo não couber, diga no mapa o que ficou sem mapear.
