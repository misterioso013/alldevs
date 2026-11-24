import contextlib
import io
import json
import re
import shutil
import struct
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

import gerar
from alldevs import paginas

REPO = Path(__file__).resolve().parent.parent.parent
CAB = paginas.CABECALHO

TITULOS = {
    "aplicativo-mobile-react-native": "Desenvolvimento de Aplicativo Mobile iOS e Android | React Native — AllDevs",
    "automacoes-integracoes-api": "Automação de Processos e Integração de Sistemas via API | Webhook — AllDevs",
    "bots-whatsapp-automacao": "Bot para WhatsApp, Discord e Telegram | Automação de Atendimento 24h — AllDevs",
    "criacao-de-sites-institucionais": "Criação de Site Institucional Profissional | A partir de R$ 800 — AllDevs",
    "desenvolvimento-mvp-startups": "Desenvolvimento de MVP para Startups Web | Next.js — AllDevs",
    "landing-page-conversao": "Landing Page de Alta Conversão com WhatsApp | Entrega em 3 Dias — AllDevs",
}


def rodar(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = gerar.main(list(args))
    return rc, out.getvalue(), err.getvalue()


def titulo(arq: Path) -> str:
    return re.search(r"<title>(.*?)</title>", arq.read_text(encoding="utf-8")).group(1)


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.saida = self.tmp / "saida"


class TestGerar(Base):
    def setUp(self):
        super().setUp()
        self.rc, _, self.err = rodar("--raiz", str(REPO), "--saida", str(self.saida))

    def test_rc_zero(self):
        self.assertEqual(self.rc, 0, self.err)

    def test_titulos_dos_servicos_iguais(self):
        for slug, esperado in TITULOS.items():
            self.assertEqual(titulo(self.saida / "servicos" / slug / "index.html"), esperado, slug)

    def test_home_titulo_do_estudio(self):
        self.assertEqual(titulo(self.saida / "index.html"),
                         "AllDevs — Estúdio de software: sites, apps e automações")

    def test_links_de_servico_com_barra(self):
        for arq in self.saida.rglob("*.html"):
            self.assertIsNone(re.search(r'href="/servicos/[a-z0-9-]+"', arq.read_text(encoding="utf-8")), arq)

    def test_servico_tem_wa_com_origem(self):
        for slug in TITULOS:
            txt = (self.saida / "servicos" / slug / "index.html").read_text(encoding="utf-8")
            self.assertIn(f"%5Bsite%C2%B7servico%C2%B7{slug}%5D", txt)
            self.assertIn("https://wa.me/558189477459?text=", txt)

    def test_sem_style_inline_nem_cdn(self):
        for arq in self.saida.rglob("*.html"):
            txt = arq.read_text(encoding="utf-8")
            self.assertNotIn("<style", txt, arq)
            self.assertNotIn(" style=", txt, arq)
            for cdn in ("googleapis", "gstatic", "cdnjs", "jsdelivr", "unpkg"):
                self.assertNotIn(cdn, txt, arq)

    def test_botoes_dentro_do_servico_cta(self):
        for slug in TITULOS:
            txt = (self.saida / "servicos" / slug / "index.html").read_text(encoding="utf-8")
            cta = txt[txt.index('class="servico-cta"'):txt.index('servicos-relacionados')]
            self.assertIn("https://wa.me/", cta, slug)
            self.assertNotIn("<!--contato-->", txt)

    def test_head_com_tokens_site_e_preload_so_do_titulo(self):
        scripts = ["/js/vendor/gsap.min.js", "/js/vendor/ScrollTrigger.min.js", "/js/vendor/SplitText.min.js",
                   "/js/vendor/lenis.min.js", "/js/site.js", "/js/paleta.js"]
        for arq in (a for a in self.saida.rglob("*.html") if a.name != "historia.html"):   # historia.html é só o redirecionamento
            head = arq.read_text(encoding="utf-8").partition("</head>")[0]
            self.assertLess(head.index('href="/css/tokens.css"'), head.index('href="/css/site.css"'), arq)
            self.assertEqual(re.findall(r'<link rel="preload" href="([^"]+)"', head),
                             ["/assets/fontes/syne-latin-800-normal.woff2"], arq)
            achados = re.findall(r'<script src="([^"]+)"( defer)?></script>', head)
            self.assertEqual([s for s, _ in achados], scripts, arq)
            self.assertTrue(all(d for _, d in achados), arq)
            self.assertNotIn('type="module"', head, arq)

    def test_og_e_twitter_card_com_imagem_existente(self):
        vistos = {}
        for arq in sorted(a for a in self.saida.rglob("*.html") if a.name != "historia.html"):
            txt = arq.read_text(encoding="utf-8")
            img = re.search(r'<meta property="og:image" content="https://all\.dev\.br/assets/og/([a-z0-9-]+)\.png">', txt)
            self.assertIsNotNone(img, arq)
            self.assertIn('<meta name="twitter:card" content="summary_large_image">', txt)
            self.assertIn('<meta property="og:image:width" content="1200">', txt)
            slug = img.group(1)
            self.assertNotIn(slug, vistos, f"{arq} e {vistos.get(slug)} com a mesma imagem OG")
            vistos[slug] = arq
            self.assertTrue((REPO / "assets" / "og" / f"{slug}.png").is_file(), f"falta assets/og/{slug}.png")
        self.assertEqual(vistos["site"].name, "index.html")

    def test_home_com_origem_e_sem_numero_solto(self):
        txt = (self.saida / "index.html").read_text(encoding="utf-8")
        self.assertIn("%5Bsite%C2%B7home%5D", txt)
        self.assertNotIn("contato@all.dev.br", txt)
        self.assertNotIn("Amott", txt)

    def test_fotos_da_home_4x5_lazy_e_sem_prioridade_alta(self):
        txt = (self.saida / "index.html").read_text(encoding="utf-8")
        fotos = re.findall(r'<article class="cartao-pessoa"[^>]*>\s*(<img [^>]+>)', txt)
        self.assertEqual(len(fotos), 2)
        for img in fotos:
            self.assertIn('width="512" height="640"', img)  # 4/5, igual ao aspect-ratio do CSS
            self.assertIn('loading="lazy"', img)  # abaixo do hero: nao disputam banda com a frente (LCP)
        for img in fotos:  # a unica prioridade alta da pagina e a da frente do hero (test_hero)
            self.assertNotIn("fetchpriority", img)
        css = (REPO / "css" / "site.css").read_text(encoding="utf-8")
        regra = css[css.index(".cartao-pessoa img {"):]
        self.assertIn("aspect-ratio: 4 / 5;", regra[:regra.index("}")])

    def test_barra_wa_em_toda_pagina_com_origem(self):
        # Home, serviço e case levam a origem da própria página; /projetos/ segue o v1 (site·home).
        # Uma barra por página, com wa.me (o redirecionamento historia.html não é página de conteúdo).
        esperada = {"index.html": "site·home", "projetos/index.html": "site·home"}
        for arq in sorted(a for a in self.saida.rglob("*.html") if a.name != "historia.html"):
            rel = arq.relative_to(self.saida).as_posix()
            txt = arq.read_text(encoding="utf-8")
            barras = re.findall(r'<div class="barra-wa"[^>]*>.*?</div>', txt, re.S)
            self.assertEqual(len(barras), 1, rel)
            href = unquote(re.search(r'href="(https://wa\.me/[^"]+)"', barras[0]).group(1))
            if rel in esperada:
                origem = esperada[rel]
            elif rel.startswith("servicos/"):
                origem = "site·servico·" + rel.split("/")[1]
            elif rel.startswith("projetos/"):
                origem = "site·case·" + rel.split("/")[1]
            else:
                self.fail(f"página inesperada: {rel}")
            self.assertIn(f"[{origem}]", href, rel)

    def test_faq_desativado_sem_js(self):
        total = 0
        for slug in TITULOS:
            txt = (self.saida / "servicos" / slug / "index.html").read_text(encoding="utf-8")
            botoes = re.findall(r'<button [^>]*class="faq-question"[^>]*>', txt)
            self.assertTrue(botoes, slug)
            for b in botoes:
                self.assertRegex(b, r"\sdisabled[\s>]", slug)
            total += len(botoes)
        self.assertEqual(total, 30)
        js = (REPO / "js" / "site.js").read_text(encoding="utf-8")
        self.assertIn('botao.removeAttribute("disabled")', js)

    def test_toda_pagina_tem_cabecalho_depois_do_doctype(self):
        for arq in self.saida.rglob("*.html"):
            linhas = arq.read_text(encoding="utf-8").split("\n")
            self.assertEqual(linhas[0].lower(), "<!doctype html>", arq)
            self.assertEqual(linhas[1], CAB, arq)

    def test_deterministico(self):
        outra = self.tmp / "outra"
        self.assertEqual(rodar("--raiz", str(REPO), "--saida", str(outra))[0], 0)
        a = {p.relative_to(self.saida): p.read_bytes() for p in self.saida.rglob("*") if p.is_file()}
        b = {p.relative_to(outra): p.read_bytes() for p in outra.rglob("*") if p.is_file()}
        self.assertEqual(a, b)


class TestEscrever(Base):
    def test_orfa_gerada_e_removida_e_manual_fica(self):
        self.saida.mkdir()
        (self.saida / "orfa.html").write_text(f"<!DOCTYPE html>\n{CAB}\n<p>x</p>", encoding="utf-8")
        (self.saida / "manual.html").write_text("<!DOCTYPE html>\n<p>meu</p>", encoding="utf-8")
        p = paginas.Pagina("a.html", "t", "d", paginas.Seguro("<!DOCTYPE html>\n<p>a</p>"), "2026-11-22", ())
        paginas.escrever([p], self.saida, False)
        self.assertFalse((self.saida / "orfa.html").exists())
        self.assertTrue((self.saida / "manual.html").exists())
        self.assertTrue((self.saida / "a.html").read_text(encoding="utf-8").startswith(f"<!DOCTYPE html>\n{CAB}\n"))

    def test_previa_copia_estaticos_sem_cname(self):
        rc, _, err = rodar("--previa", "--raiz", str(REPO), "--saida", str(self.saida))
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.saida / "css" / "site.css").is_file())
        self.assertTrue((self.saida / "js").is_dir())
        self.assertTrue((self.saida / "assets").is_dir())
        self.assertTrue((self.saida / "icon.svg").is_file())
        self.assertFalse((self.saida / "CNAME").exists())


class TestCli(Base):
    def test_previa_sem_saida_rc2(self):
        rc, _, _ = rodar("--previa", "--raiz", str(REPO))
        self.assertEqual(rc, 2)

    def test_erro_de_dados_rc1(self):
        raiz = self.tmp / "raiz"
        shutil.copytree(REPO / "fonte", raiz / "fonte", ignore=shutil.ignore_patterns("__pycache__", "testes"))
        shutil.copytree(REPO / "assets", raiz / "assets")
        arq = raiz / "fonte" / "dados" / "servicos.json"
        dados = json.loads(arq.read_text(encoding="utf-8"))
        dados[0]["tipo"] = "bot"
        arq.write_text(json.dumps(dados), encoding="utf-8")
        rc, _, err = rodar("--raiz", str(raiz), "--saida", str(self.saida))
        self.assertEqual(rc, 1)
        self.assertIn("tipo inválido: 'bot'", err)
        self.assertFalse(self.saida.exists())


class TestLeitorWebp(unittest.TestCase):
    def _arq(self, conteudo: bytes) -> Path:
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
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


if __name__ == "__main__":
    unittest.main()
