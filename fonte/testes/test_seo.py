import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from alldevs import dados as mod_dados
from alldevs import paginas, seo
from testes.test_paginas import REPO, Base, rodar


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class TestJsonLd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = mod_dados.carregar(REPO)

    def test_home_org_com_dois_membros(self):
        org = seo.json_ld_home(self.dados)
        self.assertEqual(org["@type"], "Organization")
        self.assertEqual(org["@id"], "https://all.dev.br/#organizacao")
        self.assertEqual(
            sorted(m["@id"] for m in org["member"]),
            ["https://all.dev.br/#caio-guerras", "https://all.dev.br/#rosiel-victor"],
        )

    def test_ids_das_pessoas(self):
        ids = {p.slug: seo.json_ld_pessoa(p)["@id"] for p in self.dados.pessoas}
        self.assertEqual(ids["rosiel"], "https://all.dev.br/#rosiel-victor")
        self.assertEqual(ids["caio"], "https://all.dev.br/#caio-guerras")
        self.assertEqual(seo.json_ld_pessoa(self.dados.pessoas[0])["@type"], "Person")

    def test_servico_provider(self):
        s = self.dados.servicos[0]
        ld = seo.json_ld_servico(s)
        self.assertEqual(ld["@type"], "Service")
        self.assertEqual(ld["provider"], {"@id": "https://all.dev.br/#organizacao"})

    def test_json_ld_escapa_fechamento_de_script(self):
        txt = seo.serializar([{"name": "x</script><b>"}])
        self.assertNotIn("</", txt)
        self.assertIn("<\\/script>", txt)
        self.assertEqual(json.loads(txt)[0]["name"], "x</script><b>")


class TestCaseSemProjetoReal(unittest.TestCase):
    def test_case_site_e_website(self):
        dados = mod_dados.carregar(REPO)
        from dataclasses import replace
        p = mod_dados.Projeto(
            slug="x", nome="X", autores=("caio", "rosiel"), tipo="site", situacao="no ar", ano=2026,
            resumo="r", problema="p", fizemos=(), resultado=None, stack=(), link="https://x.dev",
            imagens=(), destaque=False, visivel=True, atualizado="2026-11-22")
        ld = seo.json_ld_case(p, dados)
        self.assertEqual(ld["@type"], "WebSite")
        self.assertEqual(
            ld["author"],
            [{"@id": "https://all.dev.br/#caio-guerras"}, {"@id": "https://all.dev.br/#rosiel-victor"}])
        self.assertEqual(seo.json_ld_case(replace(p, tipo="bot"), dados)["@type"], "SoftwareApplication")


