# Redesenho do AllDevs: plano de implementação

> **Para agentes executores:** sub-skill OBRIGATÓRIA: usar superpowers:subagent-driven-development (recomendado) ou
> superpowers:executing-plans para executar este plano tarefa por tarefa. Os passos usam caixas (`- [ ]`) para acompanhar.

**Objetivo:** trocar o site estático do AllDevs (`all.dev.br`) por um site gerado a partir de dados. O estúdio tem dois
sócios com o mesmo peso, as URLs e os títulos dos serviços ficam iguais, o contato informa de onde veio e o visual não
lembra a Amott.

**Arquitetura:** um gerador em Python, só com a biblioteca padrão (`fonte/gerar.py` e o pacote `fonte/alldevs/`), lê os
JSON de `fonte/dados/` e os trechos de `fonte/conteudo/`. Ele escreve o HTML final na raiz do repo, que é o que o GitHub
Pages publica, e commita essa saída. Com `--previa`, escreve em `dist-previa/` para o Cloudflare Pages, com noindex. O CI
regenera o site e falha se houver diferença. JS e CSS ficam na mão em `js/` e `css/`. A bancada (Node + Playwright) mede a
prévia.

**Tecnologias:** Python ≥ 3.11 (CI em 3.12; local em 3.14), `unittest`, `string.Template`. GSAP 3.13.0 (com ScrollTrigger e
SplitText) e Lenis 1.x em `js/vendor/`. Fontes Fraunces, DM Sans e JetBrains Mono em woff2. Na bancada: Playwright,
`@axe-core/playwright` e Lighthouse, com versões fixas.

**Spec:** `docs/superpowers/specs/2026-11-21-alldevs-redesenho-design.md`. Quem executa lê os dois arquivos; a numeração §
abaixo é a da spec.

## Restrições globais

- Ramo `claude/redesenho`. **Nenhum push e nada na `main` sem o OK do Rosiel.** Commits com
  `git -c user.name="CGSERVER Bot" -c user.email="noreply@anthropic.com" commit`. A mensagem termina com as duas linhas
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` e `Claude-Session: https://claude.ai/code/session_01Bxzke2VKYqCL53xtnTM9Dh`.
- Nada da identidade da Amott (nome visual, cores, fontes, textos, capturas) entra no código. A Amott não aparece no
  inspetor. Como case, só com o OK do Caio.
- Python só com a biblioteca padrão. Testes: `python3 -m unittest discover -s fonte/testes -t fonte -v`.
- Ficam como estão: `CNAME`, `app-ads.txt`, `.github/FUNDING.yml` e `robots.txt` da produção.
- WhatsApp `558189477459`, e-mail `rosielvictor.dev@gmail.com` (temporário), Telegram `https://t.me/m/PYdcFSXtNjZh`.
- Cabeçalho de todo arquivo gerado: `<!-- gerado por fonte/gerar.py — não editar -->`.
- Proibido (§5.1): fundo creme, serifa didone, dourado, revelação por fluido, cursor com curva, barra de vidro no rodapé do
  celular, botão flutuante e preloader. Também ficam fora formulário, analytics, blog, modo claro e WebGL.
- Metas: LCP < 2,5 s e CLS < 0,05 no Lighthouse 4G; nenhuma rolagem horizontal em 430 px; zero problema sério ou crítico no
  axe; tudo funciona sem JS.
- Tokens (§5.2, com o ajuste de contraste deste plano): `--fundo #0d0c12`, `--claro #ecebe6`, `--suave #9b99a6`,
  `--caio #7c3aed`, `--caio-texto #a78bfa`, `--caio-texto-claro #6d28d9`, `--rosiel #f97316`, `--rosiel-texto #9a3412`.
  `--grade` é a cor das linhas de 1 px. O degradê roxo→laranja só aparece no que os dois fizeram juntos.
- Movimento: 200, 450 e 900 ms e uma curva só, todos em token. Com reduced-motion, só esmaecido e sem Lenis.

## Pontos de revisão

1. **Codificação do `wa.me`:** acento, `!`, `*`, `·`, `[` e espaço precisam virar `%XX` (`quote(safe='')`). Com `+` ou com o
   `·` cru, o WhatsApp corta ou troca a mensagem. Teste na Tarefa 3.
2. **`visivel:false` vazando:** um projeto vetado não pode aparecer no sitemap, nos destaques, na paleta, no perfil nem na
   página `/projetos/<slug>/`. Teste na Tarefa 7, mais um grep na saída na Tarefa 6.
3. **Determinismo:** rodar duas vezes dá o mesmo resultado byte a byte. O `lastmod` vem do campo `atualizado`, nunca do
   relógio nem do git. Sem `set` iterado e com `sort_keys` no JSON-LD. Teste na Tarefa 6.
4. **Serviços:** o `<title>` dos 6 serviços é igual, caractere a caractere, ao atual (lista na Tarefa 4). Os links internos
   para `/servicos/<slug>/` terminam em barra, para não gerar redirecionamento. Teste na Tarefa 4.
