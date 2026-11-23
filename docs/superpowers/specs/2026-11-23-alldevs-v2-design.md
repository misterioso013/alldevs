# ALL.dev v2: site de impacto (spec de desenho, 23/11/2026)

Substitui a direção visual de `2026-11-21-alldevs-redesenho-design.md`. A infraestrutura daquela spec continua valendo, com as
exceções listadas aqui: gerador Python, testes, bancada, SEO, imagens OG e URLs dos serviços.

## 1. Intenção (palavras do Caio, 23/11)

- O redesenho publicado em 23/11 (`26115c1`) ficou "genérico" e "parece inacabado". "Nós aprendemos tantas features" e elas não
  aparecem.
- **Objetivo:** "causar interesse; que a pessoa olhe e tenha certeza de que vai querer fechar um projeto com a gente".
- **Régua:** "fizemos algo incrível com o amott.docaio, não aceito nada menos". Queremos a mesma qualidade de acabamento, mas
  com identidade própria.
- **Base:** "voltar a se basear na versão anterior" (`7acc4d2`): fundo escuro, roxo e laranja, Syne e DM Sans, GSAP, e as
  seções serviços, cases, tecnologias, história, depoimentos e contato.
- **Projetos:** são **do estúdio**. Não existe "projeto do Caio" nem "projeto do Rosiel": os dois fizeram todos juntos.
- **Equipe:** Gemini e Codex ajudam (pesquisa, crítica visual e revisão). As referências são os prints do Caio (jiro.build,
  header.design, recent.design, landdding, fontinlogo, godly, land-book), mais awwwards e os vídeos do Gustavo Campelo.

**Por que o site existe:** é a prova. Um estúdio que vende sites e apps convence quando o próprio site já impressiona e mostra
produto real funcionando.

## 2. Metas, não-metas, antimetas

**O site está certo quando:**
1. Nos primeiros 5 s, o hero causa um "uau" ligado ao que vendemos, não um efeito solto.
2. Antes do fim da home, o visitante viu pelo menos 3 produtos reais no ar, com link, e sabe como é trabalhar com a gente.
3. Todo caminho termina num contato de WhatsApp ou e-mail que diz de onde a pessoa veio (regra da spec anterior, seção 8).
4. A busca orgânica não perde posição: as 6 URLs de serviço e os títulos atuais ficam.
5. Desempenho no celular: LCP < 2,5 s em 4G, CLS < 0,05, rolagem a 60 fps com CPU 4× mais lenta e qualidade adaptativa.
6. Um crítico externo (Codex e Gemini) compara com os 5 melhores sites de estúdio da pesquisa e dá nota de "eu contrataria"
   ≥ 8/10. Caio e Rosiel aprovam no celular.

**Não-metas:** blog, formulário próprio, analytics, modo claro, troca de hospedagem (fica no GitHub Pages).

**Antimetas (fracasso mesmo que funcione):**
- cara de template de IA (gradiente roxo genérico, cards iguais, "Lorem" de agência);
- efeito pesado que trava celular fraco;
- número, depoimento ou cliente inventado;
- separar projetos por sócio;
- copiar arte, texto ou identidade de terceiros, inclusive do Amott. Técnicas são permitidas; a arte é nossa.

## 3. Abordagens consideradas

1. **"Por trás do produto"** (revelação no hero): o produto pronto na frente; onde o cursor ou o dedo passa, aparece o que está
   por trás (código, wireframe, fluxo da automação).
2. **"Da ideia ao ar"** (história na rolagem): um projeto nasce enquanto se rola a página: rabisco → protótipo → código →
   produto no ar.
3. **Vitrine 3D de aparelhos:** descartada. É comum, pesada no celular e não diz nada sobre o estúdio.

**Escolha do Caio (23/11): juntar 1 e 2.** O 1 dá o impacto, e o 2 dá a certeza (processo e prova).

## 4. Páginas

| URL | Conteúdo |
|---|---|
| `/` | hero com revelação → faixa de prova → "da ideia ao ar" → projetos → serviços → como trabalhamos → tecnologias → quem somos → depoimentos (só se houver) → FAQ → contato |
| `/projetos/` | todos os projetos do estúdio; filtro **por tipo** (site, app, automação, produto), nunca por pessoa |
| `/projetos/<slug>/` | case: problema, o que fizemos, a revelação "por trás" com aquele produto, resultado e link |
| `/servicos/<slug>/` | os 6 atuais, **mesmas URLs e títulos**, no visual novo; cada um aponta para os projetos do tipo |
| `/caio/`, `/rosiel/` | perfil curto de cada sócio (foto, frase, links); a lista de projetos é a do estúdio inteiro e diz "fizemos juntos" |
| `/historia.html` | texto intacto, no visual novo |

Saem: o filtro Todos/Caio/Rosiel, o campo `quem_toca`, o hero "inspecionar elemento" e o portão "não parecer a Amott".
Pode ficar se couber no visual (decisão do construtor): a paleta de comandos (Ctrl/⌘+K), como detalhe para quem é dev.

## 5. Peças centrais

