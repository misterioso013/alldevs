import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "_config.yml"
EXCLUIDOS = ["docs", "bancada", "fonte", "README.md"]


class PublicacaoTest(unittest.TestCase):
    def test_config_existe(self):
        self.assertTrue(CONFIG.is_file(), "_config.yml faltando: o Pages publicaria docs/bancada/fonte")

    def test_exclude_exato(self):
        texto = CONFIG.read_text("utf-8")
        linhas = [l.strip() for l in texto.splitlines() if l.strip() and not l.strip().startswith("#")]
        self.assertEqual(len(linhas), 1, linhas)
        m = re.fullmatch(r"exclude:\s*\[(.*)\]", linhas[0])
        self.assertIsNotNone(m, linhas[0])
        itens = [i.strip() for i in m.group(1).split(",")]
        self.assertEqual(itens, EXCLUIDOS)

    def test_sem_nojekyll(self):
        self.assertFalse((REPO / ".nojekyll").exists())


class BotaoPrimarioTest(unittest.TestCase):
    def _regra(self, seletor):
        css = (REPO / "css" / "site.css").read_text("utf-8")
        m = re.search(r"(?m)^" + re.escape(seletor) + r"\s*\{([^}]*)\}", css)
        self.assertIsNotNone(m, seletor)
        return m.group(1)

    def test_repouso_so_contorno(self):
        r = self._regra(".btn-primary")
        self.assertRegex(r, r"background:\s*transparent")
        self.assertRegex(r, r"color:\s*var\(--claro\)")
        self.assertRegex(r, r"border-color:\s*var\(--claro\)")

    def test_hover_e_foco_preenchem(self):
        r = self._regra(".btn-primary:hover,\n.btn-primary:focus-visible")
        self.assertRegex(r, r"background:\s*var\(--claro\)")
        self.assertRegex(r, r"color:\s*var\(--fundo\)")

    def test_sem_cor_nova(self):
        for sel in (".btn-primary", ".btn-primary:hover,\n.btn-primary:focus-visible"):
            self.assertNotRegex(self._regra(sel), r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")


if __name__ == "__main__":
    unittest.main()
