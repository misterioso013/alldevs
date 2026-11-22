import dataclasses
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from alldevs import dados as D

FIXTURE = Path(__file__).parent / "fixtures" / "minima"


class Base(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.raiz = Path(tmp.name)
        shutil.copytree(FIXTURE / "dados", self.raiz / "fonte" / "dados")
        for rel in ("assets/pessoas/ana.webp", "assets/pessoas/bia.webp", "assets/projetos/alfa/1.png",
                    "assets/projetos/beta/1.png", "assets/og/ana.png", "assets/og/bia.png",
                    "assets/og/alfa.png", "assets/og/site.png"):
            arq = self.raiz / rel
            arq.parent.mkdir(parents=True, exist_ok=True)
            arq.write_bytes(b"x")

    def editar(self, nome, fn):
        arq = self.raiz / "fonte" / "dados" / nome
        obj = json.loads(arq.read_text(encoding="utf-8"))
        fn(obj)
        arq.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def validar(self, dados=None):
        dados = dados or D.carregar(self.raiz)
        return D.validar(dados, self.raiz)


class TestDados(Base):
    def test_carrega_fixture(self):
        d = D.carregar(self.raiz)
        self.assertEqual(len(d.pessoas), 2)
        slugs = [p.slug for p in d.projetos]
        self.assertEqual(slugs, sorted(slugs))
        self.assertEqual(self.validar(d), ([], []))

    def test_campo_obrigatorio_faltando_cita_arquivo_e_campo(self):
        self.editar("pessoas.json", lambda o: o[0].pop("frase"))
        with self.assertRaises(D.ErroDeDados) as c:
            D.carregar(self.raiz)
        self.assertIn("pessoas.json", str(c.exception))
        self.assertIn("frase", str(c.exception))

    def test_slug_duplicado_e_erro(self):
        self.editar("projetos.json", lambda o: o[0].__setitem__("slug", "alfa"))
        erros, _ = self.validar()
        self.assertTrue(any("alfa" in e and "duplicado" in e for e in erros), erros)

    def test_autor_inexistente_e_erro(self):
        self.editar("projetos.json", lambda o: o[1].__setitem__("autores", ["fantasma"]))
        erros, _ = self.validar()
        self.assertTrue(any("fantasma" in e for e in erros), erros)

    def test_imagem_inexistente_e_erro(self):
        self.editar("projetos.json", lambda o: o[1].__setitem__("imagens", ["assets/projetos/alfa/nao.png"]))
        erros, _ = self.validar()
        self.assertTrue(any("nao.png" in e for e in erros), erros)

    def test_link_http_e_erro(self):
        self.editar("projetos.json", lambda o: o[1].__setitem__("link", "http://alfa.exemplo.test"))
        erros, _ = self.validar()
        self.assertTrue(any("https" in e for e in erros), erros)
        self.editar("projetos.json", lambda o: o[1].__setitem__("link", "https://alfa.exemplo.test"))
        self.assertEqual(self.validar()[0], [])

    def test_tipo_invalido_e_erro(self):
        self.editar("projetos.json", lambda o: o[1].__setitem__("tipo", "jogo"))
        erros, _ = self.validar()
        self.assertTrue(any("tipo" in e and "jogo" in e for e in erros), erros)

    def test_inspetor_com_amott_e_erro(self):
        d = D.carregar(self.raiz)
        d = dataclasses.replace(d, estudio=dataclasses.replace(d.estudio, inspetor=("amott",)))
        erros, _ = self.validar(d)
        self.assertTrue(any("amott" in e for e in erros), erros)

    def test_inspetor_slug_sem_arquivo_e_erro(self):
        d = D.carregar(self.raiz)
        d = dataclasses.replace(d, estudio=dataclasses.replace(d.estudio, inspetor=("prosup",)))
        erros, _ = self.validar(d)
        self.assertTrue(any("prosup" in e for e in erros), erros)

    def test_descricao_fora_de_140_160_so_avisa(self):
        self.editar("servicos.json", lambda o: o[0].__setitem__("descricao", "curta demais"))
        erros, avisos = self.validar()
        self.assertEqual(erros, [])
        self.assertTrue(any("descricao" in a for a in avisos), avisos)

    def test_og_faltando_so_avisa(self):
        (self.raiz / "assets" / "og" / "alfa.png").unlink()
        erros, avisos = self.validar()
        self.assertEqual(erros, [])
        self.assertTrue(any("og/alfa.png" in a for a in avisos), avisos)

    def test_imagens_vazias_so_avisa(self):
        self.editar("projetos.json", lambda o: o[1].__setitem__("imagens", []))
        erros, avisos = self.validar()
        self.assertEqual(erros, [])
        self.assertTrue(any("alfa" in a and "imagens" in a for a in avisos), avisos)

    def test_juntra_todos_os_problemas(self):
        self.editar("projetos.json", lambda o: (o[1].__setitem__("tipo", "jogo"), o[1].__setitem__("link", "http://x")))
        erros, _ = self.validar()
        self.assertGreaterEqual(len(erros), 2)

    def test_visiveis_exclui_vetado(self):
        d = D.carregar(self.raiz)
        self.assertEqual([p.slug for p in D.visiveis(d.projetos)], ["alfa"])


if __name__ == "__main__":
    unittest.main()
