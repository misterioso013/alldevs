import json
import re
import shutil
import tempfile
import unicodedata
import unittest
from pathlib import Path

from alldevs import contato
from testes.test_conteudo import Base, gerar_copia, ler, modelo
from testes.test_paginas import REPO, rodar

TIPOS = ("projeto", "servico", "pessoa", "contato")
LIMITE_JS = 6144
GATILHO = '<a href="/projetos/" class="paleta-gatilho">&gt; ir para…</a>'


def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c)).lower()


def paleta(raiz: Path) -> list:
    return json.loads(ler(raiz / "assets" / "paleta.json"))


class TestPaletaJson(Base):
    def setUp(self):
        self.itens = paleta(self.saida)

    def por_tipo(self, tipo):
        return [i for i in self.itens if i["tipo"] == tipo]

    def test_formato(self):
        self.assertIsInstance(self.itens, list)
        for i in self.itens:
            self.assertEqual({"rotulo", "tipo", "url"} - set(i), set(), i)
            self.assertLessEqual(set(i), {"rotulo", "tipo", "url", "termos"}, i)
            self.assertIn(i["tipo"], TIPOS, i)
            self.assertTrue(i["rotulo"].strip() and i["url"].strip(), i)
            if "termos" in i:
                self.assertEqual(i["termos"], i["termos"].lower(), i)

    def test_paleta_tem_os_6_servicos_e_2_pessoas(self):
        servicos = self.por_tipo("servico")
        self.assertEqual(len(self.dados.servicos), 6)
        self.assertEqual(len(servicos), 6)
        self.assertEqual([i["rotulo"] for i in servicos], [s.nome for s in self.dados.servicos])
        self.assertEqual([i["url"] for i in servicos], [f"/servicos/{s.slug}/" for s in self.dados.servicos])
        pessoas = self.por_tipo("pessoa")
        self.assertEqual(len(self.dados.pessoas), 2)
        self.assertEqual([i["rotulo"] for i in pessoas], [p.nome for p in self.dados.pessoas])
        self.assertEqual([i["url"] for i in pessoas], [f"/{p.slug}/" for p in self.dados.pessoas])

    def test_projetos_visiveis_na_mesma_ordem_de_projetos(self):
        projetos = self.por_tipo("projeto")
        self.assertGreaterEqual(len(self.visiveis), 1)
        self.assertEqual([i["rotulo"] for i in projetos], [p.nome for p in self.visiveis])
        self.assertEqual([i["url"] for i in projetos], [f"/projetos/{p.slug}/" for p in self.visiveis])

    def test_ordem_projetos_servicos_pessoas_contato(self):
        tipos = [i["tipo"] for i in self.itens]
        self.assertEqual(tipos, sorted(tipos, key=TIPOS.index))

    def test_contato_usa_os_dados_do_estudio(self):
        est = self.dados.estudio
        c = {i["rotulo"]: i for i in self.por_tipo("contato")}
        self.assertEqual(list(c), ["Pedir orçamento", "WhatsApp", "Telegram", "E-mail"])
        self.assertEqual(c["Pedir orçamento"]["url"], "/#contato")
        self.assertEqual(c["WhatsApp"]["url"],
                         contato.link_whatsapp(est.whatsapp, contato.mensagem(est, "home")))
        self.assertIn("?text=", c["WhatsApp"]["url"])
        self.assertEqual(c["Telegram"]["url"], est.telegram)
        self.assertTrue(c["E-mail"]["url"].startswith(f"mailto:{est.email}"))

    def test_busca_acha_orcamento_whatsapp_telegram_email(self):
        for consulta in ("orcamento", "whatsapp", "telegram", "email"):
            achou = [i for i in self.itens
                     if consulta in sem_acento(f'{i["rotulo"]} {i.get("termos", "")}')]
            self.assertEqual([i["tipo"] for i in achou], ["contato"], consulta)

    def test_urls_internas_existem_na_saida(self):
        for i in self.itens:
            if not i["url"].startswith("/"):
                continue
            caminho = i["url"].split("#")[0].lstrip("/")
            alvo = self.saida / caminho / "index.html" if caminho.endswith("/") or not caminho \
                else self.saida / caminho
            self.assertTrue(alvo.is_file(), i)

    def test_sem_amott(self):
        self.assertNotIn("amott", ler(self.saida / "assets" / "paleta.json").lower())


