# Relatório da bancada — fechamento do redesenho (Task 13B)

Base: http://127.0.0.1:8765 — prévia gerada do commit `b7bb892` (ramo `claude/redesenho`, 202 testes) — 15 páginas — rodada completa em 2026-11-23T01:29:16.185Z

Este é o relatório final. A medição da 13A fica no fim, em "Medição anterior (13A)".

## Como reproduzir

```
export BANCADA_LIBS=$HOME/.local/lib/chromium-deps          # só onde faltam as bibliotecas do Chromium
python3 fonte/gerar.py --previa --saida <pasta-fora-do-repo>
python3 bancada/gzserver.py 8765 <pasta-fora-do-repo> & # pare pelo PID
node bancada/rodar.mjs --url http://127.0.0.1:8765/ --saida <pasta-das-capturas>
node bancada/inspetor.mjs --url http://127.0.0.1:8765/
node bancada/paleta.mjs --url http://127.0.0.1:8765/
```

O Lighthouse é o móvel padrão (4G simulado). As capturas (`*-430.png`, `*-1440.png`, 7,5 MB) ficaram numa pasta fora do repo (passam de 3 MB e o `.gitignore` já ignora `bancada/relatorios/*/*.png`). O relatório cita os nomes dos arquivos.

## Resumo

| Meta | Resultado | Falhas |
|---|---|---|
| Capturas em 430 e 1440 px | PASSA | 0/15 páginas |
| axe: zero problemas serious/critical | PASSA | 0/15 páginas |
| Sem JS: título, contato e (em /projetos/) todos os cards | PASSA | 0/15 páginas |
| Sem rolagem horizontal em 430 px | PASSA | 0/15 páginas |
| Links internos respondem 200, sem redirecionamento | PASSA | 0/15 páginas |
| reducedMotion: nenhum transform após 1 s | PASSA | 0/15 páginas |
| Inspetor do hero: CLS < 0,05 (12 s parado e 40 s com gesto), troca após gesto, calmo parado, botão ≥ 44 px | PASSA | 0/15 páginas |
| Paleta: Ctrl K, seta, Enter navega e Esc devolve o foco (1440 px); toque na pílula (412 px); axe aberta; reduced-motion; sem rede | PASSA | 0/15 páginas |
| Lighthouse móvel: LCP < 2500 ms e CLS < 0,05 | PASSA | 0/15 páginas |
| Alvos de toque ≥ 44 px nos controles (412 px, toque) | PASSA | 0/15 páginas; menor altura medida: 44 px |
| LCP 3× ou mais na home, /caio/ e /rosiel/ (6 medidas cada) | PASSA | máximo 2408 ms (/caio/); nenhuma página passou de 2500 ms |

Código de saída: **0**

Casos solo: `bancada/inspetor.mjs` PASSA (11 casos: parado e com gesto em 360, 430 e 1440 px, com CLS de no máximo 0,005; calmo; botão de 44 px em 360, 412, 430 e 1440 px) e
`bancada/paleta.mjs` PASSA (1440 px, 412 px, reducedMotion, sem `paleta.json`, clique sem foco).
Testes: `python3 -m unittest discover -s fonte/testes -t fonte -v` = 202 OK; `python3 fonte/gerar.py && git diff --exit-code` = limpo;
`python3 fonte/checar.py` = 0 erro.

## LCP em 3 medições nas 3 páginas de maior risco

A revisão da 13A viu /caio/ em 2406 ms e /rosiel/ em 2260 ms. Medi cada uma das três páginas 6 vezes com o Lighthouse móvel
(`lh3.mjs`, uma instância do Chromium por medida): uma série de 2, uma série de 3 e a medição da rodada completa. CLS: / de 0 a 0,005;
/caio/ 0,000; /rosiel/ 0,000 em todas.

| Página | Série A (2 medidas, ms) | Série B (3 medidas, ms) | Rodada completa (ms) | Máximo | Folga até 2500 |
|---|---|---|---|---|---|
| / | 907, 907 | 905, 907, 908 | 906 | 908 | 1592 |
| /caio/ | 2404, 2406 | 2407, 2408, 2406 | 2406 | 2408 | **92** |
| /rosiel/ | 2263, 2255 | 2260, 2256, 2256 | 2256 | 2263 | 237 |

