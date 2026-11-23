# AllDevs — redesenho do site (spec de desenho)

- Data: 21/11/2026
- Site: `https://all.dev.br`. Repo: `misterioso013/alldevs`, ramo de trabalho `claude/redesenho`.
- Quem decide: Rosiel Victor (dono do repo). O Caio Guerras decide só quais projetos dele entram.
- Estado: desenho aprovado por partes na conversa. Esta spec espera a revisão do Rosiel.

## 1. Objetivo

Hoje o site é o portfólio de uma pessoa só (Rosiel). Ele passa a ser o **site de um estúdio de dois sócios, Rosiel e Caio**.

- A marca AllDevs vem primeiro. Os dois aparecem com o mesmo peso.
- Cada sócio tem uma página própria, com garantia pessoal.
- A qualidade de acabamento toma como referência `amott.docaio.com.br`, mas com **identidade própria**.

**O site está certo quando:**
1. Quem chega entende em até 5 s o que o estúdio faz e quem são os dois.
2. Todo caminho termina num contato que diz de onde a pessoa veio.
3. A busca orgânica dos 6 serviços não perde posição: as URLs e os títulos atuais ficam.
4. Na tela do celular, LCP fica abaixo de 2,5 s (4G) e CLS abaixo de 0,05.
5. Um revisor externo, vendo capturas lado a lado, **não** acha que é o mesmo estúdio da Amott.

**Fora do escopo:**
- formulário de contato;
- analytics;
- blog;
- modo claro;
- three.js / WebGL;
- troca de hospedagem do site oficial (continua o GitHub Pages).

## 2. Posicionamento

O site se apresenta como **estúdio**, com a garantia de cada sócio:

- **Home:** é do estúdio.
- **Perfis:** `/caio/` e `/rosiel/` têm a mesma estrutura e tamanho.
- **Portfólio:** é um só, com filtro Todos / Caio / Rosiel.
- **Serviços:** cada um tem o campo `quem_toca` (`caio`, `rosiel` ou os dois).
- **Texto:** o Caio passa a ser **sócio**, não "mentor". A gratidão e a mentoria continuam na `historia.html`, que não muda de conteúdo.
- **Contato:** é do estúdio. O "Olá Rosiel" sai de todo o site.
- **ProsUp** (`prosup.app`, `docs.prosup.app`) entra como produto do Rosiel.
- **Projetos do Caio:** todos entram no começo. Os que ele vetar recebem `visivel:false` (ver 11).

## 3. Páginas

| URL | Conteúdo |
|---|---|
| `/` | hero, quem somos, destaques, serviços, contato |
| `/caio/`, `/rosiel/` | perfil: topo, "o que eu faço" (3 itens), projetos do autor, links |
| `/projetos/` | todos os projetos visíveis, com filtro Todos/Caio/Rosiel |
| `/projetos/<slug>/` | case |
| `/servicos/<slug>/` | os 6 atuais, **mesmas URLs** |
| `/historia.html` | o texto fica intacto, em `fonte/conteudo/historia.html`; o gerador põe o cabeçalho e o rodapé novos; o título passa a "A história — AllDevs"; link a partir de `/rosiel/` |

- **Ficam como estão:** `CNAME`, `app-ads.txt`, `robots.txt`, `.github/FUNDING.yml`.
- **Serviços atuais:** `aplicativo-mobile-react-native`, `automacoes-integracoes-api`, `bots-whatsapp-automacao`, `criacao-de-sites-institucionais`, `desenvolvimento-mvp-startups`, `landing-page-conversao`.

## 4. Estrutura técnica

O site é gerado por um **gerador em Python (só biblioteca padrão)** e publicado como páginas estáticas. A saída gerada é commitada.

```
fonte/
  gerar.py                 gerador
  dados/
    estudio.json           nome, whatsapp, email, telegram, mensagens, redes
    pessoas.json           caio, rosiel
    projetos.json
    servicos.json
    inspecao/<slug>.json   caixas do hero (parte 7)
  conteudo/servicos/<slug>.html   texto longo de cada serviço (migrado)
  modelos/                 modelos HTML (string.Template ou equivalente stdlib)
css/tokens.css             única fonte de cor, letra, espaço, tempo
css/*.css, js/*.js         estilos e módulos
assets/og/<slug>.png       imagens OG (geradas pela bancada)
bancada/                   scripts de teste e relatórios (fora do site)
```