class TestPaletaVetado(unittest.TestCase):
    def test_paleta_json_sem_vetado(self):
        raiz = gerar_copia(self, lambda ps: ps + [
            modelo(ps, slug="visivel-ok", nome="Visivel Ok", rascunho=False),
            modelo(ps, slug="segredo-vetado", nome="Segredo Vetado", visivel=False, destaque=True,
                   rascunho=False, autores=["caio", "rosiel"])])
        itens = paleta(raiz)
        self.assertIn(("Visivel Ok", "/projetos/visivel-ok/"), [(i["rotulo"], i["url"]) for i in itens])
        bruto = ler(raiz / "assets" / "paleta.json").lower()
        self.assertNotIn("segredo", bruto)
        self.assertNotIn("vetado", bruto)

    def test_previa_regrava_a_paleta_e_nao_copia_a_velha(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = Path(tmp.name) / "raiz"
        shutil.copytree(REPO / "fonte", raiz / "fonte", ignore=shutil.ignore_patterns("__pycache__", "testes"))
        shutil.copytree(REPO / "assets", raiz / "assets")
        (raiz / "assets" / "paleta.json").write_text("[]\n", encoding="utf-8")
        saida = Path(tmp.name) / "previa"
        rc, _, err = rodar("--previa", "--raiz", str(raiz), "--saida", str(saida))
        self.assertEqual(rc, 0, err)
        self.assertGreater(len(paleta(saida)), 6)


class TestGatilhoEScript(Base):
    def test_gatilho_sem_js_e_link_para_projetos(self):
        paginas = sorted(self.saida.rglob("*.html"))
        self.assertGreaterEqual(len(paginas), 14)
        for arq in paginas:
            txt = ler(arq)
            self.assertEqual(txt.count('class="paleta-gatilho"'), 1, arq)
            self.assertIn(GATILHO, txt, arq)
            self.assertNotIn("paleta-pilula", txt, arq)

    def test_script_defer_depois_do_site_js(self):
        for arq in self.saida.rglob("*.html"):
            head = ler(arq).partition("</head>")[0]
            self.assertIn('<script src="/js/paleta.js" defer></script>', head, arq)
            self.assertLess(head.index('src="/js/site.js"'), head.index('src="/js/paleta.js"'), arq)

    def test_css_renomeado_e_gatilho_some_em_768(self):
        css = ler(REPO / "css" / "site.css")
        self.assertFalse("paleta-pilula" in css, "css/site.css ainda usa paleta-pilula")
        # dentro do bloco @media (linhas recuadas em 2 espaços; o "}" que fecha o bloco fica na coluna 0)
        self.assertRegex(css, r"@media \(min-width: 768px\) \{\n(?:  [^\n]*\n)*?  \.paleta-gatilho \{ display: none; \}")
        self.assertIn("dialog.paleta", css)
        self.assertIn("prefers-reduced-motion", css)


class TestPaletaJs(unittest.TestCase):
    def setUp(self):
        self.js = ler(REPO / "js" / "paleta.js")

    def test_tamanho(self):
        tam = len((REPO / "js" / "paleta.js").read_bytes())
        self.assertLessEqual(tam, LIMITE_JS, f"paleta.js tem {tam} bytes (limite {LIMITE_JS})")

    def test_acessibilidade_declarada(self):
        for trecho in ("showModal", "aria-modal", "listbox", "option",
                       "aria-activedescendant", "normalize(", "Escape", "ArrowDown", "ArrowUp"):
            self.assertIn(trecho, self.js, trecho)
        self.assertRegex(self.js, r'role"?\s*[:,]\s*"dialog"')

    def test_fetch_so_na_abertura_e_sem_contato_escrito_a_mao(self):
        self.assertEqual(self.js.count("fetch("), 1)
        self.assertIn("/assets/paleta.json", self.js)
        self.assertIsNone(re.search(r"wa\.me|t\.me|mailto|gmail|\d{8,}", self.js))
        self.assertNotIn("amott", self.js.lower())

    def test_sem_cor_nem_numero_de_animacao_no_js(self):
        self.assertIsNone(re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(", self.js))
        self.assertNotIn("transform", self.js)


if __name__ == "__main__":
    unittest.main()