Nenhuma página passou de 2500 ms em nenhuma das 6 medidas, então não houve correção nem "antes/depois". Mesmo assim, a causa:

- O LCP de /caio/ e /rosiel/ é a foto de perfil (`.perfil-foto`): `caio-640.webp` (51.922 bytes) e `rosiel-640.webp` (36.616 bytes), com
  `width="320" height="320"` (640 px de arquivo para 320 px de tela, 2x), `fetchpriority="high"`, sem `loading="lazy"` e descoberta no
  HTML (não depende de JS nem de CSS). Os atributos já são os certos.
- O tempo vem do 4G simulado, que cobra pelo tamanho do arquivo: a home (sem imagem grande no LCP) fica em ~907 ms e as páginas de
  pessoa em ~2,2–2,4 s. O Lighthouse simulado é quase determinístico: nas 6 medições de cada página a variação é de até 8 ms (/rosiel/: 2255 a 2263).
- **Folga fina em /caio/ (92 ms).** A foto do Caio ainda é a provisória; as fotos reais (item [R] 2 do PR) podem mudar o peso do arquivo.
  Medir de novo quando elas chegarem. Se passar de 2500 ms, o remédio barato é um arquivo menor (por exemplo 480 px) antes de mexer
  em qualquer outra coisa.
- Oscilações isoladas na rodada completa, todas dentro da meta: /historia.html 1219 ms e /servicos/desenvolvimento-mvp-startups/ 1215 ms
  (as outras páginas ficam em ~905 ms) e CLS 0,011 em /servicos/bots-whatsapp-automacao/. São ruído do navegador na rodada longa; as
  medições 3× da home e dos perfis não mostraram nada parecido. CLS máximo da rodada: 0,029 em /projetos/ (meta 0,05), igual à 13A.

## Alvos de toque

Regra do projeto: controles (botões, CTAs, pílula da paleta, abas, filtros, links de perfil, perguntas do FAQ) com 44 px ou mais de
altura, no toque (412 px). `bancada/alvos.mjs` mede a altura de cada controle em cada página:

- **0 controles abaixo de 44 px em 15 páginas** (menor altura: 44 px em todas). O caso mais cheio é /rosiel/, com 11 controles,
  entre eles os 7 links de `.perfil-links`.
- axe, regra `target-size` (WCAG 2.5.8 AA, 24 px): 0 violações nas 15 páginas.
- **Fora da regra de projeto:** links de texto corrido, o logo do cabeçalho e links do rodapé ficam entre 17 e 34 px de altura. Passam o
  AA (2.5.8 tem a exceção para links em linha de texto e para alvos com espaçamento), mas não o AAA (2.5.5, 44 px). Não foi mexido
  (mudaria a leitura do texto); vai ao PR como item aberto.

## Limitações das capturas

- As capturas de página inteira mostram seções vazias abaixo da primeira tela: os cards só ganham opacidade quando entram na janela
  (revelação por rolagem em `js/site.js`, GSAP/ScrollTrigger). Isso é do efeito e não de conteúdo faltando. A bancada confere o conteúdo
  de outro jeito, na meta "Sem JS" (título, contato e todos os cards visíveis sem JS).
- A captura da primeira tela da home pode pegar a troca de texto do hero no meio ("software que vive", "sócios").

## Comparação com a Amott (Passo 2)

Pergunta do despacho, enviada com `codex exec -i … < /dev/null`. O Codex rodou em `read-only`, sem rede (o sandbox não resolve DNS).
Guardei só o pedido e a resposta final de cada rodada; o log bruto do Codex ficou fora do repo.

### Rodada 1 — pergunta do despacho, com as capturas de 1440 px do site novo

Capturas enviadas: `home-1440.png`, `servicos_criacao-de-sites-institucionais-1440.png`, `projetos_prosup-1440.png`, `rosiel-1440.png`.

Pedido:

> Estas são capturas do site novo de um estúdio de software. O que nelas lembra o site da Amott (amott.com.br) — layout, cores, tipografia, componentes, textos? Liste só semelhanças concretas, com a captura e o lugar.

