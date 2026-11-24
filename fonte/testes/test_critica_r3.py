"""Crítica externa, rodada 3: capas, case, ideia, Quem somos, código, sistema visual, barra do WhatsApp, botões, vazios, hero."""
import re
import unittest

from testes.test_critica_r2 import CSS, desktop, regras
from testes.test_paginas import REPO


def corpo(seletor, texto=None):
    """Declarações de todas as regras cujo seletor (lista separada por vírgula) contém `seletor` exato."""
    texto = re.sub(r"/\*.*?\*/", "", CSS if texto is None else texto, flags=re.S)
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", texto):
        if seletor in [x.strip() for x in m.group(1).split(",")]:
            out.append(m.group(2))
    return " ".join(out)


class Capas(unittest.TestCase):
    def test_duas_colunas_iguais_no_desktop(self):
        d = desktop()
        self.assertRegex(corpo(".grade-projetos > .projeto-cartao", d), r"grid-column:\s*span\s*6")
        self.assertNotRegex(d, r"\.grade-projetos\s*>\s*\.projeto-cartao:nth-child")

    def test_moldura_nao_estica(self):
        self.assertNotIn("flex: 1 0 auto", desktop())
        self.assertIn("aspect-ratio: 16 / 10", corpo(".projeto-tela"))

    def test_paisagem_preenche_e_retrato_tem_quadro(self):
        self.assertIn("object-fit: cover", corpo(".projeto-tela img"))
        r = corpo(".projeto-tela--retrato img")
        self.assertIn("height: 100%", r)
        self.assertIn("object-fit: contain", r)

    def test_um_titulo_so(self):
        self.assertIn("font-size: 1.5rem", corpo(".projeto-titulo"))
        self.assertNotRegex(CSS, r"\.projeto-cartao[^{]*h[23][^{]*\{[^}]*font-size")


def _gerar_case(slug):
    from alldevs import dados as dd, paginas
    d = dd.carregar(REPO)
    p = next(x for x in d.projetos if x.slug == slug)
    return str(paginas._case(p, d, REPO, False).corpo)


class CaseHeisuca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = _gerar_case("heisuca")

    def test_coluna_de_telas_segue_o_texto(self):
        self.assertRegex(self.html, r'<section class="case-telas case-telas-fixa"')
        self.assertIn("position: sticky", corpo(".case:not(.case-unica) .case-telas-fixa"))

    def test_icone_quadrado_tem_tamanho_de_icone(self):
        self.assertRegex(self.html, r'<img class="img-icone" src="/assets/loja/heisuca-3.webp"')
        self.assertIn("width: 120px", corpo(".case-loja img.img-icone"))

    def test_imagens_na_largura_da_coluna(self):
        self.assertIn("width: 100%", corpo(".case-loja img"))
        self.assertNotIn("540px", corpo(".case-loja img"))

    def test_print_do_app_so_uma_vez(self):
        self.assertEqual(self.html.count("assets/frente/heisuca.webp"), 1)

    def test_cursor_ignora_posicao_zero(self):
        js = (REPO / "js" / "site.js").read_text(encoding="utf-8")
        self.assertRegex(js, r"if \(!e\.clientX && !e\.clientY\) return;")


class Ideia(unittest.TestCase):
    def test_estagio_ativo_sempre_opaco(self):
        self.assertIn("opacity: 1", corpo(".ideia-pin .ideia-estagio.ativo"))
        js = (REPO / "js" / "ideia.js").read_text(encoding="utf-8")
        self.assertNotRegex(js, r"opacity\s*:")

    def test_estagio_preenche_a_tela_no_desktop(self):
        d = desktop()
        self.assertRegex(corpo(".ideia-pin .ideia-estagio", d), r"min-height:\s*min\(64vh")
        self.assertIn("font-size: 2rem", corpo(".ideia-pin .ideia-texto h3", d))
        self.assertIn("max-width: none", corpo(".ideia-pin .ideia-wire", d))


