"""Hero "por trás do produto" (Task 4): HTML de _hero, js/revelar.js e a regra de CSS do botão."""
import dataclasses
import json
import re
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from alldevs import dados as dados_mod
from alldevs import paginas

REPO = Path(__file__).resolve().parent.parent.parent
REVELAR = REPO / "js" / "revelar.js"
CSS = REPO / "css" / "site.css"


def _hero_real() -> str:
    dados = dados_mod.carregar(REPO)
    return str(paginas._hero(dados, REPO))


def _com_trecho(trecho: str) -> str:
    """_hero com o trecho da 1ª obra do ciclo trocado por `trecho` (num repositório temporário)."""
    tmp = tempfile.TemporaryDirectory()
    try:
        raiz = Path(tmp.name)
        dados = dados_mod.carregar(REPO)
        primeiro = dados.estudio.ciclo[0]
        proj = next(p for p in dados.projetos if p.slug == primeiro)
        arq = raiz / proj.por_tras["arquivo"]
        arq.parent.mkdir(parents=True)
        arq.write_text(trecho, encoding="utf-8")
        frente = raiz / proj.por_tras["frente"]
        frente.parent.mkdir(parents=True)
        shutil.copy(REPO / proj.por_tras["frente"], frente)
        for p in dados.projetos:  # as demais obras do ciclo ficam como estão
            if p.slug in dados.estudio.ciclo and p.slug != primeiro:
                for rel in (p.por_tras["arquivo"], p.por_tras["frente"]):
                    (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(REPO / rel, raiz / rel)
        return str(paginas._hero(dados, raiz))
    finally:
        tmp.cleanup()


class Tags(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []  # (tag, dict de atributos) na ordem do documento
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class TestHero(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = _hero_real()
        cls.tags = Tags(cls.html).tags

    def achar(self, tag, **attrs):
        return [a for t, a in self.tags if t == tag and all(a.get(k) == v for k, v in attrs.items())]

    def test_h1_fixo_e_antes_do_palco(self):
        self.assertEqual(self.html.count("<h1"), 1)
        self.assertLess(self.html.index("<h1"), self.html.index('class="hero-palco"'))
        self.assertTrue(self.html.lstrip().startswith('<section id="hero"'))
        self.assertIn('class="hero-texto"', self.html)

    def test_frente_img_lcp(self):
        frente = self.html[self.html.index('<figure class="hero-frente"'):]
        img = re.search(r"<img [^>]+>", frente).group(0)
        self.assertIn('fetchpriority="high"', img)
        self.assertNotIn("lazy", img)
        w, h = (int(x) for x in re.search(r'width="(\d+)" height="(\d+)"', img).groups())
        self.assertEqual((w, h), paginas._tamanho_webp(REPO / "assets/frente/amott.webp"))
        pre = re.findall(r'<link rel="preload" as="image"[^>]*>', self.html)
        self.assertEqual(len(pre), 1)
        self.assertIn("/assets/frente/amott.webp", pre[0])

    def test_camadas_decorativas_aria_hidden(self):
        self.assertEqual(len(self.achar("div", **{"class": "hero-por-tras", "aria-hidden": "true"})), 1)
        self.assertEqual(len(self.achar("canvas", **{"class": "hero-mascara", "aria-hidden": "true"})), 1)
        botao = self.achar("button", **{"class": "hero-ver-por-tras"})
        self.assertEqual(len(botao), 1)
        self.assertIn("hidden", botao[0])
        self.assertIn("Ver por trás", self.html)
        self.assertEqual(self.achar("p", **{"class": "hero-frase"})[0].get("aria-live"), "off")

    def test_por_tras_hidden_sem_js(self):
        self.assertRegex(self.html, r"<pre hidden>\s*<code>")

    def test_ciclo_json_valido_e_do_estudio(self):
        m = re.search(r'<script id="ciclo" type="application/json">(.*?)</script>', self.html, re.S)
        itens = json.loads(m.group(1))
        self.assertEqual([i["slug"] for i in itens], list(dados_mod.carregar(REPO).estudio.ciclo))
        for i in itens:
            self.assertEqual(set(i), {"slug", "nome", "frase", "cor", "frente", "por_tras"})
            self.assertEqual(set(i["frente"]), {"src", "w", "h"})
            self.assertIn(i["por_tras"]["tipo"], ("codigo", "wireframe"))
            self.assertTrue(i["por_tras"]["origem"])
        self.assertIn('data-ciclo', self.html)

    def test_ciclo_json_escapa_fechamento_de_script(self):
        html = _com_trecho("a </script><script>alert(1)</script> b <!-- c")
        m = re.search(r'<script id="ciclo" type="application/json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(m)
        corpo = m.group(1)
        self.assertNotIn("</script", corpo.lower())
        self.assertNotIn("<!--", corpo)
        self.assertEqual(html.lower().count("<script"), 2)  # o ciclo e o revelar.js: nenhum aberto pelo trecho
        itens = json.loads(corpo)  # e o JSON continua lendo o trecho original
        self.assertIn("</script>", itens[0]["por_tras"]["texto"])

    def test_codigo_escapado_no_pre(self):
        html = _com_trecho("if (a < b && c > d) { x = \"<img onerror=1>\"; }")
        pre = re.search(r"<pre hidden>\s*<code>(.*?)</code>", html, re.S).group(1)
        self.assertNotIn("<img", pre)
        self.assertIn("&lt;img onerror=1&gt;", pre)
        self.assertIn("a &lt; b &amp;&amp; c &gt; d", pre)

    def test_sem_vocabulario_do_servidor_na_cor_de_socio(self):
        # a cor do projeto nunca vira rótulo de sócio
        self.assertNotRegex(self.html.lower(), r"caio|rosiel")


class TestRevelarJs(unittest.TestCase):
    def setUp(self):
        self.js = REVELAR.read_text(encoding="utf-8")

    def test_revelar_js_ate_12kb_e_sem_dependencia(self):
        self.assertLessEqual(REVELAR.stat().st_size, 12 * 1024)
        self.assertNotRegex(self.js, r"^\s*import\s", )
        self.assertNotIn("gsap", self.js.lower())
        self.assertNotRegex(self.js, r"\bimport\s*\(")
        self.assertIn("window.AllDevsRevelar", self.js)
        self.assertIn("montarHero", self.js)
        self.assertIn("montarCartao", self.js)

    def test_revelar_sem_preventDefault_no_touchmove(self):
        self.assertNotIn("preventDefault", self.js)
        self.assertNotIn("touchmove", self.js)

    def test_revelar_pausa(self):
        self.assertIn("IntersectionObserver", self.js)
        self.assertIn("visibilitychange", self.js)
        self.assertIn("cancelAnimationFrame", self.js)

    def test_revelar_nao_ouve_scroll(self):
        self.assertNotRegex(self.js, r"addEventListener\(\s*[\"']scroll")

    def test_revelar_sem_cor_solta(self):
        self.assertNotRegex(self.js, r"#[0-9a-fA-F]{3,8}\b")
        self.assertNotRegex(self.js, r"\brgba?\(")


class TestCss(unittest.TestCase):
    def regra(self, seletor):
        css = CSS.read_text(encoding="utf-8")
        i = css.index(seletor + " {")
        return css[i:css.index("}", i)]

    def test_botao_ver_por_tras_44px(self):
        m = re.search(r"min-height:\s*(\d+)px", self.regra(".hero-ver-por-tras"))
        self.assertIsNotNone(m)
        self.assertGreaterEqual(int(m.group(1)), 44)

    def test_img_da_frente_nao_vira_lcp_com_js(self):
        css = CSS.read_text(encoding="utf-8")
        i = css.index("@media (scripting: enabled)")
        bloco = css[i:css.index("}", css.index("}", i) + 1) + 1]
        self.assertIn("prefers-reduced-motion: no-preference", bloco)
        self.assertIn(".hero-palco .hero-frente img", bloco)
        self.assertIn("opacity: 0", bloco)
        self.assertIn("hero-img-volta", bloco)
        self.assertIn("@keyframes hero-img-volta", css)

    def test_palco_toque_pan_y(self):
        self.assertIn("touch-action: pan-y", self.regra(".hero-palco"))

    def test_hero_antigo_saiu(self):
        css = CSS.read_text(encoding="utf-8")
        self.assertEqual(css.count("/* ---------- Hero"), 1)  # o bloco antigo foi trocado, não duplicado
        self.assertNotRegex(css, r"\.hero \{[^}]*grid-template-columns: minmax\(0, 7fr\)")


if __name__ == "__main__":
    unittest.main()