5. **Sem JS:** o filtro fica escondido (`hidden`) e todos os projetos aparecem. Os cartões ficam em ordem alfabética. O
   inspetor vira só a imagem e a paleta vira um link para `/projetos/`. Teste em Python na Tarefa 7 e no navegador na
   Tarefa 8.

---

## Mapa de arquivos

| Caminho | Papel |
|---|---|
| `fonte/gerar.py` | CLI `main(argv) -> int` |
| `fonte/checar.py` | CLI das checagens do CI |
| `fonte/alldevs/dados.py` | carregar e validar os JSON |
| `fonte/alldevs/contato.py` | código de origem e links de WhatsApp, e-mail e Telegram |
| `fonte/alldevs/modelos.py` | `Seguro`, `esc`, `render` |
| `fonte/alldevs/seo.py` | JSON-LD, sitemap, robots e headers da prévia |
| `fonte/alldevs/paginas.py` | `Pagina`, `montar_todas`, `escrever` |
| `fonte/alldevs/checagens.py` | grep de cor, proibidos, "Olá Rosiel" e `wa.me` |
| `fonte/dados/{estudio,pessoas,projetos,servicos,proibidos}.json`, `fonte/dados/inspecao/<slug>.json` | dados |
| `fonte/conteudo/servicos/<slug>.html`, `fonte/conteudo/historia.html` | texto migrado sem reescrever |
| `fonte/modelos/*.html` | moldes do `string.Template` |
| `fonte/testes/` (`__init__.py`, `fixtures/minima/`) | testes |
| `css/tokens.css`, `css/site.css` | tokens e estilo novo (os CSS antigos saem na Tarefa 10) |
| `js/site.js`, `js/inspetor.js`, `js/paleta.js`, `js/vendor/` (+ `VERSOES.json`) | comportamento |
| `assets/fontes/*.woff2` + `OFL.txt`, `assets/og/<slug>.png`, `assets/projetos/<slug>/` | arquivos estáticos |
| `bancada/` (`package.json`, `rodar.mjs`, `og.mjs`, `relatorios/`) | medição |
| `.github/workflows/checar.yml` | CI |

---

### Task 1: dados (carregar e validar)

**Arquivos:** criar `fonte/alldevs/__init__.py`, `fonte/alldevs/dados.py`, `fonte/testes/__init__.py`,
`fonte/testes/test_dados.py` e `fonte/testes/fixtures/minima/dados/*.json` (2 pessoas, 2 projetos, sendo 1 com
`visivel:false`, 1 serviço, estúdio e `inspecao/` vazio).

**Interfaces que esta tarefa entrega:**
- Dataclasses congeladas: `Estudio(nome, whatsapp, email, telegram, mensagens: dict[str,str], redes: tuple, inspetor:
  tuple[str,...], atualizado)`; `Pessoa(slug, nome, papel, papel_mono, frase, foto, links: tuple, cor, atualizado)`;
  `Projeto(slug, nome, autores: tuple, tipo, situacao, ano: int, resumo, problema, fizemos: tuple, resultado: str|None,
  stack: tuple, link, imagens: tuple, destaque: bool, visivel: bool, atualizado)`; `Servico(slug, nome, titulo,
  descricao, resumo, quem_toca: tuple, atualizado)`; `Dados(estudio, pessoas, projetos, servicos, inspecao: dict[str,dict])`.
- `carregar(raiz: Path) -> Dados`: lê `raiz/fonte/dados/`. As listas saem ordenadas por `slug`. Um campo obrigatório que
  falta gera `ErroDeDados` com o arquivo e o campo.
- `validar(dados: Dados, raiz: Path) -> tuple[list[str], list[str]]`, que devolve (erros, avisos).
- `visiveis(projetos) -> list[Projeto]`.
- Enumerações: `tipo ∈ {app, site, bot, produto, ferramenta}`, `situacao ∈ {no ar, beta, encerrado}`,
  `cor ∈ {roxo, laranja}` e `atualizado` no formato `AAAA-MM-DD`.

- [ ] **Passo 1: escrever os testes que falham.** Em `test_dados.py`:
  - `test_carrega_fixture`: `len(d.pessoas) == 2` e `[p.slug for p in d.projetos] == sorted(...)`.
  - `test_slug_duplicado_e_erro`, `test_autor_inexistente_e_erro`, `test_imagem_inexistente_e_erro`,
    `test_link_http_e_erro` (`http://` é erro, `https://` passa), `test_tipo_invalido_e_erro`,
    `test_inspetor_com_amott_e_erro` (`estudio.inspetor = ("amott",)` gera um erro com "amott"),
    `test_inspetor_slug_sem_arquivo_e_erro`.
  - `test_descricao_fora_de_140_160_so_avisa` (a lista de erros fica vazia e a de avisos não), `test_og_faltando_so_avisa`,
    `test_imagens_vazias_so_avisa`.
  - `test_visiveis_exclui_vetado`.
  Os testes copiam o fixture para um `TemporaryDirectory` e o alteram.
