# Redesenho do ALL.dev: estúdio do Caio e do Rosiel

Ramo `claude/redesenho`, base `7acc4d2`. O site continua estático e publicado pela raiz do repositório, mas agora a raiz é a
saída de um gerador em Python (só biblioteca padrão): o que se edita fica em `fonte/`.

**Push e PR só com o OK do Rosiel.** Este texto fica pronto no repositório até lá.

## O que muda

- **Gerador e dados.** `python3 fonte/gerar.py` escreve todas as páginas, o `sitemap.xml`, o JSON-LD e `assets/paleta.json` a partir de
  `fonte/dados/*.json` (estúdio, pessoas, serviços, projetos), `fonte/modelos/` e `fonte/conteudo/`. Telefone, e-mail e links vêm de
  `estudio.json`, nunca escritos à mão nas páginas. `python3 fonte/checar.py` valida a saída (sem erro = rc 0).
- **Visual novo.** Escuro, com tokens de cor e tipografia em `css/tokens.css` e o resto em `css/site.css` (saem `css/styles.css` e
  `css/servico.css`). Fontes Fraunces, DM Sans e JetBrains Mono servidas por nós em `assets/fontes/`. Acento violeta para o Caio e
  laranja para o Rosiel; os blocos claros usam o neutro de baixa saturação `--claro` (R236 G235 B230).
- **Movimento.** GSAP 3.13.0 (com ScrollTrigger e SplitText) e Lenis 1.3.27 em `js/vendor/`, com versão e SHA-256 fixados em
  `VERSOES.json` e conferidos por teste. Com `prefers-reduced-motion` não sobra nenhum transform depois de 1 s. Sem JS o conteúdo
  todo aparece (sai `js/servico-gsap.js`).
- **Páginas novas.** `/caio/` e `/rosiel/` (perfis), `/projetos/` (portfólio) e quatro cases: `/projetos/prosup/`,
  `/projetos/fakly/`, `/projetos/sendany/` e `/projetos/heisuca/`.
- **Hero inspetor.** A home mostra telas reais de produto (`assets/inspetor/`) com caixas de inspeção que acendem e apagam; a troca
  de tela só começa depois do primeiro gesto do visitante (para não atrasar o LCP) e, parado, o hero fica calmo. Sem JS fica só a
  primeira imagem.
- **Paleta de comandos.** `Ctrl K` (ou a pílula `> ir para…` no cabeçalho, também no toque) abre uma lista com 16 opções: projetos,
  serviços, as duas pessoas e os canais de contato; `Esc` fecha e devolve o foco. Sem JS a pílula é um link para `/projetos/`.
- **Contato.** Link do WhatsApp com mensagem pronta e um código de origem no fim dela (por exemplo `[site·case·heisuca]`), para saber de
  onde veio o contato. Sem formulário.
- **Compartilhamento.** Uma imagem OG de 1200×630 por página em `assets/og/`, gerada por `bancada/og.mjs`.
- **Bancada.** `bancada/` mede cada página com Playwright, axe e Lighthouse móvel, e confere paleta e inspetor em casos à parte.
- **CI.** `.github/workflows/checar.yml` roda os testes, regera o site e exige que o `git diff` fique limpo, e roda `checar.py`.
- **Saem do repositório:** `css/styles.css`, `css/servico.css`, `js/servico-gsap.js` e `assets/images/og-image.png`.
- **Intocados:** `CNAME`, `app-ads.txt`, `.github/FUNDING.yml` e `robots.txt`.

Nada da Amott aparece na saída do site (há teste para isso).

## URLs preservadas

Comparação com a base (`git show 7acc4d2:sitemap.xml` e `git ls-tree -r --name-only 7acc4d2 | grep index.html`) contra a saída atual:

| URL da base | Hoje |
|---|---|
| `/` | igual |
| `/historia.html` | igual (sem redirecionamento; a URL com `.html` continua) |
| `/servicos/criacao-de-sites-institucionais/` | igual |
| `/servicos/landing-page-conversao/` | igual |
| `/servicos/bots-whatsapp-automacao/` | igual |
| `/servicos/aplicativo-mobile-react-native/` | igual |
| `/servicos/desenvolvimento-mvp-startups/` | igual |
| `/servicos/automacoes-integracoes-api/` | igual |