Resposta íntegra:

> Não consigo confirmar semelhanças: o site **amott.com.br** não ficou acessível nas tentativas com e sem `www`, e a busca não trouxe páginas dele para comparação.
>
> Envie capturas da Amott. Com elas, listo somente correspondências concretas, indicando **captura, lugar e elemento semelhante** — layout, cores, tipografia, componentes ou textos.

O Codex tentou `curl https://amott.com.br` e a busca na web: `curl: (6) Could not resolve host`. **Não conseguiu abrir o site da Amott**,
então esta rodada não compara nada. Aceito como o despacho manda e registro aqui.

### Rodada 2 — comparação lado a lado (complemento meu)

Como a rodada 1 não comparou nada, repeti com uma referência local: uma captura de 1440 px da home da Amott (uma perfumaria; foi tirada de uma cópia
do site que já tínhamos à mão, porque o Codex não alcança a internet) como 1ª imagem e as capturas do site novo nas outras quatro
(1ª dobra da home, um serviço, um case, /rosiel/). A captura da Amott não entra no repo nem na saída do site.

Pedido:

> A PRIMEIRA imagem (ref-home-1440.png) é a home do site da Amott ([host omitido]), uma perfumaria. As outras quatro são capturas de 1440 px do site novo de um estúdio de software, na ordem: 2) primeira dobra da home, 3) página de um serviço, 4) página de um case, 5) perfil de uma pessoa. Compare a Amott com as quatro capturas. (a) Um revisor externo diria que são o mesmo estúdio ou a mesma família de site? Responda sim ou não e justifique em 2 linhas. (b) Liste só semelhanças concretas entre a Amott e as capturas, dizendo o número da captura e o lugar: layout, cores, tipografia, componentes, textos. Não liste o que é genérico de todo site escuro.

Resposta íntegra:

> **(a) Sim.** Um revisor poderia perceber a mesma família visual: títulos serifados de alto contraste, textos auxiliares espaçados e botões em cápsula com tratamento editorial semelhante.  
> A associação seria mais forte com a home (2); as páginas internas (3–5) repetem parte desse repertório.
>
> **(b) Semelhanças concretas:**
>
> - **Captura 2, primeira dobra:** título grande no lado esquerdo, elemento visual dominante à direita e dois botões lado a lado abaixo do texto — composição semelhante à da Amott.
> - **Captura 2, botões inferiores:** ação principal preenchida em creme, com texto escuro, acompanhada de ação secundária transparente com contorno fino; ambas em cápsula, como na Amott.
> - **Capturas 2–5, cabeçalho:** marca à esquerda, navegação horizontal à direita e último botão em cápsula, na mesma distribuição da Amott.
> - **Capturas 2–5, títulos:** serifas com contraste acentuado entre traços grossos e finos, em branco quente, próximas do tratamento de “Perfume é memória” na Amott.
> - **Capturas 2–5, pequenas chamadas acima dos títulos:** letras pequenas e espaçadas, como em “estúdio de software”, “Serviço · Popular”, “app · 2026…” e “rosiel · produto…”, cumprindo papel visual semelhante a “PERFUMARIA DE INSPIRAÇÃO”.
> - **Capturas 4 e 5, área de contato:** repetição do botão creme em cápsula junto a botões transparentes contornados, retomando o conjunto de ações da Amott.

### O que fiz com cada ponto

A resposta (a) foi "sim, mesma família". Medi o que dá para medir nas capturas, em vez de só discutir:

| | Amott (`ref-home-1440.png`) | Site novo (`nosso-home-1440-dobra.png`) |
|---|---|---|
| Fundo dominante | `#12100e`, matiz 30°, marrom quente | `#0d0c12`, matiz 250°, azul-quase-preto |
| Claro mais usado | `#ede4d4`, saturação 0,41 (creme) | `#ecebe6`, saturação 0,14 (neutro, 3x menos saturado) |
| Acento | dourado | violeta (Caio) e laranja (Rosiel), nunca dourado |
| Tipografia | didone em itálico dourado | Fraunces (serifa suave) + DM Sans + JetBrains Mono |
| Imagem principal | frasco 3D e fumaça | inspetor de código (HTML real) |

