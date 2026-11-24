// Bancada de /projetos/ e dos cases. Uso: node bancada/projetos.mjs --url <base> --capturas <pasta>
// Cenários: filtro (com JS), sem-js, palco (hover a 1440), sticky (1440x900), 360 sem rolagem horizontal; capturas.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { esperaPreloader } from './paleta.mjs';

const arg = (n) => { const i = process.argv.indexOf('--' + n); return i > 0 ? process.argv[i + 1] : null; };
const base = (arg('url') || '').replace(/\/+$/, '');
const pasta = arg('capturas');
if (!base) { console.error('uso: node bancada/projetos.mjs --url <base> [--capturas <pasta>]'); process.exit(2); }
if (pasta) fs.mkdirSync(pasta, { recursive: true });
const env = { ...process.env };
if (process.env.BANCADA_LIBS) env.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');
const nav = await chromium.launch({ env });
let falhas = 0;
const rel = (nome, ok, det = '') => { console.log((ok ? 'ok    ' : 'FALHA ') + nome + (det ? ' ' + det : '')); if (!ok) falhas++; };
async function abre(url, opts, fn, js = true) {
  const ctx = await nav.newContext({ ...opts, javaScriptEnabled: js });
  const p = await ctx.newPage();
  const erros = []; p.on('pageerror', (e) => erros.push(String(e.message)));
  try { await p.goto(base + url, { waitUntil: 'networkidle' }); if (js) await esperaPreloader(p); await fn(p); if (erros.length) throw new Error(erros[0]); }
  finally { await ctx.close().catch(() => {}); }
}
const cap = (p, nome) => pasta ? p.screenshot({ path: path.join(pasta, nome), fullPage: true }) : null;
const vis = (p) => p.evaluate(() => [...document.querySelectorAll('[data-lista-projetos] > article')].filter((a) => !a.hidden && a.offsetParent).map((a) => a.dataset.tipo));

for (const w of [1440, 430]) {
  await abre('/projetos/', { viewport: { width: w, height: 900 } }, async (p) => {
    rel(`filtro-visivel-${w}`, await p.locator('.filtro-tipos').isVisible());
    const todos = (await vis(p)).length;
    const btns = await p.locator('.filtro-tipos button').evaluateAll((bs) => bs.map((b) => { const r = b.getBoundingClientRect(); return { h: r.height, w: r.width, t: b.dataset.tipo, a: b.getAttribute('aria-pressed') }; }));
    rel(`filtro-alvos-44-${w}`, btns.every((b) => b.h >= 44 && b.w >= 44), JSON.stringify(btns.map((b) => [Math.round(b.w), Math.round(b.h)])));
    await p.locator('.filtro-tipos button[data-tipo="app"]').click();
    const v = await vis(p);
    rel(`filtro-app-${w}`, v.length > 0 && v.length < todos && v.every((t) => t === 'app'), `${v.length}/${todos}`);
    rel(`filtro-aria-${w}`, (await p.locator('.filtro-tipos button[aria-pressed="true"]').count()) === 1);
    await p.locator('.filtro-tipos button[data-tipo="todos"]').click();
    rel(`filtro-todos-${w}`, (await vis(p)).length === todos);
    await cap(p, `projetos-${w}.png`);
    const sx = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    rel(`sem-rolagem-h-${w}`, sx <= 0, String(sx));
  });
}
await abre('/projetos/', { viewport: { width: 1440, height: 900 } }, async (p) => {
  rel('sem-js-filtro-oculto', !(await p.locator('.filtro-tipos').isVisible()) && (await vis(p)).length >= 6);
}, false);
await abre('/projetos/', { viewport: { width: 360, height: 800 } }, async (p) => {
  rel('sem-rolagem-h-360-lista', (await p.evaluate(() => document.documentElement.scrollWidth - innerWidth)) <= 0);
});

for (const slug of ['amott', 'prosup', 'heisuca', 'cgflix-lite', 'fakly', 'sendany']) {
  for (const w of [1440, 430, 360]) {
    await abre(`/projetos/${slug}/`, { viewport: { width: w, height: 900 } }, async (p) => {
      const sx = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      rel(`case-${slug}-sem-rolagem-h-${w}`, sx <= 0, String(sx));
      if (w !== 360 && ['amott', 'prosup'].includes(slug)) await cap(p, `case-${slug}-${w}.png`);
      if (w === 1440) {
        const pos = await p.evaluate(() => getComputedStyle(document.querySelector('.case-texto')).position);
        const a = await p.evaluate(() => document.querySelector('.case-texto').getBoundingClientRect().top);
        await p.evaluate(() => scrollTo(0, 300)); await p.waitForTimeout(300);
        const b = await p.evaluate(() => document.querySelector('.case-texto').getBoundingClientRect().top);
        // o preso só tem o que fazer quando a coluna das capturas é mais alta que a do texto; senão a coluna do texto define a linha e rola junto
        const util = await p.evaluate(() => { const t = document.querySelector('.case-texto'), c = document.querySelector('.case'); const col2 = [...c.children].find((e) => e !== t); return col2 && col2.offsetHeight > t.offsetHeight + 100; });
        rel(`case-${slug}-sticky-1440`, pos === 'sticky' && (!util || (b >= 0 && b <= 40)), `pos=${pos} util=${util} topo ${Math.round(a)}->${Math.round(b)}`);
      }
      if (w === 430) rel(`case-${slug}-sem-sticky-430`, (await p.evaluate(() => getComputedStyle(document.querySelector('.case-texto')).position)) !== 'sticky');
    });
  }
}
await abre('/projetos/amott/', { viewport: { width: 1440, height: 900 } }, async (p) => {
  const f = p.locator('.case-palco'); await f.scrollIntoViewIfNeeded(); const b = await f.boundingBox();
  await p.mouse.move(b.x + b.width / 2, b.y + b.height / 2, { steps: 5 }); await p.waitForTimeout(700);
  const o = await p.evaluate(() => { const c = document.querySelector('.case-palco .cartao-por-tras'); const s = getComputedStyle(c); return { op: Number(s.opacity), r: parseFloat(s.getPropertyValue('--r')) || 0 }; });
  rel('palco-hover-1440', o.op > 0 && o.r > 0, JSON.stringify(o));
  if (pasta) await p.screenshot({ path: path.join(pasta, 'case-amott-palco-hover-1440.png') });
});
await abre('/projetos/prosup/', { viewport: { width: 1440, height: 900 } }, async (p) => {
  rel('prosup-sem-palco', (await p.locator('.case-palco').count()) === 0);
});
await nav.close();
process.exit(falhas ? 1 : 0);