- [ ] **Passo 2:** rodar `python3 -m unittest discover -s fonte/testes -t fonte -v`. Esperado: `ModuleNotFoundError: alldevs`.
- [ ] **Passo 3:** implementar `dados.py` com `json.load` + dataclasses. A validação junta todos os problemas antes de
  devolver; não para no primeiro.
- [ ] **Passo 4:** rodar o mesmo comando. Esperado: `OK`.
- [ ] **Passo 5:** commit `alldevs: dados e validação do gerador`.

### Task 2: moldes e migração do conteúdo atual

**Arquivos:** criar `fonte/alldevs/modelos.py`, `fonte/testes/test_modelos.py`, `fonte/modelos/base.html`,
`fonte/modelos/servico.html`, `fonte/modelos/historia.html` e `fonte/conteudo/servicos/<slug>.html` (6). Criar também
`fonte/conteudo/historia.html` e os dados reais `fonte/dados/servicos.json` e `fonte/dados/estudio.json`.

**Interfaces:**
- `class Seguro(str)`: marca HTML já pronto. `esc(v) -> Seguro` usa `html.escape(v, quote=True)` e devolve `v` intacto se já
  for `Seguro`.
- `render(nome: str, **campos) -> Seguro`: carrega `fonte/modelos/<nome>.html` e usa `string.Template.substitute`. Todo valor
  que não é `Seguro` passa por `esc`. Um campo que falta levanta `KeyError` (nunca usar `safe_substitute`).

- [ ] **Passo 1: testes.** `test_render_escapa_texto` (`<b>` vira `&lt;b&gt;`), `test_render_mantem_seguro`,
  `test_campo_faltando_e_erro`, `test_conteudo_migrado_existe` (os 6 slugs têm arquivo e não estão vazios).
- [ ] **Passo 2:** rodar. Esperado: FAIL.
- [ ] **Passo 3:** implementar `modelos.py`. Para a migração, copiar o `<main>` de cada `servicos/<slug>/index.html` para
  `fonte/conteudo/servicos/<slug>.html` **sem reescrever**. As únicas trocas são as de §6: "eu" vira "nós" e o
  botão/link de WhatsApp sai do trecho, porque o molde passa a pôr o contato. O corpo da `historia.html` vai intacto para
  `fonte/conteudo/historia.html`. Em `servicos.json` vão `titulo` e `descricao` copiados verbatim do `<title>` e da
  `<meta name="description">` atuais, mais um `nome` curto (ex.: "Landing page") e `quem_toca`.
  - Os moldes usam por enquanto `css/styles.css`, `css/servico.css` e `js/servico-gsap.js`, para que a saída da Tarefa 4
    saia igual ao site atual no visual.
- [ ] **Passo 4:** rodar. Esperado: `OK`.
- [ ] **Passo 5:** commit `alldevs: moldes e conteúdo atual migrado`.

### Task 3: contato com origem

**Arquivos:** criar `fonte/alldevs/contato.py` e `fonte/testes/test_contato.py`.

**Interfaces:**
- `TELEGRAM = "https://t.me/m/PYdcFSXtNjZh"`.
- `codigo_origem(tipo: str, slug: str | None = None) -> str`: `"home"` dá `site·home`; `"servico"`, `"case"` e `"perfil"`
  com slug dão `site·<tipo>·<slug>`. Tipo desconhecido, ou sem o slug quando ele é exigido, levanta `ValueError`.
- `mensagem(estudio: Estudio, tipo: str, alvo: str | None = None, slug: str | None = None) -> str`: aplica
  `estudio.mensagens[tipo]` com `{alvo}` e `{codigo}`. Os textos estão em §8 e vão literais em `estudio.json`.
- `link_whatsapp(numero: str, msg: str) -> str` devolve `https://wa.me/<numero>?text=<quote(msg, safe='')>`.
- `link_email(email: str, codigo: str) -> str` devolve `mailto:<email>?subject=<quote("Orçamento [" + codigo + "]", safe='')>`.

- [ ] **Passo 1: testes com os valores exatos.**
  ```python
  HOME_WA = ("https://wa.me/558189477459?text=Ol%C3%A1%2C%20AllDevs%21%20Vim%20pelo%20site%20e%20quero%20"
             "conversar%20sobre%20um%20projeto.%20%5Bsite%C2%B7home%5D")
  HOME_MAIL = "mailto:rosielvictor.dev@gmail.com?subject=Or%C3%A7amento%20%5Bsite%C2%B7home%5D"
  def test_whatsapp_home(self): self.assertEqual(link_whatsapp("558189477459", mensagem(est, "home")), HOME_WA)
  def test_email_home(self): self.assertEqual(link_email(est.email, codigo_origem("home")), HOME_MAIL)
  def test_servico_tem_asterisco_codificado(self):
      url = link_whatsapp("558189477459", mensagem(est, "servico", "Landing page", "landing-page-conversao"))
      self.assertIn("%2ALanding%20page%2A", url); self.assertNotIn("+", url); self.assertNotIn("·", url)
  def test_codigo_sem_slug_e_erro(self): self.assertRaises(ValueError, codigo_origem, "case")
  ```
  O `est` vem do `estudio.json` real (Tarefa 2).
