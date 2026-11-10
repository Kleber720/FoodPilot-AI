# Sistema de design

Use o sistema de design do projeto como fonte de verdade para cor, tipografia, espaço, componentes e estados. Quando ele não existir, defina um núcleo pequeno e coerente com o propósito do produto e seu público antes de estilizar telas.

## Tokens

- **Cor.** Nomeie pelo papel, não pelo valor: `superficie`, `texto-secundario`, `acao-primaria`, `borda`, `perigo`, `sucesso`. O componente pede o papel; trocar a paleta não deve exigir editar componente.
- **Tipografia.** Defina a escala de tamanho, os pesos e a altura de linha. Tamanho avulso dentro de componente é exceção registrada, não regra.
- **Espaço.** Use uma escala única para margem, padding e espaçamento entre itens. Fora dela, o layout desalinha na terceira tela.
- **Forma e elevação.** Raio, sombra e camadas de sobreposição têm valores nomeados. `z-index` inventado no componente quebra a ordem de sobreposição da aplicação inteira.
- **Ponto de quebra e movimento.** Nomeie os breakpoints em que o layout muda de fato e a duração e a curva das transições. Movimento precisa respeitar `prefers-reduced-motion`, conforme o guia de [acessibilidade](acessibilidade.md).

Registre onde os tokens vivem no código e mantenha uma única fonte. O mesmo valor duplicado em dois lugares é o começo da divergência.

## Componentes

- Defina a anatomia e as variantes de cada componente compartilhado: tamanho, ênfase e tom. Variação que só existe em uma tela é estilo local, não variante.
- Cubra a matriz de estados: repouso, hover, foco, ativo, desabilitado, carregando e erro. Estado que o componente pode receber e não tem estilo é falha de sistema, não detalhe.
- Documente o componente onde ele é consumido: quando usar, quando não usar, props e um exemplo breve. Documentação de componente não substitui README do projeto.

## Evolução

- Antes de criar, procure. Reaproveitar token ou variante existente vale mais que valor novo.
- Escolha o nível certo: **token novo** quando falta um papel semântico; **variante nova** quando o componente existe e o uso é compartilhado; **componente novo** quando a responsabilidade é diferente. Registre o motivo.
- Ao mudar um token ou uma variante, liste os consumidores afetados e migre-os na mesma entrega, ou preserve os antigos até a migração. Mudança silenciosa em token compartilhado atinge telas que ninguém revisou.
- Tema claro e escuro, quando existirem, são conjuntos de valores para os mesmos papéis. O componente não deve saber qual tema está ativo.

## Verificação

Confira componentes e telas representativas em tamanho estreito e largo, nos estados de interação e nos temas existentes. Verifique contraste e foco por teclado conforme o guia de [acessibilidade](acessibilidade.md). Informe os consumidores atualizados e as verificações realizadas.
