import dataclasses
import hashlib
import json
import re
import shutil
import subprocess
import struct
import tempfile
import unittest
from pathlib import Path

from alldevs import dados as D
from testes.test_paginas import REPO, rodar, titulo

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

    PROIBIDAS = ("CGSERVER", "servidor", "Whatbox", "torrent", "tracker", "acervo", "Jellyfin", "Plex",
                 "nuvem", "Emby")

    def test_cgflix_lite_e_heisuca_sem_vocabulario_do_servidor(self):
        projs = json.loads(ler(REPO / "fonte/dados/projetos.json"))
        ideia = ler(REPO / "fonte/conteudo/ideia.json")
        for slug in ("heisuca", "cgflix-lite"):
            p = next(x for x in projs if x["slug"] == slug)
            textos = {
                "pagina": ler(self.saida / "projetos" / slug / "index.html"),
                "projetos.json": json.dumps(p, ensure_ascii=False),  # inclui por_tras.frase e origem
                "ideia.json": ideia,
            }
            for arq in REPO.glob(f"fonte/conteudo/por-tras/{slug}.txt"):
                textos[arq.name] = ler(arq)
            for onde, txt in textos.items():
                for palavra in self.PROIBIDAS:
                    self.assertNotIn(palavra.lower(), txt.lower(), f"{slug} {onde}: {palavra}")

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
        self.assertEqual(case["creator"], {"@id": "https://all.dev.br/#organizacao"})
        self.assertNotIn("author", case)


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
    def test_projetos_sem_filtro_por_pessoa(self):
        txt = ler(self.saida / "projetos/index.html")
        self.assertNotIn('data-filtro="caio"', txt)
        self.assertNotIn('data-filtro="rosiel"', txt)
        achados = re.findall(r'class="cartao-projeto"[^>]*data-slug="([^"]+)"', txt)
        self.assertEqual(achados, [p.slug for p in self.visiveis])

    def test_resultado_omitido_quando_none(self):
        for p in self.visiveis:
            txt = ler(self.saida / "projetos" / p.slug / "index.html")
            self.assertEqual(p.resultado is None, "Resultado" not in txt, p.slug)

    def test_linha_mono_do_case(self):
        txt = ler(self.saida / "projetos/heisuca/index.html")
        self.assertIn("app · 2026 · no ar", txt)


class TestPerfis(Base):
    def test_perfis_mesmo_peso(self):
        def secoes(slug):
            return re.findall(r'<section[^>]*data-secao="([^"]+)"', ler(self.saida / slug / "index.html"))
        self.assertEqual(secoes("caio"), secoes("rosiel"))
        self.assertGreaterEqual(len(secoes("caio")), 3)
        for slug in ("caio", "rosiel"):
            self.assertIn('data-molde="perfil"', ler(self.saida / slug / "index.html"))

    def test_perfil_lista_todos_os_projetos_sob_fizemos_juntos(self):
        links = {}
        for slug in ("caio", "rosiel"):
            txt = ler(self.saida / slug / "index.html")
            secao = re.search(r'<section class="perfil-projetos".*?</section>', txt, re.S).group(0)
            self.assertRegex(secao, r"<h2>[^<]*Fizemos juntos[^<]*</h2>")
            links[slug] = set(re.findall(r'href="(/projetos/[^/"]+/)"', secao))
        self.assertEqual(links["caio"], links["rosiel"])
        self.assertEqual(links["caio"], {f"/projetos/{p.slug}/" for p in self.visiveis})

    def test_perfil_sem_kicker_por_socio(self):
        for slug in ("caio", "rosiel"):
            nome = next(p.nome for p in self.dados.pessoas if p.slug == slug)
            txt = ler(self.saida / slug / "index.html")
            self.assertNotRegex(txt, rf"(?i)projetos de\s+{re.escape(nome)}")
            self.assertNotRegex(txt, rf"(?i)projetos de\s+{re.escape(nome.split()[0])}")

    def test_nenhuma_pagina_tem_selo_de_autor(self):
        for arq in self.saida.rglob("*.html"):
            txt = ler(arq)
            for marca in ("selo-caio", "selo-rosiel", "data-autor"):
                self.assertNotIn(marca, txt, f"{marca} em {arq}")


