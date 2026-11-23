// Bancada de medição do site ALL.dev. Uso: node bancada/rodar.mjs --url <base> --saida <pasta>
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { launch } from 'chrome-launcher';
import lighthouse from 'lighthouse';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { medePaleta } from './paleta.mjs';

const arg = (n) => { const i = process.argv.indexOf('--' + n); return i > 0 ? process.argv[i + 1] : null; };
const base = (arg('url') || '').replace(/\/+$/, '');
const saida = arg('saida');
if (!base || !saida) { console.error('uso: node bancada/rodar.mjs --url <base> --saida <pasta>'); process.exit(2); }
fs.mkdirSync(saida, { recursive: true });
const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const origem = new URL(base).origin;
const esperados = JSON.parse(fs.readFileSync(path.join(raiz, 'fonte/dados/projetos.json'), 'utf8')).filter((p) => p.visivel !== false).length;

const metas = {
  capturas: 'Capturas em 430 e 1440 px',
  axe: 'axe: zero problemas serious/critical',
  semjs: 'Sem JS: título, contato e (em /projetos/) todos os cards',
  rolagem: 'Sem rolagem horizontal em 430 px',
  links: 'Links internos respondem 200, sem redirecionamento',
  movimento: 'reducedMotion: nenhum transform após 1 s',
  paleta: 'Paleta: Ctrl K, seta, Enter navega e Esc devolve o foco (1440 px); toque na pílula (412 px); axe aberta; reduced-motion; sem rede',
  lighthouse: 'Lighthouse móvel: LCP < 2500 ms e CLS < 0,05',
};
const res = {}; for (const k in metas) res[k] = {};
const ok = (k, pg, passou, det) => { res[k][pg] = { passou, det }; };
const nome = (u) => new URL(u).pathname.replace(/^\/|\/$/g, '').replace(/[^\w.-]+/g, '_') || 'home';
const local = (u) => { const x = new URL(u); return origem + x.pathname + x.search; };
const get = (u) => fetch(u, { redirect: 'manual' });
const falha1 = (e) => String(e && e.message || e).split('\n')[0];