### 4.1 Dados

- **`pessoas.json`**: `slug`, `nome`, `papel`, `papel_mono`, `frase`, `foto`, `links[]`, `cor` (`roxo` | `laranja`).
- **`projetos.json`**: `slug`, `nome`, `autores[]` (`caio`/`rosiel`), `tipo` (`app`, `site`, `bot`, `produto`, `ferramenta`), `situacao` (`no ar`, `beta`, `encerrado`), `ano`, `resumo`, `problema`, `fizemos[]`, `resultado` (opcional), `stack[]`, `link`, `imagens[]`, `destaque` (bool), `visivel` (bool).
- **`servicos.json`**: `slug`, `titulo` (o `<title>` atual), `descricao`, `resumo`, `quem_toca[]`.
- **`estudio.json`**: `nome`, `whatsapp` (número só aqui), `email` (provisório `rosielvictor.dev@gmail.com`, vai ser trocado pelo do domínio), `telegram` (`https://t.me/m/PYdcFSXtNjZh`), `mensagens` (modelos por tipo de página), `redes[]`.

### 4.2 Gerador (`fonte/gerar.py`)

1. Lê os dados e **valida**. Qualquer erro faz o gerador sair com código diferente de zero:
   - slugs únicos;
   - todo autor existe em `pessoas.json`;
   - toda imagem citada existe;
   - todo link externo é `https`;
   - toda `descricao` tem de 140 a 160 caracteres (fora disso, só avisa);
   - toda página tem OG em `assets/og/` (se faltar, avisa).
2. Gera as páginas a partir de `fonte/modelos/`. Cada arquivo gerado leva o comentário `<!-- gerado por fonte/gerar.py — não editar -->`.
3. Gera o `sitemap.xml`.
4. Gera o `<title>`, a descrição, o OG, o Twitter Card e o JSON-LD de cada página:
   - home: `Organization` com `member` → os dois `Person`;
   - perfis: `Person`, mantendo `@id` `https://all.dev.br/#rosiel-victor`; o novo é `https://all.dev.br/#caio-guerras`;
   - cases: `SoftwareApplication` (app) ou `WebSite` (site), com `author`;
   - serviços: `Service` com `provider` → `Organization`.
5. Rodar duas vezes seguidas dá o mesmo resultado, byte a byte.

### 4.3 Publicação e CI

- O GitHub Pages publica a `main`, como hoje.
- Checagens do GitHub Actions, rodando em todo PR:
  - roda `gerar.py`; se houver diff no que foi gerado, falha;
  - um grep reprova cor hexadecimal, `rgb(` ou `hsl(` em `css/` (menos `css/tokens.css`), `js/` (menos `js/vendor/`) e `fonte/modelos/`;
  - um grep reprova "Olá Rosiel" nos arquivos gerados, link `wa.me` sem `text=` e número diferente do `estudio.json`;
  - roda a lista de proibidos da seção 5.1 (o que for checável por grep: nomes de fontes, cores).

## 5. Sistema visual

### 5.1 Regra de identidade

**Da Amott levamos o método, não a cara.**

- **Levamos:** menos texto, poucos cards grandes, movimento com propósito, qualidade que se adapta ao aparelho, cuidado com o celular, bancada e prévia separada.
- **Proibido:**
  - fundo creme;
  - serifa didone (Bodoni e afins);
  - dourado;
  - revelação por fluido;
  - cursor virtual com curva;
  - barra de vidro no rodapé do celular;
  - botão flutuante de contato;
  - preloader.

### 5.2 Cor (só em `css/tokens.css`)

| Token | Valor | Uso |
|---|---|---|
| `--fundo` | `#0d0c12` | base escura |
| `--grade` | linhas de 1 px, opacidade baixa | grade de planta técnica no fundo |
| `--claro` | `#ecebe6` | blocos claros frios, usados pouco |
| `--caio` | `#7c3aed` | roxo: tudo do Caio |
| `--rosiel` | `#f97316` | laranja: tudo do Rosiel |
| `--rosiel-texto` | `#c2410c` | laranja em texto sobre o claro |

- O degradê roxo→laranja só aparece no **trabalho dos dois**.
- O site tem um modo de cor só. Todo texto passa no contraste AA.

### 5.3 Letras

