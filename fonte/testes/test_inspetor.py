"""Hero inspetor (tarefa 11): dados das telas, script e molde da home."""
import json
import re
import struct
import unittest
from pathlib import Path

from alldevs import dados as D
from alldevs import paginas
from testes.test_paginas import REPO

PASTA_INSP = REPO / "fonte" / "dados" / "inspecao"
PASTA_IMG = REPO / "assets" / "inspetor"
CAMPOS = ("x", "y", "w", "h", "tag", "classe", "medida", "codigo")


def tamanho_webp(caminho: Path):
    """(largura, altura) de um WebP lendo só o cabeçalho RIFF (VP8, VP8L ou VP8X)."""
    b = caminho.read_bytes()[:40]
    if b[:4] != b"RIFF" or b[8:12] != b"WEBP":
        raise ValueError(f"{caminho}: não é WebP")
    tipo = b[12:16]
    if tipo == b"VP8 ":
        if b[23:26] != b"\x9d\x01\x2a":
            raise ValueError(f"{caminho}: VP8 sem assinatura de quadro")
        w, h = struct.unpack("<HH", b[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if tipo == b"VP8L":
        if b[20] != 0x2F:
            raise ValueError(f"{caminho}: VP8L sem assinatura")
        v = int.from_bytes(b[21:25], "little")
        return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    if tipo == b"VP8X":
        return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    raise ValueError(f"{caminho}: bloco WebP desconhecido {tipo!r}")


def telas():
    return {arq.stem: json.loads(arq.read_text(encoding="utf-8")) for arq in sorted(PASTA_INSP.glob("*.json"))}


class TestDadosInspecao(unittest.TestCase):
    def test_ordem_do_rodizio(self):
        est = json.loads((REPO / "fonte" / "dados" / "estudio.json").read_text(encoding="utf-8"))
        self.assertEqual(est["inspetor"], ["prosup", "fakly", "sendany"])
        self.assertEqual(sorted(telas()), sorted(est["inspetor"]))

    def test_heisuca_fora(self):
        self.assertFalse((PASTA_INSP / "heisuca.json").exists())

    def test_inspecao_caixas_validas(self):
        t = telas()
        self.assertTrue(t)
        for slug, obj in t.items():
            self.assertEqual(obj["imagem"], f"assets/inspetor/{slug}.webp", slug)
            self.assertTrue((REPO / obj["imagem"]).is_file(), slug)
            self.assertTrue(4 <= len(obj["caixas"]) <= 6, f"{slug}: {len(obj['caixas'])} caixas")
            for n, c in enumerate(obj["caixas"]):
                rot = f"{slug}[{n}]"
                for campo in CAMPOS:
                    self.assertIn(campo, c, rot)
                for campo in ("x", "y", "w", "h"):
                    self.assertIsInstance(c[campo], (int, float), rot)
                    self.assertGreaterEqual(c[campo], 0, rot)
                self.assertGreater(c["w"], 0, rot)
                self.assertGreater(c["h"], 0, rot)
                self.assertLessEqual(c["x"] + c["w"], 100, rot)
                self.assertLessEqual(c["y"] + c["h"], 100, rot)
                for campo in ("tag", "classe", "medida", "codigo"):
                    self.assertTrue(isinstance(c[campo], str) and c[campo], rot)
                self.assertRegex(c["tag"], r"^[a-z][a-z0-9]*$", rot)
                self.assertRegex(c["classe"], r"^[A-Za-z][\w-]*$", rot)

    def test_inspecao_medida_coerente(self):
        for slug, obj in telas().items():
            lw, lh = tamanho_webp(REPO / obj["imagem"])
            for n, c in enumerate(obj["caixas"]):
                m = re.fullmatch(r"(\d+)×(\d+)", c["medida"])
                self.assertIsNotNone(m, f"{slug}[{n}]: medida {c['medida']!r}")
                mw, mh = int(m.group(1)), int(m.group(2))
                self.assertLessEqual(abs(mw - c["w"] / 100 * lw), 2, f"{slug}[{n}] largura")
                self.assertLessEqual(abs(mh - c["h"] / 100 * lh), 2, f"{slug}[{n}] altura")
                self.assertIn(f"{mw}px", c["codigo"], f"{slug}[{n}] codigo")
                self.assertIn(f"{mh}px", c["codigo"], f"{slug}[{n}] codigo")

    def test_webp_ate_960(self):
        for slug, obj in telas().items():
            lw, _ = tamanho_webp(REPO / obj["imagem"])
            self.assertLessEqual(lw, 960, slug)

    def test_sem_amott(self):
        for pasta in (PASTA_INSP, PASTA_IMG):
            for arq in pasta.iterdir():
                self.assertNotIn("amott", arq.name.lower(), arq)
                if arq.suffix == ".json":
                    self.assertNotIn("amott", arq.read_text(encoding="utf-8").lower(), arq)


class TestScript(unittest.TestCase):
    def test_inspetor_js_ate_8kb(self):
        self.assertLessEqual((REPO / "js" / "inspetor.js").stat().st_size, 8192)

    def test_sem_dependencia(self):
        js = (REPO / "js" / "inspetor.js").read_text(encoding="utf-8")
        self.assertNotIn("import ", js)
        self.assertNotIn("gsap", js.lower())
        self.assertNotIn("getContext", js)  # sem canvas/WebGL

    def test_troca_de_tela_espera_gesto(self):
        # Imagem nova pintada antes do 1º gesto vira LCP tardio; a troca automática espera o visitante mexer.
        js = (REPO / "js" / "inspetor.js").read_text(encoding="utf-8")
        for gesto in ("pointerdown", "keydown"):
            self.assertIn(f'"{gesto}"', js)
        self.assertIn("tempo >= POR_TELA && mexeu", js)


class TestHero(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dados = D.carregar(REPO)
        pags = {p.caminho: p for p in paginas.montar_todas(dados, REPO, previa=False)}
        cls.home = str(pags["index.html"].corpo)
        cls.outras = [str(p.corpo) for c, p in pags.items() if c != "index.html"]
        m = re.search(r'<div class="inspetor[ "][^>]*>.*?<!-- /inspetor -->', cls.home, re.S)
        cls.bloco = m.group(0) if m else ""

    def test_hero_aria_hidden(self):
        self.assertTrue(self.bloco, "bloco do inspetor ausente")
        abre = re.match(r"<div[^>]*>", self.bloco).group(0)
        self.assertIn('aria-hidden="true"', abre)

    def test_primeira_tela_lazy_sem_preload(self):
        imgs = re.findall(r"<img[^>]*>", self.bloco)
        self.assertEqual(len(imgs), 1)
        img = imgs[0]
        self.assertIn('src="/assets/inspetor/prosup.webp"', img)
        self.assertIn('loading="lazy"', img)
        self.assertIn('fetchpriority="low"', img)
        self.assertIn('alt="', img)
        self.assertRegex(img, r'width="\d+" height="\d+"')
        self.assertNotIn('rel="preload" href="/assets/inspetor', self.home)

    def test_dados_inline(self):
        m = re.search(r'<script type="application/json" id="inspecao">(.*?)</script>', self.home, re.S)
        self.assertIsNotNone(m)
        obj = json.loads(m.group(1))
        self.assertEqual([t["slug"] for t in obj["telas"]], ["prosup", "fakly", "sendany"])
        for t in obj["telas"]:
            self.assertTrue(t["imagem"].startswith("/assets/inspetor/"))
            self.assertTrue(t["caixas"])
            self.assertIn(t["cor"], ("caio", "rosiel", "dupla"))

    def test_botao_proximo_fora_do_aria_hidden(self):
        self.assertNotIn("<button", self.bloco)
        m = re.search(r'<button[^>]*class="inspetor-proximo"[^>]*>', self.home)
        self.assertIsNotNone(m)
        self.assertIn("aria-label=", m.group(0))
        self.assertIn("hidden", m.group(0))  # sem JS, oculto

    def test_script_defer_so_na_home(self):
        self.assertIn('<script src="/js/inspetor.js" defer></script>', self.home)
        for corpo in self.outras:
            self.assertNotIn("inspetor.js", corpo)

    def test_h1_antes_do_inspetor(self):
        self.assertLess(self.home.index("<h1"), self.home.index('class="inspetor '))
