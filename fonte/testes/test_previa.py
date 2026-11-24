import os
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "bin" / "publicar-previa"


def rodar(*args, **env):
    e = {**os.environ, **env}
    return subprocess.run([str(SCRIPT), *args], cwd=REPO, env=e, capture_output=True, text=True, timeout=120)


class PublicarPreviaTest(unittest.TestCase):
    def test_existe_e_executavel(self):
        self.assertTrue(SCRIPT.is_file())
        self.assertTrue(os.access(SCRIPT, os.X_OK))

    def test_contem_a_trava_do_destino(self):
        t = SCRIPT.read_text("utf-8")
        self.assertIn("/var/www/alldevs-previa/", t)
        self.assertIn("destino inesperado", t)
        self.assertIn("Desfazer:", t)

    def test_ensaio_nao_toca_na_rede(self):
        r = rodar("--ensaio")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--dry-run", r.stdout)
        self.assertIn("/var/www/alldevs-previa/", r.stdout)

    def test_verifica_200_e_noindex_e_quota_o_destino(self):
        t = SCRIPT.read_text("utf-8")
        self.assertIn("printf %q", t)
        self.assertIn("noindex", t.split("rsync -a --delete -e")[1])
        self.assertIn("exit 1", t.split("rsync -a --delete -e")[1])

    def test_recusa_destino_fora_da_previa(self):
        for d in ("/var/www/outro/", "/var/www/alldevs-previa/../x/", "/var/www/alldevs-previa"):
            r = rodar("--ensaio", DEST=d)
            self.assertNotEqual(r.returncode, 0, d)
            self.assertIn("destino inesperado", r.stderr)


class BancadaMetasTest(unittest.TestCase):
    """rodar.mjs mede 360/430/1440 e o FPS da home com CPU 4x (texto do script; a medição é a própria bancada)."""

    def setUp(self):
        self.t = (REPO / "bancada" / "rodar.mjs").read_text("utf-8")

    def test_larguras(self):
        self.assertIn("[[360, 800], [430, 900], [1440, 900]]", self.t)
        self.assertIn("w === 360 || w === 430", self.t)

    def test_meta_de_fps_com_cpu_4x(self):
        self.assertIn("setCPUThrottlingRate", self.t)
        self.assertIn("fps >= 50", self.t)
        self.assertIn("fps:", self.t)


if __name__ == "__main__":
    unittest.main()
