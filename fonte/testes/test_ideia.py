"""Seção #ideia, "Da ideia ao ar" (Task 5): HTML de _ideia, js/ideia.js, o carregamento de ideia.json e a correção do título no site.js."""
import json
import re
import dataclasses
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


class _Lis(HTMLParser):
    """Extrai cada <li class="ideia-estagio"> inteiro, da abertura ao </li> correspondente (os <li> dos balões aninham)."""
    def __init__(self, html):
        super().__init__()
        self.html, self.achados, self.prof, self.ini, self.chave = html, {}, 0, None, None
        self.ls = [0]
        for linha in html.splitlines(keepends=True):
            self.ls.append(self.ls[-1] + len(linha))
        self.feed(html)

    def _pos(self):
        l, c = self.getpos()
        return self.ls[l - 1] + c

    def handle_starttag(self, tag, attrs):
        if tag != "li":
            return
        a = dict(attrs)
        if self.prof == 0 and "ideia-estagio" in (a.get("class") or "").split():
            self.ini, self.chave = self._pos(), a.get("data-chave")
        if self.ini is not None:
            self.prof += 1

    def handle_endtag(self, tag):
        if tag == "li" and self.ini is not None:
            self.prof -= 1
            if self.prof == 0:
                fim = self.html.index(">", self._pos()) + 1
                self.achados[self.chave] = self.html[self.ini:fim]
                self.ini = self.chave = None


def _estagio(html: str, chave: str) -> str:
    """O <li class="ideia-estagio"> de uma chave, inteiro."""
    return _Lis(html).achados[chave]


def _pin_so_no_ramo_desk(js: str) -> list:
    """Problemas de `pin:` em ideia.js: precisa estar dentro do ramo `ctx.conditions.desk`, antes do `return` do cleanup."""
    ini = js.index("if (ctx.conditions.desk) {")
    i = js.index("{", ini)
    prof, fim = 0, None
    for k in range(i, len(js)):
        prof += (js[k] == "{") - (js[k] == "}")
        if prof == 0:
            fim = k
            break
    ramo = js[i:fim]
    corte = ramo.index("return function")
    erros = []
    for m in re.finditer(r"\bpin\s*:", js):
        if not (i < m.start() < i + corte):
            erros.append(f"pin: fora do ramo desk, antes do cleanup (posição {m.start()})")
    if not re.search(r"\bpin\s*:", js[i:i + corte]):
        erros.append("o ramo desk não tem pin:")
    return erros


ANIMAVEIS = {"opacity", "x", "y", "scaleX", "scaleY", "clipPath", "duration", "ease", "clearProps", "scrollTrigger", "defaults"}


def _chaves_animadas(js: str) -> set:
    """Chaves de 1º nível dos objetos passados a to/fromTo/set/timeline em ideia.js."""
    chaves = set()
    for m in re.finditer(r"\b(?:tl|g|gsap)\.(?:to|fromTo|set|timeline)\(|\bg\.(?:to|fromTo|set|timeline)\(", js):
        i, prof, ini = m.end(), 1, None
        while i < len(js) and prof > 0:
            c = js[i]
            if c in "{[(":
                if c == "{" and prof == 1:
                    ini = i
                prof += 1
            elif c in "}])":
                prof -= 1
                if c == "}" and prof == 1 and ini is not None:
                    chaves |= _chaves_de_nivel1(js[ini:i + 1])
                    ini = None
            i += 1
    return chaves


def _chaves_de_nivel1(obj: str) -> set:
    out, prof = set(), 0
    for m in re.finditer(r"[{}\[\]()]|([A-Za-z_]\w*)\s*:(?!:)", obj):
        t = m.group(0)
        if t in "{[(":
            prof += 1
        elif t in "}])":
            prof -= 1
        elif prof == 1 and m.group(1):
            out.add(m.group(1))
    return out


