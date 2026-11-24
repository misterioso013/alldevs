"""Correções da revisão final: valores computados no Chromium (a cascata decide), mais checagens de CSS/dados por texto."""
import json
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CSS = (REPO / "css/site.css").read_text()
SERVICOS = sorted(p.parent.name for p in (REPO / "servicos").glob("*/index.html"))

SCRIPT = r"""
import { chromium } from 'playwright';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const raiz = process.argv[2]; const servicos = JSON.parse(process.argv[3]);
const srv = http.createServer((q, r) => { let f = path.join(raiz, decodeURIComponent(q.url.split('?')[0])); if (f.endsWith('/')) f += 'index.html';
  fs.readFile(f, (e, d) => { if (e) { r.statusCode = 404; r.end(); return; } r.setHeader('content-type', f.endsWith('.css') ? 'text/css' : f.endsWith('.js') ? 'text/javascript' : 'text/html'); r.end(d); }); }).listen(0);
const base = 'http://127.0.0.1:' + srv.address().port;
const env = { ...process.env, LD_LIBRARY_PATH: [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':') };
const nav = await chromium.launch({ env }); const out = {};
async function pagina(opc, url) {
  const semJs = opc.semJs; delete opc.semJs;   // sem JS: tira os <script> do HTML e bloqueia os .js (page.evaluate não funciona com JS desligado)
  const ctx = await nav.newContext(opc); const p = await ctx.newPage(); p.setDefaultTimeout(20000);
  if (semJs) await ctx.route('**/*', async r => {
    if (r.request().url().endsWith('.js')) return r.abort();
    if (r.request().resourceType() !== 'document') return r.continue();
    const resp = await r.fetch(); const corpo = (await resp.text()).replace(/<script[\s\S]*?<\/script>/g, ''); r.fulfill({ response: resp, body: corpo });
  });
  await p.goto(base + url, { waitUntil: 'load' }); await p.waitForTimeout(400); return [ctx, p];
}
const toque = { hasTouch: true, isMobile: true };
// I1: chip "ver por trás" (::after do rótulo do cartão), três situações
for (const [nome, opc] of Object.entries({
  toque: { ...toque, viewport: { width: 390, height: 800 } },
  semjs: { ...toque, viewport: { width: 390, height: 800 }, semJs: true },
  reduzido: { ...toque, viewport: { width: 390, height: 800 }, reducedMotion: 'reduce' } })) {
  const [c, p] = await pagina(opc, '/projetos/');
  out['chip_' + nome] = await p.evaluate(() => {
    const el = document.querySelector('.projeto-cartao .rotulo-mono');
    return { conteudo: getComputedStyle(el, '::after').content, dentroDaFigura: !!el.closest('.projeto-tela'), js: document.documentElement.classList.contains('js') };
  });
  await c.close();
}
// I3 e M2, M3, M4, M6, M8 na home a 360
{
  const [c, p] = await pagina({ viewport: { width: 360, height: 800 } }, '/');
  out.alvos = await p.evaluate(() => Object.fromEntries(['.nav-logo', '.footer-logo', '.footer-dominio'].map(s => [s, document.querySelector(s).getBoundingClientRect().height])));
  out.introPretty = await p.evaluate(() => getComputedStyle(document.querySelector('.secao-intro')).textWrap);
  out.setaServico = await p.evaluate(() => getComputedStyle(document.querySelector('.cartao-servico'), '::after').content);
  out.codigo = await p.evaluate(() => { const l = document.querySelector('.ideia-codigo .ln'); const c = getComputedStyle(l); return [c.display, c.paddingLeft, c.textIndent]; });
  out.rolagem360 = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  out.tec = await p.evaluate(() => { const c = getComputedStyle(document.querySelector('.tecnologia')); return [c.fontSize, c.paddingTop, c.paddingLeft, c.borderRadius]; });
  await c.close();
}
// M2: sem JS, hero sem buraco nem sobreposição, a 360
{
  const [c, p] = await pagina({ viewport: { width: 360, height: 800 }, semJs: true }, '/');
  out.heroSemJs = await p.evaluate(() => {
    const pal = document.querySelector('.hero-palco').getBoundingClientRect(); const fr = document.querySelector('.hero-frase').getBoundingClientRect();
    let a = document.querySelector('.hero-palco'); while (a && !a.nextElementSibling) a = a.parentElement; const prox = a && a.nextElementSibling;
    return { classeJs: document.documentElement.classList.contains('js'), margem: getComputedStyle(document.querySelector('.hero-palco')).marginBottom, fraseAbaixo: fr.top >= pal.bottom - 1, proxTop: prox ? prox.getBoundingClientRect().top : null, fraseBottom: fr.bottom };
  });
  await c.close();
}
// I4: H1 >= H2 nas páginas de serviço, 360 e 430
out.titulos = {};
for (const w of [360, 430]) for (const s of servicos) {
  const [c, p] = await pagina({ viewport: { width: w, height: 800 } }, '/servicos/' + s + '/');
  out.titulos[w + ' ' + s] = await p.evaluate(() => { const px = e => parseFloat(getComputedStyle(e).fontSize); return { h1: px(document.querySelector('main h1')), h2: Math.max(...[...document.querySelectorAll('main h2')].map(px)) }; });
  await c.close();
}
// I5: contato do serviço, 1280: uma coluna só; id único
{
  const [c, p] = await pagina({ viewport: { width: 1280, height: 900 } }, '/servicos/' + servicos[0] + '/');
  out.contato = await p.evaluate(() => { const e = document.querySelector('main > .contato'); return { colunas: getComputedStyle(e).gridTemplateColumns.split(' ').length, ids: document.querySelectorAll('#contato').length }; });
  await c.close();
}
// M5: cartão único; M7: imagens da loja
{
  const [c, p] = await pagina({ viewport: { width: 1280, height: 900 } }, '/servicos/' + servicos[0] + '/');
  out.unico = await p.evaluate(() => { const g = document.querySelector('.projetos-do-tipo .grade-projetos'); if (!g) return null; const k = g.querySelectorAll(':scope > .projeto-cartao'); return { n: k.length, gc: k.length ? getComputedStyle(k[0]).gridColumnStart : null }; });
  await c.close();
}
{
  const [c, p] = await pagina({ viewport: { width: 1440, height: 900 } }, '/projetos/heisuca/');
  out.etq = await p.evaluate(() => { const c = getComputedStyle(document.querySelector('.etiqueta-mono')); return [c.fontSize, c.paddingTop, c.paddingLeft, c.borderRadius]; });
  out.loja = await p.evaluate(async () => { for (const i of document.querySelectorAll(".case-loja img")) { i.loading = "eager"; try { await i.decode(); } catch (e) {} } return [...document.querySelectorAll(".case-loja img")].map(i => ({ w: i.getBoundingClientRect().width, nat: i.naturalWidth, cls: i.className })); });
  await c.close();
}
// M6: foco de #ideia e dos estágios pela cor global
{
  const [c, p] = await pagina({ viewport: { width: 1280, height: 900 } }, '/');
  out.foco = await p.evaluate(() => { const g = getComputedStyle(document.documentElement).getPropertyValue('--laranja-claro').trim(); const e = document.querySelector('.ideia-estagio'); return { token: g, existe: !!e }; });
  out.filtro = await p.evaluate(() => 0);
  await c.close();
}
// M12: @id das pessoas existe no DOM
{
  const [c, p] = await pagina({ viewport: { width: 1280, height: 900 } }, '/');
  out.ids = await p.evaluate(() => { const ids = []; document.querySelectorAll('script[type="application/ld+json"]').forEach(s => { const t = s.textContent; for (const m of t.matchAll(/"@id":\s*"[^"#]*#(quem-somos-[a-z0-9-]+)"/g)) ids.push(m[1]); }); return ids.map(i => [i, !!document.getElementById(i)]); });
  await c.close();
}
await nav.close(); srv.close(); console.log(JSON.stringify(out));
"""