class TestVetado(unittest.TestCase):
    def test_vetado_nao_aparece(self):
        raiz = gerar_copia(self, lambda ps: ps + [
            modelo(ps, slug="visivel-ok", nome="Visivel Ok", rascunho=False),
            modelo(ps, slug="segredo-vetado", nome="Segredo Vetado", visivel=False, destaque=True,
                   rascunho=False)])
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

    def test_nenhum_projeto_segue_rascunho_e_todos_entram_no_sitemap(self):
        raiz = gerar_copia(self, lambda ps: ps)
        mapa = ler(raiz / "sitemap.xml")
        for slug in ("prosup", "fakly", "sendany", "heisuca", "cgflix-lite", "amott"):
            self.assertNotIn("noindex", ler(raiz / "projetos" / slug / "index.html"), slug)
            self.assertIn(f"<loc>https://all.dev.br/projetos/{slug}/</loc>", mapa)


class TestAno(unittest.TestCase):
    def test_ano_null_some_da_linha_mono_e_do_json_ld(self):
        raiz = gerar_copia(self, lambda ps: ps + [
            modelo(ps, slug="sem-ano", nome="Sem Ano", ano=None, rascunho=False),
            modelo(ps, slug="com-ano", nome="Com Ano", ano=2031, rascunho=False)])
        txt = ler(raiz / "projetos/sem-ano/index.html")
        self.assertIn("app · no ar", txt)
        self.assertNotIn("None", txt)
        self.assertNotIn("· 2026", txt)
        com = ler(raiz / "projetos/com-ano/index.html")
        self.assertIn("app · 2031 · no ar", com)
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

    def test_servico_tem_tipo_e_nao_quem_toca(self):
        mapa = {"criacao-de-sites-institucionais": "site", "landing-page-conversao": "site",
                "aplicativo-mobile-react-native": "app", "bots-whatsapp-automacao": "automacao",
                "automacoes-integracoes-api": "automacao", "desenvolvimento-mvp-startups": "produto"}
        self.assertEqual({s.slug: s.tipo for s in self.dados.servicos}, mapa)

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

    def test_heisuca_publicado_com_a_loja(self):
        h = self.proj("heisuca")
        self.assertFalse(h.rascunho)
        self.assertEqual(h.loja, "https://play.google.com/store/apps/details?id=app.heisuca.player")

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
                         ("produto", "no ar", 2025, "https://misterioso013.github.io/fakly/"))
        self.assertEqual(p.stack, ("HTML", "CSS", "JavaScript"))
        self.assertEqual(len(p.fizemos), 4)
        self.assertEqual(p.imagens, ("assets/images/fakly.webp",))
        txt = ler(self.saida / "projetos/fakly/index.html")
        self.assertNotIn("React", txt)
        self.assertNotIn("Node.js", txt)

    def test_sendany(self):
        p = self.proj("sendany")
        self.assertEqual((p.tipo, p.situacao, p.ano, p.link), ("produto", "no ar", 2025, "https://sendany.all.dev.br"))
        self.assertEqual(p.stack, ("Next.js", "React", "TypeScript", "PostgreSQL", "Tailwind CSS"))
        self.assertEqual(len(p.fizemos), 4)
        self.assertEqual(p.imagens, ("assets/images/sendany.webp",))

    def test_linha_mono_e_botao_de_cada_case(self):
        esperado = {"prosup": ("app · 2026 · no ar", "Ver ProsUp no ar", "https://prosup.app"),
                    "fakly": ("produto · 2025 · no ar", "Ver Fakly no ar",
                              "https://misterioso013.github.io/fakly/"),
                    "sendany": ("produto · 2025 · no ar", "Ver SendAny no ar",
                                "https://sendany.all.dev.br")}
        for slug, (linha, botao, url) in esperado.items():
            txt = ler(self.saida / "projetos" / slug / "index.html")
            self.assertIn(linha, txt, slug)
            self.assertIn(f'<a href="{url}" rel="noopener" class="btn-ghost">{botao}</a>', txt, slug)

    def test_cases_reais_indexaveis(self):
        mapa = ler(self.saida / "sitemap.xml")
        for slug in ("prosup", "fakly", "sendany", "heisuca", "cgflix-lite", "amott"):
            self.assertNotIn("noindex", ler(self.saida / "projetos" / slug / "index.html"), slug)
            self.assertIn(f"<loc>https://all.dev.br/projetos/{slug}/</loc>", mapa)

    @unittest.skipUnless(any(p["slug"] == "amott" for p in json.loads(
        (REPO / "fonte" / "dados" / "projetos.json").read_text(encoding="utf-8"))), "o case amott chega na Task 2")
    def test_amott_so_como_case(self):
        permitidos = {"index.html", "projetos/index.html", "assets/paleta.json", "sitemap.xml",
                      "caio/index.html", "rosiel/index.html"}  # perfis listam todos os projetos; Task 8 soma serviços
        for arq in self.saida.rglob("*"):
            rel = arq.relative_to(self.saida).as_posix()
            if arq.is_file() and arq.suffix in {".html", ".xml", ".txt", ".json"} and "amott" in ler(arq).lower():
                self.assertTrue(rel in permitidos or rel.startswith("projetos/amott/"), rel)


