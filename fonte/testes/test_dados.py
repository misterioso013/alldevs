import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import gerar
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
        self.assertEqual(self.validar(d), ([], ["destaques: 1 projetos visíveis em destaque (ideal 4 a 6)"]))

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

    def test_autores_nao_existe_mais(self):
        self.editar("projetos.json", lambda o: o[1].__setitem__("autores", ["ana"]))
        with self.assertRaises(D.ErroDeDados) as c:
            D.carregar(self.raiz)
        self.assertIn("projetos.json", str(c.exception))
        self.assertIn("autores", str(c.exception))

    def test_tipo_fora_de_TIPOS_e_erro(self):
        self.editar("projetos.json", lambda o: o[1].__setitem__("tipo", "bot"))
        erros, _ = self.validar()
        self.assertTrue(any("tipo" in e and "bot" in e for e in erros), erros)

    def test_ciclo_exige_por_tras(self):
        self.editar("estudio.json", lambda o: o.__setitem__("ciclo", ["alfa"]))
        erros, _ = self.validar()
        self.assertTrue(any("ciclo" in e and "alfa" in e for e in erros), erros)

    def test_ciclo_com_por_tras_passa(self):
        self.pt()
        self.editar("estudio.json", lambda o: o.__setitem__("ciclo", ["alfa"]))
        self.assertEqual(self.validar()[0], [])

    def test_loja_so_play_store(self):
        self.editar("projetos.json", lambda o: o[1].__setitem__("loja", "https://exemplo.test/app"))
        erros, _ = self.validar()
        self.assertTrue(any("loja" in e for e in erros), erros)
        self.editar("projetos.json", lambda o: o[1].__setitem__(
            "loja", "https://play.google.com/store/apps/details?id=br.com.alfa"))
        self.assertEqual(self.validar()[0], [])

    def test_tecnologia_sem_projeto_e_erro(self):
        # Beta é invisível; heisuca-like (rascunho) também não conta.
        self.editar("tecnologias.json", lambda o: o.append({"nome": "Python", "grupo": "back"}))
        erros, _ = self.validar()
        self.assertTrue(any("Python" in e for e in erros), erros)
        self.editar("projetos.json", lambda o: (o[1].__setitem__("stack", ["Python"]), o[1].__setitem__("rascunho", True)))
        erros, _ = self.validar()
        self.assertTrue(any("Python" in e for e in erros), erros)
        self.editar("projetos.json", lambda o: o[1].__setitem__("rascunho", False))
        self.assertEqual([e for e in self.validar()[0] if "Python" in e], [])

    def test_tecnologia_grupo_invalido_e_erro(self):
        self.editar("tecnologias.json", lambda o: o[0].__setitem__("grupo", "outro"))
        erros, _ = self.validar()
        self.assertTrue(any("Flutter" in e and "grupo" in e for e in erros), erros)

    def test_depoimento_nao_autorizado_e_erro(self):
        dep = {"nome": "Fulano", "papel": "Cliente", "texto": "Bom.", "autorizado": False}
        self.editar("depoimentos.json", lambda o: o.append(dep))
        erros, _ = self.validar()
        self.assertTrue(any("Fulano" in e and "autoriz" in e for e in erros), erros)
        dep["autorizado"] = True
        self.editar("depoimentos.json", lambda o: o.__setitem__(0, dep))
        self.assertEqual(self.validar()[0], [])

    def test_servico_tipo_valido(self):
        self.editar("servicos.json", lambda o: o[0].__setitem__("tipo", "bot"))
        erros, _ = self.validar()
        self.assertTrue(any("servico site" in e and "tipo" in e for e in erros), erros)
        self.editar("servicos.json", lambda o: o[0].__setitem__("tipo", "automacao"))
        self.assertEqual(self.validar()[0], [])

    def test_servico_com_quem_toca_e_erro(self):
        self.editar("servicos.json", lambda o: o[0].__setitem__("quem_toca", ["ana"]))
        with self.assertRaises(D.ErroDeDados) as c:
            D.carregar(self.raiz)
        self.assertIn("quem_toca", str(c.exception))

    # --- por_tras ---
    def pt(self, tipo="codigo", texto="def f():\n    return 1\n", **extra):
        """Liga por_tras no projeto alfa, criando os arquivos que ele cita."""
        if tipo == "codigo":
            arq = "fonte/conteudo/por-tras/alfa.txt"
            (self.raiz / arq).parent.mkdir(parents=True, exist_ok=True)
            (self.raiz / arq).write_text(texto, encoding="utf-8")
        else:
            arq = "assets/por-tras/alfa.webp"
            (self.raiz / arq).parent.mkdir(parents=True, exist_ok=True)
            (self.raiz / arq).write_bytes(b"x")
        frente = self.raiz / "assets" / "frente" / "alfa.webp"
        frente.parent.mkdir(parents=True, exist_ok=True)
        frente.write_bytes(b"x")
        bloco = {"tipo": tipo, "arquivo": arq, "origem": "alfa · js/a.js",
                 "frente": "assets/frente/alfa.webp", "frase": "O que fica por trás.", "cor": "roxo"}
        bloco.update(extra)
        self.editar("projetos.json", lambda o: o[1].__setitem__("por_tras", bloco))
        return arq

    def test_por_tras_valido_para_os_tres_tipos(self):
        for tipo in ("codigo", "wireframe", "fluxo"):
            self.pt(tipo)
            self.assertEqual(self.validar()[0], [], tipo)

    def test_por_tras_tipo_e_cor_invalidos(self):
        self.pt(tipo="codigo", cor="verde")
        self.assertTrue(any("cor" in e for e in self.validar()[0]))
        self.pt(tipo="codigo")
        self.editar("projetos.json", lambda o: o[1]["por_tras"].__setitem__("tipo", "video"))
        self.assertTrue(any("por_tras" in e and "tipo" in e for e in self.validar()[0]))

    def test_por_tras_codigo_ate_24_linhas_e_72_colunas(self):
        self.pt(texto="\n".join("x" for _ in range(24)) + "\n")
        self.assertEqual(self.validar()[0], [])
        self.pt(texto="\n".join("x" for _ in range(25)) + "\n")
        self.assertTrue(any("24 linhas" in e for e in self.validar()[0]))
        self.pt(texto="x" * 72 + "\n")
        self.assertEqual(self.validar()[0], [])
        self.pt(texto="x" * 73 + "\n")
        self.assertTrue(any("72 colunas" in e for e in self.validar()[0]))

    def test_loja_exige_id_do_pacote(self):
        base = "https://play.google.com/store/apps/details?id="
        for loja, bom in ((base, False), (base + "br", False), (base + "1abc.x", False), (base + "br.com.alfa", True),
                          (base + "br.com.alfa&hl=pt", False), (base + "br.com.alfa/x", False)):
            with self.subTest(loja=loja):
                self.editar("projetos.json", lambda o, l=loja: o[1].__setitem__("loja", l))
                self.assertEqual(self.validar()[0] == [], bom, self.validar()[0])

    def test_por_tras_campo_so_com_espacos_e_um_erro_por_campo(self):
        self.pt()
        for campo in ("tipo", "cor", "origem", "frase"):
            with self.subTest(campo=campo):
                self.editar("projetos.json", lambda o, c=campo: o[1]["por_tras"].__setitem__(c, "   "))
                erros = [e for e in self.validar()[0] if "por_tras" in e]
                self.assertEqual(len(erros), 1, erros)
                self.assertIn(f"campo {campo} ausente ou vazio", erros[0])
                self.pt()

    def test_por_tras_codigo_sem_linha_com_codigo_e_erro(self):
        for texto in ("", "\n\n", "   \n\t\n"):
            with self.subTest(texto=texto):
                self.pt(texto=texto)
                self.assertTrue(any("sem nenhuma linha" in e for e in self.validar()[0]))

    def test_por_tras_arquivo_em_pasta_ou_extensao_errada_e_erro(self):
        self.pt()
        for novo in ("assets/por-tras/alfa.txt", "fonte/conteudo/outra/alfa.txt", "fonte/conteudo/por-tras/alfa.md"):
            with self.subTest(novo=novo):
                self.editar("projetos.json", lambda o, n=novo: o[1]["por_tras"].__setitem__("arquivo", n))
                self.assertTrue(any("arquivo de codigo deve ser" in e for e in self.validar()[0]))
        self.pt("wireframe")
        self.editar("projetos.json", lambda o: o[1]["por_tras"].__setitem__("arquivo", "fonte/conteudo/por-tras/alfa.txt"))
        self.assertTrue(any("arquivo de wireframe deve ser" in e for e in self.validar()[0]))

    def test_por_tras_caminho_com_ponto_ponto_e_erro(self):
        self.pt()
        (self.raiz / "fonte" / "conteudo" / "outra").mkdir(parents=True)
        (self.raiz / "fonte" / "conteudo" / "outra" / "x.txt").write_text("a\n")
        self.editar("projetos.json", lambda o: o[1]["por_tras"].__setitem__(
            "arquivo", "fonte/conteudo/por-tras/../outra/x.txt"))
        self.assertTrue(any("não pode sair" in e for e in self.validar()[0]))
        self.pt()
        self.editar("projetos.json", lambda o: o[1]["por_tras"].__setitem__("frente", "assets/frente/../frente/alfa.webp"))
        self.assertTrue(any("frente" in e for e in self.validar()[0]))

    def test_ordem_de_tecnologias_e_depoimentos_e_a_do_json(self):
        self.editar("tecnologias.json", lambda o: o.insert(0, {"nome": "Zig", "grupo": "back"}))
        self.editar("depoimentos.json", lambda o: o.extend(
            {"nome": n, "papel": "c", "texto": "t", "autorizado": True} for n in ("Zeca", "Ana")))
        d = D.carregar(self.raiz)
        self.assertEqual([t.nome for t in d.tecnologias], ["Zig", "Flutter"])
        self.assertEqual([x.nome for x in d.depoimentos], ["Zeca", "Ana"])

    def test_por_tras_arquivo_inexistente_e_erro(self):
        arq = self.pt()
        (self.raiz / arq).unlink()
        erros, _ = self.validar()
        self.assertTrue(any("inexistente" in e and "alfa.txt" in e for e in erros), erros)

    def test_frente_inexistente_e_erro(self):
        self.pt()
        (self.raiz / "assets" / "frente" / "alfa.webp").unlink()
        erros, _ = self.validar()
        self.assertTrue(any("inexistente" in e and "frente" in e for e in erros), erros)

    def test_frase_acima_de_60_e_erro(self):
        self.pt(frase="x" * 60)
        self.assertEqual(self.validar()[0], [])
        self.pt(frase="x" * 61)
        self.assertTrue(any("frase" in e for e in self.validar()[0]))

    def test_ler_por_tras(self):
        self.pt(texto="linha\n")
        d = D.carregar(self.raiz)
        alfa = next(p for p in d.projetos if p.slug == "alfa")
        beta = next(p for p in d.projetos if p.slug == "beta")
        self.assertEqual(D.ler_por_tras(self.raiz, alfa), "linha\n")
        self.assertIsNone(D.ler_por_tras(self.raiz, beta))
        self.pt("wireframe")
        d = D.carregar(self.raiz)
        self.assertIsNone(D.ler_por_tras(self.raiz, next(p for p in d.projetos if p.slug == "alfa")))

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

    def test_visivel_e_destaque_nao_booleanos_sao_erro(self):
        for campo in ("visivel", "destaque"):
            self.editar("projetos.json", lambda o, c=campo: o[0].__setitem__(c, "false"))
            erros, _ = self.validar()
            self.assertTrue(any("beta" in e and campo in e for e in erros), erros)
            self.editar("projetos.json", lambda o, c=campo: o[0].__setitem__(c, False))

    def test_visiveis_exclui_vetado(self):
        d = D.carregar(self.raiz)
        self.assertEqual([p.slug for p in D.visiveis(d.projetos)], ["alfa"])


