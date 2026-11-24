"""História (Task 9): "Fizemos juntos" e a história entram byte a byte. As páginas de perfil saíram em 24/11 (decisão do Caio)."""
import re
import unittest
from urllib.parse import unquote

from alldevs.paginas import MARCADOR_CONTATO, _bloco_contato, _tamanho_webp
from testes.test_conteudo import Base, ler
from testes.test_paginas import REPO

PERFIS = ("caio", "rosiel")


def secao(txt, nome):
    m = re.search(rf'<section[^>]*data-secao="{nome}"[^>]*>.*?</section>', txt, re.S)
    assert m, nome
    return m.group(0)


def slugs_da_secao(txt):
    return re.findall(r'<article class="projeto-cartao" data-slug="([^"]+)"', txt)


class TestPerfis(Base):
    def test_titulo_do_fecho_sem_ch(self):
        css = ler(REPO / "css" / "site.css")
        for sel in (".closing-title {",):
            i = css.index(sel)
            self.assertNotRegex(css[i:css.index("}", i)], r"max-width:\s*[\d.]+ch", sel)

    def test_brilhos_da_historia_somem_antes_da_borda(self):
        css = ler(REPO / "css" / "site.css")
        for sel in (".hist-hero-bg {", ".closing-glow {"):
            i = css.index(sel)
            regra = css[i:css.index("}", i)]
            self.assertIn("transparent", regra, sel)
            m = re.search(r"transparent (\d+)%", regra)
            self.assertTrue(m and int(m.group(1)) <= 60, sel)

    def test_css_cobre_as_classes_dos_depoimentos(self):
        from dataclasses import replace
        from alldevs.dados import Depoimento
        from alldevs.paginas import _depoimentos
        dados = replace(self.dados, depoimentos=(Depoimento("Fulana", "Cliente", "Texto de exemplo", True),))
        html = str(_depoimentos(dados))
        classes = {c for g in re.findall(r'class="([^"]+)"', html) for c in g.split()}
        css = ler(REPO / "css" / "site.css")
        self.assertTrue(classes)
        for c in classes:
            self.assertIn("." + c, css, c)
        self.assertIn(".depoimento figcaption", css)
        self.assertIn(".depoimento blockquote", css)

    def test_css_sem_cor_nem_estilo_por_pessoa(self):
        css = ler(REPO / "css" / "site.css")
        for p in self.dados.pessoas:
            self.assertNotRegex(css, rf"(?i)[.#\[\"=-]{p.slug}\b", p.slug)
        self.assertNotIn("data-pessoa", css)


class TestHistoria(Base):
    def test_historia_texto_identico(self):
        txt = ler(self.saida / "historia.html")
        self.assertEqual(txt.count("<!--historia:inicio-->"), 1)
        self.assertEqual(txt.count("<!--historia:fim-->"), 1)
        meio = txt.split("<!--historia:inicio-->\n", 1)[1].split("\n<!--historia:fim-->", 1)[0]
        fonte = ler(REPO / "fonte/conteudo/historia.html")
        self.assertIn(MARCADOR_CONTATO, fonte)
        esperado = fonte.replace(MARCADOR_CONTATO, _bloco_contato(self.dados.estudio, "home").rstrip("\n"))
        self.assertEqual(meio, esperado)

    def test_historia_contato_home_e_titulo(self):
        txt = ler(self.saida / "historia.html")
        self.assertEqual(len(re.findall(r"<h1[ >]", txt)), 1)
        self.assertIn("[site·home]", unquote(txt))
        self.assertNotIn("/js/revelar.js", txt)


if __name__ == "__main__":
    unittest.main()
