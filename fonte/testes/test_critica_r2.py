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


class MenuESocios(unittest.TestCase):
    def test_cabecalho_tem_socios_e_nao_caio_rosiel(self):
        c = (REPO / "fonte/modelos/cabecalho.html").read_text(encoding="utf-8")
        self.assertIn('<a href="/#quem-somos">Sócios</a>', c)
        self.assertNotIn("/caio/", c)
        self.assertNotIn("/rosiel/", c)


class SemPerfisDosSocios(unittest.TestCase):
    """Decisão do Caio (24/11): nada que nos divida. /caio/ e /rosiel/ saíram; os cartões só levam foto, nome e 'Sócio do estúdio.'"""
    PAGINAS = ["index.html", *(f"{d}/{n}/index.html" for d, ns in (
        ("projetos", ("", "amott", "cgflix-lite", "fakly", "heisuca", "prosup", "sendany")),
        ("servicos", ("aplicativo-mobile-react-native", "automacoes-integracoes-api", "bots-whatsapp-automacao",
                      "criacao-de-sites-institucionais", "desenvolvimento-mvp-startups", "landing-page-conversao"))) for n in ns)]

    def textos(self):
        for rel in self.PAGINAS:
            arq = REPO / rel.replace("//", "/")
            self.assertTrue(arq.is_file(), rel)
            yield rel, arq.read_text(encoding="utf-8")

    def test_paginas_dos_socios_nao_existem(self):
        self.assertFalse((REPO / "caio").exists())
        self.assertFalse((REPO / "rosiel").exists())
        self.assertFalse((REPO / "fonte/modelos/perfil.html").exists())
        mapa = (REPO / "sitemap.xml").read_text(encoding="utf-8")
        for u in ("/caio/", "/rosiel/"):
            self.assertNotIn(u, mapa)
            self.assertNotIn(u, (REPO / "assets/paleta.json").read_text(encoding="utf-8"))

    def test_nenhuma_pagina_liga_para_os_perfis_nem_tem_rotulo_ou_frase(self):
        proibidos = ("/caio/", "/rosiel/", "Ver perfil", "caio · infraestrutura", "rosiel · produto",
                     "Cuida da infraestrutura", "Transformo ideia em produto")
        for rel, txt in self.textos():
            for x in proibidos:
                self.assertNotIn(x, txt, f"{rel}: {x}")

    def test_cartoes_so_com_foto_nome_e_socio_do_estudio(self):
        txt = (REPO / "index.html").read_text(encoding="utf-8")
        cartoes = re.findall(r'<article class="cartao-pessoa".*?</article>', txt, re.S)
        self.assertEqual(len(cartoes), 2)
        for c in cartoes:
            self.assertEqual(re.findall(r"<(\w+)", c)[1:], ["img", "h3", "p"])
            self.assertIn("<p>Sócio do estúdio.</p>", c)
            self.assertNotIn("<a ", c)

    def test_rodape_e_cabecalho_com_socios(self):
        for rel, txt in self.textos():
            self.assertEqual(txt.count('<a href="/#quem-somos">Sócios</a>'), 2, rel)   # cabeçalho e rodapé


class SemHistoriaNemDivisao(unittest.TestCase):
    """Decisão do Caio (24/11): a História saiu; historia.html é só o redirecionamento para /#quem-somos;
    nada de cargo, rede social nem nome de sócio fora de 'Quem somos'."""
    SEM_REDIRECT = SemPerfisDosSocios.PAGINAS

    def test_menu_e_rodape_sem_historia(self):
        for rel in self.SEM_REDIRECT:
            txt = (REPO / rel).read_text(encoding="utf-8")
            self.assertNotIn("historia.html", txt, rel)
            self.assertNotIn(">História<", txt, rel)
        for molde in ("cabecalho", "rodape"):
            self.assertNotIn("historia", (REPO / f"fonte/modelos/{molde}.html").read_text(encoding="utf-8"))

    def test_historia_so_redireciona(self):
        txt = (REPO / "historia.html").read_text(encoding="utf-8")
        self.assertIn('<meta http-equiv="refresh" content="0; url=/#quem-somos">', txt)
        self.assertIn('<link rel="canonical" href="https://all.dev.br/#quem-somos">', txt)
        self.assertIn('<meta name="robots" content="noindex">', txt)
        self.assertEqual(re.findall(r"<a [^>]*>(.*?)</a>", txt), ["Quem somos"])
        self.assertIn('<a href="/#quem-somos">', txt)
        self.assertNotIn("<script", txt)
        self.assertNotIn("historia", (REPO / "sitemap.xml").read_text(encoding="utf-8"))
        for rel in ("fonte/conteudo/historia.html", "fonte/modelos/historia.html", "assets/og/historia.png"):
            self.assertFalse((REPO / rel).exists(), rel)

    def test_sem_cargo_nem_same_as_nem_papel(self):
        home = (REPO / "index.html").read_text(encoding="utf-8")
        blocos = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', home, re.S).group(1))
        pessoas = [b for b in blocos if b.get("@type") == "Person"]
        self.assertEqual([p["name"] for p in pessoas], ["Caio Guerras", "Rosiel Victor"])
        for p in pessoas:
            self.assertEqual(set(p), {"@context", "@type", "@id", "name", "worksFor"}, p)
        for rel in self.SEM_REDIRECT:
            txt = (REPO / rel).read_text(encoding="utf-8")
            self.assertNotIn("jobTitle", txt, rel)
            self.assertNotIn("sameAs", txt, rel)

    def test_nome_de_socio_so_em_quem_somos(self):
        for rel in self.SEM_REDIRECT:
            txt = (REPO / rel).read_text(encoding="utf-8")
            txt = re.sub(r'<script type="application/ld\+json">.*?</script>', "", txt, flags=re.S)   # JSON-LD só com `name`
            txt = re.sub(r'<section[^>]*id="quem-somos".*?</section>', "", txt, flags=re.S)
            txt = txt.replace("rosielvictor.dev@gmail.com", "")   # o ENDEREÇO do e-mail fica (decisão do Caio, 24/11)
            for nome in ("Caio", "Rosiel"):
                self.assertNotIn(nome, txt, f"{rel}: {nome}")
                self.assertNotIn(nome.lower() + "-", txt.lower().replace("/assets/images/", ""), rel)

    def test_dados_sem_papel_nem_links_nem_perfil(self):
        for p in json.loads((REPO / "fonte/dados/pessoas.json").read_text(encoding="utf-8")):
            self.assertEqual(set(p), {"slug", "nome", "foto", "cor", "atualizado"})
        est = json.loads((REPO / "fonte/dados/estudio.json").read_text(encoding="utf-8"))
        self.assertNotIn("perfil", est["mensagens"])