- **Fraunces:** títulos.
- **DM Sans:** texto.
- **JetBrains Mono:** rótulos, como `// 02 — projetos` e `app · 2026 · caio`.
- Os títulos misturam serifa e mono na mesma frase. Exemplo: *Fazemos* `software` *que vive.*
- As fontes vêm com `font-display: swap`, só nos pesos usados, e a fonte do título é pré-carregada.

### 5.4 Forma

- Grade de 12 colunas, com até 1280 px de largura e folga lateral de 16 px no celular.
- As imagens dos cards são 16:10.
- Linhas de 1 px no lugar de sombras.
- Nunca há rolagem horizontal.

### 5.5 Movimento

- **Bibliotecas:** GSAP + ScrollTrigger + SplitText + Lenis, com versão fixa, em `js/vendor/` (sem CDN, nenhum pedido a terceiros). As fontes também ficam no repo (`assets/fontes/*.woff2`), sem Google Fonts.
- **Títulos:** entram como digitação que "compila" de mono para serifa.
- **Cards:** sobem 24 px.
- **Tempos e curva:** 200, 450 e 900 ms, todos com a mesma curva, definida em token.
- **Com `prefers-reduced-motion`:** só esmaecido e sem Lenis.
- **Laços:** param fora da tela e com a aba escondida.

### 5.6 Paleta de comandos

- Abre com `Ctrl K` / `⌘K` e busca projetos, serviços, pessoas e contato ("orçamento", "whatsapp", "telegram", "email").
- No celular, vira uma pílula `> ir para…` no cabeçalho, sem barra fixa embaixo.
- Funciona por teclado: setas, Enter e Esc. Ao fechar, o foco volta para onde estava.
- Sem JS, a pílula vira um link para `/projetos/`.

## 6. Conteúdo

**Regras gerais:**
- O texto vem na primeira pessoa do plural, com frases curtas.
- Cada bloco tem no máximo 2 linhas antes de uma imagem ou de uma lista.
- Todo texto mora em `fonte/dados/` ou `fonte/conteudo/`.

### 6.1 Home

- **Hero:** *Fazemos* `software` *que vive.* Subtítulo: "Dois desenvolvedores, um estúdio. Sites, apps, bots e produtos próprios no ar." Botões: "Ver projetos" e "Pedir orçamento".
- **Quem somos:** dois cartões do mesmo tamanho. Cada um traz foto, nome, `papel_mono` (`caio · infraestrutura, mídia, apps` / `rosiel · produto, web, automação`), frase e link para o perfil.
  - A ordem alterna a cada visita, com um sorteio no JS.
  - Sem JS, vale a ordem alfabética.
- **Destaques:** de 4 a 6 projetos com `destaque:true`, cada um com o selo do autor.
- **Serviços:** os 6, com resumo de uma linha e `quem_toca`.
- **Contato:** seção 8.

Os textos acima são de partida: o Rosiel ajusta na etapa 2.

### 6.2 Case

1. Linha mono: `tipo · ano · autor · situação`.
2. Problema (1 a 2 frases).
3. O que fizemos (3 a 5 itens).
4. Resultado: só com número ou estado real; sem dado real, a linha sai.
5. Stack (etiquetas mono).
6. Imagens 16:10 e link para o produto.

**Primeiros cases:** ProsUp, Fakly e SendAny (Rosiel); Heisuca (Caio). Depois entram os outros que o Caio liberar. O case da Amott só entra se o Caio liberar, porque o cliente é o dono da Amott; mesmo assim, só com texto e capturas, nunca com a identidade visual da Amott no nosso código.

### 6.3 Títulos

| Página | `<title>` |
|---|---|
| Home | `AllDevs — Estúdio de software: sites, apps e automações` |
| Perfis | `Caio Guerras — AllDevs` / `Rosiel Victor — AllDevs` |
| Projetos | `Projetos — AllDevs` |
| Case | `<Projeto>: <tipo> — AllDevs` |
| Serviços | os atuais, sem mudança |
| História | `A história — AllDevs` |

A descrição da home deixa de falar de "desenvolvedor full stack disponível para freelas" e passa a apresentar o estúdio, citando os dois.

### 6.4 Serviços

O texto longo é migrado **sem reescrever**. Só três coisas mudam:
- "eu" vira "nós" onde o serviço é dos dois;
- entra o selo `quem_toca`;
- o botão de contato segue a seção 8.

## 7. Hero "inspecionar elemento"