### 5.1 Hero "por trás do produto"
- **Frente:** a tela real de um produto nosso (ProsUp, Fakly, SendAny, bot de WhatsApp...) num quadro limpo, com a frase grande.
- **Fundo, revelado pela máscara:** o "por trás" do mesmo produto: o código real (trecho curto e legível), o wireframe ou o
  fluxo da automação.
- **Técnica:** a máscara de fluido em canvas 2D do Amott v2 (código nosso): baixa resolução, decaimento, borda na cor da marca.
  - **Celular:** cursor virtual e arrastar o dedo revela sem travar a rolagem.
  - **Ciclo:** a cada volta, troca o produto, a frase e a cor de destaque.
- **Garantias:** qualidade adaptativa como no Amott v2. Com `prefers-reduced-motion`, sem fluido: um botão "ver por trás" faz
  um esmaecido. Sem JS: só a frente, estática.
- **Desempenho:** o LCP é o texto do hero ou a imagem da frente, nunca o canvas.

### 5.2 "Da ideia ao ar"
- Seção presa (GSAP ScrollTrigger) com 4 estágios de **um projeto real**: ideia (nota ou rabisco) → protótipo (wireframe) →
  código (editor digitando) → no ar (produto real, link e um resultado verdadeiro).
- **Celular:** a mesma história sem prender a tela, com os estágios em sequência e transições leves.
- **Reduced-motion:** os 4 estágios estáticos.

### 5.3 Prova e confiança
- **Faixa de prova:** só números verdadeiros (anos de experiência, produtos no ar, tecnologias). Cada número tem fonte no
  `fonte/conteudo/`.
- **Projetos:** cartões com a tela real e a revelação local barata (máscara no hover ou no toque), como os cartões do Amott.
- **Depoimentos:** só reais e com autorização. Sem nenhum, a seção não aparece. Os do site anterior eram "Em breve".
- **Como trabalhamos:** 4 passos curtos, prazos honestos e o que o cliente recebe.
- **Contato:** em todo lugar. No celular, barra inferior fixa com "Falar no WhatsApp" (como a do Amott).

### 5.4 Identidade
- **Ponto de partida** (`7acc4d2`): fundo `#0a0a0f`, roxo `#7c3aed` e laranja `#f97316`, Syne nos títulos e DM Sans no texto.
- **Refinamento permitido:** proporções, escala tipográfica, grão e luz, desde que fique claro que é a mesma marca.
- **Movimento:** GSAP 3.13 e ScrollTrigger; Lenis só no desktop (já estão em `js/vendor/`). Texto cinético nos títulos,
  entradas com stagger e cursor próprio no desktop.
- **Referências:** a pesquisa em `~/cgmind/pareceres/*alldevs-ref-*.md` traz os sites e as técnicas. Usar o método do Gustavo
  Campelo: gravar a referência, anotar, reconstruir com arte nossa e comparar.

### 5.5 Referências aplicadas (pesquisa do Gemini, 23/11; domínios não reverificados)
Íntegras: `~/cgmind/pareceres/20261123-204317_pesquisa_alldevs-ref-{estudios,youtube}.md`.
- **Estúdios a estudar antes de cada peça:** basement.studio (tipografia pesada, cursor próprio, laboratório/GitHub),
  view-source.com (texto cinético, clip-path e case em `sticky`), unseen.co (ASCII ao vivo em `<pre>` só quando visível),
  n4.studio (curvas GSAP), malvah.co (entrada com `clip-path` em 400 ms), thefirstthelast.agency (grade editorial de
  projetos) e studiofreight.com (grade visível, metadados em mono).
- **Aplicações (decisões minhas):**
  - o "por trás" pode ter uma camada ASCII ou de código vivo, a 15 fps e só quando visível;
  - a revelação de títulos usa linhas com `overflow:hidden` e stagger de cerca de 0,05 s;
  - os cases usam `position: sticky` no desktop;
  - a grade e os metadados ficam em mono;
  - o preloader segue o modelo do Amott: só na primeira visita, no máximo cerca de 1 s.
- **Confiança (padrões BR):** proposta clara na 1ª dobra; stack e integrações explícitas (API oficial do WhatsApp/Meta,
  ERPs e CRMs só se já fizemos); etapas de trabalho visíveis; WhatsApp com mensagem que diz de onde a pessoa veio.
  Formulário próprio continua fora (não-meta).
- **Método (vídeos do Gustavo Campelo):** decompor a referência em blocos e reconstruir uma peça por vez. Comparar quadros
  em rodadas na bancada (Playwright). Animar só `transform` e `opacity`. Trocar listeners de rolagem por
  IntersectionObserver. Converter mídia para WebP/WebM.
- **Skills para os subagentes:** `greensock/gsap-skills` (GSAP oficial), `ibelick/ui-skills` (fixing-motion-performance) e
  `Leonxlnx/taste-skill` (anti-"cara de IA"), lidas como referência e **sem instalar nada sem OK**.

## 6. Técnica e restrições

