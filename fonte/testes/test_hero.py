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

    def test_img_da_frente_so_com_prioridade_alta_e_preload_fora_do_hero(self):
        # o preload mora no <head> da pagina (_documento), nao dentro da secao do hero
        self.assertNotIn("<link", self.html)

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


class TestPaginaHome(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dados = dados_mod.carregar(REPO)
        cls.doc = str(paginas._home(dados, REPO, False).corpo)
        cls.head = cls.doc[:cls.doc.index("</head>")]

    def test_preload_da_frente_no_head(self):
        pre = re.findall(r'<link rel="preload" as="image"[^>]*>', self.head)
        self.assertEqual(len(pre), 1)
        self.assertIn('href="/assets/frente/amott.webp"', pre[0])
        self.assertEqual(self.doc.count('rel="preload" as="image"'), 1)

    def test_uma_so_img_com_prioridade_alta_e_e_a_da_frente(self):
        imgs = [t for t in re.findall(r"<img [^>]*>", self.doc) if 'fetchpriority="high"' in t]
        self.assertEqual(len(imgs), 1, imgs)
        self.assertIn("amott.webp", imgs[0])
        self.assertLess(self.doc.index('<figure class="hero-frente"'), self.doc.index(imgs[0]))
        self.assertNotIn("caio-640", imgs[0])
        fig = self.doc[self.doc.index('<figure class="hero-frente"'):]
        self.assertTrue(fig.startswith('<figure class="hero-frente"'))
        self.assertIn(imgs[0], fig[:fig.index("</figure>")])


class TestRevelarJs(unittest.TestCase):
    def setUp(self):
        self.js = REVELAR.read_text(encoding="utf-8")

    def test_revelar_js_ate_14kb_e_sem_dependencia(self):
        self.assertLessEqual(REVELAR.stat().st_size, 14 * 1024)  # rodada 1: +2 KB pelos itens 6, 7, 9, 10 e 11
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

    def test_revelar_rect_em_cache_sem_listener_de_scroll(self):
        # visibilidade e por IntersectionObserver; o rect do palco e medido em resize/ResizeObserver e o scroll entra por scrollY
        self.assertNotRegex(self.js, r"addEventListener\(\s*[\"']scroll")
        self.assertEqual(self.js.count("getBoundingClientRect"), 2)  # medida() do hero e o cartao
        self.assertIn("window.scrollY", self.js)
        self.assertRegex(self.js, r"ResizeObserver")

    def test_revelar_sem_cor_solta(self):
        self.assertNotRegex(self.js, r"#[0-9a-fA-F]{3,8}\b")
        self.assertNotRegex(self.js, r"\brgba?\(")


def _regras(css: str):
    """(seletores, declaracoes) de cada regra folha do CSS, sem comentarios e sem depender de ordem nem de espacos."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sels = [re.sub(r"\s+", " ", x).strip() for x in m.group(1).split(",")]
        decl = {}
        for d in m.group(2).split(";"):
            if ":" in d:
                k, v = d.split(":", 1)
                decl[k.strip()] = re.sub(r"\s+", " ", v).strip()
        yield sels, decl


class TestCss(unittest.TestCase):
    def setUp(self):
        self.css = CSS.read_text(encoding="utf-8")
        self.regras = list(_regras(self.css))

    def regra(self, seletor):
        """Declaracoes mescladas de todas as regras cujo seletor e exatamente `seletor` (a ultima vence)."""
        out = {}
        for sels, decl in self.regras:
            if seletor in sels:
                out.update(decl)
        self.assertTrue(out, f"nenhuma regra com o seletor {seletor}")
        return out

    def test_regra_acha_pelo_seletor_exato(self):
        # .hero-por-tras pre nao pode ser confundido com .hero-por-tras nem com .hero-por-tras img
        self.assertIn("white-space", self.regra(".hero-por-tras pre"))
        self.assertNotIn("white-space", self.regra(".hero-por-tras"))
        self.assertEqual(list(_regras("a , b{ x : 1 ;y:2}"))[0], (["a", "b"], {"x": "1", "y": "2"}))

    def test_botao_ver_por_tras_44px(self):
        m = re.fullmatch(r"(\d+)px", self.regra(".hero-ver-por-tras")["min-height"])
        self.assertIsNotNone(m)
        self.assertGreaterEqual(int(m.group(1)), 44)

    def test_img_da_frente_nunca_comeca_invisivel(self):
        # a img e o candidato a LCP: nenhuma regra a esconde, salvo as que dependem de .vivo (o canvas ja pintou)
        for sels, decl in self.regras:
            if decl.get("opacity") == "0":
                for s in sels:
                    if "hero-frente img" in s or s.endswith(".hero-frente > img"):
                        self.assertIn(".vivo", s, f"{s} esconde a img da frente sem depender de .vivo")
        self.assertNotIn("hero-img-volta", self.css)
        self.assertNotIn("scripting", self.css)

    def test_so_o_canvas_vivo_esconde_a_img(self):
        self.assertEqual(self.regra(".hero-palco.vivo .hero-frente img").get("opacity"), "0")

    def test_palco_toque_pan_y(self):
        self.assertEqual(self.regra(".hero-palco")["touch-action"], "pan-y")

    def test_h1_do_hero_nao_parte_palavra(self):
        r = self.regra(".hero-headline")
        self.assertEqual(r.get("overflow-wrap"), "normal")
        self.assertEqual(r.get("word-break"), "normal")
        self.assertEqual(r.get("hyphens"), "manual")

    def test_trecho_com_contraste_de_texto(self):
        self.assertEqual(self.regra(".hero-por-tras pre")["color"], "var(--texto)")

    def test_trecho_oculto_vence_o_display_do_css(self):
        self.assertEqual(self.regra(".hero-por-tras [hidden]").get("display"), "none")

    def test_frase_na_mesma_transicao_da_troca(self):
        self.assertTrue(any(".hero-palco.trocando .hero-frase" in sels and d.get("opacity") == "0" for sels, d in self.regras))
        self.assertIn("opacity", self.regra(".hero-frase").get("transition", ""))

    def test_hero_antigo_saiu(self):
        self.assertEqual(self.css.count("/* ---------- Hero"), 1)  # o bloco antigo foi trocado, não duplicado
        self.assertNotRegex(self.css, r"\.hero \{[^}]*grid-template-columns: minmax\(0, 7fr\)")


if __name__ == "__main__":
    unittest.main()
