# Bancada

Mede o site ALL.dev contra a prévia local: capturas, axe, sem JS, rolagem, links, movimento reduzido e Lighthouse.

## Instalar
```
cd bancada && npm ci && npx playwright install chromium
```

## Rodar
```
python3 fonte/gerar.py --previa --saida dist-previa
python3 -m http.server 8765 -d dist-previa &      # guarde o PID e encerre depois
node bancada/rodar.mjs --url http://127.0.0.1:8765 --saida bancada/relatorios/<AAAA-MM-DD>
```
Gera `RELATORIO.md` (resumo + uma tabela por meta) e as capturas PNG (ignoradas pelo git). Sai com rc 1 se alguma meta falhar.
Páginas medidas: as do `sitemap.xml` mais os links internos `.html`/diretório achados nelas (um nível).

## Metas
- **Capturas**: página em 430 e 1440 px.
- **axe**: zero problemas `serious` ou `critical` (430 px).
- **Sem JS**: título (`title` e `h1`) e contato (mailto, wa.me ou `#contato`) aparecem; `/projetos/` lista todos os cards visíveis.
- **Rolagem**: `scrollWidth <= clientWidth` em 430 px.
- **Links**: links internos respondem 200 sem redirecionamento (diretório sem barra final dá 301 e conta como falha).
- **Movimento**: com `reducedMotion: reduce`, nenhum elemento com `transform` diferente de `none` após 1 s.
- **Lighthouse**: predefinição móvel (4G simulado), LCP < 2500 ms e CLS < 0,05.

## Máquina sem as libs do Chrome (Whatbox)
Faltam `libgbm`, `libxkbcommon` etc. Baixe os .deb do Debian bookworm (libgbm1, libdrm2, libwayland-server0, libxkbcommon0),
extraia com `ar x` + `bsdtar -xf data.tar.*` e copie só os `.so*` para `~/.local/lib/chromium-deps/`. Depois:
```
export BANCADA_LIBS=$HOME/.local/lib/chromium-deps
```
Quando `BANCADA_LIBS` está definida, o `rodar.mjs` a junta ao `LD_LIBRARY_PATH` só do navegador (Playwright e Lighthouse).
Lighthouse e Playwright usam o `chrome-headless-shell` do Playwright. Sem a variável, roda normal.