- [ ] **Passo 2:** rodar. Esperado: FAIL. **Passo 3:** implementar. **Passo 4:** rodar. Esperado: `OK`.
- [ ] **Passo 5:** commit `alldevs: contato com código de origem`.

### Task 4: páginas e `gerar.py` (site regenerado com o visual atual)

**Arquivos:** criar `fonte/alldevs/paginas.py`, `fonte/gerar.py` e `fonte/testes/test_paginas.py`. Regenerar
`servicos/*/index.html` e `historia.html`. Nesta tarefa `index.html` ainda sai do molde atual: home migrada com o
contato novo.

**Interfaces:**
- `@dataclass(frozen=True) Pagina(caminho: str, titulo: str, descricao: str, corpo: Seguro, atualizado: str, json_ld: tuple[dict, ...])`.
  `caminho` é relativo e sem barra inicial (ex.: `servicos/landing-page-conversao/index.html`).
- `montar_todas(dados: Dados, raiz: Path, previa: bool) -> list[Pagina]`, ordenada por `caminho`.
- `escrever(paginas, saida: Path, previa: bool) -> None`: grava com o cabeçalho de "gerado" logo depois do `<!doctype html>`.
  Apaga **só** os HTML da saída que tenham o cabeçalho e não estejam na lista (página órfã). Na prévia, copia também `css/`,
  `js/`, `assets/`, `icon.svg` e `CNAME` para `saida`.
- `fonte/gerar.py`: `main(argv: list[str] | None = None) -> int`, com `[--previa] [--raiz R] [--saida S]`. `--previa` sem
  `--saida` sai com rc 2. Erros de validação: imprime cada um e sai com rc 1. Avisos: imprime com prefixo `aviso:` e sai
  com rc 0. Na produção, `saida = raiz`.

- [ ] **Passo 1: testes.**
  - `test_titulos_dos_servicos_iguais`: lê o `<title>` de cada `servicos/<slug>/index.html` gerado num diretório
    temporário e compara com:
    - `aplicativo-mobile-react-native` → `Desenvolvimento de Aplicativo Mobile iOS e Android | React Native — AllDevs`
    - `automacoes-integracoes-api` → `Automação de Processos e Integração de Sistemas via API | Webhook — AllDevs`
    - `bots-whatsapp-automacao` → `Bot para WhatsApp, Discord e Telegram | Automação de Atendimento 24h — AllDevs`
    - `criacao-de-sites-institucionais` → `Criação de Site Institucional Profissional | A partir de R$ 800 — AllDevs`
    - `desenvolvimento-mvp-startups` → `Desenvolvimento de MVP para Startups Web | Next.js — AllDevs`
    - `landing-page-conversao` → `Landing Page de Alta Conversão com WhatsApp | Entrega em 3 Dias — AllDevs`
  - `test_historia_titulo`: `A história — AllDevs`.
  - `test_links_de_servico_com_barra`: nenhum `href="/servicos/<slug>"` sem a barra final em nenhuma página
    (regex `href="/servicos/[a-z0-9-]+"`).
  - `test_orfa_gerada_e_removida_e_manual_fica`: um HTML com o cabeçalho que sobra é apagado; um sem o cabeçalho fica.
  - `test_previa_sem_saida_rc2`, `test_erro_de_dados_rc1`.
  - `test_servico_tem_wa_com_origem`: a página do serviço contém `%5Bsite%C2%B7servico%C2%B7<slug>%5D`.
- [ ] **Passo 2:** rodar. Esperado: FAIL. **Passo 3:** implementar. **Passo 4:** rodar. Esperado: `OK`.
- [ ] **Passo 5:** rodar `python3 fonte/gerar.py` e conferir `git diff --stat`: só os 6 serviços, `historia.html` e
  `index.html` mudam. `git diff servicos/ | grep '^[-+]' | grep -v 'wa.me\|gerado por'` mostra só a troca "eu"→"nós" e o
  bloco de contato. Abrir no navegador com `python3 -m http.server -d .` e ver que o visual é o mesmo.
- [ ] **Passo 6:** commit `alldevs: gerador escreve o site atual a partir dos dados`.

### Task 5: SEO e prévia

**Arquivos:** criar `fonte/alldevs/seo.py` e `fonte/testes/test_seo.py`; alterar `paginas.py` e `gerar.py`; regenerar
`sitemap.xml`.

**Interfaces:**
- `json_ld_home(dados) -> dict`: `Organization`, com `member` apontando para os dois `Person` por `@id`.
- `json_ld_pessoa(p) -> dict`: `Person` com `@id` `https://all.dev.br/#<rosiel-victor|caio-guerras>`; o fragmento vem do slug
  do nome (`nome.lower()` sem acento, com hífen).
