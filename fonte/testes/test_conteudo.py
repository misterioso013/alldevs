import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from alldevs import dados as D
from testes.test_paginas import REPO, rodar, titulo

AUTORES = re.compile(r'data-autores="([^"]*)"')


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
        self.assertIn("Dois desenvolvedores, um estúdio. Sites, apps, bots e produtos próprios no ar.", txt)
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

    def test_rascunhos_reais_noindex_fora_do_sitemap(self):
        raiz = gerar_copia(self, lambda ps: ps)
        mapa = ler(raiz / "sitemap.xml")
        for slug in ("prosup", "fakly", "sendany", "heisuca"):
            self.assertIn('name="robots" content="noindex"', ler(raiz / "projetos" / slug / "index.html"))
            self.assertNotIn(f"/projetos/{slug}/", mapa)


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

    def test_proprios_sem_ano(self):
        dados = D.carregar(REPO)
        por = {p.slug: p for p in dados.projetos}
        for s in ("prosup", "fakly", "sendany"):
            self.assertIsNone(por[s].ano)
        self.assertEqual(por["heisuca"].ano, 2026)


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


class TestAvisos(unittest.TestCase):
    def test_rascunho_e_destaques_avisam(self):
        avisos = D.validar(D.carregar(REPO), REPO)[1]
        for slug in ("prosup", "fakly", "sendany", "heisuca"):
            self.assertIn(f"projeto {slug}: rascunho (texto aguarda o autor)", avisos)
        self.assertFalse([a for a in avisos if a.startswith("destaques:")])


if __name__ == "__main__":
    unittest.main()
