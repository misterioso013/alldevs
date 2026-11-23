import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from alldevs import dados as D
from testes.test_paginas import REPO, rodar, titulo

AUTORES = re.compile(r'data-autores="([^"]*)"')
SUBTITULO = "Um estúdio de software. Sites, apps, bots e produtos próprios no ar."


def ler(arq: Path) -> str:
    return arq.read_text(encoding="utf-8")


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.tmp = Path(tmp.name)
        cls.saida = cls.tmp / "saida"
        rc, _, err = rodar("--raiz", str(REPO), "--saida", str(cls.saida))
        assert rc == 0, err
        cls.dados = D.carregar(REPO)
        cls.visiveis = D.visiveis(cls.dados.projetos)


class TestPaginas(Base):
    def test_titulos_exatos(self):
        esperado = {
            "index.html": "AllDevs — Estúdio de software: sites, apps e automações",
            "caio/index.html": "Caio Guerras — AllDevs",
            "rosiel/index.html": "Rosiel Victor — AllDevs",
            "projetos/index.html": "Projetos — AllDevs",
        }
        for caminho, t in esperado.items():
            self.assertEqual(titulo(self.saida / caminho), t, caminho)

    def test_titulo_do_case(self):
        for p in self.visiveis:
            self.assertEqual(titulo(self.saida / "projetos" / p.slug / "index.html"),
                             f"{p.nome}: {p.tipo} — AllDevs")

    def test_hero_literal_e_botoes(self):
        txt = ler(self.saida / "index.html")
        self.assertIn('Fazemos <span class="titulo-mono">software</span> que vive.', txt)
        self.assertIn(SUBTITULO, txt)
        self.assertRegex(txt, r'<a href="/projetos/"[^>]*>Ver projetos</a>')
        self.assertRegex(txt, r'<a href="#contato"[^>]*>Pedir orçamento</a>')

    def test_sem_formulario_nem_botao_flutuante(self):
        for arq in self.saida.rglob("*.html"):
            txt = ler(arq)
            self.assertNotIn("wa-float", txt, arq)
            self.assertNotIn("<form", txt, arq)

    def test_cabecalho_pedir_orcamento_em_todas(self):
        paginas = list(self.saida.rglob("*.html"))
        self.assertGreaterEqual(len(paginas), 15)
        for arq in paginas:
            txt = ler(arq)
            self.assertIn('class="nav-cta">Pedir orçamento</a>', txt, arq)
            self.assertIn('class="cabecalho"', txt, arq)
            self.assertIn('class="site-footer"', txt, arq)
            self.assertIn('id="contato"', txt, arq)

    def test_rodape_sem_pular_nivel_de_titulo(self):
        for rel in ("index.html", "caio/index.html", "rosiel/index.html", "projetos/index.html",
                    "projetos/prosup/index.html"):
            niveis = [int(n) for n in re.findall(r"<h([1-6])\b", ler(self.saida / rel))]
            self.assertEqual(niveis[0], 1, rel)
            for a, b in zip(niveis, niveis[1:]):
                self.assertLessEqual(b, a + 1, f"{rel}: h{a} -> h{b}")

    def test_sem_texto_de_bastidor(self):
        for arq in self.saida.rglob("*.html"):
            txt = ler(arq).lower()
            for frase in ("aguarda", "bancada", "dados reais", "rascunho"):
                self.assertNotIn(frase, txt, f"{arq}: {frase}")

    def test_sem_ola_rosiel(self):
        for arq in self.saida.rglob("*.html"):
            self.assertIsNone(re.search(r"Ol(?:á|%C3%A1)(?:,|%2C)?(?:[\s+]|%20)+Rosiel", ler(arq), re.I), arq)

    def test_wa_do_case_e_do_perfil(self):
        self.assertIn("%5Bsite%C2%B7case%C2%B7prosup%5D", ler(self.saida / "projetos/prosup/index.html"))
        self.assertIn("%5Bsite%C2%B7perfil%C2%B7caio%5D", ler(self.saida / "caio/index.html"))
        self.assertIn("%5Bsite%C2%B7perfil%C2%B7rosiel%5D", ler(self.saida / "rosiel/index.html"))

    def test_heisuca_sem_vocabulario_do_servidor(self):
        txt = ler(self.saida / "projetos/heisuca/index.html")
        for palavra in ("CGSERVER", "servidor", "Whatbox", "torrent", "tracker", "acervo", "Jellyfin", "Plex"):
            self.assertNotIn(palavra.lower(), txt.lower(), palavra)

    def test_sitemap_tem_perfis_projetos_e_cases(self):
        mapa = ler(self.saida / "sitemap.xml")
        for u in ("/caio/", "/rosiel/", "/projetos/", "/historia.html"):
            self.assertIn(f"<loc>https://all.dev.br{u}</loc>", mapa)

    def test_json_ld_de_perfil_e_case(self):
        def ld(arq):
            m = re.search(r'<script type="application/ld\+json">(.*?)</script>', ler(self.saida / arq), re.S)
            return json.loads(m.group(1))
        self.assertEqual(ld("caio/index.html")[0]["@id"], "https://all.dev.br/#caio-guerras")
        self.assertEqual(ld("rosiel/index.html")[0]["@id"], "https://all.dev.br/#rosiel-victor")
        case = ld("projetos/heisuca/index.html")[0]
        self.assertEqual(case["@type"], "SoftwareApplication")
        self.assertEqual(case["author"], [{"@id": "https://all.dev.br/#caio-guerras"}])


