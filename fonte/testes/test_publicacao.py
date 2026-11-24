import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "_config.yml"
EXCLUIDOS = ["docs", "bancada", "bin", "fonte", "README.md"]


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


class BotoesTest(unittest.TestCase):
    """Botões da identidade v2: .btn-cheio (roxo) e .btn-linha (contorno), sem cor solta."""

    def _regra(self, seletor):
        css = (REPO / "css" / "site.css").read_text("utf-8")
        m = re.search(r"(?m)^" + re.escape(seletor) + r"\s*\{([^}]*)\}", css)
        self.assertIsNotNone(m, seletor)
        return m.group(1)

    def test_cheio_em_repouso_usa_roxo(self):
        r = self._regra(".btn-cheio")
        self.assertRegex(r, r"background:\s*var\(--roxo\)")
        self.assertRegex(r, r"color:\s*var\(--texto\)")

    def test_linha_em_repouso_so_contorno(self):
        r = self._regra(".btn-linha")
        self.assertRegex(r, r"background:\s*transparent")
        self.assertRegex(r, r"border-color:\s*var\(--texto-2\)")

    def test_hover_e_foco_mudam_o_botao(self):
        self.assertRegex(self._regra(".btn-cheio:hover,\n.btn-cheio:focus-visible"), r"background:\s*var\(--roxo-claro\)")
        self.assertRegex(self._regra(".btn-linha:hover,\n.btn-linha:focus-visible"), r"color:\s*var\(--laranja-claro\)")

    def test_sem_cor_nova(self):
        for sel in (".btn-cheio", ".btn-linha", ".btn-cheio:hover,\n.btn-cheio:focus-visible", ".btn-linha:hover,\n.btn-linha:focus-visible"):
            self.assertNotRegex(self._regra(sel), r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")


if __name__ == "__main__":
    unittest.main()