# Chaves falsas montadas por concatenação para não acionar scanners de segredo.
SEGREDOS = {
    "sk" + "-abc123def456ghi789": "chave sk-",
    "x = 'sk" + "-abc123def456ghi789'": "chave sk-",
    "AK" + "IA1234567890ABCDEF": "chave AWS",
    "AS" + "IA1234567890ABCDEF": "chave AWS",
    "gh" + "p_" + "a1B2c3D4e5" * 3 + "a1B2c3": "token GitHub",
    "gh" + "o_" + "a1B2c3D4e5" * 3 + "a1B2c3": "token GitHub",
    "github" + "_pat_" + "a1B2c3D4e5" * 3: "token GitHub",
    "-----BEGIN RSA PRIV" + "ATE KEY-----": "chave privada",
    "-----BEGIN PRIV" + "ATE KEY-----": "chave privada",
    "Authorization: Bear" + "er abcdef123456": "Bearer",
    'token = "x"': "credencial",
    '"token": "x"': "credencial",
    "'senha': '1'": "credencial",
    "password=": "credencial",
    "senha: abc": "credencial",
    "API_KEY_PROD = 1": "credencial",
    "TOKEN_JWT=abc": "credencial",
    "DB_PASSWORD_1=abc": "credencial",
    "host 143.95.215.156": "IP",
    "host 192.168.0.1": "IP",
    "fale com alguem@exemplo.com": "e-mail",
    "alguem@sub.exemplo.com.br": "e-mail",
    "http://localhost:8080": "host interno",
    "api.docaio.com.br": "host interno",
}
NAO_CASAM = [
    "import gsap@3.13.0",
    "gsap@3.13.0",
    "task-scheduler-worker-pool",
    "const total = itens.length;",
    "Bearer token no cabeçalho",
    "versão 3.13.0",
]