class TestHome(Base):
    def test_cartoes_ordem_alfabetica(self):
        txt = ler(self.saida / "index.html")
        self.assertIn("data-sortear", txt)
        i = [m.group(1) for m in re.finditer(r'class="cartao-pessoa"[^>]*data-slug="([^"]+)"', txt)]
        self.assertEqual(i, sorted(i))
        self.assertEqual(i, ["caio", "rosiel"])

    def test_destaques_sao_os_visiveis_com_destaque(self):
        txt = ler(self.saida / "index.html")
        esperados = [p.slug for p in self.visiveis if p.destaque]
        achados = re.findall(r'class="cartao-destaque"[^>]*data-slug="([^"]+)"', txt)
        self.assertEqual(achados, esperados)

    def test_servicos_na_home(self):
        txt = ler(self.saida / "index.html")
        for s in self.dados.servicos:
            self.assertIn(f'href="/servicos/{s.slug}/"', txt)


class TestPortfolio(Base):
    def test_sem_js_filtro_hidden_e_todos_listados(self):
        txt = ler(self.saida / "projetos/index.html")
        botoes = re.findall(r"<button\b[^>]*data-filtro[^>]*>", txt)
        self.assertEqual(len(botoes), 3)
        for b in botoes:
            self.assertRegex(b, r"\shidden[\s>]")
        self.assertEqual(len(AUTORES.findall(txt)), len(self.visiveis))
        self.assertIn('data-autores="rosiel"', txt)
        self.assertIn('data-autores="caio"', txt)

    def test_resultado_omitido_quando_none(self):
        for p in self.visiveis:
            txt = ler(self.saida / "projetos" / p.slug / "index.html")
            self.assertEqual(p.resultado is None, "Resultado" not in txt, p.slug)

    def test_linha_mono_do_case(self):
        txt = ler(self.saida / "projetos/heisuca/index.html")
        self.assertIn("app · 2026 · Caio Guerras · no ar", txt)


class TestPerfis(Base):
    def test_perfis_mesmo_peso(self):
        def secoes(slug):
            return re.findall(r'<section[^>]*data-secao="([^"]+)"', ler(self.saida / slug / "index.html"))
        self.assertEqual(secoes("caio"), secoes("rosiel"))
        self.assertGreaterEqual(len(secoes("caio")), 3)
        for slug in ("caio", "rosiel"):
            self.assertIn('data-molde="perfil"', ler(self.saida / slug / "index.html"))

    def test_perfil_lista_so_os_projetos_do_autor(self):
        txt = ler(self.saida / "rosiel/index.html")
        self.assertIn("/projetos/prosup/", txt)
        self.assertNotIn("/projetos/heisuca/", txt)