Os 6 pontos do Codex, um a um (na rodada 2 nada foi alterado; a mudança do botão principal veio depois, na revisão final, e a comparação foi refeita na seção ao fim):

1. **Captura 2, composição do hero** (título grande à esquerda, visual à direita, dois botões abaixo). Composição de hero muito comum
   (título, visual, dois botões); é estrutural, não uma cópia de componente. Mantido. Item aberto, avaliação: risco baixo.
2. **Captura 2, botão principal "creme" com texto escuro + secundário contornado, em cápsula.** É o único ponto de cor/componente que
   daria para mexer em uma linha (`.btn-primary` em `css/site.css`). Mantido, por duas razões. Primeiro, `#ecebe6` é o `--claro` da
   spec (que o descreve como "blocos claros frios, usados pouco"; a cor real é quente e pouco saturada, R236 G235 B230), o mesmo tom do
   texto do site, com um terço da saturação do creme da Amott. Segundo, trocar
   o preenchimento obriga a escolher outra cor para o CTA: usar violeta ou laranja o ligaria a um dos sócios, e um terceiro acento é
   decisão de marca. Na revisão final a opção barata foi aplicada: CTA principal só com contorno e o preenchimento no `:hover`/`:focus-visible` (ver "Comparação refeita").
3. **Capturas 2–5, cabeçalho** (marca à esquerda, navegação à direita, último botão em cápsula). Estrutural e padrão de mercado
   (a pílula `> ir para…` da paleta de comandos fica nesse mesmo cabeçalho, `fonte/modelos/cabecalho.html`). Mantido.
4. **Capturas 2–5, títulos serifados de contraste acentuado, "em branco quente".** Fraunces em peso 600 é uma serifa suave, não
   didone; a cor do título é o neutro acima. Discutível, não barato: trocar a família do título (`--fonte-titulo` em `css/tokens.css`)
   muda a identidade tipográfica inteira, e isso é redesenho, fora desta tarefa. Mantido; item aberto.
5. **Capturas 2–5, chamadas pequenas e espaçadas acima dos títulos** ("estúdio de software", "Serviço · Popular"). Padrão (eyebrow)
   em JetBrains Mono, sem relação com o texto da Amott. Mantido.
6. **Capturas 4–5, área de contato com o botão claro e botões contornados.** Mesma resposta do ponto 2.

Resumo: o Codex enxerga "mesma família" no repertório editorial escuro e apontou componentes de padrão comum (botões em cápsula com o
principal claro e o secundário contornado, cabeçalho com o último item em cápsula, chamadas pequenas e espaçadas acima dos títulos, hero
em duas colunas) e a serifa dos títulos. Nenhum texto nem rótulo da Amott apareceu na resposta. Na rodada 2 mantive todos; as diferenças
medidas (matiz do fundo, saturação do claro, acento, fonte, imagem) são grandes. O botão principal `--claro` tinha opção barata e foi
mudado na revisão final (item [R] 7 do PR, feito); a serifa e o hero (item [R] 8) só se resolveriam com redesenho e ficam registrados com esta avaliação.

## Detalhe por meta (rodada completa de 2026-11-23T01:29:16.185Z)

### Capturas em 430 e 1440 px

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | home-430.png, home-1440.png |
| /caio/ | passa | caio-430.png, caio-1440.png |
| /historia.html | passa | historia.html-430.png, historia.html-1440.png |
| /projetos/ | passa | projetos-430.png, projetos-1440.png |
| /projetos/fakly/ | passa | projetos_fakly-430.png, projetos_fakly-1440.png |
| /projetos/heisuca/ | passa | projetos_heisuca-430.png, projetos_heisuca-1440.png |
| /projetos/prosup/ | passa | projetos_prosup-430.png, projetos_prosup-1440.png |
| /projetos/sendany/ | passa | projetos_sendany-430.png, projetos_sendany-1440.png |
| /rosiel/ | passa | rosiel-430.png, rosiel-1440.png |
| /servicos/aplicativo-mobile-react-native/ | passa | servicos_aplicativo-mobile-react-native-430.png, servicos_aplicativo-mobile-react-native-1440.png |
| /servicos/automacoes-integracoes-api/ | passa | servicos_automacoes-integracoes-api-430.png, servicos_automacoes-integracoes-api-1440.png |
| /servicos/bots-whatsapp-automacao/ | passa | servicos_bots-whatsapp-automacao-430.png, servicos_bots-whatsapp-automacao-1440.png |
| /servicos/criacao-de-sites-institucionais/ | passa | servicos_criacao-de-sites-institucionais-430.png, servicos_criacao-de-sites-institucionais-1440.png |
| /servicos/desenvolvimento-mvp-startups/ | passa | servicos_desenvolvimento-mvp-startups-430.png, servicos_desenvolvimento-mvp-startups-1440.png |
| /servicos/landing-page-conversao/ | passa | servicos_landing-page-conversao-430.png, servicos_landing-page-conversao-1440.png |

