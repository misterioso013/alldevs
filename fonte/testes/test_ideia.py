"""Seção #ideia, "Da ideia ao ar" (Task 5): HTML de _ideia, js/ideia.js, o carregamento de ideia.json e a correção do título no site.js."""
import json
import re
import html as html_lib
import shutil
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from alldevs import dados as dados_mod
from alldevs import paginas

REPO = Path(__file__).resolve().parent.parent.parent
IDEIA_JS = REPO / "js" / "ideia.js"
SITE_JS = REPO / "js" / "site.js"
CHAVES = ["conversa", "encontro", "prototipo", "codigo", "no-ar"]
PROIBIDAS = ("CGSERVER", "servidor", "Whatbox", "torrent", "tracker", "acervo", "Jellyfin", "Plex", "nuvem", "Emby")


def _secao() -> str:
    return str(paginas._ideia(dados_mod.carregar(REPO), REPO))


def _estagio(html: str, chave: str) -> str:
    """O <li> de um estágio, do início até o próximo estágio (ou o fim da lista)."""
    i = html.index(f'data-chave="{chave}"')
    prox = html.find('class="ideia-estagio"', i)
    return html[i:prox if prox > 0 else len(html)]


class Tags(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class TestIdeiaHtml(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = dados_mod.carregar(REPO)
        cls.html = _secao()
        cls.tags = Tags(cls.html).tags
        cls.est = {e["chave"]: e for e in cls.dados.ideia["estagios"]}

    def achar(self, tag, **attrs):
        return [a for t, a in self.tags if t == tag and all(a.get(k) == v for k, v in attrs.items())]

    def test_dados_carrega_ideia_json(self):
        self.assertEqual(self.dados.ideia["projeto"], "heisuca")
        self.assertEqual([e["chave"] for e in self.dados.ideia["estagios"]], CHAVES)

    def test_cinco_estagios_na_ordem(self):
        self.assertTrue(self.html.lstrip().startswith('<section id="ideia"'))
        self.assertEqual(len(self.achar("ol", **{"class": "ideia-estagios"})), 1)
        lis = self.achar("li", **{"class": "ideia-estagio"})
        self.assertEqual([a["data-chave"] for a in lis], CHAVES)
        # a lista é filha direta da seção: nenhum invólucro entre as duas
        self.assertRegex(self.html, r'</header>\s*<ol class="ideia-estagios"')

    def test_rotulo_reconstrucao_no_chat(self):
        chat = _estagio(self.html, "conversa")
        self.assertRegex(chat, r'<p class="rotulo-mono ideia-reconstrucao">reconstrução</p>')
        self.assertEqual(chat.count("<ul"), 1)
        self.assertEqual(chat.count('class="balao'), len(self.est["conversa"]["mensagens"]))

    def test_sem_telegram_no_chat(self):
        chat = _estagio(self.html, "conversa")
        self.assertNotIn("telegram", chat.lower())
        self.assertNotIn("<svg", chat)
        self.assertNotIn("<img", chat)

    def test_chat_nao_amarra_socio_a_cor(self):
        # a cor é do lado do balão (1º e 2º a falar), nunca do nome; a classe e os atributos não citam sócio algum
        chat = _estagio(self.html, "conversa")
        marcas = re.findall(r'<[a-z]+[^>]*>', chat)
        for m in marcas:
            self.assertNotRegex(m.lower(), r"caio|rosiel")
        lados = re.findall(r'class="balao balao-(\w)"', chat)
        self.assertEqual(lados, ["a", "b", "a", "b"])
        # as falas aparecem inteiras e escapadas
        for m in self.est["conversa"]["mensagens"]:
            self.assertIn(paginas.esc(m["texto"]), chat)

    def test_encontro_e_rabisco_svg_inline(self):
        enc = _estagio(self.html, "encontro")
        self.assertEqual(enc.count("<svg"), 1)
        self.assertRegex(enc, r'<svg[^>]*aria-hidden="true"')
        self.assertIn(paginas.esc(self.est["encontro"]["texto"]), enc)
        self.assertNotIn("<img", enc)
        self.assertNotIn("href=", enc)

    def test_prototipo_wireframe_com_fonte_em_mono(self):
        proto = _estagio(self.html, "prototipo")
        self.assertRegex(proto, r'<div class="ideia-wire"[^>]*aria-hidden="true"')
        self.assertNotIn("<img", proto)
        self.assertRegex(proto, r'<p class="ideia-fonte">' + re.escape(paginas.esc(self.est["prototipo"]["fonte"])) + "</p>")

    def test_codigo_vem_do_arquivo_escapado_em_pre_code(self):
        cod = _estagio(self.html, "codigo")
        m = re.search(r'<pre class="ideia-codigo"[^>]*><code>(.*?)</code></pre>', cod, re.S)
        self.assertIsNotNone(m)
        texto = (REPO / self.est["codigo"]["arquivo"]).read_text(encoding="utf-8")
        self.assertNotRegex(m.group(1), r"#(?!x?\d+;)")   # "#" solto vira entidade (checar.py reprova cor hex)
        self.assertEqual(html_lib.unescape(m.group(1)), texto)
        self.assertNotIn("hidden", cod)  # o texto inteiro está no DOM e visível sem JS

    def test_codigo_escapa_marcacao_do_arquivo(self):
        with tempfile.TemporaryDirectory() as t:
            raiz = Path(t)
            (raiz / "fonte/conteudo/por-tras").mkdir(parents=True)
            frente = next(p for p in self.dados.projetos if p.slug == "heisuca").por_tras["frente"]
            (raiz / frente).parent.mkdir(parents=True)
            shutil.copy(REPO / frente, raiz / frente)
            (raiz / self.est["codigo"]["arquivo"]).write_text('x </code></pre><script>alert(1)</script> #fff', encoding="utf-8")
            html = str(paginas._ideia(self.dados, raiz))
        self.assertNotIn("<script>alert", html)
        self.assertNotIn("#fff", html)
        self.assertIn("&lt;/code&gt;&lt;/pre&gt;&lt;script&gt;", html)

    def test_no_ar_tem_link_e_resultado_dos_dados(self):
        no_ar = _estagio(self.html, "no-ar")
        e = self.est["no-ar"]
        self.assertIn(paginas.esc(e["resultado"]), no_ar)
        a = re.search(r'<a [^>]*href="' + re.escape(paginas.esc(e["link"])) + r'"[^>]*>', no_ar).group(0)
        self.assertIn('target="_blank"', a)
        self.assertIn('rel="noopener"', a)

    def test_no_ar_imagem_da_frente_sem_cls_e_sem_prioridade(self):
        img = re.search(r"<img [^>]+>", _estagio(self.html, "no-ar")).group(0)
        proj = next(p for p in self.dados.projetos if p.slug == "heisuca")
        w, h = paginas._tamanho_webp(REPO / proj.por_tras["frente"])
        self.assertIn(f'src="/{proj.por_tras["frente"]}"', img)
        self.assertIn(f'width="{w}" height="{h}"', img)
        self.assertIn('loading="lazy"', img)
        self.assertNotIn("fetchpriority", self.html)

    def test_conteudo_legivel_sem_js(self):
        for _, attrs in self.tags:
            self.assertNotIn("hidden", attrs)
            self.assertNotIn("inert", attrs)
        self.assertNotIn(" style=", self.html)
        # cada estágio mostra o título e o texto dos dados
        for chave in CHAVES:
            li = _estagio(self.html, chave)
            self.assertIn(paginas.esc(self.est[chave]["titulo"]), li)
            self.assertIn(paginas.esc(self.est[chave]["texto"]), li)

    def test_titulo_da_secao_usa_revela_do_site_js(self):
        self.assertRegex(self.html, r'<h2 class="titulo-revela"')
        self.assertIn("data-revela", self.html)

    def test_script_da_secao_defer_e_unico(self):
        self.assertEqual(re.findall(r'<script src="([^"]+)" defer></script>', self.html), ["/js/ideia.js"])

    def test_vocabulario_do_servidor_fora_da_secao(self):
        baixo = self.html.lower()
        for palavra in PROIBIDAS:
            self.assertNotIn(palavra.lower(), baixo, palavra)

    def test_so_um_estudio_sem_nome_de_socio_fora_do_chat(self):
        fora = self.html.replace(_estagio(self.html, "conversa"), "")
        self.assertNotRegex(fora.lower(), r"caio|rosiel")


class TestIdeiaNaHome(unittest.TestCase):
    def test_secao_logo_abaixo_do_hero(self):
        doc = str(paginas._home(dados_mod.carregar(REPO), REPO, False).corpo)
        self.assertEqual(doc.count('id="ideia"'), 1)
        self.assertLess(doc.index('id="hero"'), doc.index('id="ideia"'))
        self.assertLess(doc.index('id="ideia"'), doc.index('id="quem-somos"'))


class TestIdeiaJs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = IDEIA_JS.read_text("utf-8")

    def test_ideia_js_sem_listener_de_scroll(self):
        self.assertNotRegex(self.js, r"""addEventListener\(\s*["']scroll""")
        self.assertNotRegex(self.js, r"\bonscroll\b")
        self.assertNotRegex(self.js, r"""addEventListener\(\s*["'](wheel|touchmove)""")

    def test_pin_so_desktop(self):
        self.assertIn("gsap.matchMedia", self.js)
        self.assertIn("(min-width: 1024px) and (prefers-reduced-motion: no-preference)", self.js)
        # todo "pin:" mora dentro do bloco da consulta de desktop
        corpo = self.js[self.js.index("(min-width: 1024px) and (prefers-reduced-motion: no-preference)"):]
        for m in re.finditer(r"\bpin\s*:", self.js):
            self.assertGreaterEqual(m.start(), len(self.js) - len(corpo))

    def test_celular_usa_intersection_observer_e_reduced_motion_fica_estatico(self):
        self.assertIn("IntersectionObserver", self.js)
        self.assertIn("(max-width: 1023px) and (prefers-reduced-motion: no-preference)", self.js)

    def test_so_anima_transform_opacity_e_clip_path(self):
        for prop in ("top", "left", "width", "height", "margin", "background", "color"):
            self.assertNotRegex(self.js, r"(?<![-\w])" + prop + r"\s*:\s*[\d\"']", prop)

    def test_codigo_digita_por_clip_path_sem_reescrever_texto(self):
        self.assertIn("clipPath", self.js)
        self.assertNotRegex(self.js, r"textContent\s*=|innerHTML\s*=|innerText\s*=")


class TestSiteJsTituloSobPreloader(unittest.TestCase):
    def test_titulo_fora_da_tela_sob_o_preloader_esconde(self):
        js = SITE_JS.read_text("utf-8")
        self.assertRegex(js, r"var esconder = !naTela\(titulo\) \|\| coberto > 0;")
        self.assertNotRegex(js, r"coberto >= 0 \? naTela\(titulo\) && coberto > 0")


if __name__ == "__main__":
    unittest.main()