class TestVetado(unittest.TestCase):
    def test_vetado_nao_aparece(self):
        raiz = gerar_copia(self, lambda ps: ps + [
            modelo(ps, slug="visivel-ok", nome="Visivel Ok", rascunho=False),
            modelo(ps, slug="segredo-vetado", nome="Segredo Vetado", visivel=False, destaque=True,
                   rascunho=False, autores=["caio", "rosiel"])])
        # controle positivo: o visível aparece em todos os pontos
        visivel = "visivel-ok"
        for pagina in ("index.html", "projetos/index.html", "caio/index.html", "sitemap.xml"):
            self.assertIn(f"/projetos/{visivel}/", ler(raiz / pagina), pagina)
        self.assertTrue((raiz / "projetos" / visivel / "index.html").is_file())
        # vetado: nem página nem menção
        self.assertFalse((raiz / "projetos" / "segredo-vetado").exists())
        # a paleta de comandos (T12) é gerada dos mesmos dados: o visível entra, o vetado não
        paleta = json.loads(ler(raiz / "assets" / "paleta.json"))
        self.assertIn(f"/projetos/{visivel}/", [i["url"] for i in paleta])
        self.assertEqual([i for i in paleta if "segredo" in json.dumps(i, ensure_ascii=False).lower()], [])
        for arq in raiz.rglob("*"):
            if arq.is_file() and arq.suffix in {".html", ".xml", ".txt", ".json"} and "fonte" not in arq.relative_to(raiz).parts[:1]:
                txt = ler(arq).lower()
                self.assertNotIn("segredo-vetado", txt, arq)
                self.assertNotIn("segredo vetado", txt, arq)


def gerar_copia(testcase, editar):
    """Copia o repo, edita a lista de projetos e gera (produção). Devolve a raiz."""
    tmp = tempfile.TemporaryDirectory()
    testcase.addCleanup(tmp.cleanup)
    raiz = Path(tmp.name) / "raiz"
    shutil.copytree(REPO / "fonte", raiz / "fonte", ignore=shutil.ignore_patterns("__pycache__", "testes"))
    shutil.copytree(REPO / "assets", raiz / "assets")
    arq = raiz / "fonte" / "dados" / "projetos.json"
    projetos = json.loads(arq.read_text(encoding="utf-8"))
    arq.write_text(json.dumps(editar(projetos)), encoding="utf-8")
    rc, _, err = rodar("--raiz", str(raiz))
    testcase.assertEqual(rc, 0, err)
    return raiz


def modelo(projetos, **mudancas):
    base = next(p for p in projetos if p["slug"] == "heisuca")
    return dict(base, **mudancas)


class TestRascunhoNoindex(unittest.TestCase):
    def test_rascunho_noindex_e_fora_do_sitemap_e_publicado_nao(self):
        raiz = gerar_copia(self, lambda ps: ps + [
            modelo(ps, slug="pronto", nome="Pronto", rascunho=False),
            modelo(ps, slug="esboco", nome="Esboco", rascunho=True)])
        mapa = ler(raiz / "sitemap.xml")
        noindex = '<meta name="robots" content="noindex">'
        self.assertIn(noindex, ler(raiz / "projetos/esboco/index.html"))
        self.assertNotIn("/projetos/esboco/", mapa)
        self.assertNotIn(noindex, ler(raiz / "projetos/pronto/index.html"))
        self.assertIn("/projetos/pronto/", mapa)
        self.assertNotIn(noindex, ler(raiz / "index.html"))

    def test_so_o_heisuca_segue_rascunho_com_noindex_fora_do_sitemap(self):
        raiz = gerar_copia(self, lambda ps: ps)
        mapa = ler(raiz / "sitemap.xml")
        self.assertIn('name="robots" content="noindex"', ler(raiz / "projetos" / "heisuca" / "index.html"))
        self.assertNotIn("/projetos/heisuca/", mapa)
        for slug in ("prosup", "fakly", "sendany"):
            self.assertNotIn("noindex", ler(raiz / "projetos" / slug / "index.html"), slug)
            self.assertIn(f"<loc>https://all.dev.br/projetos/{slug}/</loc>", mapa)


