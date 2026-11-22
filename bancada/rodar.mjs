// Bancada de medição do site ALL.dev. Uso: node bancada/rodar.mjs --url <base> --saida <pasta>
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { launch } from 'chrome-launcher';
import lighthouse from 'lighthouse';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

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
  lighthouse: 'Lighthouse móvel: LCP < 2500 ms e CLS < 0,05',
};
const res = {}; for (const k in metas) res[k] = {};
const ok = (k, pg, passou, det) => { res[k][pg] = { passou, det }; };
const nome = (u) => new URL(u).pathname.replace(/^\/|\/$/g, '').replace(/[^\w.-]+/g, '_') || 'home';
const local = (u) => { const x = new URL(u); return origem + x.pathname + x.search; };
const get = (u) => fetch(u, { redirect: 'manual' });

// Conjunto de páginas: sitemap (origem reescrita) + links internos (um nível).
const sm = await (await get(base + '/sitemap.xml')).text();
const paginas = new Set([...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => local(m[1])));
const internos = (html, de) => [...html.matchAll(/href="([^"#]+)(?:#[^"]*)?"/g)].map((m) => m[1])
  .filter((h) => !/^(mailto:|tel:|javascript:)/i.test(h))
  .map((h) => { try { return new URL(h, de); } catch { return null; } })
  .filter((u) => u && u.origin === origem && (u.pathname.endsWith('.html') || u.pathname.endsWith('/')))
  .map((u) => origem + u.pathname);
const extra = new Set();
for (const p of [...paginas]) {
  const r = await get(p);
  if (r.status === 200) internos(await r.text(), p).forEach((u) => extra.add(u));
}
const lista = [...new Set([...paginas, ...extra])].sort();
console.log(`${lista.length} páginas`);
const rot = (u) => new URL(u).pathname;

// BANCADA_LIBS (opcional): diretório de .so extras, junto ao LD_LIBRARY_PATH só do navegador.
const envNav = { ...process.env };
if (process.env.BANCADA_LIBS) envNav.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');
const navegador = await chromium.launch({ env: envNav });
// Lighthouse usa o mesmo chrome-headless-shell do Playwright (pasta irmã do executável completo).
const cache = path.dirname(path.dirname(path.dirname(chromium.executablePath())));
const hs = fs.readdirSync(cache).filter((d) => d.startsWith('chromium_headless_shell-')).sort().pop();
const exe = path.join(cache, hs, 'chrome-headless-shell-linux64', 'chrome-headless-shell');

for (const url of lista) {
  const pg = rot(url), n = nome(url);
  console.log('>', pg);
  // capturas, rolagem e axe
  try {
    for (const [w, h] of [[430, 900], [1440, 900]]) {
      const ctx = await navegador.newContext({ viewport: { width: w, height: h } });
      const p = await ctx.newPage();
      await p.goto(url, { waitUntil: 'networkidle' });
      await p.screenshot({ path: path.join(saida, `${n}-${w}.png`), fullPage: true });
      if (w === 430) {
        const [sw, cw] = await p.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
        ok('rolagem', pg, sw <= cw, `scrollWidth ${sw} / clientWidth ${cw}`);
        const r = await new AxeBuilder({ page: p }).analyze();
        const gr = r.violations.filter((v) => ['serious', 'critical'].includes(v.impact));
        ok('axe', pg, gr.length === 0, gr.length ? gr.map((v) => `${v.id} (${v.impact}, ${v.nodes.length})`).join('; ') : `0 graves (${r.violations.length} leves)`);
      }
      await ctx.close();
    }
    ok('capturas', pg, true, `${n}-430.png, ${n}-1440.png`);
  } catch (e) { ok('capturas', pg, false, String(e.message).split('\n')[0]); }

  // sem JS
  try {
    const ctx = await navegador.newContext({ javaScriptEnabled: false });
    const p = await ctx.newPage();
    await p.goto(url);
    const titulo = await p.evaluate(() => ({ t: document.title.trim(), h1: (document.querySelector('h1') || {}).textContent?.trim() || '' }));
    const contato = await p.locator('a[href^="mailto:"], a[href*="wa.me"], #contato').count();
    const falhas = [];
    if (!titulo.t || !titulo.h1) falhas.push('sem título/h1');
    if (!contato) falhas.push('sem contato');
    let det = `h1 "${titulo.h1}", contato ${contato}`;
    if (pg === '/projetos/') {
      const c = await p.locator('article[data-slug]').count();
      det += `, cards ${c}/${esperados}`;
      if (c !== esperados) falhas.push(`cards ${c} de ${esperados}`);
    }
    ok('semjs', pg, !falhas.length, falhas.length ? falhas.join('; ') : det);
    await ctx.close();
  } catch (e) { ok('semjs', pg, false, String(e.message).split('\n')[0]); }

  // movimento reduzido
  try {
    const ctx = await navegador.newContext({ reducedMotion: 'reduce' });
    const p = await ctx.newPage();
    await p.goto(url, { waitUntil: 'networkidle' });
    await p.waitForTimeout(1000);
    const of = await p.evaluate(() => [...document.querySelectorAll('*')].map((el) => [el, getComputedStyle(el).transform])
      .filter(([, t]) => t && t !== 'none').map(([el, t]) => {
        const s = el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + [...el.classList].map((c) => '.' + c).join('');
        return `${s} = ${t}`;
      }));
    ok('movimento', pg, of.length === 0, of.length ? `${of.length}: ` + of.slice(0, 5).join('; ') : 'nenhum');
    await ctx.close();
  } catch (e) { ok('movimento', pg, false, String(e.message).split('\n')[0]); }

  // links internos
  try {
    const r = await get(url);
    const alvos = new Set();
    const html = await r.text();
    for (const m of html.matchAll(/(?:href|src)="([^"#]+)(?:#[^"]*)?"/g)) {
      try { const u = new URL(m[1], url); if (u.origin === origem) alvos.add(origem + u.pathname + u.search); } catch { /* ignora */ }
    }
    const ruins = [];
    for (const a of [...alvos].sort()) {
      const x = await get(a);
      if (x.status !== 200) ruins.push(`${new URL(a).pathname} -> ${x.status}`);
    }
    ok('links', pg, ruins.length === 0, ruins.length ? ruins.join('; ') : `${alvos.size} ok`);
  } catch (e) { ok('links', pg, false, String(e.message).split('\n')[0]); }

  // Lighthouse (predefinição móvel padrão: 4G simulado)
  let chrome;
  try {
    chrome = await launch({ chromePath: exe, chromeFlags: ['--headless=new', '--no-sandbox'], envVars: { LD_LIBRARY_PATH: envNav.LD_LIBRARY_PATH || '' } });
    const lh = await lighthouse(url, { port: chrome.port, onlyCategories: ['performance'], output: 'json', logLevel: 'error' });
    const a = lh.lhr.audits;
    const lcp = a['largest-contentful-paint'].numericValue, cls = a['cumulative-layout-shift'].numericValue;
    ok('lighthouse', pg, lcp < 2500 && cls < 0.05, `LCP ${Math.round(lcp)} ms, CLS ${cls.toFixed(3)}`);
  } catch (e) { ok('lighthouse', pg, false, String(e.message).split('\n')[0]); }
  finally { if (chrome) await chrome.kill(); }
}
await navegador.close();

// Relatório
const esc = (s) => String(s).replace(/\|/g, '\\|');
let falhou = false;
const resumo = [], tabelas = [];
for (const [k, titulo] of Object.entries(metas)) {
  const linhas = Object.entries(res[k]).sort();
  const f = linhas.filter(([, v]) => !v.passou);
  const passa = linhas.length > 0 && f.length === 0;
  if (!passa) falhou = true;
  resumo.push(`| ${titulo} | ${passa ? 'PASSA' : 'FALHA'} | ${f.length}/${lista.length} páginas |`);
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