- **Reaproveitar:** o gerador `fonte/gerar.py`, os módulos `fonte/alldevs/*`, os testes, a bancada (`bancada/`), o sitemap e
  a OG.
- **Refazer:** CSS e JS da camada visual.
- **Stack:** só HTML, CSS e JS estáticos, sem framework e sem build de npm no site. Canvas 2D sim; WebGL só se um crítico
  provar ganho grande e houver fallback.
- **Conteúdo:**
  - reaproveitar os textos aprovados no redesenho (serviços, FAQ, descrições);
  - cases (ver 10): Amott, Heisuca, CGFLIX Lite, ProsUp, Fakly e SendAny. ForjaDev, AllDevs Platform e o "site em 2 h" do
    site antigo só entram se houver tela e link reais.
- **Prévia:** fora do `main`, num caminho da VPS com `noindex`. O link vai ao Caio por `cgf-telegram aviso entrega`. O
  `main`, ou seja o site no ar, só muda com OK do Caio ou do Rosiel.
- **Site no ar até lá:** fica o `26115c1` (proposta de 23/11; o Caio não pediu reverter).

## 7. Trabalho e revisão

- **Pesquisa e crítica:** Gemini (`cgmind`), mais o Codex como crítico visual com a régua "você contrataria?".
- **Implementação:** subagentes Sonnet, uma peça por vez. Ordem: hero → "da ideia ao ar" → home → projetos/cases →
  serviços → perfis/história.
- **Revisão:** Claude e Gemini por peça. Bancada com capturas em 360, 430 e 1440 px, LCP/CLS, FPS com CPU 4×, axe e sem-JS.
- **Aprovação:** prints e prévia para o Caio e o Rosiel (pelo Branco) antes de ir ao `main`.

## 8. O que fica com o construtor

Disposição exata das seções, escala tipográfica, quais trechos de código e wireframes aparecem no hero, curvas e tempos das
animações, e o desenho do cursor. Tudo passa pela crítica externa e pela bancada.

## 9. Respostas da checagem do construtor (23/11)

**Já respondidas pelo projeto:**
- **Código do fluido:** está embutido em `index.html` no ramo `claude/amott-v2` do repo `~/amott`. Ler com
  `git -C ~/amott show origin/claude/amott-v2:index.html`. Não mexer nesse repo: outra sessão trabalha nele. A técnica é
  portada para `js/` daqui, com arte e parâmetros nossos.
- **Anos de experiência:** "8 anos" já está aprovado em `fonte/conteudo/`.

**Decisões minhas (o Caio pode corrigir):**
- **Fontes:** hospedar a Syne (OFL) em `assets/fontes/` ao lado da DM Sans; a JetBrains Mono fica para o código do "por trás";
  a Fraunces sai.
- **Faixa de prova:** só números contáveis no próprio conteúdo: "8 anos", nº de produtos com link no ar e nº de tecnologias
  da seção Tecnologias. Nada de "clientes satisfeitos" ou porcentagem.
- **Prévia:** no mesmo modelo do Amott (`publicar-previa`), num subdomínio `docaio` com `noindex` e `robots` bloqueado. A
  bancada mede local, com gzip; a medida no celular real é feita pelo Caio e pelo Rosiel.
- **`/caio/`, `/rosiel/` e `/historia.html`:** fotos e frases como estão; a história mantém o texto (revisado pelo Rosiel em
  `c0a1742`); só o layout muda.
- **Sem conteúdo real para um "por trás":** o produto entra no site como case comum, sem revelação, e não no ciclo do hero.
  Código ilustrativo inventado não entra.

## 10. Respostas do Caio (23/11)

- **Projetos:** "Pode incluir o Amott sim, tbm inclua o Heisuca, pode pegar prints da Google Play mostrando que nosso app é
  reconhecido, o CGFLIX lite também."
  - Heisuca e CGFLIX Lite entram com prints da página da Google Play (prova de app publicado e reconhecido). **Minha
    decisão:** o link vai para a página da loja; os cases falam do app (player, recursos) e nunca do servidor ou do acervo
    (a marca dos players é separada do CGSERVER).
  - Amott entra como case com link para amott.docaio.com.br e a revelação "por trás" no cartão.
- **Depoimentos:** "No momento sem depoimentos isso fica mais pra frente." A seção não aparece; o gerador já prevê a entrada
  futura (lista vazia = sem seção).
- **"Da ideia ao ar":** "Pode redesenhar, geralmente a ideia vinha de conversas do telegram, nos víamos e pensávamos." O
  estágio 1 é uma conversa de chat redesenhada por nós (balões no visual da marca, sem logo do Telegram), com texto curto
  no espírito real, marcada como reconstrução. Depois: "nos víamos e pensávamos" (rabisco ou quadro) → protótipo → código →
  no ar.
- **Código "por trás" (sem resposta explícita; minha decisão):** os projetos são do estúdio, então uso trechos curtos e
  reais dos nossos repositórios, revisados para não ter segredo, chave, URL interna nem dado de cliente. A lista de trechos
  vai para o Caio e o Rosiel conferirem na prévia antes do `main`.