class TestAno(unittest.TestCase):
    def test_ano_null_some_da_linha_mono_e_do_json_ld(self):
        raiz = gerar_copia(self, lambda ps: ps + [
            modelo(ps, slug="sem-ano", nome="Sem Ano", ano=None, rascunho=False),
            modelo(ps, slug="com-ano", nome="Com Ano", ano=2031, rascunho=False)])
        txt = ler(raiz / "projetos/sem-ano/index.html")
        self.assertIn("app · Caio Guerras · no ar", txt)
        self.assertNotIn("None", txt)
        self.assertNotIn("· 2026", txt)
        com = ler(raiz / "projetos/com-ano/index.html")
        self.assertIn("app · 2031 · Caio Guerras · no ar", com)
        ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', txt, re.S).group(1)
        self.assertNotRegex(ld, r"\b(19|20)\d\d\b")
        self.assertNotIn("None", ler(raiz / "projetos/index.html"))
        self.assertIn("app · 2031<", ler(raiz / "projetos/index.html"))

    def test_anos_reais_dos_projetos(self):
        dados = D.carregar(REPO)
        por = {p.slug: p for p in dados.projetos}
        self.assertEqual({s: por[s].ano for s in ("prosup", "fakly", "sendany", "heisuca")},
                         {"prosup": 2026, "fakly": 2025, "sendany": 2025, "heisuca": 2026})


class TestControlesPositivos(unittest.TestCase):
    def test_resultado_preenchido_aparece(self):
        raiz = gerar_copia(self, lambda ps: ps + [
            modelo(ps, slug="com-resultado", nome="Com Resultado", resultado="12 lojas atendidas", rascunho=False),
            modelo(ps, slug="sem-resultado", nome="Sem Resultado", resultado=None, rascunho=False)])
        com = ler(raiz / "projetos/com-resultado/index.html")
        self.assertIn("<h2>Resultado</h2>", com)
        self.assertIn("12 lojas atendidas", com)
        self.assertNotIn("Resultado</h2>", ler(raiz / "projetos/sem-resultado/index.html"))

    def test_destaque_false_fora_da_home_mas_no_portfolio(self):
        raiz = gerar_copia(self, lambda ps: ps + [
            modelo(ps, slug="discreto", nome="Discreto", destaque=False, rascunho=False),
            modelo(ps, slug="vitrine", nome="Vitrine", destaque=True, rascunho=False)])
        home = ler(raiz / "index.html")
        self.assertIn('data-slug="vitrine"', home)
        self.assertNotIn("/projetos/discreto/", home)
        port = ler(raiz / "projetos/index.html")
        self.assertIn('data-slug="discreto"', port)
        self.assertIn('data-slug="vitrine"', port)


class TestPerfilConteudo(Base):
    def test_faz_com_tres_itens_nos_dois_perfis(self):
        for slug in ("caio", "rosiel"):
            txt = ler(self.saida / slug / "index.html")
            m = re.search(r'<section[^>]*data-secao="faz".*?</section>', txt, re.S)
            self.assertIsNotNone(m, slug)
            self.assertIn("O que eu faço", m.group(0))
            self.assertEqual(len(re.findall(r"<li>", m.group(0))), 3, slug)

    def test_link_para_historia_so_no_rosiel(self):
        self.assertIn('class="link-seta perfil-historia" href="/historia.html"',
                      ler(self.saida / "rosiel/index.html"))
        self.assertNotIn("perfil-historia", ler(self.saida / "caio/index.html"))

    def test_dados_exigem_exatamente_tres_faz(self):
        from dataclasses import replace
        d = D.carregar(REPO)
        ruim = replace(d, pessoas=(replace(d.pessoas[0], faz=("a", "b")), *d.pessoas[1:]))
        erros = D.validar(ruim, REPO)[0]
        self.assertTrue([e for e in erros if "faz" in e and "3" in e], erros)