### axe: zero problemas serious/critical

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /caio/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /historia.html | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /projetos/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /projetos/fakly/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /projetos/heisuca/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /projetos/prosup/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /projetos/sendany/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /rosiel/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /servicos/aplicativo-mobile-react-native/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /servicos/automacoes-integracoes-api/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /servicos/bots-whatsapp-automacao/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /servicos/criacao-de-sites-institucionais/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /servicos/desenvolvimento-mvp-startups/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |
| /servicos/landing-page-conversao/ | passa | 0 graves em 430 e 1440 px (0/0 leves) |

### Sem JS: título, contato e (em /projetos/) todos os cards

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | h1 "Fazemos software que vive.", contatos visíveis 3/3 |
| /caio/ | passa | h1 "Caio Guerras", contatos visíveis 3/3 |
| /historia.html | passa | h1 "Uma históriafora do roteiro", contatos visíveis 3/3 |
| /projetos/ | passa | h1 "Projetos", contatos visíveis 3/3, cards visíveis 4/4 |
| /projetos/fakly/ | passa | h1 "Fakly", contatos visíveis 3/3 |
| /projetos/heisuca/ | passa | h1 "Heisuca", contatos visíveis 3/3 |
| /projetos/prosup/ | passa | h1 "ProsUp", contatos visíveis 3/3 |
| /projetos/sendany/ | passa | h1 "SendAny", contatos visíveis 3/3 |
| /rosiel/ | passa | h1 "Rosiel Victor", contatos visíveis 3/3 |
| /servicos/aplicativo-mobile-react-native/ | passa | h1 "Desenvolvimento de Aplicativo Mobile iOS e Android com React Native", contatos visíveis 3/3 |
| /servicos/automacoes-integracoes-api/ | passa | h1 "Automação de Processos e Integração de Sistemas via API e Webhook", contatos visíveis 3/3 |
| /servicos/bots-whatsapp-automacao/ | passa | h1 "Bot para WhatsApp, Discord e Telegram — Automação de Atendimento 24h", contatos visíveis 3/3 |
| /servicos/criacao-de-sites-institucionais/ | passa | h1 "Criação de Site Institucional Profissional para Empresas", contatos visíveis 3/3 |
| /servicos/desenvolvimento-mvp-startups/ | passa | h1 "Desenvolvimento de MVP Web para Startups — Do Zero ao Ar em Semanas", contatos visíveis 3/3 |
| /servicos/landing-page-conversao/ | passa | h1 "Landing Page de Alta Conversão com Integração WhatsApp", contatos visíveis 3/3 |

### Sem rolagem horizontal em 430 px

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | scrollWidth 430 / clientWidth 430 |
| /caio/ | passa | scrollWidth 430 / clientWidth 430 |
| /historia.html | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/ | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/fakly/ | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/heisuca/ | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/prosup/ | passa | scrollWidth 430 / clientWidth 430 |
| /projetos/sendany/ | passa | scrollWidth 430 / clientWidth 430 |
| /rosiel/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/aplicativo-mobile-react-native/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/automacoes-integracoes-api/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/bots-whatsapp-automacao/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/criacao-de-sites-institucionais/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/desenvolvimento-mvp-startups/ | passa | scrollWidth 430 / clientWidth 430 |
| /servicos/landing-page-conversao/ | passa | scrollWidth 430 / clientWidth 430 |