- `json_ld_case(proj, dados) -> dict`: `SoftwareApplication` quando `tipo ∈ {app, bot, produto, ferramenta}` e `WebSite`
  quando é `site`. Leva `author`, que é a lista de `@id` dos autores.
- `json_ld_servico(s) -> dict`: `Service`, com `provider` `{"@id": "https://all.dev.br/#organizacao"}`.
- `sitemap(paginas: list[Pagina]) -> str`: `https://all.dev.br/<caminho sem index.html>`, com `lastmod = p.atualizado`.
- `robots_previa() -> str` = `"User-agent: *\nDisallow: /\n"`; `headers_previa() -> str` = `"/*\n  X-Robots-Tag: noindex\n"`.
- O molde `base.html` recebe `$json_ld` (lista serializada com `json.dumps(..., sort_keys=True, ensure_ascii=False)`, e
  `</` escapado como `<\/`), `$canonical` e `$robots_meta`. Na prévia, `$robots_meta` vale `<meta name="robots" content="noindex">`;
  na produção, fica vazio.

- [ ] **Passo 1: testes.** `test_home_org_com_dois_membros`, `test_ids_das_pessoas` (os dois `@id` literais acima),
  `test_case_site_e_website`, `test_servico_provider`, `test_sitemap_sem_vetado`, `test_sitemap_lastmod_do_campo`,
  `test_previa_robots_headers_e_meta` (a saída da prévia tem `robots.txt` com `Disallow: /`, `_headers` com
  `X-Robots-Tag: noindex` e a meta em todas as páginas), `test_producao_nao_toca_robots` (o `robots.txt` da raiz fica com o
  mesmo sha256 depois do `main([])`), `test_json_ld_escapa_fechamento_de_script`.
- [ ] **Passo 2:** FAIL. **Passo 3:** implementar. **Passo 4:** `OK`.
- [ ] **Passo 5:** commit `alldevs: JSON-LD, sitemap e prévia com noindex`.

### Task 6: determinismo, checagens e CI

**Arquivos:** criar `fonte/alldevs/checagens.py`, `fonte/checar.py`, `fonte/dados/proibidos.json`,
`fonte/testes/test_checagens.py`, `fonte/testes/test_determinismo.py` e `.github/workflows/checar.yml`.

**Interfaces:**
- `checar(raiz: Path) -> list[str]` (uma linha por problema, `arquivo:linha: motivo`). Ela verifica:
  - hex/`rgb(`/`hsl(` em `*.css`, `*.js` e `*.html` fora de `css/tokens.css` e `js/vendor/`. **Exceção temporária** para
    `css/styles.css` e `css/servico.css`, em `EXCECOES_TEMPORARIAS`, que a Tarefa 10 esvazia;
  - `Olá Rosiel` em qualquer HTML;
  - `wa.me/` sem `?text=`;
  - número `wa.me/<n>` diferente de `estudio.whatsapp`;
  - cada `{padrao, motivo}` de `proibidos.json` (regex, sem diferenciar maiúscula). A lista inicial tem
    `Playfair|Bodoni|Didot|DM Serif|Cormorant`, `preloader`, `cursor:\s*none`, `#f5f0e6|#faf6ef` (creme) e
    `#c9a227|#d4af37` (dourado);
  - página com `visivel:false` presente na saída (`projetos/<slug>/index.html`) ou citada em `sitemap.xml`.
- `fonte/checar.py`: imprime os problemas e devolve rc 1 se houver algum, rc 0 se não houver.
- Workflow `checar.yml` (em `push` e `pull_request`): `actions/checkout@v4` e `actions/setup-python@v5` com `3.12`. Roda o
  unittest, depois `python3 fonte/gerar.py && git diff --exit-code` e por fim `python3 fonte/checar.py`.

- [ ] **Passo 1: testes.**
  - `test_duas_execucoes_byte_a_byte`: gera duas vezes em diretórios diferentes; os sha256 de todos os arquivos são iguais.
  - `test_saida_nao_depende_do_relogio`: com `os.environ["SOURCE_DATE_EPOCH"]` diferente e
    `time.time` trocado por `unittest.mock`, a saída sai igual.
  - `test_hex_fora_de_tokens_reprova` (arquivo temporário com `color:#fff`), `test_vendor_liberado`,
    `test_ola_rosiel_reprova`, `test_wa_sem_text_reprova`, `test_numero_errado_reprova`, `test_proibido_reprova`
    (`font-family: Playfair Display`), `test_vetado_na_saida_reprova`.
- [ ] **Passo 2:** FAIL. **Passo 3:** implementar. **Passo 4:** `OK`, e `python3 fonte/checar.py` dá rc 0 no repo.
- [ ] **Passo 5:** commit `alldevs: checagens e CI`.

### Task 7: conteúdo novo (pessoas, projetos, perfis e home)