class TestServicosSemSeloDePessoa(Base):
    """Decisão 1: serviço é da equipe; selo de pessoa só em projeto, case e hero."""

    def test_quem_toca_continua_nos_dados(self):
        self.assertTrue(all(s.quem_toca for s in self.dados.servicos))

    def test_cartoes_de_servico_da_home_sem_selo_nem_degrade(self):
        txt = ler(self.saida / "index.html")
        cartoes = re.findall(r'<article class="cartao-servico[^"]*".*?</article>', txt, re.S)
        self.assertEqual(len(cartoes), len(self.dados.servicos))
        for c in cartoes:
            self.assertTrue(c.startswith('<article class="cartao-servico">'), c)
            self.assertNotIn("selo", c)
            self.assertNotIn("Caio", c)
            self.assertNotIn("Rosiel", c)

    def test_pagina_de_servico_sem_selo_nem_degrade(self):
        for s in self.dados.servicos:
            txt = ler(self.saida / "servicos" / s.slug / "index.html")
            self.assertNotIn('class="selo', txt, s.slug)
            self.assertNotIn("obra-dupla", txt, s.slug)

    def test_molde_do_servico_nao_tem_mais_o_marcador(self):
        self.assertNotIn("quem_toca", ler(REPO / "fonte" / "modelos" / "servico.html"))

    def test_breadcrumb_segue_irmao_da_primeira_secao(self):
        """`main > .breadcrumb + section { border-top: 0 }` só vale se nada se interpuser."""
        for s in self.dados.servicos:
            txt = ler(self.saida / "servicos" / s.slug / "index.html")
            self.assertRegex(txt, r'class="breadcrumb-current">[^<]+</span>\s*</div>\s*<section class="servico-hero">', s.slug)
        css = ler(REPO / "css" / "site.css")
        self.assertIn("main > .breadcrumb + section { border-top: 0; }", css)

    def test_selo_de_autor_continua_nos_projetos(self):
        txt = ler(self.saida / "index.html")
        destaque = re.search(r'<article class="cartao-destaque[^"]*"[^>]*data-slug="prosup".*?</article>', txt, re.S)
        self.assertIsNotNone(destaque)
        self.assertIn('class="selo selo-rosiel"', destaque.group(0))


class TestTextosNovos(Base):
    def test_subtitulo_do_hero_e_slogan_do_rodape(self):
        for arq in self.saida.rglob("*.html"):
            txt = ler(arq)
            self.assertIn(f"<p>{SUBTITULO}</p>", txt, arq)
            self.assertNotIn("Dois desenvolvedores", txt, arq)
        self.assertIn(f'<p class="hero-sub">{SUBTITULO}</p>', ler(self.saida / "index.html"))

    def test_faq_vocês_podem_fazer(self):
        txt = ler(self.saida / "servicos/automacoes-integracoes-api/index.html")
        self.assertIn("Quais exemplos de automações vocês podem fazer?", txt)
        self.assertNotIn("podemos fazer", txt)

    def test_experiencia_sem_senioridade_e_sem_erro_de_digitacao(self):
        txt = ler(self.saida / "servicos/criacao-de-sites-institucionais/index.html")
        self.assertIn("Somos uma equipe qualificada, com mais de 8 anos de experiência, "
                      "e já entregamos projetos para empresas em múltiplos países.", txt)
        for velho in ("engenheiros de software", "sêniores", "já entrei"):
            self.assertNotIn(velho, txt)

    def test_cta_do_servico_no_imperativo(self):
        txt = ler(self.saida / "servicos/criacao-de-sites-institucionais/index.html")
        self.assertIn("Conte o projeto pelo WhatsApp e receba a proposta em até 24h úteis.", txt)
        self.assertNotIn("Conta o projeto", txt)
        self.assertNotIn("recebo a proposta", txt)

    def test_nenhum_html_gerado_chama_o_estudio_de_senior(self):
        for arq in self.saida.rglob("*.html"):
            txt = ler(arq)
            self.assertNotIn("full stack sênior", txt, arq)
            self.assertNotIn("dois desenvolvedores sêniores", txt.lower(), arq)