### Links internos respondem 200, sem redirecionamento

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 29 ok |
| /caio/ | passa | 23 ok |
| /historia.html | passa | 21 ok |
| /projetos/ | passa | 25 ok |
| /projetos/fakly/ | passa | 23 ok |
| /projetos/heisuca/ | passa | 22 ok |
| /projetos/prosup/ | passa | 26 ok |
| /projetos/sendany/ | passa | 23 ok |
| /rosiel/ | passa | 25 ok |
| /servicos/aplicativo-mobile-react-native/ | passa | 26 ok |
| /servicos/automacoes-integracoes-api/ | passa | 25 ok |
| /servicos/bots-whatsapp-automacao/ | passa | 24 ok |
| /servicos/criacao-de-sites-institucionais/ | passa | 25 ok |
| /servicos/desenvolvimento-mvp-startups/ | passa | 26 ok |
| /servicos/landing-page-conversao/ | passa | 24 ok |

### reducedMotion: nenhum transform após 1 s

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | nenhum |
| /caio/ | passa | nenhum |
| /historia.html | passa | nenhum |
| /projetos/ | passa | nenhum |
| /projetos/fakly/ | passa | nenhum |
| /projetos/heisuca/ | passa | nenhum |
| /projetos/prosup/ | passa | nenhum |
| /projetos/sendany/ | passa | nenhum |
| /rosiel/ | passa | nenhum |
| /servicos/aplicativo-mobile-react-native/ | passa | nenhum |
| /servicos/automacoes-integracoes-api/ | passa | nenhum |
| /servicos/bots-whatsapp-automacao/ | passa | nenhum |
| /servicos/criacao-de-sites-institucionais/ | passa | nenhum |
| /servicos/desenvolvimento-mvp-startups/ | passa | nenhum |
| /servicos/landing-page-conversao/ | passa | nenhum |

### Inspetor do hero: CLS < 0,05 (12 s parado e 40 s com gesto), troca após gesto, calmo parado, botão ≥ 44 px

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 360 parado: CLS 0.002 (1 mudanças), 6 passos, LCP H1.hero-headline; 430 parado: CLS 0.005 (1 mudanças), 6 passos, LCP H1.hero-headline; 1440 parado: CLS 0.003 (1 mudanças), 6 passos, LCP H1.hero-headline; 360 gesto: CLS 0.005 (1 mudanças), 4 trocas; 430 gesto: CLS 0.005 (1 mudanças), 4 trocas; 1440 gesto: CLS 0.000 (0 mudanças), 4 trocas; calmo: 2 acesas, paradas após hover/clique; 360: botão 44 px, selo 77–249, botão 299–343; 412: botão 44 px, selo 77–249, botão 351–395; 430: botão 44 px, selo 77–249, botão 369–413; 1440: botão 44 px, selo 908–1080, botão 1223–1359 |
| /caio/ | passa | sem inspetor |
| /historia.html | passa | sem inspetor |
| /projetos/ | passa | sem inspetor |
| /projetos/fakly/ | passa | sem inspetor |
| /projetos/heisuca/ | passa | sem inspetor |
| /projetos/prosup/ | passa | sem inspetor |
| /projetos/sendany/ | passa | sem inspetor |
| /rosiel/ | passa | sem inspetor |
| /servicos/aplicativo-mobile-react-native/ | passa | sem inspetor |
| /servicos/automacoes-integracoes-api/ | passa | sem inspetor |
| /servicos/bots-whatsapp-automacao/ | passa | sem inspetor |
| /servicos/criacao-de-sites-institucionais/ | passa | sem inspetor |
| /servicos/desenvolvimento-mvp-startups/ | passa | sem inspetor |
| /servicos/landing-page-conversao/ | passa | sem inspetor |

