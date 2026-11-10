# Acessibilidade

Acessibilidade é parte do critério de pronto de qualquer tela, não uma etapa final. Verifique o que segue em cada entrega, não só quando a tarefa pedir.

## Estrutura e semântica

- Use o elemento nativo que já carrega o comportamento: `button` para ação, `a` para navegação, `label` para rótulo, `nav`, `main` e `header` para regiões. O nativo entrega teclado e leitor de tela de graça.
- Use ARIA só quando o HTML não resolve, e nunca para compensar comportamento ausente. `role` sem o comportamento correspondente piora a experiência.
- Mantenha a hierarquia de títulos em ordem, sem pular nível por motivo visual. A tela tem um título principal.
- O que parece link é link e o que dispara ação é botão. `div` clicável não recebe foco nem responde a Enter.

## Teclado e foco

- Todo controle alcançável por mouse precisa ser alcançável por Tab e acionável por Enter ou Espaço.
- Foco visível sempre. Remover o contorno sem oferecer substituto é falha, não escolha estética.
- Em modal e menu, prenda o foco dentro do componente enquanto ele estiver aberto, devolva o foco ao gatilho ao fechar e feche com Esc.
- Não capture tecla globalmente sem devolver o comportamento padrão do navegador.
- Ao trocar de tela por rota, mova o foco para o título ou para a região principal, para o leitor de tela não continuar no lugar anterior.

## Percepção

- Contraste mínimo de 4.5:1 para texto e 3:1 para ícone e borda de componente interativo.
- Nunca use cor como único sinal de estado. Erro precisa de texto ou ícone além do vermelho.
- Suporte zoom de 200% e texto ampliado sem perda de conteúdo nem sobreposição.
- Toda imagem tem `alt` com o que ela informa; imagem decorativa tem `alt` vazio.

## Formulários e mensagens

- Rótulo associado ao campo por `label`/`for` ou por `aria-label`. Placeholder não substitui rótulo.
- Mensagem de erro junto ao campo, ligada por `aria-describedby` e anunciada em região `aria-live` quando aparecer depois da interação.
- Não use o botão desabilitado como única defesa contra envio inválido: diga o que falta.
- Mensagem de erro e de sucesso que muda sem recarregar a página precisa ser anunciada.

## Movimento

Respeite `prefers-reduced-motion`: animação essencial pode permanecer, animação decorativa deve ser desligada.

## Como verificar

Percorra o fluxo inteiro só com teclado, da abertura ao envio e ao fechamento, e confira onde o foco está em cada passo. Verifique o contraste do texto e dos estados interativos. Rode a verificação automatizada de acessibilidade que o projeto tiver e trate o que ela aponta, mesmo que o problema seja anterior à sua mudança. Quando possível, teste com leitor de tela.