// Conjunto de páginas: sitemap (origem reescrita) + links internos (um nível).
const reescreve = (h, de) => { try { const u = new URL(h, de); return u.origin === origem || u.origin === 'https://all.dev.br' ? origem + u.pathname + u.search : null; } catch { return null; } };
const refs = (html) => [...html.matchAll(/(?:href|src)=(?:"([^"]*)"|'([^']*)')/g)].map((m) => (m[1] ?? m[2]).split('#')[0]).filter((h) => h && !/^(mailto:|tel:|javascript:|data:)/i.test(h));
const smr = await get(base + '/sitemap.xml');
if (smr.status !== 200) { console.error('sitemap.xml respondeu ' + smr.status); process.exit(2); }
const sm = await smr.text();
const paginas = new Set([...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => local(m[1])));
const extra = new Set();
for (const p of [...paginas]) {
  const r = await get(p);
  if (r.status === 200) refs(await r.text()).map((h) => reescreve(h, p)).filter((u) => u && (u.endsWith('.html') || u.endsWith('/')))
    .forEach((u) => extra.add(new URL(u).origin + new URL(u).pathname));
}
const lista = [...new Set([...paginas, ...extra])].sort();
console.log(`${lista.length} páginas`);
const rot = (u) => new URL(u).pathname;

// BANCADA_LIBS (opcional): diretório de .so extras, junto ao LD_LIBRARY_PATH só do navegador.
const envNav = { ...process.env };
if (process.env.BANCADA_LIBS) envNav.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');

// Executável do Lighthouse: CHROME_PATH, senão o chrome-headless-shell da mesma revisão do Chromium do Playwright.
function achaExe() {
  if (process.env.CHROME_PATH) return { exe: process.env.CHROME_PATH, shell: /headless[-_]shell/.test(process.env.CHROME_PATH) };
  const completo = chromium.executablePath();
  const cache = path.dirname(path.dirname(path.dirname(completo)));
  const rev = path.basename(path.dirname(path.dirname(completo))).replace(/^chromium-/, '');
  const dir = path.join(cache, 'chromium_headless_shell-' + rev);
  if (fs.existsSync(dir)) {
    for (const sub of fs.readdirSync(dir)) {
      for (const nomeBin of ['chrome-headless-shell', 'chrome-headless-shell.exe']) {
        const f = path.join(dir, sub, nomeBin);
        if (fs.existsSync(f)) return { exe: f, shell: true };
      }
    }
  }
  return { exe: completo, shell: false };
}
const { exe, shell } = achaExe();

const navegador = await chromium.launch({ env: envNav });
const status = (resp) => (resp && resp.status() === 200 ? null : 'página respondeu ' + (resp ? resp.status() : 'sem resposta'));
const comCtx = async (opts, fn) => { const ctx = await navegador.newContext(opts); try { return await fn(await ctx.newPage()); } finally { await ctx.close(); } };
const marca = (pg, chaves, e) => chaves.forEach((k) => { if (!res[k][pg]) ok(k, pg, false, falha1(e)); });

try {
  for (const url of lista) {
    const pg = rot(url), n = nome(url);
    console.log('>', pg);
    // capturas, rolagem e axe (axe em 430 e 1440 px)
    try {
      const axeRes = [];
      for (const [w, h] of [[430, 900], [1440, 900]]) {
        await comCtx({ viewport: { width: w, height: h } }, async (p) => {
          const e = status(await p.goto(url, { waitUntil: 'networkidle' }));
          if (e) throw new Error(e);
          await p.screenshot({ path: path.join(saida, `${n}-${w}.png`), fullPage: true });
          if (w === 430) {
            const [sw, cw] = await p.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
            ok('rolagem', pg, sw <= cw, `scrollWidth ${sw} / clientWidth ${cw}`);
          }
          const r = await new AxeBuilder({ page: p }).analyze();
          const gr = r.violations.filter((v) => ['serious', 'critical'].includes(v.impact));
          axeRes.push([w, gr, r.violations.length]);
        });
      }
      const graves = axeRes.flatMap(([w, gr]) => gr.map((v) => `${v.id} (${v.impact}, ${v.nodes.length}, ${w} px)`));
      ok('axe', pg, graves.length === 0, graves.length ? graves.join('; ') : `0 graves em 430 e 1440 px (${axeRes[0][2]}/${axeRes[1][2]} leves)`);
      ok('capturas', pg, true, `${n}-430.png, ${n}-1440.png`);
    } catch (e) { marca(pg, ['capturas', 'rolagem', 'axe'], e); }

    // sem JS
    try {
      await comCtx({ javaScriptEnabled: false }, async (p) => {
        const e = status(await p.goto(url));
        if (e) throw new Error(e);
        const t = (await p.title()).trim();
        const h1 = ((await p.locator('h1').first().textContent()) || '').trim();
        const h1vis = await p.locator('h1').first().isVisible();
        const contatos = p.locator('a[href^="mailto:"], a[href*="wa.me"], #contato');
        let vis = 0; const tot = await contatos.count();
        for (let i = 0; i < tot; i++) if (await contatos.nth(i).isVisible()) vis++;
        const falhas = [];
        if (!t || !h1 || !h1vis) falhas.push('sem título/h1 visível');
        if (!vis) falhas.push(`sem contato visível (${tot} no DOM)`);
        let det = `h1 "${h1}", contatos visíveis ${vis}/${tot}`;
        if (pg === '/projetos/') {
          const cards = p.locator('article[data-slug]'); const c = await cards.count();
          let cv = 0; for (let i = 0; i < c; i++) if (await cards.nth(i).isVisible()) cv++;
          det += `, cards visíveis ${cv}/${esperados}`;
          if (cv !== esperados || c !== esperados) falhas.push(`cards ${cv} visíveis (${c} no DOM) de ${esperados}`);
        }
        ok('semjs', pg, !falhas.length, falhas.length ? falhas.join('; ') : det);
      });
    } catch (e) { marca(pg, ['semjs'], e); }

    // movimento reduzido
    try {
      await comCtx({ reducedMotion: 'reduce' }, async (p) => {
        const e = status(await p.goto(url, { waitUntil: 'networkidle' }));
        if (e) throw new Error(e);
        await p.waitForTimeout(1000);
        const of = await p.evaluate(() => [...document.querySelectorAll('*')].map((el) => [el, getComputedStyle(el).transform])
          .filter(([, t]) => t && t !== 'none').map(([el, t]) => {
            const s = el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + [...el.classList].map((c) => '.' + c).join('');
            return `${s} = ${t}`;
          }));
        ok('movimento', pg, of.length === 0, of.length ? `${of.length}: ` + of.slice(0, 5).join('; ') : 'nenhum');
      });
    } catch (e) { marca(pg, ['movimento'], e); }

    // paleta de comandos (bancada/paleta.mjs; ~10 s por página, o cabeçalho a tem em todas)
    try {
      const r = await get(url);
      if (r.status !== 200) throw new Error('página respondeu ' + r.status);
      const m = await medePaleta(navegador, url); ok('paleta', pg, m.passou, m.det);
    } catch (e) { marca(pg, ['paleta'], e); }

    // links internos
    try {
      const r = await get(url);
      if (r.status !== 200) throw new Error('página respondeu ' + r.status);
      const alvos = new Set(refs(await r.text()).map((h) => reescreve(h, url)).filter(Boolean));
      if (!alvos.size) throw new Error('nenhum link interno extraído (0 alvos)');
      const ruins = [];
      for (const a of [...alvos].sort()) {
        const x = await get(a);
        if (x.status !== 200) ruins.push(`${new URL(a).pathname} -> ${x.status}`);
      }
      ok('links', pg, ruins.length === 0, ruins.length ? ruins.join('; ') : `${alvos.size} ok`);
    } catch (e) { marca(pg, ['links'], e); }

    // Lighthouse (predefinição móvel padrão: 4G simulado)
    let chrome;
    try {
      chrome = await launch({ chromePath: exe, chromeFlags: ['--no-sandbox', ...(shell ? [] : ['--headless=new'])], envVars: { ...envNav } });
      const lh = await lighthouse(url, { port: chrome.port, onlyCategories: ['performance'], output: 'json', logLevel: 'error' });
      if (lh.lhr.runtimeError) throw new Error('Lighthouse: ' + lh.lhr.runtimeError.code);
      const st = lh.lhr.audits['largest-contentful-paint'], sc = lh.lhr.audits['cumulative-layout-shift'];
      const lcp = st && st.numericValue, cls = sc && sc.numericValue;
      if (!Number.isFinite(lcp) || !Number.isFinite(cls)) throw new Error('Lighthouse sem LCP/CLS válidos');
      ok('lighthouse', pg, lcp < 2500 && cls < 0.05, `LCP ${Math.round(lcp)} ms, CLS ${cls.toFixed(3)}`);
    } catch (e) { marca(pg, ['lighthouse'], e); }
    finally { if (chrome) await chrome.kill(); }
  }
} finally { await navegador.close(); }

// Relatório. Página sem linha numa meta conta como falha.
const esc = (s) => String(s).replace(/\|/g, '\\|');
let falhou = false;
const resumo = [], tabelas = [];
for (const [k, titulo] of Object.entries(metas)) {
  const linhas = lista.map((u) => [rot(u), res[k][rot(u)] || { passou: false, det: 'sem medição' }]);
  const f = linhas.filter(([, v]) => !v.passou);
  if (f.length) falhou = true;
  resumo.push(`| ${titulo} | ${f.length ? 'FALHA' : 'PASSA'} | ${f.length}/${lista.length} páginas |`);
  tabelas.push(`## ${titulo}\n\n| Página | Resultado | Detalhe |\n|---|---|---|\n` +
    linhas.map(([p, v]) => `| ${p} | ${v.passou ? 'passa' : 'FALHA'} | ${esc(v.det)} |`).join('\n'));
}
const rc = falhou ? 1 : 0;
const md = `# Relatório da bancada\n\nBase: ${base} — ${lista.length} páginas — gerado em ${new Date().toISOString()}\n\n` +
  `## Resumo\n\n| Meta | Resultado | Falhas |\n|---|---|---|\n${resumo.join('\n')}\n\nCódigo de saída: **${rc}**\n\n` +
  tabelas.join('\n\n') + '\n';
fs.writeFileSync(path.join(saida, 'RELATORIO.md'), md);
console.log(resumo.join('\n'), '\nrc', rc);
process.exit(rc);
