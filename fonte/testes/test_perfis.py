"""Seções da home e CSS dos depoimentos. As páginas de perfil e a História saíram em 24/11 (decisão do Caio)."""
import re
import unittest

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


if __name__ == "__main__":
    unittest.main()