**Nenhuma página da base sumiu.** A base tinha 8 páginas; a saída tem 15. As 7 novas são `/caio/`, `/rosiel/`, `/projetos/` e os
quatro cases. O `sitemap.xml` lista 14: `/projetos/heisuca/` fica de fora, porque é rascunho e sai com `noindex` (ver itens em aberto).

**URLs de arquivo que deixam de existir: 4.** São todos os arquivos servidos da base `7acc4d2` que não estão mais na saída (conferido com
`git ls-tree -r --name-only 7acc4d2` contra a árvore atual; `fonte/`, `bancada/`, `docs/` e `.superpowers/` são novos e não contam). Os
outros 37 arquivos da base seguem no mesmo caminho. Os 4 passam a dar 404:

| URL que some | Destino |
|---|---|
| `/assets/images/og-image.png` | `/assets/og/<página>.png`: a imagem de compartilhamento antiga, que as páginas da base citavam em `og:image` e `twitter:image`; agora cada página cita a sua |
| `/css/styles.css` | removido, sem substituto (o CSS é `/css/tokens.css` e `/css/site.css`); nenhuma página o referencia |
| `/css/servico.css` | removido, sem substituto (idem); nenhuma página o referencia |
| `/js/servico-gsap.js` | removido, sem substituto (o movimento está em `/js/site.js` e em `/js/vendor/`); nenhuma página o referencia |

Só o `README.md` ainda cita os três de CSS/JS (ver "Técnicos"). Quem já compartilhou um link pode ver a prévia antiga em cache até a rede
social atualizar; o link da página em si não muda. Se quiserem evitar o 404 da imagem OG, basta voltar a gerar um arquivo com esse nome
(não fiz: seria um arquivo a mais só para cache de terceiros).

## Como ver a prévia

A prévia sai com `noindex` em todas as páginas, `robots.txt` com `Disallow: /` e o cabeçalho `X-Robots-Tag: noindex` (`_headers`).

Local:

```
python3 fonte/gerar.py --previa --saida <pasta-fora-do-repo>
python3 bancada/gzserver.py 8765 <pasta-fora-do-repo>
# abrir http://127.0.0.1:8765/
```

Cloudflare Pages, no ramo `previa`:

```
Comando de build:   python3 fonte/gerar.py --previa --saida dist-previa
Pasta de saída:     dist-previa
```

(`dist-previa/` está no `.gitignore`.) Para a bancada, ver `bancada/LEIA.md`.

## Metas medidas

Rodada de 2026-11-23 sobre o commit `b7bb892`, nas 15 páginas, Lighthouse móvel com 4G simulado. Detalhe, capturas citadas, as 6
medidas de LCP por página, o inspetor, a paleta e a comparação com a Amott: [`bancada/relatorios/2026-11-23/RELATORIO.md`](../../bancada/relatorios/2026-11-23/RELATORIO.md).

| Meta | Resultado |
|---|---|
| LCP < 2500 ms | passa em 15/15. Home ~907 ms; `/rosiel/` até 2263 ms; `/caio/` até 2408 ms (6 medidas cada) |
| CLS < 0,05 | passa em 15/15 (máximo 0,029, em `/projetos/`) |
| axe: 0 serious/critical | passa em 15/15, em 430 e 1440 px (inclui a regra `target-size`, AA) |
| Sem rolagem horizontal em 430 px | passa em 15/15 |
| Alvos de toque ≥ 44 px nos controles | passa: 0 controles abaixo de 44 px em 15 páginas |
| Funciona sem JS | passa em 15/15 (título, contato e, em `/projetos/`, todos os cards) |
| `reducedMotion` sem transform após 1 s | passa em 15/15 |
| Links internos com 200 e sem redirecionamento | passa em 15/15 |
| Inspetor do hero e paleta de comandos | passam (casos solo `bancada/inspetor.mjs` e `bancada/paleta.mjs`) |
| Testes | `python3 -m unittest discover -s fonte/testes -t fonte -v`: 202 OK; `gerar.py` sem diff; `checar.py` com 0 erro |