- **Layout:** à esquerda, título, subtítulo e botões. À direita, uma janela com uma tela real de produto e o inspetor por cima. No celular, a janela fica abaixo do título.
- **Rodízio:** Heisuca (Caio), ProsUp (Rosiel) e Fakly ou SendAny (Rosiel).
  - A Amott fica **fora** do hero, de propósito.
  - Cada tela fica cerca de 8 s.
  - Há um botão "próximo" acessível pelo teclado.
  - O selo do autor sai na cor dele.
- **Dados:** cada tela é uma imagem WebP/AVIF com o seu `fonte/dados/inspecao/<slug>.json`. Cada caixa tem `x`, `y`, `w`, `h` em %, `tag`, `classe`, `medida` e `codigo`.
  - **Produtos web:** um script Playwright da bancada mede as caixas na página real.
  - **App Android:** as caixas são marcadas à mão.
- **Desenho:** poucos `div` com `transform`, sem canvas.
  - A caixa tem contorno na cor do autor e padding hachurado.
  - Réguas vão até as bordas.
  - A etiqueta mono mostra, por exemplo, `button.cta · 312×48`.
  - Uma linha de código embaixo da janela mostra o trecho correspondente.
- **Comportamento:**
  - **Com mouse:** a caixa sob o cursor acende.
  - **Parado ou sem mouse:** o inspetor percorre as caixas a cada ~1,2 s, pulando de uma para outra, sem cursor andando.
  - **No celular:** o percurso é automático enquanto o hero está visível e não prende a rolagem. Um toque inspeciona a caixa.
  - **Com reduced-motion:** a imagem fica parada com 2 caixas acesas.
  - **Sem JS:** só a imagem.
- **Código:** `js/inspetor.js`, com até 8 KB do jeito que está no repo (o site não tem etapa de build).
- **Acessibilidade e desempenho:**
  - O inspetor tem `aria-hidden` e a imagem tem `alt`.
  - O LCP é o título.
  - A 1ª tela é pré-carregada e as outras carregam quando o hero aparece.
  - O laço para fora da tela e com a aba escondida.

## 8. Contato

- **Onde fica:**
  - O cabeçalho sempre mostra "Pedir orçamento".
  - O bloco de contato fecha a home, os perfis, os cases e os serviços.
  - A paleta de comandos também leva ao contato.
- **O que oferece:**
  - WhatsApp é o botão principal.
  - Telegram e e-mail aparecem como links secundários.
  - Não há botão flutuante nem formulário.
- **WhatsApp:** `<a href="https://wa.me/<número>?text=…">`, montado pelo gerador e funcionando sem JS. O número sai do `estudio.json` e nunca é escrito à mão.
  - **Mensagens prontas:**
    - Home: "Olá, AllDevs! Vim pelo site e quero conversar sobre um projeto. [site·home]"
    - Serviço: "Olá, AllDevs! Tenho interesse em *<serviço>*. [site·servico·<slug>]"
    - Case: "Olá, AllDevs! Vi o case do *<projeto>* e quero algo parecido. [site·case·<slug>]"
    - Perfil: "Olá, AllDevs! Vim pela página do <nome>. [site·perfil·<slug>]"
  - O código `[site·…]` mostra a origem sem cookie, sem pixel e sem serviço de terceiros.
- **Telegram:** o link `https://t.me/m/PYdcFSXtNjZh` tem mensagem fixa, então não leva o código de origem.
- **E-mail:** `mailto:` com o assunto "Orçamento [site·…]".
  - O endereço é provisório. Na troca pelo do domínio, muda só o `estudio.json`.
  - Como é provisório, fica em texto puro mesmo com risco de spam. Quando vier o do domínio, vale ligar um filtro ali.
- **Medição:**
  - Sem analytics.
  - Se um dia quiserem números de visita, a opção é uma ferramenta sem cookie (por exemplo, Cloudflare Web Analytics). Só entra com o OK do Rosiel.

## 9. Bancada e prévia

- **Local:** `python3 fonte/gerar.py && python3 -m http.server`.
- **Online:** o ramo `previa` é publicado pelo **Cloudflare Pages**, que cria o link a cada push. Ligar a conta é tarefa do Rosiel.
  - A prévia tem `noindex` na meta e no `X-Robots-Tag`, mais um `robots.txt` que bloqueia tudo.
  - O gerador recebe `--previa` para ligar esse modo.