### Paleta: Ctrl K, seta, Enter navega e Esc devolve o foco (1440 px); toque na pílula (412 px); axe aberta; reduced-motion; sem rede

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /caio/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /historia.html | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /projetos/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /projetos/fakly/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /projetos/heisuca/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /projetos/prosup/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /projetos/sendany/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /rosiel/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /servicos/aplicativo-mobile-react-native/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /servicos/automacoes-integracoes-api/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /servicos/bots-whatsapp-automacao/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /servicos/criacao-de-sites-institucionais/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /servicos/desenvolvimento-mvp-startups/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |
| /servicos/landing-page-conversao/ | passa | 1440 px: Ctrl K, seta, Enter -> /projetos/heisuca/, Esc devolve o foco, 16 opções, 1 pedido, axe 0 violações, 0 serious/critical; 412 px: pílula 44 px, toque abre, Esc devolve o foco, toque na opção -> /projetos/heisuca/, sem barra fixa, axe 0 violações, 0 serious/critical; reducedMotion: aberta, sem transform, opaca; sem o paleta.json: a pílula leva a /projetos/; clique sem foco no link: Esc devolve o foco à pílula (a.paleta-gatilho) |

### Lighthouse móvel: LCP < 2500 ms e CLS < 0,05

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | LCP 906 ms, CLS 0.005 |
| /caio/ | passa | LCP 2406 ms, CLS 0.000 |
| /historia.html | passa | LCP 1219 ms, CLS 0.000 |
| /projetos/ | passa | LCP 904 ms, CLS 0.029 |
| /projetos/fakly/ | passa | LCP 908 ms, CLS 0.000 |
| /projetos/heisuca/ | passa | LCP 905 ms, CLS 0.000 |
| /projetos/prosup/ | passa | LCP 907 ms, CLS 0.000 |
| /projetos/sendany/ | passa | LCP 906 ms, CLS 0.000 |
| /rosiel/ | passa | LCP 2256 ms, CLS 0.000 |
| /servicos/aplicativo-mobile-react-native/ | passa | LCP 907 ms, CLS 0.000 |
| /servicos/automacoes-integracoes-api/ | passa | LCP 907 ms, CLS 0.000 |
| /servicos/bots-whatsapp-automacao/ | passa | LCP 905 ms, CLS 0.011 |
| /servicos/criacao-de-sites-institucionais/ | passa | LCP 905 ms, CLS 0.000 |
| /servicos/desenvolvimento-mvp-startups/ | passa | LCP 1215 ms, CLS 0.000 |
| /servicos/landing-page-conversao/ | passa | LCP 905 ms, CLS 0.000 |

## Medição anterior (13A)

Rodada de 2026-11-23T01:06:46.575Z, feita na 13A sobre o conteúdo real do Rosiel (commit `de2a7ee`), antes das correções da revisão
(`b7bb892`). Só a tabela do Lighthouse; todas as outras metas também passavam (0/15). Os números são quase iguais aos de hoje: o
Lighthouse simulado é praticamente determinístico, e as correções da revisão (imagem `prosup-3.webp` e uma linha de CSS) só mudaram
o ProsUp, de 910 para 907 ms.

| Página | Resultado | Detalhe |
|---|---|---|
| / | passa | LCP 907 ms, CLS 0.005 |
| /caio/ | passa | LCP 2406 ms, CLS 0.000 |
| /historia.html | passa | LCP 906 ms, CLS 0.000 |
| /projetos/ | passa | LCP 908 ms, CLS 0.029 |
| /projetos/fakly/ | passa | LCP 904 ms, CLS 0.000 |
| /projetos/heisuca/ | passa | LCP 906 ms, CLS 0.000 |
| /projetos/prosup/ | passa | LCP 910 ms, CLS 0.000 |
| /projetos/sendany/ | passa | LCP 906 ms, CLS 0.000 |
| /rosiel/ | passa | LCP 2260 ms, CLS 0.000 |
| /servicos/aplicativo-mobile-react-native/ | passa | LCP 909 ms, CLS 0.000 |
| /servicos/automacoes-integracoes-api/ | passa | LCP 907 ms, CLS 0.000 |
| /servicos/bots-whatsapp-automacao/ | passa | LCP 908 ms, CLS 0.000 |
| /servicos/criacao-de-sites-institucionais/ | passa | LCP 908 ms, CLS 0.000 |
| /servicos/desenvolvimento-mvp-startups/ | passa | LCP 908 ms, CLS 0.000 |
| /servicos/landing-page-conversao/ | passa | LCP 909 ms, CLS 0.000 |

## Comparação refeita (revisão final)