class PorTrasSegredoTest(Base):
    pt = TestDados.pt

    def test_cada_classe_de_segredo_e_erro_com_arquivo_e_linha(self):
        for linha, classe in SEGREDOS.items():
            with self.subTest(linha=linha):
                arq = self.pt(texto=f"ok\n{linha}\n")
                erros, _ = self.validar()
                achou = [e for e in erros if f"{arq}:2" in e and classe in e]
                self.assertTrue(achou, erros)
                self.assertFalse(any(linha in e for e in erros), "o erro não pode mostrar o valor")

    def test_linhas_inocentes_nao_casam(self):
        for linha in NAO_CASAM:
            with self.subTest(linha=linha):
                self.pt(texto=f"ok\n{linha}\n")
                self.assertEqual(self.validar()[0], [])

    def test_codigo_limpo_passa(self):
        self.pt(texto="const total = itens.length;\nreturn total;\n")
        self.assertEqual(self.validar()[0], [])


class ProjetoSemPorTrasTest(Base):
    def test_sem_por_tras_gera_case_comum(self):
        d = D.carregar(self.raiz)
        self.assertTrue(all(p.por_tras is None for p in d.projetos))
        self.assertEqual(self.validar(d)[0], [])

    def test_gerar_rc_zero_com_dados_reais_sem_por_tras(self):
        repo = Path(__file__).resolve().parent.parent.parent
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = Path(tmp.name) / "raiz"
        shutil.copytree(repo / "fonte", raiz / "fonte", ignore=shutil.ignore_patterns("__pycache__", "testes"))
        shutil.copytree(repo / "assets", raiz / "assets")
        shutil.copytree(repo / "js", raiz / "js")
        arq = raiz / "fonte" / "dados" / "projetos.json"
        obj = json.loads(arq.read_text(encoding="utf-8"))
        for p in obj:
            p["por_tras"] = None
        arq.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = gerar.main(["--raiz", str(raiz), "--saida", str(Path(tmp.name) / "saida")])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