**Arquivos:** criar `fonte/dados/pessoas.json` e `fonte/dados/projetos.json` (ProsUp, Fakly e SendAny do Rosiel; Heisuca do
Caio; a Amott fica fora). Criar os moldes `fonte/modelos/{home,perfil,projetos,case,contato}.html` e o
`fonte/testes/test_conteudo.py`. Alterar `paginas.py`.

**Interfaces (consome as das Tarefas 1 a 5):**
- `paginas.py` ganha estas páginas:
  - `index.html`, com o título `AllDevs — Estúdio de software: sites, apps e automações`;
  - `caio/index.html` e `rosiel/index.html`, com os títulos `Caio Guerras — AllDevs` e `Rosiel Victor — AllDevs`;
  - `projetos/index.html`, com `Projetos — AllDevs`;
  - `projetos/<slug>/index.html`, com `<Projeto>: <tipo> — AllDevs`.
- Bloco de contato (`contato.html`): WhatsApp como botão principal, Telegram e e-mail como secundários, com a origem da
  página. O cabeçalho tem "Pedir orçamento" fixo.
- Hero com o texto literal de §6: *Fazemos* `software` *que vive.* / "Dois desenvolvedores, um estúdio. Sites, apps, bots e
  produtos próprios no ar." Botões "Ver projetos" (`/projetos/`) e "Pedir orçamento" (`#contato`).
- Cartões das pessoas em ordem alfabética pelo `slug` (caio, rosiel), com `data-sortear` no contêiner. Nos destaques, os
  projetos visíveis com `destaque:true`. Se forem menos de 4 ou mais de 6, a validação avisa.
- Linha mono do case: `tipo · ano · autor · situação`. O bloco "Resultado" só aparece quando `resultado` não é `None`.
- Filtro do portfólio: os botões Todos/Caio/Rosiel ficam com `hidden` no HTML. Cada card leva `data-autores="caio rosiel"`.

- [ ] **Passo 1: testes.**
  - Títulos exatos das 5 páginas acima.
  - `test_sem_ola_rosiel`.
  - `test_vetado_nao_aparece`: com um projeto `visivel:false` no fixture, o slug não aparece na home, em `/projetos/`, nos
    perfis nem no índice da paleta (`assets/paleta.json`, Tarefa 12; até lá, os outros pontos). A página do case também não
    é criada.
  - `test_sem_js_filtro_hidden_e_todos_listados`: todos os botões do filtro têm `hidden` e o número de cards é igual a
    `len(visiveis)`.
  - `test_cartoes_ordem_alfabetica`.
  - `test_resultado_omitido_quando_none`.
  - `test_perfis_mesmo_peso`: os dois perfis usam o mesmo molde e têm a mesma lista de seções.
  - `test_wa_do_case_e_do_perfil`: aparecem `%5Bsite%C2%B7case%C2%B7prosup%5D` e `%5Bsite%C2%B7perfil%C2%B7caio%5D`.
- [ ] **Passo 2:** FAIL. **Passo 3:** implementar. Os textos que o Rosiel ainda não mandou vêm de `prosup.app`,
  `docs.prosup.app` e do README atual, marcados com `"rascunho": true` no JSON. A validação avisa sobre cada rascunho.
  O Caio entra como "sócio" (§2).
- [ ] **Passo 4:** `OK`; `python3 fonte/gerar.py && python3 fonte/checar.py` dá rc 0.
- [ ] **Passo 5:** commit `alldevs: perfis, portfólio e home com os dois sócios`.

### Task 8: bancada

**Arquivos:** criar `bancada/package.json` (versões fixas, sem `^`) com `package-lock.json`, `bancada/rodar.mjs`,
`bancada/LEIA.md` e `bancada/relatorios/.gitkeep`.

**Interfaces:**
- `node bancada/rodar.mjs --url <base> --saida bancada/relatorios/<AAAA-MM-DD>` gera `RELATORIO.md` e as capturas. Sai com
  rc 1 se alguma meta falhar. Para cada página do `sitemap.xml` da base, verifica:
  - capturas em 430 e 1440 px;
  - axe, com zero problemas `serious` ou `critical`;
  - sem JS (`javaScriptEnabled:false`): o título e o contato aparecem e `/projetos/` lista todos os cards;
  - `document.documentElement.scrollWidth <= clientWidth` em 430 px;
  - links internos com resposta 200, sem redirecionamento;
  - `reducedMotion:'reduce'`: nenhum elemento com `transform` diferente de `none` depois de 1 s;
  - Lighthouse com a predefinição móvel (4G simulado): LCP < 2500 e CLS < 0,05.
- Servidor local para a prévia: `python3 fonte/gerar.py --previa --saida dist-previa && python3 -m http.server 8765 -d dist-previa`.

- [ ] **Passo 1:** rodar contra o site da Tarefa 7, ainda com o visual antigo, e guardar o relatório como linha de base
  (`relatorios/<data>-base/`). Falhas aqui são esperadas e anotadas, não corrigidas.
- [ ] **Passo 2:** commit `alldevs: bancada (capturas, axe, sem JS, Lighthouse)`.

