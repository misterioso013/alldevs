"""Projetos e cases (Task 7): filtro por tipo, ordem dos blocos do case, palco, loja, resultado e contato com origem."""
import dataclasses
import re
import unittest

from alldevs import dados as D
from alldevs import seo
from testes.test_conteudo import Base, ler

ORDEM_CASE = ["topo", "problema", "fizemos", "por-tras", "resultado", "stack", "link", "contato"]


def secoes_do_case(txt):
    return re.findall(r'data-secao="([a-z-]+)"', txt)


class TestListaDeProjetos(Base):
    def setUp(self):
        self.txt = ler(self.saida / "projetos/index.html")

    def test_filtro_so_tipos_com_projeto(self):
        filtro = re.search(r'<div class="filtro-tipos"[^>]*>.*?</div>', self.txt, re.S).group(0)
        botoes = re.findall(r'<button[^>]*data-tipo="([^"]+)"[^>]*>([^<]+)</button>', filtro)
        tipos = [t for t in D.TIPO_ROTULO if any(p.tipo == t for p in self.visiveis)]
        self.assertEqual(botoes, [("todos", "Todos")] + [(t, D.TIPO_ROTULO[t]) for t in tipos])
        self.assertNotIn("automacao", [b[0] for b in botoes])   # nenhum projeto desse tipo: sem botão
        self.assertIn('data-tipo="todos"', filtro)
        self.assertRegex(filtro, r'data-tipo="todos"[^>]*aria-pressed="true"')
        for t, _ in botoes[1:]:
            self.assertRegex(filtro, rf'data-tipo="{t}"[^>]*aria-pressed="false"')

    def test_filtro_sem_pessoa(self):
        main = self.txt[self.txt.index("<main"):self.txt.index("</main>")]
        self.assertNotRegex(main, r'data-filtro|data-pessoa')
        self.assertNotRegex(main.lower(), r"\b(caio|rosiel)\b")

    def test_sem_js_filtro_hidden_e_todos_listados(self):
        # o gerador entrega o filtro oculto (o site.js o abre); sem JS a lista inteira aparece, sem nenhum cartão hidden
        self.assertRegex(self.txt, r'<div class="filtro-tipos"[^>]*\bhidden\b')
        achados = re.findall(r'<article class="projeto-cartao"([^>]*)>', self.txt)
        self.assertEqual([re.search(r'data-slug="([^"]+)"', a).group(1) for a in achados], [p.slug for p in self.visiveis])
        for a, p in zip(achados, self.visiveis):
            self.assertNotRegex(a, r"\bhidden\b")
            self.assertIn(f'data-tipo="{p.tipo}"', a)

    def test_cartao_da_home_com_nivel_2(self):
        for p in self.visiveis:
            self.assertRegex(self.txt, rf'<h2><a href="/projetos/{p.slug}/">')
        self.assertEqual(len(re.findall(r"<h1\b", self.txt)), 1)

    def test_revelar_so_com_cartao_de_revelacao(self):
        self.assertEqual(self.txt.count('src="/js/revelar.js"'), 1)
        self.assertIn("data-revela-cartao", self.txt)


