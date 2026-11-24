import unittest
from pathlib import Path

from alldevs import dados as D
from alldevs.contato import TELEGRAM, codigo_origem, link_email, link_whatsapp, mensagem

RAIZ = Path(__file__).resolve().parent.parent.parent
# carregar() exige todos os JSON; o real ainda não os tem, então monta só o estúdio.
est = D._montar(D.Estudio, D._ler(RAIZ / "fonte" / "dados" / "estudio.json"), "estudio.json")

HOME_WA = ("https://wa.me/558189477459?text=Ol%C3%A1%2C%20AllDevs%21%20Vim%20pelo%20site%20e%20quero%20"
           "conversar%20sobre%20um%20projeto.%20%5Bsite%C2%B7home%5D")
HOME_MAIL = "mailto:rosielvictor.dev@gmail.com?subject=Or%C3%A7amento%20%5Bsite%C2%B7home%5D"


class TestContato(unittest.TestCase):
    def test_whatsapp_home(self):
        self.assertEqual(link_whatsapp("558189477459", mensagem(est, "home")), HOME_WA)

    def test_email_home(self):
        self.assertEqual(link_email(est.email, codigo_origem("home")), HOME_MAIL)

    def test_servico_tem_asterisco_codificado(self):
        url = link_whatsapp("558189477459", mensagem(est, "servico", "Landing page", "landing-page-conversao"))
        self.assertIn("%2ALanding%20page%2A", url)
        self.assertNotIn("+", url)
        self.assertNotIn("·", url)

    def test_codigo_sem_slug_e_erro(self):
        self.assertRaises(ValueError, codigo_origem, "case")

    def test_codigos(self):
        self.assertEqual(codigo_origem("home"), "site·home")
        self.assertEqual(codigo_origem("case", "alfa"), "site·case·alfa")

    def test_tipo_desconhecido(self):
        self.assertRaises(ValueError, codigo_origem, "xyz")
        self.assertRaises(ValueError, mensagem, est, "xyz")

    def test_mensagens_textos(self):
        self.assertEqual(mensagem(est, "home"),
                         "Olá, AllDevs! Vim pelo site e quero conversar sobre um projeto. [site·home]")
        self.assertEqual(mensagem(est, "case", "Alfa", "alfa"),
                         "Olá, AllDevs! Vi o case do *Alfa* e quero algo parecido. [site·case·alfa]")
        self.assertRaises(ValueError, codigo_origem, "perfil", "ana")   # o tipo perfil saiu em 24/11

    def test_sem_alvo_e_erro(self):
        for tipo in ("servico", "case"):
            self.assertRaises(ValueError, mensagem, est, tipo, None, "x")

    def test_telegram(self):
        self.assertEqual(TELEGRAM, est.telegram)


if __name__ == "__main__":
    unittest.main()