### Task 9: tokens, fontes e vendor

**Arquivos:** criar `css/tokens.css`, `assets/fontes/{fraunces,dm-sans,jetbrains-mono}-*.woff2` + `assets/fontes/OFL.txt`
(vindos dos pacotes @fontsource com versão fixa, só os pesos usados e com o subconjunto latin), `js/vendor/gsap.min.js`,
`ScrollTrigger.min.js`, `SplitText.min.js` (3.13.0), `lenis.min.js` (1.x estável, publicada há mais de 2 semanas) e
`js/vendor/VERSOES.json` (`{arquivo: {pacote, versao, sha256}}`). Criar também `fonte/testes/test_tokens.py`.

**Interfaces:** variáveis CSS com os nomes de "Restrições globais", mais `--t-curto: 200ms`, `--t-medio: 450ms`,
`--t-longo: 900ms`, `--curva` (uma só) e `--fonte-titulo/--fonte-texto/--fonte-mono`.

- [ ] **Passo 1: testes.**
  - `test_contraste_aa`: lê `tokens.css`, calcula o contraste WCAG e exige ≥ 4,5 em `--claro`/`--fundo`, `--suave`/`--fundo`,
    `--caio-texto`/`--fundo`, `--caio-texto-claro`/`--claro` e `--rosiel-texto`/`--claro`.
  - `test_vendor_sha256`: confere cada arquivo contra o `VERSOES.json`.
  - `test_fontes_com_licenca`.
- [ ] **Passo 2:** FAIL. **Passo 3:** criar os arquivos e calcular os sha256 com `sha256sum`. **Passo 4:** `OK`.
- [ ] **Passo 5:** commit `alldevs: tokens, fontes e bibliotecas com versão fixa`.

### Task 10: visual novo e imagens OG

**Arquivos:** criar `css/site.css` e `js/site.js`; alterar os moldes para usar `tokens.css` + `site.css` + `site.js`.
Os CSS antigos (`css/styles.css`, `css/servico.css`) e o `js/servico-gsap.js` vão para
`~/Arquivos_Obsoletos/2026-11-21_alldevs_css_antigo/` (cópia) e saem do repo com `git rm`. `EXCECOES_TEMPORARIAS` fica vazia.
Criar `fonte/modelos/og.html`, `bancada/og.mjs` e `assets/og/<slug>.png`.

**Interfaces:**
- `site.css`: grade de 12 colunas até 1280 px, folga de 16 px, imagens 16:10, linhas de 1 px e nenhuma sombra. Fraunces nos
  títulos, DM Sans no texto e JetBrains Mono nos rótulos, com `font-display: swap`. O `<link rel="preload">` só para a
  fonte do título.
- `site.js` (carregado com `defer`, sem módulo):
  - digitação mono→serifa nos títulos (SplitText);
  - cards sobem 24 px com ScrollTrigger;
  - Lenis só sem reduced-motion;
  - sorteio dos cartões `[data-sortear]`;
  - tira o `hidden` dos botões do filtro e aplica `data-autores`;
  - laços com `IntersectionObserver` e `visibilitychange`.
- `node bancada/og.mjs --base http://127.0.0.1:8765` cria um PNG 1200×630 por página, com o título e o tipo.

- [ ] **Passo 1:** `test_checagens` passa a exigir `EXCECOES_TEMPORARIAS == ()`. Rodar: FAIL enquanto os CSS antigos existem.
- [ ] **Passo 2:** implementar e arquivar os antigos. Rodar o unittest e o `checar.py`: os dois dão `OK`/rc 0.
- [ ] **Passo 3:** rodar a bancada na prévia. Metas: LCP < 2500, CLS < 0,05, axe sem problemas sérios, sem rolagem
  horizontal e o teste sem JS passando. Se o LCP falhar, a primeira suspeita é a fonte do título.
- [ ] **Passo 4:** gerar as OG; o aviso "OG faltando" some do `gerar.py`.
- [ ] **Passo 5:** commit `alldevs: visual novo (tokens, grade, movimento) e imagens OG`.

### Task 11: hero inspetor

**Arquivos:** criar `js/inspetor.js` (≤ 8 KB sem minificar), `fonte/dados/inspecao/{heisuca,prosup,fakly}.json`,
`assets/inspetor/<slug>.webp` e `fonte/testes/test_inspetor.py`. Alterar `home.html`.

**Interfaces:**
- `inspecao/<slug>.json` = `{"imagem": "assets/inspetor/<slug>.webp", "caixas": [{"x","y","w","h"(%), "tag", "classe", "medida", "codigo"}]}`.
- O molde põe a 1ª tela como `<img loading="lazy" fetchpriority="low">`, sem `<link rel="preload">` (não pode disputar banda com o `<h1>`). O contêiner tem
  `aria-hidden="true"`. O LCP continua sendo o `<h1>`. Os dados vão inline num
  `<script type="application/json" id="inspecao">`.
