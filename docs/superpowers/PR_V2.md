# ALL.dev v2: site de estúdio, nova identidade

Ramo `claude/v2`. O site segue estático e gerado por `fonte/gerar.py`. **Push e PR só com o OK do Caio e do Rosiel.** O `main` não muda até lá.

**Prévia:** https://alldevs.docaio.com.br (publicada por `bin/publicar-previa`; para desfazer, rodar o script a partir de um commit anterior).

## O que mudou

Por página, com o commit de cada task (`git log --oneline` a partir de `684da15`):

- **Base e dados (T1, T2).** Dados do estúdio sem autor por projeto, `por_tras` e tecnologias (`21d8332`, `024cb71`); conteúdo real: capturas, lojas e trechos (`6bcc4e0`).
- **Identidade (T3).** Syne, roxo e laranja, tokens e base visual (`eccbae1`, `6686408`).
- **Hero "por trás do produto" (T4, `/`).** Canvas 2D com revelação, qualidade adaptativa, LCP no `h1`/imagem da frente (`143c10c`, `8ff2a6e`, `5459891`, `69fb74e`).
- **Da ideia ao ar (T5, `/`).** Trilha em 3 estágios (protótipo, código, no ar) com o código revelado (`aa04410`, `d9d2d94`).
- **Home completa (T6, `/`).** Faixa de prova, serviços, projetos, quem somos (cartões só com nome e "Sócio do estúdio.", decisão de 24/11) e contato (`357aafe`, `517b9b9`).
- **Projetos e cases (T7, `/projetos/` e `/projetos/<slug>/`).** Filtro que guarda o lugar (CLS), cases com "por trás" (`162b053`, `52f75cd`, `91408cf`, `9add6ab`, `4bf7220`, `1bdaa1b`, `37e86a3`, `a9621c4`).
- **Serviços (T8, 6 páginas em `/servicos/`).** Visual novo, a11y (`6807317`, `3ed0a4b`).
- **Perfis e história (T9).** Feita e depois retirada por decisão do Caio de 24/11 (`d60489a`): sem perfis e sem História; `/historia.html` só redireciona para `/#quem-somos`.
- **Bancada final e prévia (T10).** `bancada/rodar.mjs` em 360, 430 e 1440 px, meta de FPS com CPU 4× na `/`; `bin/publicar-previa`; este texto (`dbe4772`).

## Capturas

Em `bancada/relatorios/2026-11-24-final-fix/` (fora do git, só os PNG; o `RELATORIO.md` fica na pasta): `<página>-360.png`, `<página>-430.png` e `<página>-1440.png`
(14 páginas, 42 imagens; pasta `bancada/relatorios/2026-11-24-final-fix/`). Capturas do hero e da trilha: `bancada/relatorios/2026-11-23-hero/` e `2026-11-23-ideia/`.

## Resultado da bancada

`node bancada/rodar.mjs` sobre a prévia local (14 páginas), rc 0. Relatório completo em `bancada/relatorios/2026-11-24-final-fix/RELATORIO.md`.

| Meta | Resultado |
|---|---|
| Capturas em 360, 430 e 1440 px | passa, 14/14 |
| axe sem `serious`/`critical` (360, 430, 1440 px) | passa, 14/14 |
| Sem JS legível (título, contato, todos os cards) | passa, 14/14 |
| Sem rolagem horizontal em 360 e 430 px | passa, 14/14 |
| Links internos 200, sem redirecionamento | passa, 14/14 |
| `reducedMotion`: nenhum transform após 1 s | passa, 14/14 |
| Paleta de comandos | passa, 14/14 |
| FPS ≥ 50 com CPU 4× na `/` | passa, 56,2 fps |
| Lighthouse móvel, LCP < 2,5 s e CLS < 0,05 | passa, 14/14 |

LCP mais alto, numa rodada da bancada de 24/11 (LCP ms / CLS): `/projetos/` 2427 / 0,000; `/` 2293 / 0,001; `/servicos/criacao-de-sites-institucionais/` 1434 / 0,001; as demais páginas ficam em cerca de 907 ms. O CLS máximo foi 0,015 (`/servicos/bots-whatsapp-automacao/`, que já oscilava entre 0 e 0,015 em rodadas anteriores). FPS na `/` com CPU 4×: 56,2. A margem de `/projetos/` para o limite de 2500 ms é de 73 ms: qualquer foto maior estoura a meta.

## Crítica externa

Três rodadas de correção (meta: nota ≥ 8). O Codex ficou sem cota até 25/11 06:05 e não entrou.

| Crítica | r1 | r2 | r3 |
|---|---|---|---|
| Visual (capturas) | 5/10 | 5/10 | 6/10 |
| Gemini (código) | 6/10 | 6/10 | 7,5/10 |

A meta não foi atingida no teto de rodadas. O que sobra e é objetivo (sem texto nem imagem nova) entrou na revisão final
do ramo (`.superpowers/sdd/2026-11-23-alldevs-v2/critica-r3-para-revisao-final.md`). O resto depende de texto, foto ou
decisão de desenho e está na lista abaixo.

## Para o Caio e o Rosiel conferirem

Só a lista. Nada aqui foi decidido.

**Trechos "por trás"** (`fonte/conteudo/por-tras/`; origens em `docs/superpowers/CONTEUDO_V2.md`)
- fakly: `main.js`, linhas 12-30 de misterioso013/fakly @4c3ea1a.
- sendany: `src/lib/database.ts`, linhas 29-43 de misterioso013/sendany @1117310.
- amott: `index.html`, linhas 30-33 de CaioGuerras/amott-perfumes @00aa67a.
- heisuca: `tema_hisui.dart`, linhas 10-18 @9755d4a (ramo `claude/heisuca-v2`).
- cgflix-lite: `CgflixPalette.kt`, linhas 24-35 @8aa925d (campos da paleta, sem os nomes dos temas).
- prosup: sem trecho (`por_tras: null`; falta repositório).

**Textos `[C]` e pendências**
- Ideia (`ideia.json`): o texto do protótipo.
- Textos de amott, cgflix-lite (problema) e heisuca (problema e "fizemos") merecem leitura do autor.
- Tizen no stack do Heisuca: confirmar.
- cgflix-lite sem captura de tela real (só ícone e cabeçalho da loja): pedir um print limpo.
- Capturas de frente de fakly e sendany mostram caixas no lugar de emojis (fonte de emoji ausente na bancada); a de sendany é só a abertura do site.
- Rótulos "Por trás" e "Todos" (filtro de `/projetos/`) e "// projetos" e "// contato" (serviços).
- Home: e-mail gmail no CTA.
- Textos sem fonte na faixa de prova e nos títulos da home.
- Furo do hero escuro na captura e foto magenta do Rosiel.
- amott aponta para `amott.docaio.com.br`; trocar quando migrar para `amott.com.br`.
- Sem imagens em `assets/por-tras` (nenhum wireframe ou fluxo real).
