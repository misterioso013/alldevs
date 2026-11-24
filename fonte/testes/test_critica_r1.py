"""Crítica externa, rodada 1: por trás fechado, estágios ocultos fora do Tab, enquadramento das capas."""
import html
import json
import re
import unittest

from alldevs import dados as D
from alldevs import paginas
from testes.test_paginas import REPO

CSS = (REPO / "css" / "site.css").read_text(encoding="utf-8")


def regra(seletor):
    m = re.search(re.escape(seletor) + r"\s*\{([^}]*)\}", CSS)
    return m.group(1) if m else ""


def equilibrado(txt):
    return all(txt.count(a) == txt.count(b) for a, b in ("{}", "[]", "()"))


class PorTrasFechado(unittest.TestCase):
    def setUp(self):
        self.dados = D.carregar(REPO)

    def test_cartao_sem_bloco_aberto(self):
        n = 0
        for p in self.dados.projetos:
            if not p.por_tras or D.ler_por_tras(REPO, p) is None:
                continue
            m = re.search(r"<pre><code>(.*?)</code></pre>", str(paginas._camada_por_tras(p, REPO)), re.S)
            cod = html.unescape(m.group(1))
            self.assertTrue(equilibrado(cod), p.slug)
            n += 1
        self.assertGreaterEqual(n, 3)

    def test_ciclo_do_hero_sem_bloco_aberto(self):
        for p in self.dados.projetos:
            if p.por_tras and D.ler_por_tras(REPO, p) is not None:
                self.assertTrue(equilibrado(paginas._item_ciclo(p, REPO)["por_tras"]["texto"]), p.slug)

    def test_trecho_real_e_preservado(self):
        for p in self.dados.projetos:
            txt = D.ler_por_tras(REPO, p) if p.por_tras else None
            if txt:
                self.assertTrue(paginas._item_ciclo(p, REPO)["por_tras"]["texto"].startswith(txt.rstrip()), p.slug)


class CssCritica(unittest.TestCase):
    def test_estagio_inativo_fora_do_tab(self):
        self.assertIn("visibility: hidden", regra(".ideia-pin .ideia-estagio:not(.ativo)"))

    def test_estagios_nao_esticam(self):
        self.assertIn("flex: none", regra(".ideia-pin .ideia-estagios"))

    def test_por_tras_alinhado_a_esquerda(self):
        r = regra(".hero-por-tras pre")
        self.assertNotIn("justify-content: center", r)
        self.assertIn("mask-image", CSS[CSS.index(".hero-por-tras pre"):CSS.index(".hero-por-tras pre") + 900])
        self.assertNotIn("max-height: 7.5em", CSS)

    def test_capa_uniforme(self):
        r = regra(".projeto-tela img")
        self.assertIn("object-fit: contain", r)
        self.assertNotIn("object-position: top", r)



class CssAlvos(unittest.TestCase):
    def test_alvos_de_44px(self):
        for sel in (".link-seta", ".projeto-cartao h2 a", ".footer-col a"):
            self.assertIn("min-height: 44px", regra(sel), sel)

    def test_ancora_contato_cobre_o_titulo(self):
        self.assertIn("scroll-margin-top", regra(".cta-buttons#contato"))

    def test_h1_do_case_e_do_servico_menores(self):
        self.assertIn("clamp(2.2rem", regra(".case-topo h1"))
        self.assertIn("clamp(1.45rem", regra(".servico-h1"))



class ServicoClicavel(unittest.TestCase):
    def test_cartao_inteiro_e_link(self):
        self.assertIn("inset: 0", regra(".cartao-servico h3 a::after"))
        self.assertIn("position: relative", regra(".cartao-pessoa,\n.cartao-servico,\n.relacionado-card"))



class RitmoDesktop(unittest.TestCase):
    def test_h2_maior_e_respiro_variado(self):
        self.assertIn("3.6rem", regra("h2"))
        self.assertIn("padding-block: 128px", CSS)
        self.assertIn("padding-block: 80px", CSS)


if __name__ == "__main__":
    unittest.main()
