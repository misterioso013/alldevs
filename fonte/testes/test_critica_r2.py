"""Crítica externa, rodada 2: hierarquia dos projetos, Quem somos, seções densas, História, print do Heisuca."""
import json
import re
import unittest

from testes.test_paginas import REPO

CSS = (REPO / "css" / "site.css").read_text(encoding="utf-8")
HOME_MOLDE = (REPO / "fonte" / "modelos" / "home.html").read_text(encoding="utf-8")
JS = (REPO / "js" / "site.js").read_text(encoding="utf-8")


def desktop():
    """Só o que está nos blocos @media (min-width: 1024px) do CSS."""
    return "\n".join(re.findall(r"@media \(min-width: 1024px\)\s*\{(.*?)\n\}", CSS, re.S))


def regras(seletor_re, texto=None):
    texto = CSS if texto is None else texto
    return [m.group(1) for m in re.finditer(seletor_re + r"\s*\{([^}]*)\}", texto)]


class ProjetosAssimetricos(unittest.TestCase):
    def test_primeiro_cartao_destaca_e_a_trinca_fecha(self):
        d = desktop()
        spans = {}
        for k in range(1, 7):
            corpo = " ".join(regras(r"[^{}]*\.grade-projetos\s*>\s*\.projeto-cartao:nth-child\(6n\s*\+\s*%d\)[^{}]*" % k, d))
            m = re.search(r"grid-column:\s*span\s*(\d+)", corpo)
            self.assertIsNotNone(m, f"cartão 6n+{k} sem span a 1024")
            spans[k] = int(m.group(1))
        # cada fileira soma 12 colunas: sem buraco com 6 projetos
        self.assertEqual(spans[1] + spans[2], 12)
        self.assertEqual(spans[3] + spans[4], 12)
        self.assertEqual(spans[5] + spans[6], 12)
        self.assertNotEqual(spans[1], spans[2])   # assimétrico

    def test_filtro_nao_deixa_buraco(self):
        self.assertRegex(d_ou(r"\.grade-projetos\[data-lista-projetos\]"), r"grid-auto-flow:\s*dense")


def d_ou(seletor):
    return " ".join(regras(r"[^{}]*" + seletor + r"[^{}]*"))


class QuemSomos(unittest.TestCase):
    def test_ordem_fixa_no_html(self):
        self.assertNotIn("data-sortear", HOME_MOLDE)

    def test_retrato_de_320_a_360_com_texto_ao_lado(self):
        d = desktop()
        corpo = " ".join(regras(r"[^{}]*\.cartao-pessoa[^{}]*", d))
        m = re.search(r"grid-template-columns:\s*(\d+)px\s+minmax\(0,\s*1fr\)", corpo)
        self.assertIsNotNone(m)
        self.assertTrue(320 <= int(m.group(1)) <= 360)

    def test_perfil_foto_na_largura_da_coluna(self):
        corpo = regras(r"\.perfil-foto")[0]   # a regra base, a de 430 px
        self.assertRegex(corpo, r"width:\s*100%")
        self.assertNotIn("360px", corpo)


class SecoesDensas(unittest.TestCase):
    def test_tecnologias_em_colunas(self):
        self.assertRegex(" ".join(regras(r"[^{}]*\.tec-grupos[^{}]*", desktop())), r"grid-template-columns:\s*repeat\((3|auto-fit)")

    def test_faq_titulo_a_esquerda_perguntas_a_direita(self):
        corpo = " ".join(regras(r"[^{}]*\.faq-home[^{}]*", desktop()))
        self.assertRegex(corpo, r"grid-template-columns")

    def test_contato_em_faixa_de_largura_total(self):
        corpo = " ".join(regras(r"[^{}]*main\s*>\s*#contato[^{}]*", desktop()))
        self.assertIn("100vmax", corpo)
        self.assertIn("var(--fundo-2)", corpo)

    def test_manifesto_nao_fica_na_metade_esquerda(self):
        corpo = " ".join(regras(r"[^{}]*\.horizontal-story__text[^{}]*", desktop()))
        m = re.search(r"max-width:\s*(\d+(?:\.\d+)?)rem", corpo)
        self.assertIsNotNone(m)
        self.assertGreaterEqual(float(m.group(1)), 64)

    def test_brilho_roxo_nao_flutua(self):
        corpo = " ".join(regras(r"\.hist-hero-bg"))
        self.assertNotIn("72% 45%", corpo)   # a bolinha solta à direita
        self.assertIn("60% 40%", corpo)


class Heisuca(unittest.TestCase):
    def test_print_do_app_uma_vez_so(self):
        dados = json.loads((REPO / "fonte/dados/projetos.json").read_text(encoding="utf-8"))
        lista = dados["projetos"] if isinstance(dados, dict) else dados
        proj = next(p for p in lista if p["slug"] == "heisuca")
        self.assertNotIn("assets/loja/heisuca-2.webp", proj["imagens"])

    def test_imagens_da_coluna_direita_mesma_largura(self):
        corpo = " ".join(regras(r"[^{}]*\.case-loja\s+img[^{}]*"))
        self.assertRegex(corpo, r"width:\s*min\(100%,\s*540px\)")


if __name__ == "__main__":
    unittest.main()