class TestImagensDosCases(Base):
    TAMANHOS = {
        "assets/images/prosup-1.webp": (720, 1524), "assets/images/prosup-2.webp": (720, 1524),
        "assets/images/prosup-3.webp": (720, 1524), "assets/images/prosup-4.webp": (720, 1524),
        "assets/images/fakly.webp": (960, 347), "assets/images/sendany.webp": (960, 461),
    }

    def imgs(self, slug):
        txt = ler(self.saida / "projetos" / slug / "index.html")
        secao = re.search(r'<section data-secao="imagens">(.*?)</section>', txt, re.S).group(1)
        return re.findall(r"<img [^>]+>", secao)

    def test_leitor_de_png_e_de_webp(self):
        from alldevs import paginas
        for rel, wh in self.TAMANHOS.items():
            self.assertEqual(paginas._tamanho_imagem(REPO / rel), wh, rel)
        with tempfile.TemporaryDirectory() as d:
            png = Path(d) / "x.png"
            png.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 2549, 921) + b"\0" * 5)
            self.assertEqual(paginas._tamanho_png(png), (2549, 921))
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
                               "fakly": ["assets/images/fakly.webp"],
                               "sendany": ["assets/images/sendany.webp"]}.items():
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


class TestRodada1(Base):
    """Correções da revisão da 13A: crases, link de afiliado, alvo de 44 px e h2 do serviço de sites."""

    # sha256 da prosup-3.webp que mostrava o link de afiliado legível (não pode voltar).
    SHA_PROSUP3_LEGIVEL = "f4c64751f8d3a0f858e68798ca5cc69ef6d3d2e5aeee78a5943b9a775830d7e4"
    # Região do "https://meli.la/..." na captura 720x1524 (x0, y0, x1, y1).
    CAIXA_LINK = (258, 1406, 568, 1452)

    def textos(self, p):
        for campo in dataclasses.fields(p):
            v = getattr(p, campo.name)
            if isinstance(v, str):
                yield campo.name, v
            elif isinstance(v, tuple):
                for i, item in enumerate(v):
                    if isinstance(item, str):
                        yield f"{campo.name}[{i}]", item

    def test_dados_dos_projetos_sem_crase_de_markdown(self):
        for p in self.dados.projetos:
            for nome, txt in self.textos(p):
                self.assertNotIn("`", txt, f"{p.slug}.{nome}")

    def test_paginas_de_case_sem_crase(self):
        arquivos = [self.saida / "projetos" / "index.html"] + sorted((self.saida / "projetos").glob("*/index.html"))
        self.assertGreaterEqual(len(arquivos), 5)
        for arq in arquivos:
            self.assertNotIn("`", ler(arq), arq)

    def test_prosup_3_nao_e_mais_a_captura_com_o_link_legivel(self):
        arq = REPO / "assets/images/prosup-3.webp"
        self.assertNotEqual(hashlib.sha256(arq.read_bytes()).hexdigest(), self.SHA_PROSUP3_LEGIVEL)
        from alldevs import paginas
        self.assertEqual(paginas._tamanho_webp(arq), (720, 1524))

    @unittest.skipUnless(shutil.which("dwebp"), "dwebp ausente")
    def test_link_de_afiliado_ilegivel_na_prosup_3(self):
        def energia(arq):
            ppm = subprocess.run(["dwebp", "-quiet", "-ppm", "-o", "-", str(arq)],
                                 capture_output=True, check=True).stdout
            m = re.match(rb"P6\s+(\d+)\s+(\d+)\s+255\s", ppm)
            w, h = int(m.group(1)), int(m.group(2))
            dados = ppm[m.end():]
            x0, y0, x1, y1 = self.CAIXA_LINK
            tot = n = 0
            for y in range(y0, y1):
                for x in range(x0, x1 - 1):
                    a = dados[(y * w + x) * 3 + 1]
                    b = dados[(y * w + x + 1) * 3 + 1]
                    tot += abs(a - b)
                    n += 1
            return tot / n
        # texto nítido dá ~11; região borrada fica perto de 0
        self.assertLess(energia(REPO / "assets/images/prosup-3.webp"), 3.0)
        # controle: o mesmo cálculo numa captura com texto nítido na mesma altura é alto
        self.assertGreater(energia(REPO / "assets/images/prosup-1.webp"), 0.0)

    def test_links_do_perfil_tem_alvo_de_44px(self):
        css = ler(REPO / "css" / "site.css")
        i = css.index(".perfil-links a {")
        regra = css[i:css.index("}", i)]
        self.assertIn("display: inline-flex", regra)
        self.assertIn("align-items: center", regra)
        self.assertIn("min-height: 44px", regra)
        for token in re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", regra):
            self.fail(f"cor fora dos tokens: {token}")

    def test_h2_do_servico_de_sites_fala_em_equipe(self):
        fonte = ler(REPO / "fonte/conteudo/servicos/criacao-de-sites-institucionais.html")
        txt = ler(self.saida / "servicos/criacao-de-sites-institucionais/index.html")
        for t in (fonte, txt):
            self.assertIn("<h2>Por que contratar uma equipe especializada?</h2>", t)
            self.assertNotIn("desenvolvedor freelancer", t)
        for arq in self.saida.rglob("*.html"):
            self.assertNotIn("freelancer", ler(arq).lower(), arq)