Duas margens finas, ambas explicadas no relatório: `/caio/` tem 92 ms de folga no LCP e `/rosiel/` tem 237 ms (o LCP das duas é a foto
de perfil, hoje provisória).

## O que muda em relação à spec

- Contraste AA: `--rosiel-texto` passa de `#c2410c` para **`#9a3412`**, e entram `--suave #9b99a6`, `--caio-texto #a78bfa` e
  `--caio-texto-claro #6d28d9`.
- Campos novos nos dados: `nome` curto nos serviços (para a mensagem do WhatsApp), `atualizado` (para o `lastmod`), `inspetor` no
  `estudio.json` e `rascunho` nos textos provisórios.
- A bancada vem antes do visual (Tarefa 8), para medir a linha de base.
- Exceção temporária da regra de cor para os CSS antigos até a Tarefa 10.
- Workflow de CI novo (`.github/workflows/checar.yml`).
- A spec descreve o `--claro` (`#ecebe6`) como "blocos claros frios". A cor real é quente e pouco saturada (R236 G235 B230, matiz de
  cerca de 50°, saturação 0,14), não fria. A spec fica como está e o valor da cor não mudou; só o rótulo, e por isso este PR a chama de
  neutro de baixa saturação. A comparação com a Amott (item [R] 7 abaixo) usa essa saturação, não a temperatura.

## Itens em aberto

### [R] Rosiel

Já feitos na 13A: dados do ProsUp, do Fakly e do SendAny (brief 3) e os textos de §6 (brief 5).

1. (brief 1) Ligar o Cloudflare Pages no ramo `previa`, com o comando e a pasta da seção "Como ver a prévia".
2. (brief 2) Mandar as fotos dos dois. As atuais são provisórias; medir o LCP de `/caio/` e `/rosiel/` de novo quando chegarem (folga de 92 e
   237 ms, ver acima). Se passar de 2500 ms, o primeiro remédio é um arquivo menor (por exemplo 480 px).
