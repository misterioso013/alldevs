"""Projetos ForjaDev e Huntar (24/11): entram em /projetos/, ganham case e aparecem nos serviços do tipo, e o ForjaDev substitui o SendAny na home."""
import re

from testes.test_conteudo import Base, ler

NOVOS = {"forjadev": ("ForjaDev", "site", "https://www.forjadev.com.br"),
         "huntar": ("Huntar", "produto", "https://www.huntar.com.br")}
SERVICO_DO_TIPO = {"site": "criacao-de-sites-institucionais", "produto": "desenvolvimento-mvp-startups"}


def slugs_dos_cartoes(txt):
    return re.findall(r'<article class="projeto-cartao" data-slug="([a-z0-9-]+)" data-tipo="([a-z]+)"', txt)


class TestNovosProjetos(Base):
    def test_cartoes_em_projetos(self):
        cartoes = slugs_dos_cartoes(ler(self.saida / "projetos/index.html"))
        for slug, (_, tipo, _) in NOVOS.items():
            self.assertIn((slug, tipo), cartoes)
        self.assertEqual(len(cartoes) % 2, 0)   # 2 colunas iguais a 1024+: grade fecha sem buraco

    def test_pagina_do_case(self):
        for slug, (nome, _, link) in NOVOS.items():
            txt = ler(self.saida / f"projetos/{slug}/index.html")
            self.assertIn("<h1", txt)
            self.assertIn(nome, txt)
            self.assertIn(f'href="{link}"', txt)
            self.assertIn(f"/assets/images/{slug}-2.webp", txt)
            self.assertIn(f"/assets/images/{slug}-3.webp", txt)
            self.assertIn(f"/assets/og/{slug}.png", txt)

    def test_home_troca_sendany_por_forjadev(self):
        """24/11: o ForjaDev entra na home no lugar do SendAny (a home ordena por nome); o Huntar fica só em /projetos/."""
        home = ler(self.saida / "index.html")
        cartoes = [s for s, _ in slugs_dos_cartoes(home)]
        self.assertEqual(cartoes, ["amott", "cgflix-lite", "fakly", "forjadev", "heisuca", "prosup"])
        self.assertIn("sendany", [s for s, _ in slugs_dos_cartoes(ler(self.saida / "projetos/index.html"))])

    def test_nos_servicos_do_tipo(self):
        for slug, (_, tipo, _) in NOVOS.items():
            txt = ler(self.saida / f"servicos/{SERVICO_DO_TIPO[tipo]}/index.html")
            fim = re.search(r'data-secao="projetos-do-tipo".*?</section>', txt, re.S).group(0)
            self.assertIn((slug, tipo), slugs_dos_cartoes(fim))

    def test_og_existe_no_repo(self):
        from testes.test_conteudo import REPO
        for slug in NOVOS:
            self.assertTrue((REPO / f"assets/og/{slug}.png").is_file(), slug)

    def test_no_sitemap(self):
        sm = ler(self.saida / "sitemap.xml")
        for slug in NOVOS:
            self.assertIn(f"/projetos/{slug}/</loc>", sm)