def _estagios_ocultos(html: str) -> list:
    """Estágios (li, .ideia-texto, .ideia-visual) marcados como ocultos no HTML gerado."""
    achados = []
    for t, a in Tags(html).tags:
        classes = (a.get("class") or "").split()
        if t in ("li", "div") and {"ideia-estagio", "ideia-texto", "ideia-visual"} & set(classes):
            if "hidden" in a or "inert" in a or a.get("aria-hidden") == "true":
                achados.append((t, classes))
    return achados


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

    def test_estagio_extrai_o_li_inteiro(self):
        for i, chave in enumerate(CHAVES):
            li = _estagio(self.html, chave)
            self.assertTrue(li.startswith('<li class="ideia-estagio"'), chave)
            self.assertTrue(li.endswith("</li>"), chave)
            self.assertEqual(li.count('data-chave='), 1, chave)
            for outra in CHAVES:
                if outra != chave:
                    self.assertNotIn(f'data-chave="{outra}"', li)
        self.assertEqual(_estagio(self.html, "conversa").count('class="balao '), 4)
        self.assertIn("</a>", _estagio(self.html, "no-ar"))
        self.assertNotIn("<li", _estagio(self.html, "no-ar").replace('<li class="ideia-estagio" data-chave="no-ar">', "", 1))

    def test_rotulo_reconstrucao_no_chat(self):
        chat = _estagio(self.html, "conversa")
        self.assertRegex(chat, r'<p class="rotulo-mono ideia-reconstrucao">reconstrução</p>')
        self.assertEqual(chat.count("<ul"), 1)
        self.assertEqual(chat.count('class="balao'), len(self.est["conversa"]["mensagens"]))

    def test_sem_telegram_no_chat(self):
        chat = _estagio(self.html, "conversa")
        self.assertNotIn("telegram", self.html.lower())   # a seção inteira, não só o chat
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
        self.assertEqual(_estagios_ocultos(self.html), [])
        # o detector pega um estágio escondido (aria-hidden="true" também esconde de quem usa leitor de tela)
        ruim = self.html.replace('<li class="ideia-estagio" data-chave="codigo"', '<li class="ideia-estagio" aria-hidden="true" data-chave="codigo"', 1)
        self.assertEqual(len(_estagios_ocultos(ruim)), 1)
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


class TestIdeiaValidacao(unittest.TestCase):
    """validar_ideia: ideia.json errado vira ErroDeDados/erro de validação com mensagem clara (nada de KeyError no gerador)."""
    @classmethod
    def setUpClass(cls):
        cls.dados = dados_mod.carregar(REPO)

    def com(self, **mudar):
        ideia = json.loads(json.dumps(self.dados.ideia))
        ideia.update(mudar)
        return dataclasses.replace(self.dados, ideia=ideia)

    def estagios(self):
        return json.loads(json.dumps(self.dados.ideia["estagios"]))

    def erros(self, d, raiz=REPO):
        return dados_mod.validar_ideia(d, raiz)

    def test_dados_reais_validam(self):
        self.assertEqual(self.erros(self.dados), [])
        self.assertEqual(dados_mod.validar(self.dados, REPO)[0], [])

    def test_projeto_inexistente(self):
        e = self.erros(self.com(projeto="nao-existe"))
        self.assertTrue(any("projeto inexistente" in x and "nao-existe" in x for x in e), e)

    def test_projeto_invisivel(self):
        projs = [dataclasses.replace(p, visivel=False) if p.slug == "heisuca" else p for p in self.dados.projetos]
        e = self.erros(dataclasses.replace(self.dados, projetos=projs))
        self.assertTrue(any("não é visível" in x for x in e), e)

    def test_falta_estagio(self):
        est = [x for x in self.estagios() if x["chave"] != "codigo"]
        e = self.erros(self.com(estagios=est))
        self.assertTrue(any("estágios devem ser" in x for x in e), e)

    def test_estagios_fora_de_ordem(self):
        est = self.estagios()
        est[1], est[2] = est[2], est[1]
        e = self.erros(self.com(estagios=est))
        self.assertTrue(any("estágios devem ser" in x for x in e), e)

    def test_mais_de_dois_interlocutores(self):
        est = self.estagios()
        est[0]["mensagens"][1]["de"] = "um-terceiro"
        est[0]["mensagens"].append({"de": "outro", "texto": "oi"})
        e = self.erros(self.com(estagios=est))
        self.assertTrue(any("no máximo 2 interlocutores" in x for x in e), e)

    def test_link_sem_https(self):
        est = self.estagios()
        est[4]["link"] = "http://play.google.com/store/apps/details?id=app.heisuca.player"
        e = self.erros(self.com(estagios=est))
        self.assertTrue(any("https://" in x for x in e), e)

    def test_arquivo_do_codigo_fora_da_pasta(self):
        for fora in ("fonte/dados/estudio.json", "fonte/conteudo/por-tras/../../dados/estudio.json", "/etc/passwd"):
            est = self.estagios()
            est[3]["arquivo"] = fora
            e = self.erros(self.com(estagios=est))
            self.assertTrue(any("fonte/conteudo/por-tras/" in x for x in e), (fora, e))

    def test_trecho_do_codigo_respeita_limites_e_segredos(self):
        with tempfile.TemporaryDirectory() as t:
            raiz = Path(t)
            (raiz / "fonte/conteudo/por-tras").mkdir(parents=True)
            est = self.estagios()
            est[3]["arquivo"] = "fonte/conteudo/por-tras/x.txt"
            d = self.com(estagios=est)
            casos = {
                "linhas": ("a\n" * 30, "linhas"),
                "colunas": ("x" * 90 + "\n", "colunas"),
                "segredo": ("senha = 1\n", "credencial"),
            }
            for nome, (texto, achado) in casos.items():
                (raiz / "fonte/conteudo/por-tras/x.txt").write_text(texto, encoding="utf-8")
                e = self.erros(d, raiz)
                self.assertTrue(any(achado in x for x in e), (nome, e))

    def test_ideia_levanta_erro_de_dados_em_vez_de_keyerror(self):
        est = self.estagios()
        est[4]["link"] = "http://x"
        with self.assertRaises(dados_mod.ErroDeDados) as c:
            paginas._ideia(self.com(estagios=est), REPO)
        self.assertIn("https://", str(c.exception))

    def test_validar_inclui_os_erros_da_ideia(self):
        est = self.estagios()
        est[4]["link"] = "http://x"
        self.assertTrue(any("ideia.json" in x for x in dados_mod.validar(self.com(estagios=est), REPO)[0]))