A revisão final reprovou o portão da spec §9.5 (o Codex tinha dito "sim, mesma família"). Mudança feita: `.btn-primary` em `css/site.css`
passou a ter só contorno (fundo transparente, borda e texto em `--claro`) e se preenche com `--claro` no `:hover` e no `:focus-visible`
(texto em `--fundo`; é o mesmo par de cores do texto do site, contraste já travado por teste). Sem cor nova, só tokens. O botão claro em cápsula
era o ponto 2 e o ponto 6 do Codex. A bancada rodou de novo na prévia local (15 páginas): capturas, axe, sem JS, rolagem, links, movimento,
inspetor, paleta e Lighthouse passam, e `bancada/alvos.mjs` dá 0 controles abaixo de 44 px.

| Meta | Resultado |
|---|---|
| Lighthouse móvel, home | LCP 907 ms, CLS 0,000 |
| Lighthouse móvel, serviço (`/servicos/criacao-de-sites-institucionais/`) | LCP 905 ms, CLS 0,000 |
| Lighthouse móvel, pior página (`/rosiel/`, foto) | LCP 2260 ms, CLS 0,000 (meta 2500 ms) |
| axe, 430 e 1440 px | 0 sérios ou críticos nas 15 páginas |
| Rolagem horizontal em 430 px | nenhuma |
| Alvos de toque (412 px): home, serviço, /rosiel/ | menor altura 44 px, 0 abaixo de 44 |

Capturas de 1440 px enviadas, nesta ordem: Amott (a mesma da rodada 1), primeira dobra da home, página do serviço de sites institucionais,
`/projetos/prosup/` e `/rosiel/` (as três últimas, de página inteira, geradas pela bancada). Pergunta: a mesma da rodada 2, com uma linha final.

Pedido:

> A PRIMEIRA imagem (ref-home-1440.png) é a home do site da Amott ([host omitido]), uma perfumaria. As outras quatro são capturas de 1440 px do site novo de um estúdio de software, na ordem: 2) primeira dobra da home, 3) página de um serviço, 4) página de um case, 5) perfil de uma pessoa. Compare a Amott com as quatro capturas. (a) Um revisor externo diria que são o mesmo estúdio ou a mesma família de site? Responda sim ou não e justifique em 2 linhas. (b) Liste só semelhanças concretas entre a Amott e as capturas, dizendo o número da captura e o lugar: layout, cores, tipografia, componentes, textos. Não liste o que é genérico de todo site escuro.
> Responda também, em uma frase: parecem o mesmo estúdio? (sim/não)

Resposta íntegra:

> **(a) Não.** A Amott tem direção de arte centrada no frasco, com dourado, brilho e formas orgânicas; o estúdio usa divisórias, monoespaçadas e elementos técnicos.
> A semelhança mais forte está na composição da primeira dobra da captura 2; as páginas internas não sustentam uma identidade comum com a Amott.
>
> **(b) Semelhanças concretas:**
>
> - **Captura 2, primeira dobra:** título grande à esquerda e demonstração visual do produto à direita, com dois botões arredondados lado a lado abaixo do texto — composição também presente na Amott.
> - **Capturas 2–5, cabeçalho:** marca pequena à esquerda, navegação à direita e botão em formato de cápsula na extremidade direita.
> - **Capturas 2–5, títulos:** serifadas claras com contraste entre traços finos e grossos, próximas do recurso editorial usado no título principal da Amott.
> - **Capturas 2–5, pequenos rótulos:** espaçamento ampliado entre letras em chamadas que antecedem os títulos, semelhante aos rótulos superiores da Amott.
>
> **Parecem o mesmo estúdio? Não.**

Veredicto: **não**, não parecem o mesmo estúdio. O ponto do botão em creme sumiu da lista. O Codex ainda cita a composição do hero
(título à esquerda, visual à direita, dois botões), o cabeçalho com a cápsula, a serifa dos títulos e os rótulos espaçados, mas
conclui que as páginas internas não sustentam uma identidade comum com a Amott. O portão §9.5 passa com esta resposta; os itens
estruturais restantes (serifa dos títulos, hero em duas colunas) seguem como item [R] 8 do PR, decisão do Rosiel.