class TestCase(Base):
    def case(self, slug):
        return ler(self.saida / "projetos" / slug / "index.html")

    def test_case_ordem_dos_blocos(self):
        for slug in ("heisuca", "cgflix-lite"):   # os que têm tudo: por trás, resultado, stack, loja
            p = next(x for x in self.visiveis if x.slug == slug)
            self.assertIsNotNone(p.resultado)
            sec = [s for s in secoes_do_case(self.case(slug)) if s in ORDEM_CASE]
            self.assertEqual(sec, ORDEM_CASE, slug)
        # as capturas ficam na outra coluna, depois do texto no HTML
        txt = self.case("heisuca")
        self.assertGreater(txt.index('data-secao="imagens"'), txt.index('data-secao="link"'))
        self.assertLess(txt.index('data-secao="imagens"'), txt.index('data-secao="contato"'))

    def test_case_coluna_de_texto_e_a_das_telas(self):
        txt = self.case("heisuca")
        self.assertIn('class="case-texto"', txt)
        self.assertRegex(txt, r'<section class="case-telas" data-secao="imagens"')

    def test_case_sem_por_tras_sem_palco(self):
        sem = [p for p in self.visiveis if not p.por_tras]
        self.assertTrue(sem)
        for p in sem:
            txt = self.case(p.slug)
            self.assertNotIn('data-secao="por-tras"', txt)
            self.assertNotIn("data-revela-cartao", txt)
            self.assertNotIn("revelar.js", txt)
            self.assertNotIn("cartao-por-tras", txt)

    def test_case_com_por_tras_tem_palco_e_revelar(self):
        for p in (x for x in self.visiveis if x.por_tras):
            txt = self.case(p.slug)
            palco = re.search(r'<section[^>]*data-secao="por-tras".*?</section>', txt, re.S).group(0)
            self.assertIn("data-revela-cartao", palco)
            self.assertRegex(palco, r'<figure class="projeto-tela case-palco"')
            self.assertRegex(palco, r'<div class="cartao-por-tras" aria-hidden="true">')
            self.assertIn("<h2>Por trás</h2>", palco)
            self.assertEqual(txt.count('<script src="/js/revelar.js" defer></script>'), 1, p.slug)
            self.assertIn(p.por_tras["origem"], palco)

    def test_palco_mais_linhas_que_o_cartao(self):
        txt = self.case("heisuca")
        palco = re.search(r'<section[^>]*data-secao="por-tras".*?</section>', txt, re.S).group(0)
        home = ler(self.saida / "index.html")
        cart = re.search(r'<article class="projeto-cartao"[^>]*data-slug="heisuca".*?</article>', home, re.S).group(0)
        self.assertGreater(palco.count("\n"), cart.count("\n"))

    def test_case_loja_com_legenda_e_link_play(self):
        for slug in ("heisuca", "cgflix-lite"):
            p = next(x for x in self.visiveis if x.slug == slug)
            txt = self.case(slug)
            telas = re.search(r'<section[^>]*data-secao="imagens".*?</section>', txt, re.S).group(0)
            self.assertIn("<figcaption>Na Google Play</figcaption>", telas)
            self.assertEqual(telas.count("<img"), len(p.imagens))
            link = re.search(r'<p class="case-link"[^>]*data-secao="link">(.*?)</p>', txt, re.S).group(1)
            self.assertIn(f'href="{p.loja}"', link)
            self.assertIn('target="_blank" rel="noopener"', link)
            self.assertIn('<span class="so-leitor"> (abre em nova aba)</span>', link)
            self.assertEqual(link.count("<a "), 1)   # loja e link iguais: um botão só

    def test_case_com_link_e_sem_loja_ve_no_ar(self):
        txt = self.case("amott")
        self.assertNotIn("Na Google Play", txt)
        self.assertRegex(txt, r'href="https://amott\.docaio\.com\.br" target="_blank" rel="noopener"[^>]*>Ver amott no ar'
                         r'<span class="so-leitor"> \(abre em nova aba\)</span>')

    def test_capturas_de_loja_estreitas_e_sem_ampliar(self):
        for slug in ("heisuca", "cgflix-lite"):
            for w in re.findall(r'<img[^>]*width="(\d+)"', re.search(
                    r'<section[^>]*data-secao="imagens".*?</section>', self.case(slug), re.S).group(0)):
                self.assertLessEqual(int(w), 540, slug)

    def test_resultado_omitido_quando_none(self):
        for p in self.visiveis:
            txt = self.case(p.slug)
            self.assertEqual(p.resultado is None, "Resultado" not in txt, p.slug)
            self.assertEqual(p.resultado is None, 'data-secao="resultado"' not in txt, p.slug)

    def test_wa_do_case_com_origem(self):
        for p in self.visiveis:
            self.assertIn(f"%5Bsite%C2%B7case%C2%B7{p.slug}%5D", self.case(p.slug), p.slug)

    def test_json_ld_case_creator_organizacao(self):
        for p in self.visiveis:
            self.assertEqual(seo.json_ld_case(p, self.dados)["creator"], {"@id": seo.ID_ORGANIZACAO})
            self.assertIn(f'"creator": {{"@id": "{seo.ID_ORGANIZACAO}"}}', self.case(p.slug))

    def test_case_sem_socio(self):
        for p in self.visiveis:
            txt = self.case(p.slug)
            main = txt[txt.index("<main"):txt.index("</main>")]
            self.assertNotRegex(main.lower(), r"\b(caio|rosiel)\b", p.slug)


class TestCss(unittest.TestCase):
    def test_sticky_so_no_desktop_e_filtro_hidden(self):
        from testes.test_paginas import REPO
        css = ler(REPO / "css/site.css")
        m = re.search(r"@media \(min-width: 1024px\)[^{]*\{[^@]*?\.case-texto\s*\{[^}]*position: sticky", css, re.S)
        self.assertTrue(m, "sticky do .case-texto só a partir de 1024 px")
        self.assertRegex(css, r"\.projeto-cartao\[hidden\]\s*\{\s*display: none")
        self.assertRegex(css, r"\.filtro-tipos button\s*\{[^}]*min-height: 44px")


if __name__ == "__main__":
    unittest.main()