class TestAvisos(unittest.TestCase):
    def test_rascunho_e_destaques_avisam(self):
        avisos = D.validar(D.carregar(REPO), REPO)[1]
        self.assertFalse([a for a in avisos if "rascunho" in a], avisos)
        for slug in ("prosup", "fakly", "sendany", "heisuca", "cgflix-lite", "amott"):
            self.assertFalse([a for a in avisos if a.startswith(f"projeto {slug}:")], slug)
        self.assertFalse([a for a in avisos if a.startswith("destaques:")])
        self.assertFalse([a for a in avisos if "descricao com" in a], avisos)


class TestConteudoV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = D.carregar(REPO)
        cls.por_slug = {p.slug: p for p in cls.dados.projetos}
        cls.ideia = json.loads(ler(REPO / "fonte/conteudo/ideia.json"))

    def test_ciclo_tem_ao_menos_3_com_por_tras(self):
        ciclo = self.dados.estudio.ciclo
        self.assertGreaterEqual(len(ciclo), 3)
        for s in ciclo:
            self.assertTrue(self.por_slug[s].por_tras, s)

    def test_ciclo_so_publicados(self):
        for s in self.dados.estudio.ciclo:
            p = self.por_slug[s]
            self.assertTrue(p.visivel, s)
            self.assertFalse(p.rascunho, s)

    def test_cada_captura_existe_e_cabe_no_limite(self):
        from alldevs import paginas
        achou = 0
        for pasta, limite in (("frente", 960), ("por-tras", 960), ("loja", 540)):
            for arq in sorted((REPO / "assets" / pasta).glob("*.webp")):
                achou += 1
                self.assertLessEqual(paginas._tamanho_webp(arq)[0], limite, arq)
        self.assertGreaterEqual(achou, 11)
        for p in self.por_slug.values():
            if p.por_tras:
                self.assertTrue((REPO / p.por_tras["frente"]).is_file(), p.slug)
        for slug in ("heisuca", "cgflix-lite"):
            for n in (1, 2, 3):
                self.assertTrue((REPO / f"assets/loja/{slug}-{n}.webp").is_file(), (slug, n))

    def test_ideia_tem_os_5_estagios_na_ordem(self):
        self.assertEqual([e["chave"] for e in self.ideia["estagios"]],
                         ["conversa", "encontro", "prototipo", "codigo", "no-ar"])
        self.assertIn(self.ideia["projeto"], self.por_slug)
        for e in self.ideia["estagios"]:
            self.assertTrue(e["titulo"].strip() and e["texto"].strip(), e["chave"])
        cod = next(e for e in self.ideia["estagios"] if e["chave"] == "codigo")
        self.assertTrue(cod["arquivo"].startswith("fonte/conteudo/por-tras/") and (REPO / cod["arquivo"]).is_file())
        no_ar = next(e for e in self.ideia["estagios"] if e["chave"] == "no-ar")
        self.assertTrue(no_ar["link"].startswith("https://") and no_ar["resultado"].strip())
        self.assertEqual(no_ar["link"], self.por_slug[self.ideia["projeto"]].loja)
        enc = next(e for e in self.ideia["estagios"] if e["chave"] == "encontro")
        self.assertIn("nos víamos e pensávamos", enc["texto"].lower())

    def test_conversa_marcada_como_reconstrucao(self):
        conv = self.ideia["estagios"][0]
        self.assertIs(conv["reconstrucao"], True)
        self.assertGreaterEqual(len(conv["mensagens"]), 2)
        self.assertEqual({m["de"] for m in conv["mensagens"]}, {"caio", "rosiel"})
        for m in conv["mensagens"]:
            self.assertLessEqual(len(m["texto"]), 120)
            self.assertNotIn("telegram", m["texto"].lower())
        for campo in ("titulo", "texto"):
            self.assertNotIn("telegram", conv[campo].lower())

    def test_trechos_por_tras_cabem_em_24x72(self):
        arqs = sorted((REPO / "fonte/conteudo/por-tras").glob("*.txt"))
        self.assertGreaterEqual(len(arqs), 5)
        for arq in arqs:
            linhas = ler(arq).splitlines()
            self.assertLessEqual(len(linhas), 24, arq.name)
            for n, l in enumerate(linhas, 1):
                self.assertLessEqual(len(l), 72, f"{arq.name}:{n}")

    def test_imagens_e_frentes_dos_visiveis_sao_webp_no_limite(self):
        from alldevs import paginas
        for p in self.por_slug.values():
            if not p.visivel:
                continue
            itens = [(i, 960) for i in p.imagens]
            if p.por_tras:
                itens.append((p.por_tras["frente"], 960))
            for rel, limite in itens:
                self.assertTrue(rel.endswith(".webp"), f"{p.slug}: {rel}")
                lim = 540 if rel.startswith("assets/loja/") else limite
                self.assertLessEqual(paginas._tamanho_webp(REPO / rel)[0], lim, f"{p.slug}: {rel}")

    def test_og_existe_para_todo_projeto_publicado(self):
        for p in self.por_slug.values():
            if p.visivel and not p.rascunho:
                self.assertTrue((REPO / "assets/og" / f"{p.slug}.png").is_file(), p.slug)

    def test_amott_link_amott_docaio(self):
        self.assertEqual(self.por_slug["amott"].link, "https://amott.docaio.com.br")


if __name__ == "__main__":
    unittest.main()
