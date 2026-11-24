"""Serviços (Task 8): "Projetos de <tipo>" no fim, contato com origem, FAQ sem seta lida, sem selo de sócio."""
import re
import unittest
from pathlib import Path

from alldevs import dados as D
from testes.test_conteudo import Base, ler
from testes.test_paginas import TITULOS


def secao_projetos(txt):
    m = re.search(r'<section[^>]*data-secao="projetos-do-tipo"[^>]*>.*?</section>', txt, re.S)
    return m.group(0) if m else None


class TestServicos(Base):
    raiz_fonte = Path(__file__).resolve().parent.parent / "conteudo" / "servicos"

    def pagina(self, slug):
        return ler(self.saida / "servicos" / slug / "index.html")

    def test_servico_aponta_projetos_do_tipo(self):
        for s in self.dados.servicos:
            doc = self.pagina(s.slug)
            esperados = [p for p in self.visiveis if p.tipo == s.tipo]
            if not esperados:
                continue
            sec = secao_projetos(doc)
            self.assertIsNotNone(sec, s.slug)
            rotulo = D.TIPO_ROTULO[s.tipo].lower()
            self.assertRegex(sec, rf'<h2 class="titulo-revela">Projetos de {rotulo}</h2>', s.slug)
            slugs = re.findall(r'<article class="projeto-cartao" data-slug="([^"]+)" data-tipo="([^"]+)"', sec)
            self.assertEqual(slugs, [(p.slug, s.tipo) for p in esperados], s.slug)
            self.assertNotIn("Ver todos os projetos", sec, s.slug)
            for p in esperados:
                self.assertIn(f'href="/projetos/{p.slug}/"', sec, s.slug)
            self.assertEqual(len(re.findall(r"<h3", sec)), len(esperados), s.slug)

    def test_servico_sem_projeto_do_tipo_mostra_link_geral(self):
        vazios = [s for s in self.dados.servicos if not any(p.tipo == s.tipo for p in self.visiveis)]
        self.assertTrue(vazios)   # hoje: os dois de automação
        for s in vazios:
            sec = secao_projetos(self.pagina(s.slug))
            self.assertIsNotNone(sec, s.slug)
            self.assertIn("Projetos de automação", sec)
            self.assertNotIn("projeto-cartao", sec, s.slug)
            self.assertRegex(sec, r'<a href="/projetos/" class="link-seta">Ver todos os projetos</a>', s.slug)

    def test_termina_com_projetos_e_contato_com_origem(self):
        for slug in TITULOS:
            doc = self.pagina(slug)
            main = doc[doc.index("<main"):doc.index("</main>")]
            self.assertLess(main.index("servicos-relacionados"), main.index('data-secao="projetos-do-tipo"'), slug)
            fim = main[main.index('data-secao="projetos-do-tipo"'):]
            self.assertIn("https://wa.me/", fim, slug)
            self.assertIn(f"%5Bsite%C2%B7servico%C2%B7{slug}%5D", fim, slug)
            self.assertIn("mailto:", fim, slug)
            self.assertEqual(doc.count('id="contato"'), 1, slug)   # o do .servico-cta; o final não repete o id

    def test_faq_chevron_escondido_dos_leitores(self):
        for slug in TITULOS:
            svgs = re.findall(r'<svg[^>]*class="faq-chevron"[^>]*>', self.pagina(slug))
            self.assertTrue(svgs, slug)
            for svg in svgs:
                self.assertIn('aria-hidden="true"', svg, slug)
                self.assertIn('focusable="false"', svg, slug)

    def test_conteudo_de_servico_intacto(self):
        # o HTML de conteúdo entra byte a byte, só com o marcador trocado e o chevron marcado como decorativo
        for slug in TITULOS:
            fonte = ler(self.raiz_fonte / f"{slug}.html")
            antes, _, depois = fonte.partition("<!--contato-->")
            antes = antes.replace('<svg class="faq-chevron" ', '<svg class="faq-chevron" aria-hidden="true" focusable="false" ')
            depois = depois.replace('<svg class="faq-chevron" ', '<svg class="faq-chevron" aria-hidden="true" focusable="false" ')
            doc = self.pagina(slug)
            self.assertIn(antes, doc, slug)
            self.assertIn(depois, doc, slug)

    def test_sem_selo_quem_toca(self):
        socios = [p.nome for p in self.dados.pessoas] + [p.slug for p in self.dados.pessoas]
        for slug in TITULOS:
            doc = self.pagina(slug)
            for proibido in ("selo-caio", "selo-rosiel", "data-autor", "quem_toca"):
                self.assertNotIn(proibido, doc, slug)
            main = doc[doc.index("<main"):doc.index("</main>")]
            for nome in socios:
                self.assertNotRegex(main, rf"\b{re.escape(nome)}\b", f"{slug}: {nome}")

    def test_sem_h1_extra_e_h2_do_molde_revela(self):
        for slug in TITULOS:
            doc = self.pagina(slug)
            self.assertEqual(doc.count("<h1"), 1, slug)
            self.assertRegex(secao_projetos(doc), r'<h2 class="titulo-revela">', slug)

    def test_secoes_do_molde_tem_nome_acessivel(self):
        for slug in TITULOS:
            doc = self.pagina(slug)
            main = doc[doc.index("<main"):doc.index("</main>")]
            ini = main.index('<section class="projetos-do-tipo"')
            for m in re.finditer(r"<section\b([^>]*)>(.*?)</section>", main[ini:], re.S):
                self.assertTrue("<h2" in m.group(2) or "aria-label=" in m.group(1), f"{slug}: {m.group(1)}")
            self.assertIn('<section class="contato" data-secao="contato" aria-label="Contato">', doc, slug)

    def test_trilha_semantica(self):
        for slug in TITULOS:
            doc = self.pagina(slug)
            self.assertIn('<nav class="breadcrumb" aria-label="Trilha">', doc, slug)
            self.assertNotIn('<div class="breadcrumb"', doc, slug)
            self.assertEqual(doc.count('<span class="breadcrumb-sep" aria-hidden="true">'), 2, slug)
            self.assertIn('<span class="breadcrumb-current" aria-current="page">', doc, slug)

    def test_nenhum_svg_sem_aria_hidden_no_site(self):
        for arq in sorted(self.saida.rglob("*.html")):
            for m in re.finditer(r"<svg\b[^>]*>", ler(arq)):
                self.assertIn('aria-hidden="true"', m.group(0), f"{arq}: {m.group(0)[:80]}")


if __name__ == "__main__":
    unittest.main()
