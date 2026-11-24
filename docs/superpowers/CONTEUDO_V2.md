# Conteúdo v2: origem de cada captura e trecho

Formato: repositório · caminho@commit. Tudo foi lido sem alterar os repositórios de origem.

## Trechos "por trás" (fonte/conteudo/por-tras/)
| Projeto | Arquivo | Origem |
|---|---|---|
| fakly | fakly.txt (19 linhas) | misterioso013/fakly · main.js, linhas 12-30 @4c3ea1a |
| sendany | sendany.txt (15 linhas) | misterioso013/sendany · src/lib/database.ts, linhas 29-43 @1117310 |
| amott | amott.txt (4 linhas) | CaioGuerras/amott-perfumes · index.html, linhas 30-33 @00aa67a |
| heisuca | heisuca.txt (10 linhas) | heisuca · apps/app/lib/heisuca/theme/temas/tema_hisui.dart, linhas 10-18 e 32 (a chave que fecha a classe; corte sem edição) @9755d4a (ramo claude/heisuca-v2) |
| cgflix-lite | cgflix-lite.txt (12 linhas) | cgflix-lite · core/src/main/java/dev/jdtech/jellyfin/core/presentation/theme/CgflixPalette.kt, linhas 24-35 @8aa925d (campos da paleta; sem os nomes dos temas) |
| prosup | sem trecho (`por_tras: null`) | sem repositório disponível |

No site, o campo `origem` do cgflix-lite traz só `CgflixPalette.kt@8aa925d`: o caminho completo tem o nome do servidor de mídia e não pode aparecer num texto do app. O caminho completo fica só neste documento. Os trechos são cópias sem edição (só cortes).

## Capturas de frente (assets/frente/, até 960 px)
- amott (cena parada, com `prefers-reduced-motion`), fakly (com a fonte Noto Color Emoji instalada só no usuário), sendany: captura do site no ar (Chromium, 960x600), em 2026-11-23.
- heisuca: imagem individual da Google Play (tela de temas), 540x960. Sem título de obra, pôster nem nome de outro serviço na imagem.
- cgflix-lite: nenhuma captura da loja serve (todas mostram títulos, pôsteres ou nomes de uso interno). A frente é o ícone do app da loja sobre fundo escuro (960x600).
- fakly e sendany (assets/images/): PNG de 2549 e 1352 px trocados por WebP de 960 px; os PNG antigos foram para ~/Arquivos_Obsoletos/2026-11-23_alldevs_v1/.

## Lojas (assets/loja/, 540 px)
Heisuca: 1 = cabeçalho da loja (nome, ícone, AllDevs, classificação e downloads); 2 = imagem individual de captura (tela de temas, 540x960; saiu da página em 24/11 para o print aparecer uma vez só, arquivo mantido); 3 = ícone oficial (512 px). CGFLIX Lite: 1 = cabeçalho da loja; 2 = ícone do app (512 px); 3 = recorte do topo do cabeçalho. Nenhuma captura de carrossel. Nenhuma das capturas individuais do CGFLIX Lite foi usada, porque todas mostram títulos, pôsteres ou nomes que não podem aparecer. Fonte: app.heisuca.player e br.com.docaio.cgflix.lite (página da Google Play, 2026-11-23, desenvolvedor AllDevs).

## Ideia (fonte/conteudo/ideia.json)
Projeto Heisuca. Decisão do Caio (24/11): saíram os estágios `conversa` (conversa reconstruída) e `encontro` ("Nos víamos e pensávamos." e o desenho dos bonecos na mesa), porque Caio (Rio de Janeiro) e Rosiel (Pernambuco) nunca se encontraram pessoalmente. Ficam `prototipo`, `codigo` e `no-ar`, com os textos atuais; não há mais falas inventadas. O estágio `prototipo` é fato com fonte: o primeiro commit do `tema_hisui.dart` no repositório do Heisuca é 612b0a6, de 2026-10-20 (primeiro app em Flutter); o site web do Heisuca começou em 2026-10-18 (e512785). O resultado "Publicado na Google Play." é fato verificado.

## Pendências
- Caio e Rosiel devem aprovar ou reescrever o texto do protótipo (ideia.json). As falas da conversa não existem mais (decisão de 24/11).
- O texto de abertura da seção "Da ideia ao ar" ainda diz "do primeiro papo ao app na loja"; decidir com o Caio se fica.
- Menu do topo (24/11): "Caio" e "Rosiel" viraram "Sócios" (/#quem-somos); o rodapé também (um item só, "Sócios").
- Decisão do Caio (24/11), "remover toda citação que nos divide": as páginas /caio/ e /rosiel/ saíram do site (e do sitemap e da paleta); os cartões de "Quem somos" ficam só com foto, nome e "Sócio do estúdio."; saíram o rótulo por pessoa, a frase e o link "Ver perfil". Segunda resposta do Caio (24/11): a História saiu do v2 (menu, rodapé, sitemap, bancada; `historia.html` é só um redirecionamento para `/#quem-somos`, fora do sitemap); o JSON-LD das pessoas leva só `name` (sem `jobTitle` nem `sameAs`; `papel` e `links` saíram de pessoas.json); o tipo de contato `perfil` saiu. O ENDEREÇO de e-mail do Rosiel (mailto) fica por enquanto. A descrição da home deixou de citar os nomes.
- Os textos de amott, cgflix-lite (problema) e heisuca (problema/fizemos, já existentes) merecem leitura do autor.
- Capturas de frente de fakly e sendany mostram caixas no lugar de emojis (fonte de emoji ausente no Chromium da bancada); refazer num navegador com fonte de emoji.
- A captura de frente do sendany é só a abertura do site, quase vazia.
- prosup sem por_tras: falta repositório.
- Tizen foi mantido no stack do Heisuca por vir do texto original; confirmar.
- amott aponta para amott.docaio.com.br; trocar quando migrar para amott.com.br.
- Sem imagens em assets/por-tras (nenhum wireframe ou fluxo real disponível).