- `inspetor.js`:
  - rodízio na ordem de `estudio.inspetor`, ~8 s por tela, com o botão "próximo" (fora do `aria-hidden`, com rótulo);
  - percurso das caixas a cada ~1,2 s;
  - etiqueta no formato `tag.classe · LxA` (ex.: `button.cta · 312×48`);
  - com reduced-motion, 2 caixas acesas e paradas;
  - pausa fora da tela e com a aba escondida.

- [ ] **Passo 1: testes.** `test_inspetor_js_ate_8kb` (`os.path.getsize <= 8192`), `test_inspecao_caixas_validas` (x+w ≤ 100,
  y+h ≤ 100, os campos presentes), `test_hero_aria_hidden`, `test_sem_amott` (nenhum arquivo em `inspecao/` nem em
  `assets/inspetor/` com "amott").
- [ ] **Passo 2:** FAIL. **Passo 3:** implementar. As capturas vêm de `prosup.app` e do Heisuca; o Fakly entra quando o
  Rosiel mandar a captura, e até lá o rodízio fica com 2 telas. **Passo 4:** `OK`, e a bancada mantém o LCP < 2500.
- [ ] **Passo 5:** commit `alldevs: hero inspetor`.

### Task 12: paleta de comandos

**Arquivos:** criar `js/paleta.js` e `fonte/testes/test_paleta.py`. Alterar `paginas.py` (gera `assets/paleta.json`) e
`base.html`.

**Interfaces:**
- `assets/paleta.json` (gerado) = lista ordenada de `{"rotulo", "tipo": "projeto|servico|pessoa|contato", "url"}`, só com os
  projetos visíveis.
- Sem JS: `<a class="paleta-gatilho" href="/projetos/">` com o texto `> ir para…`. O JS transforma esse link num botão que
  abre o diálogo:
  - abre com Ctrl K / ⌘K;
  - no celular, mostra a pílula;
  - setas, Enter e Esc funcionam;
  - `role="dialog"`, `aria-modal`, `role="listbox"`/`option`;
  - o foco volta ao gatilho quando fecha.

- [ ] **Passo 1: testes.** `test_paleta_json_sem_vetado`, `test_paleta_tem_os_6_servicos_e_2_pessoas`,
  `test_gatilho_sem_js_e_link_para_projetos`. Completar o `test_vetado_nao_aparece` da Tarefa 7 com o `paleta.json`.
- [ ] **Passo 2:** FAIL. **Passo 3:** implementar. **Passo 4:** `OK`. A bancada ganha o caso "Ctrl K, seta, Enter navega;
  Esc devolve o foco".
- [ ] **Passo 5:** commit `alldevs: paleta de comandos`.

### Task 13: fechamento e PR (sem push)

- [ ] **Passo 1:** rodar tudo: o unittest, `python3 fonte/gerar.py && git diff --exit-code`, `python3 fonte/checar.py` e a
  bancada na prévia. O relatório fica em `bancada/relatorios/<data>/RELATORIO.md`.
- [ ] **Passo 2:** comparar com a Amott: mandar as capturas de 1440 px ao Codex (`codex exec -i … < /dev/null`), perguntando
  "o que lembra a Amott?". Anexar a resposta ao relatório e corrigir o que for apontado.
- [ ] **Passo 3:** escrever `docs/superpowers/PR_REDESENHO.md`: o que muda, as URLs preservadas, como ver a prévia, as
  metas medidas e os itens [C]/[R] em aberto. **Push e PR só com o OK do Rosiel.**
- [ ] **Passo 4:** commit `alldevs: relatório da bancada e texto do PR`.

---

## Dependem de pessoas

- **[C] Caio:** escolher os projetos dele que entram, e se a Amott entra como case. A pergunta vai pelo Telegram só com o OK
  do Rosiel. Até lá, só o Heisuca; o que ele vetar ganha `visivel:false`.
- **[R] Rosiel:**
  1. ligar o Cloudflare Pages no ramo `previa`, com o comando `python3 fonte/gerar.py --previa --saida dist-previa` e a pasta
     `dist-previa`;
  2. mandar as fotos dos dois;
  3. mandar capturas e dados do ProsUp, do Fakly e do SendAny;
  4. dizer se o Ultron tem acesso ao repo;
  5. aprovar os textos de §6;
  6. trocar o e-mail pelo do domínio (basta mudar `estudio.json`).

## O que muda em relação à spec

- Contraste AA: `--rosiel-texto` passa de #c2410c para **#9a3412**, e entram `--suave #9b99a6`, `--caio-texto #a78bfa` e
  `--caio-texto-claro #6d28d9`.
- Campos novos nos dados: `nome` curto nos serviços (para a mensagem do WhatsApp), `atualizado` (para o `lastmod`),
  `inspetor` no `estudio.json` e `rascunho` nos textos provisórios.
- A bancada vem antes do visual (Tarefa 8), para medir a linha de base.
- Exceção temporária da regra de cor para os CSS antigos até a Tarefa 10.
- Workflow de CI novo (`.github/workflows/checar.yml`).
