# Conteúdo v2: origem de cada captura e trecho

Formato: repositório · caminho@commit. Tudo foi lido sem alterar os repositórios de origem.

## Trechos "por trás" (fonte/conteudo/por-tras/)
| Projeto | Arquivo | Origem |
|---|---|---|
| fakly | fakly.txt (19 linhas) | misterioso013/fakly · main.js, linhas 12-30 @4c3ea1a |
| sendany | sendany.txt (15 linhas) | misterioso013/sendany · src/lib/database.ts, linhas 29-43 @1117310 |
| amott | amott.txt (4 linhas) | CaioGuerras/amott-perfumes · index.html, linhas 30-33 @00aa67a |
| heisuca | heisuca.txt (9 linhas) | heisuca · apps/app/lib/heisuca/theme/temas/tema_hisui.dart, linhas 10-18 @9755d4a (ramo claude/heisuca-v2) |
| cgflix-lite | cgflix-lite.txt (23 linhas) | cgflix-lite · core/src/main/java/dev/jdtech/jellyfin/core/presentation/theme/CgflixPalette.kt, linhas 54-76 @8aa925d |
| prosup | sem trecho (`por_tras: null`) | sem repositório disponível |

No site, o campo `origem` do cgflix-lite traz só `CgflixPalette.kt@8aa925d`: o caminho completo tem o nome do servidor de mídia e não pode aparecer num texto do app. O caminho completo fica só neste documento. Os trechos são cópias sem edição (só cortes).

## Capturas de frente (assets/frente/, até 960 px)
- amott, fakly, sendany: captura do site no ar (Chromium, 960x600), em 2026-11-23.
- heisuca: phoneScreenshots_2.png do material da loja (~/TMP/loja-play/backup_20261116), reduzida de 1080x1920 para 540x960.
- cgflix-lite: tela inicial baixada da página da Google Play (540x960).

## Lojas (assets/loja/, 540 px)
Recortes da página móvel da Google Play (Chromium, viewport 540, 2026-11-23): cabeçalho, faixa de capturas e "Segurança dos dados". Heisuca: app.heisuca.player. CGFLIX Lite: br.com.docaio.cgflix.lite. Ambas responderam 200 e o desenvolvedor é AllDevs. As imagens trazem o texto da própria loja.

## Ideia (fonte/conteudo/ideia.json)
Projeto Heisuca. A conversa é reconstrução (marcada `reconstrucao: true`), com falas curtas inventadas só como ilustração; nada vem de mensagem real. O resultado "Publicado na Google Play." é fato verificado.

## Pendências
- Caio e Rosiel devem aprovar ou reescrever as quatro falas da conversa e o texto do protótipo (ideia.json).
- Os textos de amott, cgflix-lite (problema) e heisuca (problema/fizemos, já existentes) merecem leitura do autor.
- Capturas de frente de fakly e sendany mostram caixas no lugar de emojis (fonte de emoji ausente no Chromium da bancada); refazer num navegador com fonte de emoji.
- A captura de frente do sendany é só a abertura do site, quase vazia.
- prosup sem por_tras: falta repositório.
- Tizen foi mantido no stack do Heisuca por vir do texto original; confirmar.
- amott aponta para amott.docaio.com.br; trocar quando migrar para amott.com.br.
- Sem imagens em assets/por-tras (nenhum wireframe ou fluxo real disponível).
