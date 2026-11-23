import hashlib
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOKENS = REPO / "css" / "tokens.css"
VENDOR = REPO / "js" / "vendor"
FONTES = REPO / "assets" / "fontes"


def _variaveis() -> dict:
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", TOKENS.read_text("utf-8")))


def _luminancia(hexa: str) -> float:
    h = hexa.strip().lstrip("#")
    canais = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        canais.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def contraste(a: str, b: str) -> float:
    la, lb = sorted((_luminancia(a), _luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


SYNE_SHA256 = {
    "syne-latin-600-normal.woff2": "f1dc13cad7ce032771fc930cca6f5693074faf907cd67e051b74f508b7721265",
    "syne-latin-700-normal.woff2": "0aad69416fc0ccf6f340647c46e759d5c6e4628d92576b279ec5ada0afbd9d35",
    "syne-latin-800-normal.woff2": "1a340e84b78c7e1e7ed24306d682fdcd6dc8cc6cb52b158fbaf22c03f7f001c3",
}


# Pares (texto, fundo) realmente usados em css/site.css.
PARES_TEXTO = [
    ("--texto", "--fundo"), ("--texto", "--fundo-2"),
    ("--texto-2", "--fundo"), ("--texto-2", "--fundo-2"),
    ("--roxo-claro", "--fundo"), ("--roxo-claro", "--fundo-2"),      # a:hover
    ("--laranja", "--fundo"), ("--laranja", "--fundo-2"),            # logo, em, datas
    ("--laranja-claro", "--fundo"), ("--laranja-claro", "--fundo-2"),  # rótulo-mono, links
    ("--texto", "--roxo"),                                           # .btn-cheio e .nav-cta:hover
    ("--fundo", "--roxo-claro"),                                     # .btn-cheio:hover
    ("--fundo", "--laranja"), ("--fundo", "--laranja-claro"),        # texto do cursor sobre o laranja
]


def _ler_sem_binarios(pastas):
    for pasta in pastas:
        for p in Path(pasta).rglob("*"):
            if p.is_file() and p.suffix in (".css", ".html", ".js", ".txt", ".py", ".json", ".md"):
                yield p


def _corpo_da_funcao(js: str, nome: str) -> str:
    m = re.search(r"function\s+" + nome + r"\s*\([^)]*\)\s*\{", js)
    assert m, nome
    i, n = m.end(), 1
    while n and i < len(js):
        n += {"{": 1, "}": -1}.get(js[i], 0)
        i += 1
    return js[m.end():i - 1]


class TestTokens(unittest.TestCase):
    def test_tokens_cores_do_7acc4d2(self):
        v = _variaveis()
        for nome, valor in [("--fundo", "#0a0a0f"), ("--roxo", "#7c3aed"), ("--roxo-claro", "#9d6bf0"),
                            ("--laranja", "#f97316"), ("--laranja-claro", "#fb923c"), ("--texto", "#eeeef5")]:
            self.assertEqual(v[nome].strip().lower(), valor, nome)

    def test_nomes_e_movimento(self):
        v = _variaveis()
        for nome in ("--fundo-2", "--texto-2", "--linha", "--curva-saida", "--curva-entrada",
                     "--fonte-titulo", "--fonte-texto", "--fonte-mono"):
            self.assertIn(nome, v)
        for nome, valor in [("--dur-curta", "200ms"), ("--dur-media", "400ms"), ("--dur-longa", "800ms")]:
            self.assertEqual(v[nome].strip(), valor, nome)

    def test_roxo_e_laranja_sao_do_estudio(self):
        # Cor de marca do estúdio: nenhum token ou classe liga uma cor a um sócio.
        for p in _ler_sem_binarios([REPO / "css"]):
            txt = p.read_text("utf-8")
            self.assertNotRegex(txt, r"--(caio|rosiel)\b", p)
            self.assertNotRegex(txt, r"\.(selo|inspetor)-(caio|rosiel)", p)

    def test_grao_com_opacidade_baixa(self):
        css = TOKENS.read_text("utf-8")
        self.assertIn("--grao:", css)
        self.assertIn("svg+xml", css)
        self.assertIn("feTurbulence", css)
        m = re.search(r"--grao-opacidade:\s*([\d.]+);", css)
        self.assertTrue(m)
        self.assertLessEqual(float(m.group(1)), 0.06)

    def test_contraste_aa(self):
        v = _variaveis()
        self.assertGreaterEqual(contraste(v["--texto"], v["--fundo"]), 7)
        self.assertGreaterEqual(contraste(v["--texto-2"], v["--fundo"]), 4.5)
        self.assertGreaterEqual(contraste(v["--texto-2"], v["--fundo-2"]), 4.5)
        # Todo par texto/fundo que o site.css usa de fato (4,5:1; os de texto grande ou negrito grande teriam 3:1).
        for texto, fundo in PARES_TEXTO:
            with self.subTest(texto=texto, fundo=fundo):
                self.assertGreaterEqual(contraste(v[texto], v[fundo]), 4.5)

    def test_pares_de_texto_cobrem_o_site_css(self):
        # Toda cor de texto de marca usada em site.css precisa estar na tabela de pares, senão o teste de contraste
        # não a enxerga. Hoje: roxo-claro, laranja e laranja-claro como cor de texto.
        css = (REPO / "css" / "site.css").read_text("utf-8")
        usadas = set(re.findall(r"(?<![-\w])color:\s*var\((--(?:roxo-claro|laranja-claro|laranja|roxo))\)", css))
        cobertas = {t for t, _ in PARES_TEXTO}
        self.assertEqual(usadas - cobertas, set())
        for token in ("--roxo-claro", "--laranja", "--laranja-claro"):
            for fundo in ("--fundo", "--fundo-2"):
                self.assertIn((token, fundo), PARES_TEXTO)

    def test_sem_fraunces(self):
        for p in _ler_sem_binarios([REPO / "css", REPO / "fonte" / "modelos", FONTES]):
            self.assertNotIn("fraunces", p.read_text("utf-8").lower(), p)
        self.assertEqual([p.name for p in FONTES.glob("*") if "fraunces" in p.name.lower()], [])

    def test_syne_com_sha_e_ofl(self):
        for nome, sha in SYNE_SHA256.items():
            with self.subTest(arquivo=nome):
                self.assertEqual(hashlib.sha256((FONTES / nome).read_bytes()).hexdigest(), sha)
        licenca = (FONTES / "OFL.txt").read_text("utf-8")
        self.assertIn("Syne", licenca)
        self.assertIn("SIL OPEN FONT LICENSE", licenca)
        v = _variaveis()
        self.assertTrue(v["--fonte-titulo"].startswith('"Syne", "Syne Reserva"'))

    def test_site_js_sem_listener_de_scroll(self):
        for p in (REPO / "js").glob("*.js"):
            txt = p.read_text("utf-8")
            self.assertNotRegex(txt, r"""addEventListener\(\s*['"]scroll['"]""", p)

    def test_lenis_condicionado(self):
        js = (REPO / "js" / "site.js").read_text("utf-8")
        # O único "new ... Lenis" do arquivo mora dentro de ligarLenis().
        self.assertEqual(len(re.findall(r"new\s+(?:window\.)?Lenis\b", js)), 1)
        corpo = _corpo_da_funcao(js, "ligarLenis")
        self.assertRegex(corpo, r"new\s+(?:window\.)?Lenis\b")
        # ligarLenis() só é chamada dentro de um único if com as três condições.
        chamadas = re.findall(r"ligarLenis\s*\(", js)
        self.assertEqual(len(chamadas), 2)  # a declaração e uma chamada
        m = re.search(r"if\s*\(([^;{}]*)\)\s*\{?\s*ligarLenis\s*\(\s*\)", js)
        self.assertTrue(m, "a chamada de ligarLenis() não está sob um if")
        cond = m.group(1)
        self.assertIn("(pointer: fine)", cond)
        self.assertIn("(min-width: 1024px)", cond)
        self.assertIn("reduz", cond)
        self.assertRegex(js, r"var reduz = mq\(\"\(prefers-reduced-motion: reduce\)\"\)")

    def test_vendor_sha256(self):
        versoes = json.loads((VENDOR / "VERSOES.json").read_text("utf-8"))
        for arq, info in versoes.items():
            with self.subTest(arquivo=arq):
                self.assertEqual(hashlib.sha256((VENDOR / arq).read_bytes()).hexdigest(), info["sha256"])
                self.assertTrue(info["pacote"] and info["versao"])
        no_disco = {p.name for p in VENDOR.glob("*") if p.is_file()} - {"VERSOES.json", "LICENCAS.md"}
        self.assertEqual(no_disco, set(versoes))

    def test_reservas_com_metrica_nas_pilhas(self):
        css = TOKENS.read_text("utf-8")
        for familia, local in (("DM Sans Reserva", "Arial"), ("Syne Reserva", "Arial")):
            blocos = [b for b in re.findall(r"@font-face\s*\{[^}]*\}", css) if f'"{familia}"' in b]
            self.assertTrue(blocos, familia)
            for b in blocos:
                self.assertIn(f'local("{local}', b)
                self.assertNotIn("url(", b)
                for prop in ("size-adjust", "ascent-override", "descent-override"):
                    self.assertRegex(b, prop + r":\s*[\d.]+%;")
        v = _variaveis()
        self.assertTrue(v["--fonte-texto"].startswith('"DM Sans", "DM Sans Reserva"'))

    def test_syne_reserva_uma_por_peso(self):
        css = TOKENS.read_text("utf-8")
        blocos = re.findall(r"@font-face\s*\{[^}]*\}", css)
        pesos = lambda fam: sorted(re.findall(r"font-weight:\s*(\d{3})\s*;", b)[0] for b in blocos if f'"{fam}"' in b)
        self.assertEqual(pesos("Syne Reserva"), pesos("Syne"))
        self.assertEqual(pesos("Syne Reserva"), ["600", "700", "800"])
        ajustes = [re.search(r"size-adjust:\s*([\d.]+)%", b).group(1) for b in blocos if '"Syne Reserva"' in b]
        self.assertEqual(len(set(ajustes)), 3, "cada peso tem a sua métrica")

    def test_fontes_com_licenca(self):
        css = TOKENS.read_text("utf-8")
        blocos = re.findall(r"@font-face\s*\{[^}]*\}", css)
        urls = [u for b in blocos for u in re.findall(r"url\(\s*[\"']?([^\"')]+)[\"']?\s*\)", b)]
        self.assertEqual(len(urls), 7)  # DM Sans 3, JetBrains Mono 1, Syne 3
        for u in urls:
            self.assertTrue((TOKENS.parent / u).resolve().is_file(), u)
        referenciados = {(TOKENS.parent / u).resolve().name for u in urls}
        em_disco = {p.name for p in FONTES.glob("*.woff2")}
        self.assertEqual(em_disco, referenciados)
        for b in blocos:
            if "url(" in b:
                self.assertRegex(b, r"font-weight:\s*\d{3};")
        self.assertIn("font-display: swap", css)
        licenca = (FONTES / "OFL.txt").read_text("utf-8")
        for familia in ("Syne", "DM Sans", "JetBrains Mono"):
            self.assertIn(familia, licenca)

    # ---------- Preloader (R2, G1, G6) ----------
    def test_preloader_decidido_por_script_inline_no_head(self):
        html = (REPO / "index.html").read_text("utf-8")
        head = html[:html.index("</head>")]
        m = re.search(r"<script>(?P<js>[^<]*)</script>", head)
        self.assertTrue(m, "falta o script inline do preloader no <head>")
        js = m.group("js")
        for trecho in ("sessionStorage", "prefers-reduced-motion", "pre-1a", "try", "catch"):
            self.assertIn(trecho, js)
        primeiro_externo = min(i for i in (head.find('<link rel="stylesheet"'), head.find("<script src")) if i >= 0)
        self.assertLess(m.start(), primeiro_externo)
        self.assertLess(m.start(), head.find('<link rel="preload"'))

    def test_overlay_do_preloader_no_html_e_visivel_so_sob_a_classe(self):
        html = (REPO / "index.html").read_text("utf-8")
        self.assertIn('class="preloader"', html)
        css = (REPO / "css" / "site.css").read_text("utf-8")
        self.assertRegex(css, r"\.preloader\s*\{[^}]*display:\s*none")
        self.assertRegex(css, r"html\.pre-1a\s+\.preloader\s*\{[^}]*display:\s*grid")

    def test_preloader_anima_so_opacity_e_clip_path(self):
        css = (REPO / "css" / "site.css").read_text("utf-8")
        regras = [r for r in re.findall(r"[^{}]*\.preloader[^{}]*\{[^}]*\}", css)]
        self.assertTrue(regras)
        for r in regras:
            self.assertNotRegex(r, r"background(-color)?[^;]*transition|transition[^;]*background", r)
        kf = re.findall(r"@keyframes\s+[\w-]*pre[\w-]*\s*\{(?:[^{}]*\{[^}]*\})*[^{}]*\}", css)
        for bloco in kf:
            props = set(re.findall(r"([\w-]+)\s*:", bloco))
            self.assertLessEqual(props, {"opacity", "clip-path"}, bloco)
        self.assertRegex(css, r"html\.pre-1a\s+\.preloader\s*\{[^}]*animation:[^;]*var\(--dur-media\)")

    def test_preloader_js_so_sai_e_grava_flag(self):
        js = (REPO / "js" / "site.js").read_text("utf-8")
        self.assertNotIn('createElement("div")', js.split("Preloader")[1].split("Cursor")[0])
        self.assertIn("pre-1a", js)
        self.assertNotRegex(js, r"setTimeout\([^)]*,\s*\d{3,}")  # nada de milissegundos soltos

    # ---------- Título revela (G2, G8) ----------
    def test_titulo_revela_so_esconde_o_que_ainda_nao_esta_na_tela(self):
        js = (REPO / "js" / "site.js").read_text("utf-8")
        bloco = js[js.index(".titulo-revela: linhas"):js.index("Lenis: só com mouse")]
        self.assertIn("naTela(", bloco)
        self.assertIn("autoSplit", bloco)
        self.assertIn("onSplit", bloco)
        self.assertIn("!reduz", bloco)
        self.assertIn("aindaCoberto(", bloco)  # sob o preloader: só esconde enquanto o overlay cobre
        self.assertIn("pre-1a", js)

    # ---------- Movimento reduzido (G5) ----------
    def test_btn_active_so_sem_reduced_motion(self):
        css = (REPO / "css" / "site.css").read_text("utf-8")
        fora = re.sub(r"@media\s*\(prefers-reduced-motion:\s*no-preference\)\s*\{(?:[^{}]*\{[^}]*\})*[^{}]*\}", "", css)
        self.assertNotRegex(fora, r"\.btn:active")
        self.assertRegex(css, r"@media\s*\(prefers-reduced-motion:\s*no-preference\)\s*\{[^@]*\.btn:active\s*\{[^}]*scale\(0\.98\)")

    def test_reduce_zera_animacao_e_transicao(self):
        css = (REPO / "css" / "site.css").read_text("utf-8")
        m = re.search(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{(?:[^{}]*\{[^}]*\})*[^{}]*\}", css)
        self.assertTrue(m)
        for prop in ("transition-duration", "animation-duration", "animation-iteration-count"):
            self.assertIn(prop, m.group(0))

    # ---------- Cursor (G7) ----------
    def test_cursor_filtra_ponteiro_que_nao_e_mouse(self):
        js = (REPO / "js" / "site.js").read_text("utf-8")
        for evento in ("pointerover", "pointerout", "pointerdown"):
            m = re.search(r"addEventListener\(\"" + evento + r"\",\s*function \(e\)\s*\{(.*?)\n    \}\);", js, re.S)
            self.assertTrue(m, evento)
            self.assertRegex(m.group(1), r"pointerType|ehMouse\(e\)", evento)
        self.assertRegex(js, r"ehMouse\s*=\s*function\s*\(e\)\s*\{[^}]*pointerType\s*===\s*\"mouse\"")
        self.assertRegex(js, r"esconde\s*=\s*function\s*\(\)\s*\{[^}]*classList\.remove\(\"cursor-ativo\"\)")
        self.assertRegex(re.search(r"\"pointerdown\".*?\n    \}\);", js, re.S).group(0), r"esconde\(\)")

    def test_cursor_com_texto_cresce_por_transform(self):
        css = (REPO / "css" / "site.css").read_text("utf-8")
        regra = re.search(r"\.cursor\.cursor-com-texto\s+\.cursor-anel\s*\{([^}]*)\}", css).group(1)
        self.assertIn("scale(", regra)
        for prop in ("width", "height", "margin"):
            self.assertNotRegex(regra, prop + r"\s*:")
        # O texto não é filho do anel que escala: continua do mesmo tamanho.
        self.assertNotRegex(css, r"\.cursor-com-texto[^{]*\.cursor-texto\s*\{[^}]*scale")


if __name__ == "__main__":
    unittest.main()