- **Bancada** (Playwright, em `bancada/`), a cada entrega:
  1. **Capturas:** 430 px e 1440 px de home, perfil, projetos, um case, um serviço e a história.
  2. **Desempenho:** Lighthouse com perfil celular 4G. Reprova com LCP de 2,5 s ou mais, ou CLS de 0,05 ou mais.
  3. **Acessibilidade:** axe-core sem erro grave, e navegação por Tab no hero, na paleta e no filtro com reduced-motion ligado.
  4. **Sem JS:** o conteúdo e os links funcionam.
  5. **Teste de diferença com a Amott:**
     - capturas lado a lado nas duas larguras;
     - um revisor externo (Gemini ou Codex) responde: "parecem o mesmo estúdio?";
     - roda a lista de proibidos.
     - Se o revisor disser que sim, a peça volta para refazer.
  6. **Links:** todos os internos respondem 200, e os de contato passam nas regras da seção 8.
  7. **Imagens OG:** o script captura `assets/og/<slug>.png` (1200×630).
- **Relatório:** sai em `bancada/relatorios/<data>/RELATORIO.md`, com as capturas, fora do site publicado.

## 10. Divisão de trabalho

| # | Etapa | Faz | Revisa |
|---|---|---|---|
| 1 | Fundação: gerador, dados, modelos, validações, sitemap, JSON-LD, CI. O site sai com o **visual atual**. | Claude | Codex |
| 2 | Conteúdo: migração dos 6 serviços, textos da home e dos perfis, cases do Rosiel (ProsUp primeiro) | Claude + Rosiel | Gemini (texto) |
| 3 | Sistema visual: `tokens.css`, letras, grade, componentes, movimento | Claude | Gemini (teste de diferença) |
| 4 | Hero inspetor: `js/inspetor.js`, JSON das caixas, script de medição | Codex/Ultron → Claude integra | Claude |
| 5 | Paleta de comandos | Codex/Ultron | Claude |
| 6 | Bancada completa | Claude (subagente `operario`) | Codex |
| 7 | Revisão final e PR para a `main` | Claude | **Rosiel aprova** |

- As etapas 4 e 5 podem correr junto com a 3, porque só dependem dos tokens.
- O Ultron só enxerga o GitHub. Se o repo não estiver ligado à conta dele, as tarefas 4 e 5 vão para o Codex local (`codex exec … < /dev/null`).
- O Gemini só revisa, pelo `cgmind`, e não toca no código.

**Regras para todos:**
- O trabalho sai em ramos `claude/…` e `codex/…`, nunca direto na `main`.
- Nenhum push no repo do Rosiel sem o OK dele.
- Nada da identidade visual da Amott (do dono da Amott) entra no código: nem fontes, nem cores, nem trechos copiados.
- Cada entrega diz o que foi e o que não foi testado.

## 11. Tarefas de pessoas

- **[C] Caio:** escolher quais projetos dele entram.
  - Na etapa 2, o Claude monta a lista com a prévia de cada case e envia pelo Telegram (`cgf-telegram aviso acao`). **O envio só sai com o OK do Rosiel.**
  - Todos os projetos entram; os vetados recebem `visivel:false`.
- **[R] Rosiel:**
  1. ligar o Cloudflare Pages ao repo;
  2. mandar fotos dos dois para os perfis, ou indicar de onde tirar;
  3. mandar as capturas e os dados reais do ProsUp, do Fakly e do SendAny, ou liberar a bancada para capturar;
  4. dizer se o Ultron tem acesso ao repo;
  5. aprovar os textos de partida da seção 6.1;
  6. trocar o e-mail provisório pelo do domínio quando estiver pronto.

## 12. Riscos

| Risco | Como evitamos |
|---|---|
| Ficar parecido com a Amott | regra da seção 5.1, lista de proibidos no CI, teste de diferença com revisor externo |
| Perder posição na busca dos serviços | mesmas URLs, mesmos títulos, texto migrado sem reescrever, sitemap gerado |
| Alguém editar o HTML gerado | aviso "não editar" no arquivo + CI falha quando há diff |
| Peso do movimento no celular fraco | laços param fora da tela, reduced-motion, metas de LCP e CLS que reprovam |
| Projeto do Caio exposto sem querer | `visivel:false` + consulta [C] antes do merge final |
| E-mail provisório atrair spam | é provisório; troca por uma linha no `estudio.json` |