class Codigo(unittest.TestCase):
    def test_camada_mostra_o_trecho_uma_vez(self):
        from alldevs import paginas
        from alldevs.dados import carregar
        d = carregar(REPO)
        for p in d.projetos:
            if not p.por_tras:
                continue
            camada = str(paginas._camada_por_tras(p, REPO))
            m = re.search(r"<pre><code>(.*?)</code></pre>", camada, re.S)
            if not m:
                continue
            cod = m.group(1).strip()
            primeira = cod.splitlines()[0]
            self.assertEqual(cod.count(primeira), 1, p.slug)

    def test_trecho_da_ideia_fecha_a_classe(self):
        html = (REPO / "index.html").read_text(encoding="utf-8")
        m = re.search(r'<pre class="ideia-codigo".*?<code>(.*?)</code>', html, re.S)
        self.assertTrue(m.group(1).rstrip().endswith("}"))

    def test_celular_quebra_a_linha_do_codigo(self):
        css = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
        m = re.search(r"@media \(max-width: 767px\) \{\s*\.ideia-codigo \{(.*?)\n\}", css, re.S)
        self.assertIn("pre-wrap", m.group(1))
        self.assertIn(".ideia-frente { width: 100%; }", m.group(1))


class QuemSomos(unittest.TestCase):
    def test_dois_socios_lado_a_lado_no_desktop(self):
        d = desktop()
        self.assertIn("grid-column: span 6", corpo(".cartoes-pessoas > *", d))
        self.assertIn("200px", corpo(".cartoes-pessoas > .cartao-pessoa", d))

    def test_mesma_ordem_no_html(self):
        html = (REPO / "index.html").read_text(encoding="utf-8")
        self.assertLess(html.index('data-slug="caio"'), html.index('data-slug="rosiel"'))


class Sistema(unittest.TestCase):
    def test_sem_emoji_como_icone_nos_servicos(self):
        emoji = re.compile("[\U0001F000-\U0001FAFF☀-⛿✀-✒✔-➿⭐]")
        for f in (REPO / "servicos").glob("*/index.html"):
            self.assertIsNone(emoji.search(f.read_text(encoding="utf-8")), f.parent.name)
            self.assertNotIn("relacionado-icon", f.read_text(encoding="utf-8"))

    def test_filtro_com_o_raio_das_pilulas(self):
        self.assertIn("border-radius: 999px", corpo(".filtro-tipos button"))
        self.assertIn("border-radius: 999px", corpo(".btn"))

    def test_seta_do_faq_com_20px_de_desenho(self):
        r = corpo(".faq-chevron")
        self.assertIn("width: 40px", r)
        self.assertIn("height: 40px", r)


class BarraWaEContato(unittest.TestCase):
    def test_barra_some_por_transform_e_opacity(self):
        r = corpo(".barra-wa--oculta", re.sub(r"@media[^{]*\{", "", CSS))
        self.assertIn("translateY(100%)", r)
        self.assertIn("opacity: 0", r)
        js = (REPO / "js" / "site.js").read_text(encoding="utf-8")
        self.assertIn("ligarBarraWa", js)
        self.assertIn('a[href*="wa.me"], footer', js)

    def test_fim_do_conteudo_com_respiro_da_barra(self):
        self.assertRegex(CSS, r"main \{ padding-bottom: 72px; \}")

    def test_trio_uma_vez_so_na_pagina_de_servico(self):
        for f in (REPO / "servicos").glob("*/index.html"):
            h = f.read_text(encoding="utf-8")
            self.assertEqual(h.count(">Telegram</a>"), 1, f.parent.name)
            self.assertEqual(h.count(">Enviar e-mail</a>"), 1, f.parent.name)
            self.assertEqual(h.count('id="contato"'), 1, f.parent.name)
            cartao = re.search(r'<div class="servico-cta">.*?</div>\s*</div>', h, re.S).group(0)
            self.assertIn("Solicitar orçamento pelo WhatsApp", cartao)
            self.assertNotIn("Telegram", cartao)

    def test_contato_igual_fora_da_home(self):
        self.assertEqual(corpo("main > #contato"), "")
        self.assertIn("var(--fundo-2)", corpo("main > .contato", desktop()))
        self.assertIn("nowrap", corpo("main > .contato > .cta-buttons", desktop()))
        for pg in ("projetos/index.html", "projetos/heisuca/index.html"):
            h = (REPO / pg).read_text(encoding="utf-8")
            self.assertEqual(h.count('id="contato"'), 1, pg)
            self.assertEqual(h.count('<section class="contato"'), 1, pg)

    def test_botao_principal_numa_linha(self):
        self.assertIn("white-space: nowrap", corpo(".cta-buttons .btn"))


