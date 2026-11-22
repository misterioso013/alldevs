# Bancada

Mede o site ALL.dev contra a prévia local: capturas, axe, sem JS, rolagem, links, movimento reduzido e Lighthouse.

## Instalar
```
cd bancada && npm ci && npx playwright install chromium
```

## Rodar
```
PREVIA=$(mktemp -d)                                 # prévia FORA do repo
python3 fonte/gerar.py --previa --saida $PREVIA
python3 bancada/gzserver.py 8765 $PREVIA &          # com gzip, como o GitHub Pages; guarde o PID e encerre depois (kill <PID>)
node bancada/rodar.mjs --url http://127.0.0.1:8765 --saida bancada/relatorios/<AAAA-MM-DD>
```
Use o `gzserver.py`, não o `python3 -m http.server`: sem compressão o JS de vendor chega inteiro e o LCP do
Lighthouse sobe uns 600 ms nas páginas com foto (`/`, `/caio/`, `/rosiel/`), o que não acontece em produção.
Aviso: não gere a prévia dentro do repo (`dist-previa/`): `checar.py` varre o repo e a cor `rgba()` dos estáticos o reprova
(`dist-previa/` agora é ignorada pelo `checar.py`, mas mantenha a prévia fora). Não mexa na prévia durante a rodada.
Gera `RELATORIO.md` (resumo + uma tabela por meta) e as capturas PNG (ignoradas pelo git). Sai com rc 1 se alguma meta falhar.
Páginas medidas: as do `sitemap.xml` mais os links internos `.html`/diretório achados nelas (um nível).

Só o caso do inspetor do hero (~45 s, os cenários rodam em paralelo), com a mesma prévia e o mesmo servidor:
```
node bancada/inspetor.mjs --url http://127.0.0.1:8765/     # uma linha por cenário; rc 1 se algum falhar
```

## Metas
- **Capturas**: página em 430 e 1440 px.
- **axe**: zero problemas `serious` ou `critical`, em 430 e em 1440 px.
- **Sem JS**: título (`title` e `h1`) e ao menos um contato (mailto, wa.me ou `#contato`) VISÍVEIS; `/projetos/` lista todos os cards visíveis.
Toda página precisa responder 200; página sem medição numa meta conta como FALHA.
- **Rolagem**: `scrollWidth <= clientWidth` em 430 px.
- **Links**: links internos respondem 200 sem redirecionamento (diretório sem barra final dá 301 e conta como falha).
- **Movimento**: com `reducedMotion: reduce`, nenhum elemento com `transform` diferente de `none` após 1 s.
- **Lighthouse**: predefinição móvel (4G simulado), LCP < 2500 ms e CLS < 0,05.
- **Inspetor** (`bancada/inspetor.mjs`, só nas páginas com `class="inspetor "`; as outras passam como "sem inspetor"):
  CLS = maior janela de sessão (1 s entre mudanças, 5 s no máximo) sem as mudanças com `hadRecentInput`.
  - 360, 430 e 1440 px, 12 s sem gesto: CLS < 0,05, o percurso anda (≥ 3 textos de código), a tela NÃO troca e todo LCP é o `<h1>`;
  - 360, 430 e 1440 px, tecla aos 0,5 s e 40 s abertos, mouse passando no palco a cada 5 s: CLS < 0,05 e ≥ 2 trocas de tela;
  - `reducedMotion: reduce`: 2 caixas acesas em lugares diferentes, paradas depois de hover e clique nelas;
  - 360, 412, 430 e 1440 px: botão "próxima tela" com altura ≥ 44 px e sem sobrepor o selo do autor.

## Máquina sem as libs do Chrome (Whatbox)
Faltam `libgbm`, `libxkbcommon` etc. Baixe os .deb do Debian bookworm (libgbm1, libdrm2, libwayland-server0, libxkbcommon0),
extraia com `ar x` + `bsdtar -xf data.tar.*` e copie só os `.so*` para `~/.local/lib/chromium-deps/`. Depois:
```
export BANCADA_LIBS=$HOME/.local/lib/chromium-deps
```
Quando `BANCADA_LIBS` está definida, o `rodar.mjs` a junta ao `LD_LIBRARY_PATH` só do navegador (Playwright e Lighthouse).
Lighthouse e Playwright usam o `chrome-headless-shell` do Playwright (ou o binário de `CHROME_PATH`, se definido). Sem a variável, roda normal.
