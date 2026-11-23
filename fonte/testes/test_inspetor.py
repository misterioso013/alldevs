"""Hero inspetor (tarefa 11): dados das telas, script e molde da home."""
import json
import re
import struct
import tempfile
import unittest
from pathlib import Path

from alldevs import dados as D
from alldevs import paginas
from testes.test_paginas import REPO

PASTA_INSP = REPO / "fonte" / "dados" / "inspecao"
PASTA_IMG = REPO / "assets" / "inspetor"
CAMPOS = ("x", "y", "w", "h", "tag", "classe", "medida", "codigo")


tamanho_webp = paginas._tamanho_webp  # leitor único (o do gerador)


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

    def test_caixas_sem_transicao_de_geometria(self):
        # A caixa pula (spec §7): nenhuma regra do inspetor anima left/top/width/height/inset (CLS em runtime).
        # O comportamento (gesto -> troca, reduced-motion, CLS) é medido na bancada: bancada/inspetor.mjs.
        css = (REPO / "css" / "site.css").read_text(encoding="utf-8")
        regras = re.findall(r"([^{}]*\.inspetor[^{}]*)\{([^{}]*)\}", css)
        self.assertTrue(regras)
        for sel, corpo in regras:
            for m in re.finditer(r"transition(?:-property)?\s*:([^;]*)", corpo):
                for prop in ("left", "top", "width", "height", "inset", "right", "bottom", "all"):
                    self.assertNotRegex(m.group(1), rf"(^|[\s,]){prop}(\s|,|$)", f"{sel.strip()}: transição de {prop}")
            self.assertNotIn("transform", corpo, f"{sel.strip()}: sem transform no inspetor")

    def test_botao_proximo_44px(self):
        css = (REPO / "css" / "site.css").read_text(encoding="utf-8")
        m = re.search(r"\n\.inspetor-proximo\s*\{([^}]*)\}", css)
        self.assertIsNotNone(m)
        self.assertRegex(m.group(1), r"min-height:\s*44px")


class TestLeitorWebp(unittest.TestCase):
    def _arq(self, conteudo: bytes) -> Path:
        d = tempfile.mkdtemp()
        f = Path(d) / "x.webp"
        f.write_bytes(conteudo)
        return f

    def test_vp8_exige_assinatura(self):
        cab = b"RIFF" + b"\0" * 4 + b"WEBP" + b"VP8 " + b"\0" * 4 + b"\0" * 3
        bom = cab + b"\x9d\x01\x2a" + struct.pack("<HH", 480, 384) + b"\0" * 10
        self.assertEqual(paginas._tamanho_webp(self._arq(bom)), (480, 384))
        ruim = cab + b"\0\0\0" + struct.pack("<HH", 480, 384) + b"\0" * 10
        with self.assertRaises(ValueError):
            paginas._tamanho_webp(self._arq(ruim))

    def test_vp8l_exige_assinatura(self):
        v = (480 - 1) | ((384 - 1) << 14)
        cab = b"RIFF" + b"\0" * 4 + b"WEBP" + b"VP8L" + b"\0" * 4
        bom = cab + b"\x2f" + v.to_bytes(4, "little") + b"\0" * 15
        self.assertEqual(paginas._tamanho_webp(self._arq(bom)), (480, 384))
        with self.assertRaises(ValueError):
            paginas._tamanho_webp(self._arq(cab + b"\x00" + v.to_bytes(4, "little") + b"\0" * 15))

    def test_teste_usa_o_leitor_do_gerador(self):
        self.assertIs(tamanho_webp, paginas._tamanho_webp)


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
