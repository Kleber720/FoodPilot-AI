---
name: arbitrar-conflito
description: Resolve a discordância entre especialistas pela fonte da verdade — contrato, guia ou decisão registrada — e escala ao humano o que for decisão de produto.
---

# Arbitrar um conflito

1. **Separe relato de fato.** Peça a cada lado o que foi observado e com qual evidência: requisição, resposta, diff, tela. Relato sem evidência não entra na decisão.
2. **Vá à fonte da verdade.** Contrato documentado, guia de domínio (`docs/dominio/`), decisão registrada, registro em `problemas/`. Se a fonte responde, não há conflito: há um lado que não leu, e você devolve a referência.
3. **Decida pela fronteira de escopo e pelo custo de reversão.** Se a fonte não responde: quem é dono do comportamento decide o formato; a opção mais fácil de desfazer é a padrão. Não invente terceira via.
4. **Registre a decisão** no formato de [`decisoes/modelo.md`](../../design/decisoes/modelo.md), no projeto. Decisão sem registro volta na próxima entrega como se nunca tivesse existido.
5. **Comunique o mesmo texto aos dois.** Decisão, não versão da decisão. Os dois recebem o mesmo parágrafo e o mesmo registro.
6. **Pare no que é de produto.** Mudar contrato público, cortar escopo, aceitar risco: pergunte ao humano com a opção recomendada, e não decida por ele.
7. **Não divida a diferença, não vote, não deixe cada um seguir do seu jeito.** Meio caminho entre dois contratos é um terceiro contrato sem dono.

## Quando não é conflito

- **Falta de informação:** ligue as partes e peça o dado; não decida por quem tem menos contexto.
- **Triagem de registro:** é do Kakashi. Ele decide o dono e o critério de verificação; sua decisão é sobre a ordem, não sobre a procedência.
- **Preferência de implementação:** não é conflito. Quem é dono do código escolhe e segue.