class TestCodigoEscape(unittest.TestCase):
    def test_cada_caractere_sai_certo(self):
        texto = "a\ue000b # c ' d & e < f > g \" h\n"
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "fonte/conteudo/por-tras").mkdir(parents=True)
            (Path(t) / "fonte/conteudo/por-tras/c.txt").write_text(texto, encoding="utf-8")
            out = paginas._est_codigo(Path(t), {"arquivo": "fonte/conteudo/por-tras/c.txt"})
        m = re.search(r"<code>(.*?)</code>", out, re.S)
        bruto = m.group(1)
        self.assertEqual(html_lib.unescape(bruto), texto)
        self.assertIn("\ue000", bruto)                   # o caractere do uso privado não vira "#"
        self.assertEqual(bruto.count("&#35;"), 1)          # só o "#" do texto
        for ent in ("&#x27;", "&amp;", "&lt;", "&gt;", "&quot;"):
            self.assertIn(ent, bruto)
        self.assertNotRegex(bruto, r"#(?!x?\d+;)")        # nenhum "#" solto (checar.py reprova cor hex)


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
        self.assertEqual(_pin_so_no_ramo_desk(self.js), [])

    def test_pin_no_ramo_movel_reprova(self):
        ruim = self.js.replace("var io = new IntersectionObserver(", "var pin_falso = { pin: true }; var io = new IntersectionObserver(", 1)
        self.assertNotEqual(ruim, self.js)
        self.assertTrue(_pin_so_no_ramo_desk(ruim))
        # e um pin depois do cleanup do ramo desk também reprova
        ruim2 = self.js.replace("   return function () {\n    sec.classList.remove", "   var x = { pin: true };\n   return function () {\n    sec.classList.remove", 1)
        self.assertEqual(_pin_so_no_ramo_desk(ruim2), [])  # antes do return: ainda dentro do ramo
        ruim3 = self.js.replace("sec.classList.remove(\"ideia-pin\");", "sec.classList.remove(\"ideia-pin\"); var y = { pin: true };", 1)
        self.assertTrue(_pin_so_no_ramo_desk(ruim3))

    def test_celular_usa_intersection_observer_e_reduced_motion_fica_estatico(self):
        self.assertIn("IntersectionObserver", self.js)
        self.assertIn("(max-width: 1023px) and (prefers-reduced-motion: no-preference)", self.js)

    def test_so_anima_transform_opacity_e_clip_path(self):
        chaves = _chaves_animadas(self.js)
        self.assertTrue({"opacity", "clipPath", "scaleX", "y"} <= chaves, chaves)
        self.assertEqual(chaves - ANIMAVEIS, set())

    def test_so_anima_pega_propriedade_fora_da_lista(self):
        for extra in ("rotation: 3", "left: 4", "width: 10", "backgroundColor: 1"):
            ruim = self.js.replace("{ opacity: 0, y: 28 }", "{ opacity: 0, y: 28, " + extra + " }", 1)
            self.assertNotEqual(ruim, self.js)
            self.assertNotEqual(_chaves_animadas(ruim) - ANIMAVEIS, set(), extra)

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