class TestSitemap(unittest.TestCase):
    def pag(self, caminho, data):
        return paginas.Pagina(caminho, "t", "d", paginas.Seguro(""), data, ())

    def test_sitemap_lastmod_do_campo(self):
        xml = seo.sitemap([self.pag("index.html", "2026-01-02"),
                           self.pag("servicos/a/index.html", "2026-03-04"),
                           self.pag("historia.html", "2026-05-06")])
        self.assertIn("<loc>https://all.dev.br/</loc>\n    <lastmod>2026-01-02</lastmod>", xml)
        self.assertIn("<loc>https://all.dev.br/servicos/a/</loc>\n    <lastmod>2026-03-04</lastmod>", xml)
        self.assertIn("<loc>https://all.dev.br/historia.html</loc>\n    <lastmod>2026-05-06</lastmod>", xml)
        self.assertNotIn("index.html", xml)

    def test_sitemap_omite_pagina_nao_indexavel(self):
        a = self.pag("projetos/a/index.html", "2026-01-01")
        b = paginas.Pagina("projetos/b/index.html", "t", "d", paginas.Seguro(""), "2026-01-01", (), indexar=False)
        xml = seo.sitemap([a, b])
        self.assertIn("/projetos/a/", xml)
        self.assertNotIn("/projetos/b/", xml)

    def test_sitemap_sem_vetado(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = Path(tmp.name)
        shutil.copytree(REPO / "fonte", raiz / "fonte", ignore=shutil.ignore_patterns("__pycache__"))
        for d in ("assets", "css", "js"):
            if (REPO / d).is_dir():
                shutil.copytree(REPO / d, raiz / d)
        shutil.copy2(REPO / "icon.svg", raiz / "icon.svg")
        arq = raiz / "fonte" / "dados" / "projetos.json"
        proj = json.loads(arq.read_text(encoding="utf-8"))
        proj.append({
            "slug": "segredo-vetado", "nome": "Segredo Vetado", "autores": ["caio"], "tipo": "app",
            "situacao": "beta", "ano": 2026, "resumo": "r", "problema": "p", "fizemos": [],
            "resultado": None, "stack": [], "link": "", "imagens": [], "destaque": False,
            "visivel": False, "atualizado": "2026-11-22"})
        arq.write_text(json.dumps(proj), encoding="utf-8")
        saida = raiz / "saida"
        rc, _, err = rodar("--raiz", str(raiz), "--saida", str(saida))
        self.assertEqual(rc, 0, err)
        mapa = (saida / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("https://all.dev.br/historia.html", mapa)
        for f in saida.rglob("*"):
            if f.is_file() and f.suffix in {".html", ".xml", ".txt"}:
                self.assertNotIn("segredo-vetado", f.read_text(encoding="utf-8"), f.name)


class TestPrevia(Base):
    def test_previa_robots_headers_e_meta(self):
        rc, _, err = rodar("--previa", "--raiz", str(REPO), "--saida", str(self.saida))
        self.assertEqual(rc, 0, err)
        self.assertEqual((self.saida / "robots.txt").read_text(encoding="utf-8"), "User-agent: *\nDisallow: /\n")
        self.assertEqual((self.saida / "_headers").read_text(encoding="utf-8"), "/*\n  X-Robots-Tag: noindex\n")
        htmls = list(self.saida.rglob("*.html"))
        self.assertGreaterEqual(len(htmls), 8)
        for h in htmls:
            if h.relative_to(self.saida).parts[0] in paginas.ESTATICOS:
                continue
            self.assertIn('<meta name="robots" content="noindex">', h.read_text(encoding="utf-8"), h.name)

    def test_producao_sem_meta_noindex(self):
        rc, _, err = rodar("--raiz", str(REPO), "--saida", str(self.saida))
        self.assertEqual(rc, 0, err)
        self.assertNotIn("noindex", (self.saida / "index.html").read_text(encoding="utf-8"))
        self.assertFalse((self.saida / "robots.txt").exists())
        self.assertFalse((self.saida / "_headers").exists())

    def test_historia_sem_json_ld_e_home_com_tres(self):
        rodar("--raiz", str(REPO), "--saida", str(self.saida))
        self.assertNotIn("application/ld+json", (self.saida / "historia.html").read_text(encoding="utf-8"))
        home = (self.saida / "index.html").read_text(encoding="utf-8")
        blocos = re.findall(r'<script type="application/ld\+json">(.*?)</script>', home, re.S)
        self.assertEqual(len(blocos), 1)
        self.assertEqual(len(json.loads(blocos[0])), 3)

    def test_determinismo(self):
        rodar("--raiz", str(REPO), "--saida", str(self.saida))
        a = {f.relative_to(self.saida): sha(f) for f in self.saida.rglob("*") if f.is_file()}
        rodar("--raiz", str(REPO), "--saida", str(self.saida))
        b = {f.relative_to(self.saida): sha(f) for f in self.saida.rglob("*") if f.is_file()}
        self.assertEqual(a, b)


class TestProducaoNaoTocaRobots(unittest.TestCase):
    INTOCADOS = ("robots.txt", "CNAME", "app-ads.txt", ".github/FUNDING.yml")

    def test_producao_nao_toca_robots(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = Path(tmp.name)
        shutil.copytree(REPO / "fonte", raiz / "fonte", ignore=shutil.ignore_patterns("__pycache__"))
        for d in paginas.ESTATICOS:
            origem = REPO / d
            if origem.is_dir():
                shutil.copytree(origem, raiz / d)
            elif origem.is_file():
                shutil.copy2(origem, raiz / d)
        for n in self.INTOCADOS:
            self.assertTrue((REPO / n).is_file(), f"{n} ausente no repo")
            (raiz / n).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / n, raiz / n)
        antes = {n: sha(raiz / n) for n in self.INTOCADOS}
        rc, _, err = rodar("--raiz", str(raiz))
        self.assertEqual(rc, 0, err)
        for n, h in antes.items():
            self.assertEqual(sha(raiz / n), h, n)
        self.assertFalse((raiz / "_headers").exists())


if __name__ == "__main__":
    unittest.main()
