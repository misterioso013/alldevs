import unittest
from pathlib import Path

from alldevs.modelos import Seguro, esc, render

RAIZ_FONTE = Path(__file__).resolve().parent.parent
SLUGS = [
    "aplicativo-mobile-react-native",
    "automacoes-integracoes-api",
    "bots-whatsapp-automacao",
    "criacao-de-sites-institucionais",
    "desenvolvimento-mvp-startups",
    "landing-page-conversao",
]


class TestModelos(unittest.TestCase):
    def test_render_escapa_texto(self):
        out = render("base", titulo="<b>x</b>", descricao="d", canonical="c", css=Seguro(""), corpo=Seguro(""))
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", out)
        self.assertNotIn("<b>x</b>", out)

    def test_render_mantem_seguro(self):
        out = render("base", titulo="t", descricao="d", canonical="c", css=Seguro(""), corpo=Seguro("<p>oi</p>"))
        self.assertIn("<p>oi</p>", out)
        self.assertIsInstance(out, Seguro)
        self.assertIs(esc(Seguro("<i>")).__class__, Seguro)
        self.assertEqual(esc("<i>"), "&lt;i&gt;")

    def test_campo_faltando_e_erro(self):
        with self.assertRaises(KeyError):
            render("base", titulo="t")

    def test_conteudo_migrado_existe(self):
        for slug in SLUGS:
            p = RAIZ_FONTE / "conteudo" / "servicos" / f"{slug}.html"
            self.assertTrue(p.is_file(), slug)
            self.assertTrue(p.read_text(encoding="utf-8").strip(), slug)
        h = RAIZ_FONTE / "conteudo" / "historia.html"
        self.assertTrue(h.read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    unittest.main()