3. (brief 4) Dizer se o Ultron tem acesso ao repositório.
4. (brief 6) Trocar o e-mail pelo do domínio: basta mudar `fonte/dados/estudio.json` e gerar de novo.
5. (novo) **"Engenheiro sênior" e "sócios".** `fonte/conteudo/historia.html` ("virou engenheiro sênior") e as constantes `HOME_DESCRICAO` ("dois
   sócios") e `HISTORIA_DESCRICAO` em `fonte/alldevs/paginas.py` ainda trazem a bio dele como estava (não mexi). Confirmar se vale ou
   trocar o texto.
6. (novo) **Uma voz só.** A frase do Rosiel está em 1ª pessoa e a do Caio em 3ª. Escolher uma e ajustar a outra.
7. (feito) **Botão principal.** O botão principal claro em cápsula era o ponto mais concreto do Codex. `.btn-primary` em `css/site.css` agora
   tem só contorno (`--claro`, fundo transparente) e se preenche no `:hover` e no `:focus-visible`. Só tokens, sem cor nova. Com isso, o
   Codex respondeu **não** na comparação refeita.
8. (aberto, decisão do Rosiel) **Títulos e hero.** O Codex ainda cita a serifa dos títulos e o hero em duas colunas (título à esquerda,
   visual à direita, dois botões), embora conclua que não parecem o mesmo estúdio. Fraunces 600 é serifa suave, não didone, e o hero em duas
   colunas é comum. Trocar a família do título (`--fonte-titulo` em `css/tokens.css`) ou o hero seria redesenho: se o Rosiel quiser, é
   uma tarefa à parte; se não, o portão §9.5 fica dispensado nesses dois pontos por decisão dele. Resposta íntegra no relatório.

### [C] Caio

A pergunta só sai pelo Telegram com o OK do Rosiel. Resumo do que falta ele responder:

1. **Na página do estúdio:** o papel dele (hoje "Infraestrutura, mídia e apps"), uma frase em voz própria, links (só `https`: GitHub,
   LinkedIn, outros) e se a foto atual (`assets/images/caio.jpeg`) fica.
2. **Experiência:** se o estúdio pode dizer "mais de 8 anos" ou 10, e como ele quer ser descrito (equipe qualificada, ou com o papel de
   marketing, design e prototipação).
3. **Serviços:** o site não mostra quem toca cada serviço (decisão do Rosiel; o cliente vê "a equipe"). Só precisa dizer se tem objeção.
4. **Heisuca e outros projetos:** tipo, situação real, ano, resumo, problema, o que foi feito, resultado (só com número ou estado
   real), stack, link, imagens, autores e destaque; e se algum outro projeto dele entra como case. A Amott fica fora (o cliente é o
   dono da Amott), salvo se ele liberar.
5. **Telas do Heisuca no hero:** quais ele autoriza mostrar.
6. **Trava de segurança:** nenhum texto, captura ou dado de cliente entra sem o OK dele; dizer o que do Heisuca não pode aparecer
   (servidor, contas, nomes de pessoas).

Enquanto ele não responde:

- **O Heisuca está visível** (`/projetos/heisuca/`, na lista de projetos e na paleta), mas com `noindex`, fora do `sitemap.xml` e **sem
  link externo**, porque o texto é provisório (`rascunho: true`). O que ele vetar ganha `visivel: false`.
- **Os serviços estão sem selo de pessoa**, como o Rosiel decidiu.

### Técnicos

- **`_config.yml` na raiz** (`exclude: [docs, bancada, fonte, README.md]`) tira essas pastas do site publicado. Depois do merge,
  conferir que `/README.md`, `/docs/`, `/bancada/` e `/fonte/gerar.py` dão 404; se não derem, o Pages está em deploy por Actions e
  é preciso publicar só os arquivos do site.
- **`README.md`** atualizado: estrutura, gerador, testes, prévia e bancada.
- **Links de texto corrido, logo e rodapé** têm entre 17 e 34 px de altura. Passam o AA (2.5.8, que tem exceção para link em linha de
  texto), mas não o AAA (2.5.5, 44 px). Não mexi porque mudaria a leitura do texto. A regra de 44 px vale, e passa, para controles.
- **Os 4 arquivos removidos** (imagem OG antiga e 3 de CSS/JS) devolvem 404 (ver "URLs preservadas").
- **Capturas de página inteira** da bancada mostram seções vazias abaixo da primeira tela: a revelação por rolagem só pinta o que
  entra na janela. O conteúdo está lá (meta "Sem JS" passa em 15/15).
- **Oscilações isoladas** na rodada completa do Lighthouse (`/historia.html` 1219 ms, `/servicos/desenvolvimento-mvp-startups/` 1215 ms,
  CLS 0,011 em `/servicos/bots-whatsapp-automacao/`), todas dentro das metas e sem repetir nas medições 3×.
- **Comparação com a Amott (Passo 2).** O primeiro Codex não abriu o site de referência (sem DNS no sandbox) e pediu capturas dela; fiz a
  segunda rodada lado a lado. Resposta: "sim, mesma família visual", com 6 pontos. O Codex apontou componentes de padrão comum (botões em
  cápsula com o principal claro e o secundário contornado, cabeçalho com o último item em cápsula, chamadas pequenas e espaçadas acima dos
  títulos, hero em duas colunas) e a serifa dos títulos; nenhum texto nem rótulo da Amott apareceu. Na revisão final apliquei a opção barata (item [R] 7: botão
  principal só com contorno) e refiz a comparação: o Codex respondeu **não**, não parecem o mesmo estúdio. Ele ainda cita o hero em duas
  colunas, o cabeçalho, a serifa dos títulos e os rótulos espaçados; esses itens ficam no item [R] 8. Resposta íntegra no relatório,
  seção "Comparação refeita (revisão final)".

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01Bxzke1fDqMR8GQ6eWNkVxj
