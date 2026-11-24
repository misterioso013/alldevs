# Bancada

Mede o site ALL.dev contra a prévia local: capturas, axe, sem JS, rolagem, links, movimento reduzido, paleta de comandos, FPS da home e Lighthouse.

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
Para medir só uma parte do site, acrescente `--so /servicos/` (só os caminhos que começam com esse prefixo).
Gera `RELATORIO.md` (resumo + uma tabela por meta) e as capturas PNG (ignoradas pelo git). Sai com rc 1 se alguma meta falhar.
Páginas medidas: as do `sitemap.xml` mais os links internos `.html`/diretório achados nelas (um nível).

Só o caso da paleta de comandos (~10 s por página), com a mesma prévia e o mesmo servidor:
```
node bancada/paleta.mjs --url http://127.0.0.1:8765/       # uma linha por cenário; rc 1 se algum falhar
```

## Metas
- **Capturas**: página em 360, 430 e 1440 px (`<nome>-<largura>.png`).
- **axe**: zero problemas `serious` ou `critical`, em 360, 430 e em 1440 px.
- **Sem JS**: título (`title` e `h1`) e ao menos um contato (mailto, wa.me ou `#contato`) VISÍVEIS; `/projetos/` lista todos os cards visíveis.
Toda página precisa responder 200; página sem medição numa meta conta como FALHA.
- **Rolagem**: `scrollWidth <= clientWidth` em 360 e em 430 px.
- **FPS** (só na `/`): ≥ 50 fps com CPU 4× mais lenta (`Emulation.setCPUThrottlingRate`, 1440 px, ponteiro varrendo o palco do hero; 4 s de aquecimento e 3 s medidos), a mesma técnica do `hero.mjs`.
- **Links**: links internos respondem 200 sem redirecionamento (diretório sem barra final dá 301 e conta como falha).
- **Movimento**: com `reducedMotion: reduce`, nenhum elemento com `transform` diferente de `none` após 1 s.
- **Lighthouse**: predefinição móvel (4G simulado), LCP < 2500 ms e CLS < 0,05.
- **Paleta** (`bancada/paleta.mjs`, em todas as páginas; o `paleta.json` vem do mesmo servidor):
  - 1440 px, teclado: sem pedido do `paleta.json` na carga e pílula oculta; Ctrl K abre com o foco no campo, 1 pedido e todas as opções;
    seta para baixo/cima muda a opção (`aria-selected` e `aria-activedescendant`, com volta cíclica); a busca ignora acento ("orcamento" acha 1);
    Enter navega até o destino da opção; Esc fecha e devolve o foco ao elemento que o tinha (o logo); ⌘K (`Meta+K`) também abre; axe com a paleta aberta, 0 `serious`/`critical`;
  - 412 px, toque: pílula visível com ≥ 44 px, sem elemento fixo colado ao rodapé; tocar na pílula abre; opções com ≥ 44 px; axe aberta;
    Esc devolve o foco à pílula; tocar numa opção navega;
  - `reducedMotion: reduce`: aberta, nenhum `transform` após 1 s e o diálogo termina opaco (só esmaece);
  - 412 px com o `paleta.json` bloqueado: a pílula segue como link e leva a `/projetos/`;
  - 412 px, clique sem foco no link (o que o toque faz no Safari/iOS: o `activeElement` fica no `body`): aberta pela pílula, Esc devolve o foco à pílula.

## Máquina sem as libs do Chrome (Whatbox)
Faltam `libgbm`, `libxkbcommon` etc. Baixe os .deb do Debian bookworm (libgbm1, libdrm2, libwayland-server0, libxkbcommon0),
extraia com `ar x` + `bsdtar -xf data.tar.*` e copie só os `.so*` para `~/.local/lib/chromium-deps/`. Depois:
```
export BANCADA_LIBS=$HOME/.local/lib/chromium-deps
```
Quando `BANCADA_LIBS` está definida, o `rodar.mjs` a junta ao `LD_LIBRARY_PATH` só do navegador (Playwright e Lighthouse).
Lighthouse e Playwright usam o `chrome-headless-shell` do Playwright (ou o binário de `CHROME_PATH`, se definido). Sem a variável, roda normal.

## Prévia na VPS
`bin/publicar-previa` gera com `--previa` e envia por rsync para `/var/www/alldevs-previa/` (https://alldevs.docaio.com.br/, noindex).
`bin/publicar-previa --ensaio` (ou `DRY=1`) gera, valida e só imprime o rsync, sem rede. Recusa qualquer destino fora de `/var/www/alldevs-previa/`.