class TestDescricoes(Base):
    SITES = ("Site institucional profissional, responsivo e otimizado para o Google. "
             "Entrega em 7 dias, a partir de R$ 800. Feito por uma equipe qualificada.")
    LANDING = ("Landing page profissional focada em conversão, com WhatsApp e formulários. "
               "Entrega em 3 dias, a partir de R$ 600. Ideal para capturar leads e vender mais.")

    def por(self):
        return {s.slug: s.descricao for s in self.dados.servicos}

    def test_todas_entre_140_e_160(self):
        for slug, d in self.por().items():
            self.assertTrue(140 <= len(d) <= 160, f"{slug}: {len(d)}")

    def test_sites_e_landing_ao_pe_da_letra(self):
        d = self.por()
        self.assertEqual(d["criacao-de-sites-institucionais"], self.SITES)
        self.assertEqual(len(self.SITES), 143)
        self.assertEqual(d["landing-page-conversao"], self.LANDING)
        self.assertEqual(len(self.LANDING), 154)

    def test_mvp_so_troca_a_ultima_frase(self):
        d = self.por()["desenvolvimento-mvp-startups"]
        self.assertTrue(d.startswith("Transforme sua ideia em um MVP web funcional com Next.js e backend robusto. "
                                     "Do zero ao ar em semanas. "), d)
        self.assertTrue(d.endswith("Feito por uma equipe full stack para startups."), d)
        self.assertNotIn("sênior", d)

    def test_as_outras_tres_nao_mudam(self):
        d = self.por()
        self.assertEqual(d["bots-whatsapp-automacao"][:40], "Crie um bot para WhatsApp, Discord ou Te")
        for slug in ("aplicativo-mobile-react-native", "automacoes-integracoes-api", "bots-whatsapp-automacao"):
            self.assertNotIn("equipe", d[slug])
            self.assertNotIn("sênior", d[slug])

    def test_validar_sem_aviso_de_tamanho(self):
        self.assertFalse([a for a in D.validar(self.dados, REPO)[1] if "descricao com" in a])

    def test_descricao_vai_para_a_meta(self):
        for s in self.dados.servicos:
            txt = ler(self.saida / "servicos" / s.slug / "index.html")
            self.assertIn(f'<meta name="description" content="{s.descricao.replace("&", "&amp;")}">', txt, s.slug)


class TestRosielReal(Base):
    LINKS = [
        ("GitHub", "https://github.com/misterioso013"),
        ("LinkedIn", "https://www.linkedin.com/in/rosielvictor"),
        ("X", "https://twitter.com/RVictor013"),
        ("Instagram", "https://www.instagram.com/rosielvictor"),
        ("YouTube", "https://www.youtube.com/channel/UCbkvqP3kbIVbFcaKk9fTpFQ"),
        ("Telegram", "https://t.me/misterioso013"),
        ("CV", "https://misterioso013.github.io/my-cv/"),
    ]

    def pessoa(self, slug):
        return next(p for p in self.dados.pessoas if p.slug == slug)

    def test_frase_nova(self):
        r = self.pessoa("rosiel")
        self.assertEqual(r.frase, "Transformo ideia em produto no ar, do protótipo à automação.")
        self.assertIn(r.frase, ler(self.saida / "rosiel/index.html"))
        self.assertNotIn("Sócio do estúdio", ler(self.saida / "rosiel/index.html"))

    def test_sete_links_na_ordem_dada_todos_https(self):
        links = [(l["rotulo"], l["url"]) for l in self.pessoa("rosiel").links]
        self.assertEqual(links, self.LINKS)
        self.assertTrue(all(u.startswith("https://") for _, u in links))

    def test_links_renderizados_na_ordem(self):
        txt = ler(self.saida / "rosiel/index.html")
        ul = re.search(r'<ul class="perfil-links">(.*?)</ul>', txt, re.S).group(1)
        achados = re.findall(r'<a href="([^"]+)" rel="noopener">([^<]+)</a>', ul)
        self.assertEqual([(r, u) for u, r in achados], self.LINKS)

    def test_json_ld_same_as_com_os_sete(self):
        txt = ler(self.saida / "rosiel/index.html")
        ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', txt, re.S).group(1))
        self.assertEqual(ld[0]["sameAs"], [u for _, u in self.LINKS])

    def test_nunca_o_whatsapp_pessoal(self):
        for l in self.pessoa("rosiel").links:
            self.assertNotIn("wa.me", l["url"])
        perfil = ler(self.saida / "rosiel/index.html")
        ul = re.search(r'<ul class="perfil-links">(.*?)</ul>', perfil, re.S).group(1)
        self.assertNotIn("wa.me", ul)

    def test_papel_do_rosiel_e_o_caio_ficam_como_estavam(self):
        r, c = self.pessoa("rosiel"), self.pessoa("caio")
        self.assertEqual((r.papel, r.papel_mono), ("Produto, web e automação", "rosiel · produto, web, automação"))
        self.assertEqual(c.links, ())
        self.assertEqual(c.frase, "Sócio do estúdio. Cuida da infraestrutura, da mídia e dos apps.")