class VaziosDesktop(unittest.TestCase):
    def test_faq_titulo_sticky(self):
        c = " ".join(regras(r"[^{}]*\.faq-home > h2[^{}]*", desktop()))
        self.assertIn("position: sticky", c)

    def test_tecnologias_sem_coluna_vazia(self):
        c = " ".join(regras(r"[^{}]*\.tec-grupos[^{}]*", desktop()))
        self.assertIn("column-count: 3", c)
        self.assertNotRegex(CSS, r"\n\.tec-grupos \{[^}]*display: grid")   # a regra base não pode vencer a do desktop
        self.assertIn("break-inside: avoid", " ".join(regras(r"[^{}]*\.tec-grupo\b[^{}]*", desktop())))

    def test_servico_430_sem_vao_entre_selo_e_divisor(self):
        mob = CSS[CSS.index("max-width: 767px) {\n  .servico-hero"):][:300]
        self.assertIn(".servico-body > h2:first-child", mob)

    def test_hero_360_botao_fora_do_codigo_e_frase_no_fluxo(self):
        m = re.search(r"max-width: 959px\) \{([^@]*)\}\n", CSS)
        self.assertTrue(m)
        self.assertIn(".hero-palco { margin-bottom", m.group(1))
        self.assertIn("bottom: -52px", m.group(1))

    def test_dica_ver_por_tras_no_toque(self):
        m = re.search(r"@media \(hover: none\), \(pointer: coarse\) \{\s*\[data-cursor=\"ver por trás\"\]::after \{([^}]*)\}", CSS)
        self.assertTrue(m)
        self.assertIn("content: attr(data-cursor)", m.group(1))


class ComputadoNoNavegador(unittest.TestCase):
    """Lê o valor computado no Chromium (a cascata decide), não só a string do CSS."""
    @classmethod
    def setUpClass(cls):
        import os, shutil, subprocess, json
        cls.ok = shutil.which("node") is not None and (REPO / "bancada/node_modules/playwright").exists()
        if not cls.ok:
            return
        script = (REPO / "bancada/_computado.mjs")
        script.write_text(r"""
import { chromium } from 'playwright';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const raiz = process.argv[2];
const srv = http.createServer((q, r) => { let f = path.join(raiz, decodeURIComponent(q.url.split('?')[0])); if (f.endsWith('/')) f += 'index.html';
  fs.readFile(f, (e, d) => { if (e) { r.statusCode = 404; r.end(); return; } r.setHeader('content-type', f.endsWith('.css') ? 'text/css' : f.endsWith('.js') ? 'text/javascript' : 'text/html'); r.end(d); }); }).listen(0);
const base = 'http://127.0.0.1:' + srv.address().port;
const env = { ...process.env, LD_LIBRARY_PATH: [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':') };
const nav = await chromium.launch({ env }); const out = {};
const ctx = await nav.newContext({ viewport: { width: 1440, height: 900 } }); const p = await ctx.newPage();
await p.goto(base + '/', { waitUntil: 'load' });
out.tec = await p.evaluate(() => { const e = document.querySelector('.tec-grupos'); const c = getComputedStyle(e); return [c.display, c.columnCount]; });
out.pesoHome = await p.evaluate(() => { const c = getComputedStyle(document.querySelector('.projeto-titulo')); return [c.fontWeight, c.fontSize, c.lineHeight, c.fontFamily]; });
await p.goto(base + '/projetos/', { waitUntil: 'load' });
out.pesoProj = await p.evaluate(() => { const c = getComputedStyle(document.querySelector('.projeto-titulo')); return [c.fontWeight, c.fontSize, c.lineHeight, c.fontFamily]; });
await nav.close(); srv.close(); console.log(JSON.stringify(out));
""")
        env = dict(os.environ, BANCADA_LIBS=os.path.expanduser("~/.local/lib/chromium-deps"))
        try:
            r = subprocess.run(["node", str(script), str(REPO)], cwd=REPO / "bancada", env=env, capture_output=True, text=True, timeout=120)
            cls.d = json.loads(r.stdout.strip().splitlines()[-1])
        finally:
            script.unlink(missing_ok=True)

    def test_tecnologias_1440_em_colunas(self):
        if not self.ok: self.skipTest("sem playwright")
        self.assertEqual(self.d["tec"], ["block", "3"])

    def test_titulo_de_projeto_igual_na_home_e_em_projetos(self):
        if not self.ok: self.skipTest("sem playwright")
        self.assertEqual(self.d["pesoHome"], self.d["pesoProj"])
        self.assertEqual(self.d["pesoHome"][0], "700")
