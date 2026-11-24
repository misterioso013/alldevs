# ALL.dev v2: site de estúdio, nova identidade

Ramo `claude/v2`. O site segue estático e gerado por `fonte/gerar.py`. **Push e PR só com o OK do Caio e do Rosiel.** O `main` não muda até lá.

**Prévia:** https://alldevs.docaio.com.br (publicada por `bin/publicar-previa`; para desfazer, rodar o script a partir de um commit anterior).

## O que mudou

Por página, com o commit de cada task (`git log --oneline` a partir de `684da15`):

- **Base e dados (T1, T2).** Dados do estúdio sem autor por projeto, `por_tras` e tecnologias (`21d8332`, `024cb71`); conteúdo real: capturas, lojas e trechos (`6bcc4e0`).
- **Identidade (T3).** Syne, roxo e laranja, tokens e base visual (`eccbae1`, `6686408`).
- **Hero "por trás do produto" (T4, `/`).** Canvas 2D com revelação, qualidade adaptativa, LCP no `h1`/imagem da frente (`143c10c`, `8ff2a6e`, `5459891`, `69fb74e`).
- **Da ideia ao ar (T5, `/`).** Trilha em 5 estágios com o código revelado (`aa04410`, `d9d2d94`).
- **Home completa (T6, `/`).** Faixa de prova, serviços, projetos, quem somos e contato (`357aafe`, `517b9b9`).
- **Projetos e cases (T7, `/projetos/` e `/projetos/<slug>/`).** Filtro que guarda o lugar (CLS), cases com "por trás" (`162b053`, `52f75cd`, `91408cf`, `9add6ab`, `4bf7220`, `1bdaa1b`, `37e86a3`, `a9621c4`).
- **Serviços (T8, 6 páginas em `/servicos/`).** Visual novo, a11y (`6807317`, `3ed0a4b`).
- **Perfis e história (T9, `/caio/`, `/rosiel/`, `/historia.html`).** Todos os projetos sob "Fizemos juntos" (`49907a8`, `3c8959c`, `3ec36ed`, `7f90685`).
- **Bancada final e prévia (T10).** `bancada/rodar.mjs` em 360, 430 e 1440 px, meta de FPS com CPU 4× na `/`; `bin/publicar-previa`; este texto (`dbe4772`).

## Capturas

Em `bancada/relatorios/2026-11-24-final/` (fora do git, só os PNG; o `RELATORIO.md` fica na pasta): `<página>-360.png`, `<página>-430.png` e `<página>-1440.png`
(17 páginas, 51 imagens). Capturas do hero e da trilha: `bancada/relatorios/2026-11-23-hero/` e `2026-11-23-ideia/`.

## Resultado da bancada

`node bancada/rodar.mjs` sobre a prévia local (17 páginas), rc 0. Relatório completo em `bancada/relatorios/2026-11-24-final/RELATORIO.md`.

| Meta | Resultado |
|---|---|
| Capturas em 360, 430 e 1440 px | passa, 17/17 |
| axe sem `serious`/`critical` (360, 430, 1440 px) | passa, 17/17 |
| Sem JS legível (título, contato, todos os cards) | passa, 17/17 |
| Sem rolagem horizontal em 360 e 430 px | passa, 17/17 |
| Links internos 200, sem redirecionamento | passa, 17/17 |
| `reducedMotion`: nenhum transform após 1 s | passa, 17/17 |
| Paleta de comandos | passa, 17/17 |
| FPS ≥ 50 com CPU 4× na `/` | passa, 60,0 fps |
| Lighthouse móvel, LCP < 2,5 s e CLS < 0,05 | passa, 17/17 |
| `hero.mjs` (20 cenários, `cpu4x` 59,2 fps) e `ideia.mjs` (11 cenários, CLS 0,0004) | todos ok |

LCP mais alto, em 3 rodadas (LCP ms / CLS): `/caio/` 2481, 2482, 2480; `/projetos/` 2461, 2424, 2423; `/rosiel/` 2410, 2414, 2409; `/` 2111, 1423, 1430. A margem de `/caio/` é de 19 ms: qualquer foto maior estoura a meta.

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
- Ideia (`ideia.json`): as quatro falas da conversa (reconstrução, marcada `reconstrucao: true`) e o texto do protótipo.
- Textos de amott, cgflix-lite (problema) e heisuca (problema e "fizemos") merecem leitura do autor.
- Tizen no stack do Heisuca: confirmar.
- cgflix-lite sem captura de tela real (só ícone e cabeçalho da loja): pedir um print limpo.
- Capturas de frente de fakly e sendany mostram caixas no lugar de emojis (fonte de emoji ausente na bancada); a de sendany é só a abertura do site.
- Rótulos "Por trás" e "Todos" (filtro de `/projetos/`) e "// projetos" e "// contato" (serviços).
- Home: voz em 3ª/1ª pessoa em `#quem-somos` e e-mail gmail no CTA.
- Textos sem fonte na faixa de prova e nos títulos da home.
- Furo do hero escuro na captura e foto magenta do Rosiel; reavaliar a foto reduzida (a frase do perfil tem 32 ch por causa do LCP de `/caio/`).
- amott aponta para `amott.docaio.com.br`; trocar quando migrar para `amott.com.br`.
- Sem imagens em `assets/por-tras` (nenhum wireframe ou fluxo real).
