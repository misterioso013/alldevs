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


class TestTokens(unittest.TestCase):
    def test_contraste_aa(self):
        v = _variaveis()
        pares = [
            ("--claro", "--fundo"), ("--suave", "--fundo"),
            ("--caio-texto", "--fundo"),
            ("--caio-texto-claro", "--claro"), ("--rosiel-texto", "--claro"),
        ]
        for fg, bg in pares:
            with self.subTest(par=f"{fg}/{bg}"):
                self.assertGreaterEqual(contraste(v[fg], v[bg]), 4.5)

    def test_nomes_e_movimento(self):
        v = _variaveis()
        for nome, valor in [("--fundo", "#0d0c12"), ("--claro", "#ecebe6"), ("--suave", "#9b99a6"),
                            ("--caio", "#7c3aed"), ("--caio-texto", "#a78bfa"),
                            ("--caio-texto-claro", "#6d28d9"), ("--rosiel", "#f97316"),
                            ("--rosiel-texto", "#9a3412"), ("--t-curto", "200ms"),
                            ("--t-medio", "450ms"), ("--t-longo", "900ms")]:
            self.assertEqual(v[nome].strip().lower(), valor, nome)
        for nome in ("--grade", "--curva", "--fonte-titulo", "--fonte-texto", "--fonte-mono"):
            self.assertIn(nome, v)

    def test_vendor_sha256(self):
        versoes = json.loads((VENDOR / "VERSOES.json").read_text("utf-8"))
        for arq, info in versoes.items():
            with self.subTest(arquivo=arq):
                self.assertEqual(hashlib.sha256((VENDOR / arq).read_bytes()).hexdigest(), info["sha256"])
                self.assertTrue(info["pacote"] and info["versao"])
        no_disco = {p.name for p in VENDOR.glob("*") if p.is_file()} - {"VERSOES.json", "LICENCAS.md"}
        self.assertEqual(no_disco, set(versoes))

    def test_fontes_com_licenca(self):
        css = TOKENS.read_text("utf-8")
        blocos = re.findall(r"@font-face\s*\{[^}]*\}", css)
        urls = [u for b in blocos for u in re.findall(r"url\(\s*[\"']?([^\"')]+)[\"']?\s*\)", b)]
        self.assertEqual(len(urls), 6)
        for u in urls:
            self.assertTrue((TOKENS.parent / u).resolve().is_file(), u)
        referenciados = {(TOKENS.parent / u).resolve().name for u in urls}
        em_disco = {p.name for p in FONTES.glob("*.woff2")}
        self.assertEqual(em_disco, referenciados)
        self.assertEqual(len(em_disco), 6)
        for b in blocos:
            self.assertRegex(b, r"font-weight:\s*\d{3};")
        self.assertIn("font-display: swap", css)
        licenca = (FONTES / "OFL.txt").read_text("utf-8")
        for familia in ("Fraunces", "DM Sans", "JetBrains Mono"):
            self.assertIn(familia, licenca)


if __name__ == "__main__":
    unittest.main()
