import contextlib
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

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

    def test_historia_titulo(self):
        self.assertEqual(titulo(self.saida / "historia.html"), "A história — AllDevs")

    def test_home_titulo_igual_ao_atual(self):
        self.assertEqual(titulo(self.saida / "index.html"),
                         "AllDevs — Desenvolvimento Web, Mobile e Automações | Rosiel Victor")

    def test_links_de_servico_com_barra(self):
        for arq in self.saida.rglob("*.html"):
            self.assertIsNone(re.search(r'href="/servicos/[a-z0-9-]+"', arq.read_text(encoding="utf-8")), arq)

    def test_servico_tem_wa_com_origem(self):
        for slug in TITULOS:
            txt = (self.saida / "servicos" / slug / "index.html").read_text(encoding="utf-8")
            self.assertIn(f"%5Bsite%C2%B7servico%C2%B7{slug}%5D", txt)
            self.assertIn("https://wa.me/558189477459?text=", txt)

    def test_historia_style_no_head(self):
        txt = (self.saida / "historia.html").read_text(encoding="utf-8")
        head, _, corpo = txt.partition("</head>")
        self.assertIn("<style>", head)
        self.assertNotIn("<style", corpo)

    def test_botoes_dentro_do_servico_cta(self):
        for slug in TITULOS:
            txt = (self.saida / "servicos" / slug / "index.html").read_text(encoding="utf-8")
            cta = txt[txt.index('class="servico-cta"'):txt.index('servicos-relacionados')]
            self.assertIn("https://wa.me/", cta, slug)
            self.assertNotIn("<!--contato-->", txt)
        hist = (self.saida / "historia.html").read_text(encoding="utf-8")
        fecho = hist[hist.index('class="closing-inner'):hist.index("</section>", hist.index('class="closing-inner'))]
        self.assertIn("https://wa.me/", fecho)

    def test_fonte_com_italico_na_home_e_historia(self):
        for nome in ("index.html", "historia.html"):
            self.assertIn("0,9..40,500;1,9..40,300&display", (self.saida / nome).read_text(encoding="utf-8"))

    def test_home_com_origem_e_sem_numero_solto(self):
        txt = (self.saida / "index.html").read_text(encoding="utf-8")
        self.assertIn("%5Bsite%C2%B7home%5D", txt)
        self.assertIn("[site·home]", txt)
        self.assertNotIn("contato@all.dev.br", txt)
        self.assertNotIn("Amott", txt)

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
        self.assertTrue((self.saida / "css" / "styles.css").is_file())
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
        dados[0]["quem_toca"] = ["ninguem"]
        arq.write_text(json.dumps(dados), encoding="utf-8")
        rc, _, err = rodar("--raiz", str(raiz), "--saida", str(self.saida))
        self.assertEqual(rc, 1)
        self.assertIn("quem_toca inexistente: ninguem", err)
        self.assertFalse(self.saida.exists())


if __name__ == "__main__":
    unittest.main()