class TestCasesReais(Base):
    def proj(self, slug):
        return next(p for p in self.dados.projetos if p.slug == slug)

    def test_tres_cases_publicados_destacados_e_fora_do_rascunho(self):
        for slug in ("prosup", "fakly", "sendany"):
            p = self.proj(slug)
            self.assertFalse(p.rascunho, slug)
            self.assertTrue(p.destaque, slug)
            self.assertTrue(p.visivel, slug)
            self.assertEqual(p.autores, ("rosiel",), slug)

    def test_heisuca_continua_rascunho_sem_link_nem_imagens(self):
        h = self.proj("heisuca")
        self.assertTrue(h.rascunho)
        self.assertEqual(h.link, "")
        self.assertEqual(h.imagens, ())

    def test_prosup(self):
        p = self.proj("prosup")
        self.assertEqual((p.tipo, p.situacao, p.ano, p.link), ("app", "no ar", 2026, "https://prosup.app"))
        self.assertEqual(p.stack, ("React Native", "TypeScript", "Node.js", "AWS Lambda", "DynamoDB",
                                   "API Gateway", "Cognito", "SNS", "S3", "Secrets Manager"))
        self.assertEqual(len(p.fizemos), 5)
        self.assertIsNone(p.resultado)
        self.assertEqual(p.imagens, tuple(f"assets/images/prosup-{n}.webp" for n in (1, 2, 3, 4)))

    def test_fakly(self):
        p = self.proj("fakly")
        self.assertEqual((p.tipo, p.situacao, p.ano, p.link),
                         ("ferramenta", "no ar", 2025, "https://misterioso013.github.io/fakly/"))
        self.assertEqual(p.stack, ("HTML", "CSS", "JavaScript"))
        self.assertEqual(len(p.fizemos), 4)
        self.assertEqual(p.imagens, ("assets/images/fakly.png",))
        txt = ler(self.saida / "projetos/fakly/index.html")
        self.assertNotIn("React", txt)
        self.assertNotIn("Node.js", txt)

    def test_sendany(self):
        p = self.proj("sendany")
        self.assertEqual((p.tipo, p.situacao, p.ano, p.link), ("produto", "no ar", 2025, "https://sendany.all.dev.br"))
        self.assertEqual(p.stack, ("Next.js", "React", "TypeScript", "PostgreSQL", "Tailwind CSS"))
        self.assertEqual(len(p.fizemos), 4)
        self.assertEqual(p.imagens, ("assets/images/sendany.png",))

    def test_linha_mono_e_botao_de_cada_case(self):
        esperado = {"prosup": ("app · 2026 · Rosiel Victor · no ar", "Ver ProsUp no ar", "https://prosup.app"),
                    "fakly": ("ferramenta · 2025 · Rosiel Victor · no ar", "Ver Fakly no ar",
                              "https://misterioso013.github.io/fakly/"),
                    "sendany": ("produto · 2025 · Rosiel Victor · no ar", "Ver SendAny no ar",
                                "https://sendany.all.dev.br")}
        for slug, (linha, botao, url) in esperado.items():
            txt = ler(self.saida / "projetos" / slug / "index.html")
            self.assertIn(linha, txt, slug)
            self.assertIn(f'<a href="{url}" rel="noopener" class="btn-ghost">{botao}</a>', txt, slug)

    def test_cases_reais_indexaveis_e_heisuca_nao(self):
        mapa = ler(self.saida / "sitemap.xml")
        for slug in ("prosup", "fakly", "sendany"):
            self.assertNotIn("noindex", ler(self.saida / "projetos" / slug / "index.html"), slug)
            self.assertIn(f"<loc>https://all.dev.br/projetos/{slug}/</loc>", mapa)
        self.assertIn('<meta name="robots" content="noindex">', ler(self.saida / "projetos/heisuca/index.html"))
        self.assertNotIn("/projetos/heisuca/", mapa)

    def test_sem_amott_em_lugar_nenhum(self):
        for arq in self.saida.rglob("*"):
            if arq.is_file() and arq.suffix in {".html", ".xml", ".txt", ".json"}:
                self.assertNotIn("amott", ler(arq).lower(), arq)


