import json
import shutil
import tempfile
import unittest
from pathlib import Path

from alldevs import checagens
from testes.test_paginas import REPO

PROJETO_OCULTO = {
    "slug": "oculto", "nome": "Oculto", "tipo": "site", "situacao": "no ar", "ano": 2026,
    "resumo": "r", "problema": "p", "fizemos": [], "resultado": None, "stack": [], "link": "https://x.dev",
    "imagens": [], "destaque": False, "visivel": False, "atualizado": "2026-11-22",
}


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.raiz = Path(tmp.name)
        shutil.copytree(REPO / "fonte" / "dados", self.raiz / "fonte" / "dados")

    def escrever(self, rel, texto):
        p = self.raiz / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")

    def problemas(self):
        return checagens.checar(self.raiz)


class TestChecagens(Base):
    def test_limpo_nao_reprova(self):
        self.escrever("css/a.css", "a{color:var(--x)}\n")
        self.assertEqual(self.problemas(), [])

    def test_hex_fora_de_tokens_reprova(self):
        self.escrever("css/a.css", "a{\ncolor:#fff}\n")
        self.assertEqual(len(self.problemas()), 1)
        self.assertTrue(self.problemas()[0].startswith("css/a.css:2: "))

    def test_rgb_e_hsl_reprovam(self):
        self.escrever("js/a.js", "x='rgb(1,2,3)'\ny='hsl(1,2%,3%)'\n")
        self.assertEqual(len(self.problemas()), 2)

    def test_vendor_liberado(self):
        self.escrever("css/tokens.css", ":root{--a:#fff}\n")
        self.escrever("js/vendor/lib.js", "var c='#abcdef'\n")
        self.assertEqual(self.problemas(), [])

    def test_sem_excecoes_temporarias(self):
        self.assertEqual(checagens.EXCECOES_TEMPORARIAS, ())

    def test_css_antigo_nao_tem_mais_passe_livre(self):
        self.escrever("css/styles.css", "a{color:#fff}\n")
        self.assertEqual(self.problemas(), ["css/styles.css:1: cor fora dos tokens (#fff)"])

    def test_pastas_fora_do_site_ignoradas(self):
        self.escrever("docs/a.html", "Olá Rosiel #fff Playfair\n")
        self.assertEqual(self.problemas(), [])

    def test_ola_rosiel_reprova(self):
        self.escrever("a.html", "<p>Olá Rosiel</p>\n")
        self.assertEqual(self.problemas(), ["a.html:1: 'Olá Rosiel' proibido"])

    def test_wa_sem_text_reprova(self):
        self.escrever("a.html", '<a href="https://wa.me/558189477459">x</a>\n')
        self.assertEqual(self.problemas(), ["a.html:1: wa.me sem ?text="])

    def test_numero_errado_reprova(self):
        self.escrever("a.html", '<a href="https://wa.me/5511999999999?text=oi">x</a>\n')
        self.assertEqual(len(self.problemas()), 1)
        self.assertIn("número wa.me", self.problemas()[0])

    def test_wa_correto_passa(self):
        self.escrever("a.html", '<a href="https://wa.me/558189477459?text=oi">x</a>\n')
        self.assertEqual(self.problemas(), [])

    def test_proibido_reprova(self):
        self.escrever("css/a.css", "a{font-family: Playfair Display}\n")
        self.assertEqual(self.problemas(), ["css/a.css:1: fonte serifada vetada"])

    def test_proibido_ignora_maiuscula(self):
        self.escrever("css/a.css", "a{CURSOR: NONE}\n")
        self.assertEqual(len(self.problemas()), 1)

    def test_vetado_na_saida_reprova(self):
        self.escrever("fonte/dados/projetos.json", json.dumps([PROJETO_OCULTO]))
        self.escrever("projetos/oculto/index.html", "<p>x</p>\n")
        self.escrever("sitemap.xml", "<loc>https://all.dev.br/projetos/oculto/</loc>\n")
        self.assertEqual(self.problemas(), [
            "projetos/oculto/index.html:1: projeto invisível presente na saída",
            "sitemap.xml:1: projeto invisível no sitemap (oculto)",
        ])

    def test_entidade_e_ancora_nao_acusam(self):
        self.escrever("a.html", '<p>a&#160;b</p>\n<a href="#cafe">x</a>\n<i id="face"></i>\n<use href="url(#fff)">\n')
        self.assertEqual(self.problemas(), [])

    def test_hex_de_5_digitos_nao_acusa(self):
        self.escrever("css/a.css", "a{x:#abcde}\n")
        self.assertEqual(self.problemas(), [])

    def test_hex_de_4_6_8_digitos_acusam(self):
        self.escrever("css/a.css", "a{x:#abcd}\nb{x:#aabbcc}\nc{x:#aabbccdd}\n")
        self.assertEqual(len(self.problemas()), 3)

    def test_duas_cores_na_mesma_linha(self):
        self.escrever("css/a.css", "a{background:#fff;color:rgb(0,0,0)}\n")
        self.assertEqual(len(self.problemas()), 2)

    def test_wa_numero_com_sufixo_reprova(self):
        self.escrever("a.html", '<a href="https://wa.me/558189477459abc?text=oi">x</a>\n')
        self.assertEqual(len(self.problemas()), 1)
        self.assertIn("número wa.me", self.problemas()[0])

    def test_wa_com_mais_e_text_passa(self):
        self.escrever("a.html", '<a href="https://WA.me/+558189477459?text=oi">x</a>\n')
        self.assertEqual(self.problemas(), [])

    def test_wa_text_vazio_reprova(self):
        self.escrever("a.html", '<a href="https://wa.me/558189477459?text=">x</a>\n')
        self.assertEqual(self.problemas(), ["a.html:1: wa.me sem ?text="])

    def test_ola_rosiel_variantes(self):
        self.escrever("a.html", "OLÁ ROSIEL\nhref=?text=Ol%C3%A1%20Rosiel\nhref=?text=Ol%C3%A1+Rosiel\n")
        self.assertEqual(len(self.problemas()), 3)

    def test_repo_atual_limpo(self):
        self.assertEqual(checagens.checar(REPO), [])


if __name__ == "__main__":
    unittest.main()
