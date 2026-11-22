import hashlib
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from alldevs import paginas
from testes.test_paginas import REPO, rodar

FONTES = ("robots.txt", "CNAME", "app-ads.txt")


def gerar_numa_copia(testcase) -> Path:
    tmp = tempfile.TemporaryDirectory()
    testcase.addCleanup(tmp.cleanup)
    raiz = Path(tmp.name)
    shutil.copytree(REPO / "fonte", raiz / "fonte", ignore=shutil.ignore_patterns("__pycache__"))
    for d in paginas.ESTATICOS:
        origem = REPO / d
        if origem.is_dir():
            shutil.copytree(origem, raiz / d)
        elif origem.is_file():
            shutil.copy2(origem, raiz / d)
    for n in FONTES:
        if (REPO / n).is_file():
            shutil.copy2(REPO / n, raiz / n)
    rc, _, err = rodar("--raiz", str(raiz))
    testcase.assertEqual(rc, 0, err)
    return raiz


def hashes(raiz: Path) -> dict:
    return {
        p.relative_to(raiz).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(raiz.rglob("*"))
        if p.is_file() and "fonte" not in p.relative_to(raiz).parts[:1]
    }


class TestDeterminismo(unittest.TestCase):
    def test_duas_execucoes_byte_a_byte(self):
        a, b = hashes(gerar_numa_copia(self)), hashes(gerar_numa_copia(self))
        self.assertIn("index.html", a)
        self.assertEqual(a, b)

    def test_saida_nao_depende_do_relogio(self):
        a = hashes(gerar_numa_copia(self))
        with mock.patch.dict(os.environ, {"SOURCE_DATE_EPOCH": "1"}), mock.patch.object(time, "time", return_value=42.0):
            b = hashes(gerar_numa_copia(self))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
