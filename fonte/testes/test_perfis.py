"""Perfis e história (Task 9): os dois perfis têm o mesmo peso, "Fizemos juntos" é o de /projetos/, a história entra byte a byte."""
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
    def perfil(self, slug):
        return ler(self.saida / slug / "index.html")

    def test_perfis_mesmo_peso(self):
        def estrutura(slug):
            txt = self.perfil(slug)
            return (re.findall(r'<section[^>]*data-secao="([^"]+)"', txt),
                    re.findall(r'<(?:section|img|ul|p|h1|h2|a)[^>]*class="([^"]+)"', txt))
        a, b = estrutura("caio"), estrutura("rosiel")
        self.assertEqual(a[0], b[0])
        self.assertEqual(a[0], ["apresentacao", "faz", "projetos", "contato"])
        # as mesmas classes; a única diferença é o link "Leia a história" (só quem tem link_historia)
        # (links externos e "Leia a história" só saem para quem tem o dado; hoje o Caio não tem links)
        solto = ("link-seta perfil-historia", "perfil-links")
        self.assertEqual([c for c in a[1] if c not in solto], [c for c in b[1] if c not in solto])
        for slug in PERFIS:
            txt = self.perfil(slug)
            self.assertIn('data-molde="perfil"', txt)
            self.assertNotIn("data-pessoa", txt)
            self.assertEqual(len(re.findall(r"<h1[ >]", txt)), 1)

    def test_foto_igual_nos_dois_e_com_a_proporcao_real(self):
        tamanhos = set()
        for p in self.dados.pessoas:
            img = re.search(r'<img class="perfil-foto"[^>]+>', self.perfil(p.slug)).group(0)
            w, h = (int(x) for x in re.search(r'width="(\d+)" height="(\d+)"', img).groups())
            rw, rh = _tamanho_webp(REPO / p.foto)
            self.assertEqual((w, h), (rw, rh), p.slug)
            tamanhos.add((w, h))
            self.assertNotIn('loading="lazy"', img)   # a foto é o LCP do perfil
            self.assertIn('fetchpriority="high"', img)
        self.assertEqual(len(tamanhos), 1)

    def test_fizemos_juntos_igual_nos_dois(self):
        da_lista = slugs_da_secao(ler(self.saida / "projetos/index.html"))
        self.assertEqual(da_lista, [p.slug for p in self.visiveis])
        for slug in PERFIS:
            sec = secao(self.perfil(slug), "projetos")
            self.assertRegex(sec, r"<h2[^>]*>[^<]*Fizemos juntos[^<]*</h2>")
            self.assertEqual(slugs_da_secao(sec), da_lista, slug)
            self.assertEqual(re.findall(r"<h3>", sec).__len__(), len(da_lista))

    def test_revelar_so_com_cartao_que_revela(self):
        for slug in PERFIS:
            txt = self.perfil(slug)
            self.assertEqual("/js/revelar.js" in txt, "data-revela-cartao" in txt, slug)

    def test_links_do_perfil_44px(self):
        css = ler(REPO / "css" / "site.css")
        i = css.index(".perfil-links a {")
        regra = css[i:css.index("}", i)]
        self.assertIn("display: inline-flex", regra)
        self.assertIn("align-items: center", regra)
        self.assertIn("min-height: 44px", regra)
        for token in re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", regra):
            self.fail(f"cor fora dos tokens: {token}")
        i = css.index(".perfil-historia {")
        self.assertIn("min-height: 44px", css[i:css.index("}", i)])

    def test_foto_sem_decoding_async_e_com_prioridade(self):
        for slug in PERFIS:
            img = re.search(r'<img class="perfil-foto"[^>]*>', self.perfil(slug)).group(0)
            self.assertNotIn("decoding", img)
            self.assertIn('fetchpriority="high"', img)

    def test_titulos_com_webfont_sem_ch(self):
        css = ler(REPO / "css" / "site.css")
        for sel in (".perfil-frase {", ".closing-title {"):
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

    def test_wa_do_perfil_com_origem(self):
        for slug in PERFIS:
            txt = self.perfil(slug)
            self.assertIn(f"%5Bsite%C2%B7perfil%C2%B7{slug}%5D", txt)
            self.assertIn(f"[site·perfil·{slug}]", unquote(secao(txt, "contato")))

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