class TestImagensDosCases(Base):
    TAMANHOS = {
        "assets/images/prosup-1.webp": (720, 1524), "assets/images/prosup-2.webp": (720, 1524),
        "assets/images/prosup-3.webp": (720, 1524), "assets/images/prosup-4.webp": (720, 1524),
        "assets/images/fakly.png": (2549, 921), "assets/images/sendany.png": (1352, 649),
    }

    def imgs(self, slug):
        txt = ler(self.saida / "projetos" / slug / "index.html")
        secao = re.search(r'<section data-secao="imagens">(.*?)</section>', txt, re.S).group(1)
        return re.findall(r"<img [^>]+>", secao)

    def test_leitor_de_png_e_de_webp(self):
        from alldevs import paginas
        for rel, wh in self.TAMANHOS.items():
            self.assertEqual(paginas._tamanho_imagem(REPO / rel), wh, rel)
        self.assertEqual(paginas._tamanho_png(REPO / "assets/images/fakly.png"), (2549, 921))
        self.assertEqual(paginas._tamanho_webp(REPO / "assets/images/prosup-1.webp"), (720, 1524))

    def test_leitor_recusa_arquivo_que_nao_e_png(self):
        from alldevs import paginas
        with tempfile.TemporaryDirectory() as d:
            ruim = Path(d) / "x.png"
            ruim.write_bytes(b"GIF89a" + b"\0" * 40)
            with self.assertRaises(ValueError):
                paginas._tamanho_png(ruim)
            curto = Path(d) / "y.png"
            curto.write_bytes(b"\x89PNG\r\n\x1a\n")
            with self.assertRaises(ValueError):
                paginas._tamanho_png(curto)
            with self.assertRaises(ValueError):
                paginas._tamanho_imagem(Path(d) / "z.gif")

    def test_img_com_width_e_height_reais(self):
        for slug, arquivos in {"prosup": [f"assets/images/prosup-{n}.webp" for n in (1, 2, 3, 4)],
                               "fakly": ["assets/images/fakly.png"],
                               "sendany": ["assets/images/sendany.png"]}.items():
            tags = self.imgs(slug)
            self.assertEqual(len(tags), len(arquivos), slug)
            for tag, rel in zip(tags, arquivos):
                w, h = self.TAMANHOS[rel]
                self.assertIn(f'src="/{rel}"', tag)
                self.assertIn(f'width="{w}" height="{h}"', tag)
                self.assertIn('loading="lazy"', tag)
                self.assertIn("decoding=\"async\"", tag)

    def test_retrato_e_captura_recebem_classes_diferentes(self):
        for tag in self.imgs("prosup"):
            self.assertIn('class="img-retrato"', tag)
        for slug in ("fakly", "sendany"):
            for tag in self.imgs(slug):
                self.assertIn('class="img-captura"', tag)
        for arq in self.saida.rglob("*.html"):
            self.assertNotIn("img-16-10", ler(arq), arq)

    def test_alt_distinto_quando_ha_varias_imagens(self):
        alts = [re.search(r'alt="([^"]+)"', t).group(1) for t in self.imgs("prosup")]
        self.assertEqual(len(set(alts)), 4, alts)
        self.assertTrue(all("ProsUp" in a for a in alts))
        self.assertEqual(re.search(r'alt="([^"]+)"', self.imgs("fakly")[0]).group(1), "Captura de Fakly")

    def test_css_define_as_duas_classes_sem_cortar_a_imagem(self):
        css = ler(REPO / "css" / "site.css")
        for classe in (".img-captura", ".img-retrato"):
            regra = css[css.index(f"{classe} {{"):]
            regra = regra[:regra.index("}")]
            self.assertNotIn("object-fit: cover", regra, classe)
            self.assertNotIn("aspect-ratio", regra, classe)
        self.assertNotIn("img-16-10", css)

    def test_webp_do_prosup_dentro_do_limite_de_largura(self):
        from alldevs import paginas
        for n in (1, 2, 3, 4):
            w, _ = paginas._tamanho_webp(REPO / f"assets/images/prosup-{n}.webp")
            self.assertLessEqual(w, 960)


class TestAvisos(unittest.TestCase):
    def test_rascunho_e_destaques_avisam(self):
        avisos = D.validar(D.carregar(REPO), REPO)[1]
        self.assertIn("projeto heisuca: rascunho (texto aguarda o autor)", avisos)
        for slug in ("prosup", "fakly", "sendany"):
            self.assertFalse([a for a in avisos if a.startswith(f"projeto {slug}:")], slug)
        self.assertFalse([a for a in avisos if a.startswith("destaques:")])
        self.assertFalse([a for a in avisos if "descricao com" in a], avisos)


if __name__ == "__main__":
    unittest.main()