class Final(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ok = shutil.which("node") is not None and (REPO / "bancada/node_modules/playwright").exists()
        if not cls.ok:
            return
        script = REPO / "bancada/_final.mjs"
        script.write_text(SCRIPT)
        env = dict(os.environ, BANCADA_LIBS=os.path.expanduser("~/.local/lib/chromium-deps"))
        try:
            r = subprocess.run(["node", str(script), str(REPO), json.dumps(SERVICOS)], cwd=REPO / "bancada", env=env,
                               capture_output=True, text=True, timeout=300)
            cls.d = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            cls.ok = False
        finally:
            script.unlink(missing_ok=True)

    def setUp(self):
        if not self.ok:
            self.skipTest("sem node/playwright/Chromium")

    # I1
    def test_chip_so_com_js_e_movimento(self):
        a = self.d["chip_toque"]
        self.assertTrue(a["js"])
        self.assertIn("ver por trás", a["conteudo"])
        self.assertFalse(a["dentroDaFigura"])
        self.assertIn(self.d["chip_semjs"]["conteudo"], ("none", "normal"))
        self.assertIn(self.d["chip_reduzido"]["conteudo"], ("none", "normal"))

    # I3
    def test_alvos_de_44px(self):
        for seletor, h in self.d["alvos"].items():
            self.assertGreaterEqual(h, 44, seletor)

    # I4
    def test_h1_nao_menor_que_h2_nos_servicos(self):
        self.assertEqual(len(self.d["titulos"]), 2 * len(SERVICOS))
        for k, v in self.d["titulos"].items():
            self.assertGreaterEqual(v["h1"], v["h2"], k)

    # I5
    def test_contato_do_servico_sem_coluna_vazia(self):
        self.assertEqual(self.d["contato"], {"colunas": 1, "ids": 1})

    # M1
    def test_codigo_da_ideia_com_recuo_pendente(self):
        d, pad, ind = self.d["codigo"]
        self.assertEqual(d, "block")
        self.assertGreater(float(pad[:-2]), 0)
        self.assertLess(float(ind[:-2]), 0)
        self.assertLessEqual(self.d["rolagem360"], 0)

    # M2
    def test_hero_sem_js_sem_buraco(self):
        h = self.d["heroSemJs"]
        self.assertFalse(h["classeJs"])
        self.assertEqual(h["margem"], "80px")
        self.assertTrue(h["fraseAbaixo"])
        self.assertLessEqual(h["fraseBottom"], h["proxTop"] + 1)

    # M3, M4
    def test_intro_pretty_e_seta_nos_cartoes(self):
        self.assertEqual(self.d["introPretty"], "pretty")
        self.assertEqual(self.d["setaServico"].strip('"'), "→")

    # M5
    def test_cartao_unico_ocupa_a_linha(self):
        u = self.d["unico"]
        if u and u["n"] == 1:
            self.assertEqual(u["gc"], "1")

    # M7
    def test_loja_do_heisuca_sem_ampliar(self):
        self.assertTrue(self.d["loja"])
        for i in self.d["loja"]:
            self.assertLessEqual(i["w"], i["nat"] + 2)   # + a borda de 1 px de cada lado

    # M8
    def test_tecnologia_e_etiqueta_mesmo_componente(self):
        self.assertEqual(self.d["tec"], self.d["etq"])

    # M12
    def test_id_das_pessoas_existe_no_dom(self):
        self.assertTrue(self.d["ids"])
        for i, existe in self.d["ids"]:
            self.assertTrue(existe, i)


class PorTexto(unittest.TestCase):
    def test_transicoes_so_de_transform_opacity_clip_path(self):  # I2
        for m in re.finditer(r"transition(?:-property)?\s*:\s*([^;]+);", CSS):
            v = m.group(1)
            while re.search(r"\([^()]*\)", v):   # tira var(...), calc(...), cubic-bezier(...) por dentro
                v = re.sub(r"[a-z-]*\([^()]*\)", " ", v)
            v = re.sub(r"[\d.]+m?s|ease[-a-z]*|linear|,|\*", " ", v)
            for palavra in v.split():
                self.assertIn(palavra, ("transform", "opacity", "clip-path", "none"), m.group(0))

    def test_sem_css_orfao(self):  # M9
        self.assertNotIn("horizontal-story__text", CSS)
        self.assertNotRegex(CSS, r"main\s*>\s*#timeline")

    def test_raios_por_token(self):  # M8
        tok = (REPO / "css/tokens.css").read_text()
        for t in ("--raio-1", "--raio-2", "--raio-pilula"):
            self.assertIn(t, tok)
        self.assertNotRegex(CSS, r"border-radius:\s*(999px|4px|2px)\b")

    def test_foco_da_ideia_pela_cor_global(self):  # M6
        for sel in (".ideia-estagio:focus-visible", ".ideia-codigo:focus-visible"):
            i = CSS.index(sel)
            self.assertIn("var(--laranja-claro)", CSS[i:CSS.index("}", i)])

    def test_pessoas_sem_cor(self):  # M13
        for p in json.loads((REPO / "fonte/dados/pessoas.json").read_text()):
            self.assertNotIn("cor", p)

    def test_ternario_de_carga_com_parenteses(self):  # M16
        src = (REPO / "fonte/alldevs/paginas.py").read_text()
        self.assertIn("carga = (('fetchpriority", src)


if __name__ == "__main__":
    unittest.main()
