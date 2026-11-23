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


def _ler_sem_binarios(pastas):
    for pasta in pastas:
        for p in Path(pasta).rglob("*"):
            if p.is_file() and p.suffix in (".css", ".html", ".js", ".txt", ".py", ".json", ".md"):
                yield p


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
        # Botão cheio: texto claro sobre o roxo.
        self.assertGreaterEqual(contraste(v["--texto"], v["--roxo"]), 4.5)

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
        self.assertIn("(pointer: fine)", js)
        self.assertIn("(min-width: 1024px)", js)
        self.assertIn("prefers-reduced-motion", js)

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


if __name__ == "__main__":
    unittest.main()
