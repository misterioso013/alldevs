// Bancada de /projetos/ e dos cases. Uso: node bancada/projetos.mjs --url <base> --capturas <pasta>
// Cenários: filtro (com JS), sem-js, palco (hover a 1440), grade e fim do texto alcançável (1440x900 e 1440x1200), coluna única sem grade, 360 sem rolagem horizontal; capturas rolando a página.
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
const rolaTudo = async (p) => {
  // rola até o fim em passos e para em cada [data-revela] (o IntersectionObserver só revela o que entra na tela); depois volta ao topo
  await p.evaluate(async () => {
    const espera = (ms) => new Promise((r) => setTimeout(r, ms));
    const h = document.documentElement.scrollHeight;
    for (let y = 0; y < h; y += 300) { scrollTo({ top: y, behavior: 'instant' }); await espera(120); }
    for (const el of document.querySelectorAll('[data-revela], .projeto-cartao')) { if (el.hidden) continue; el.scrollIntoView({ block: 'center', behavior: 'instant' }); await espera(350); }
    scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }); await espera(300);
  });
  await p.waitForLoadState('networkidle').catch(() => {});
  await p.evaluate(async () => { await Promise.all([...document.images].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))); scrollTo({ top: 0, behavior: 'instant' }); });
  await p.waitForTimeout(700);
  const ocultos = await p.evaluate(() => [...document.querySelectorAll('[data-revela]')].filter((e) => !e.hidden && getComputedStyle(e).opacity < 0.99).length);
  rel('captura-sem-bloco-oculto', ocultos === 0, `${ocultos} ocultos`);
  // cartões de /projetos/: todos os .projeto-cartao não ocultos pelo filtro precisam estar visíveis (opacity > 0.9) e dentro do documento
  const c = await p.evaluate(() => { const l = [...document.querySelectorAll('.projeto-cartao')]; const H = document.documentElement.scrollHeight; const v = l.filter((e) => { const r = e.getBoundingClientRect(); return !e.closest('[hidden]') && getComputedStyle(e).opacity > 0.9 && r.height > 0 && r.top + scrollY < H; }); return [v.length, l.filter((e) => !e.closest('[hidden]')).length]; });
  if (c[1] > 0) rel('captura-cartoes-visiveis', c[0] === c[1], `${c[0]}/${c[1]} cartões visíveis`);
};
const cap = async (p, nome) => { if (!pasta) return; await rolaTudo(p); await p.screenshot({ path: path.join(pasta, nome), fullPage: true }); };
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

const info = (p) => p.evaluate(() => {
  const c = document.querySelector('.case'), t = document.querySelector('.case-texto');
  const cs = getComputedStyle(c), ts = getComputedStyle(t);
  const fim = [...t.querySelectorAll('a, button')].pop();
  return { unica: c.classList.contains('case-unica'), grade: cs.display === 'grid', pos: ts.position, fixa: !!document.querySelector('.case-telas-fixa'), telasPos: document.querySelector('.case-telas') ? getComputedStyle(document.querySelector('.case-telas')).position : null, th: t.offsetHeight, topo: t.getBoundingClientRect().top, temFim: !!fim, ih: innerHeight, palcoW: (document.querySelector('.case-palco') || { offsetWidth: 0 }).offsetWidth };
});
const fimAlcancavel = (p) => p.evaluate(async () => {
  const t = document.querySelector('.case-texto'); const fim = [...t.querySelectorAll('a, button')].pop();
  if (!fim) return { ok: false, r: 'sem link/botao no fim' };
  fim.scrollIntoView({ block: 'center', behavior: 'instant' }); await new Promise((r) => setTimeout(r, 400));
  const r = fim.getBoundingClientRect();
  return { ok: r.top >= 0 && r.bottom <= innerHeight, r: Math.round(r.top) + '..' + Math.round(r.bottom) + ' de ' + innerHeight };
});
// sticky da coluna de capturas: onde há a classe, rolar 600 px e o topo fica em 24 +-2 e o fundo cabe na janela; onde não há, position != sticky
async function provaTelas(p, slug, i) {
  if (!i.fixa) { rel(`case-${slug}-telas-sem-sticky-1440x900`, i.telasPos !== 'sticky', `telas=${i.telasPos}`); return; }
  await p.evaluate(() => scrollTo({ top: 0, behavior: 'instant' })); await p.waitForTimeout(200);
  await p.evaluate(() => scrollTo({ top: 600, behavior: 'instant' })); await p.waitForTimeout(500);
  const r = await p.evaluate(() => { const b = document.querySelector('.case-telas-fixa').getBoundingClientRect(); return { top: b.top, bottom: b.bottom, pos: getComputedStyle(document.querySelector('.case-telas-fixa')).position, ih: innerHeight }; });
  rel(`case-${slug}-telas-sticky-1440x900`, r.pos === 'sticky' && Math.abs(r.top - 24) <= 2 && r.bottom <= r.ih, JSON.stringify(r));
}
for (const slug of ['amott', 'prosup', 'heisuca', 'cgflix-lite', 'fakly', 'sendany']) {
  for (const w of [1440, 430, 360]) {
    await abre(`/projetos/${slug}/`, { viewport: { width: w, height: 900 } }, async (p) => {
      const sx = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      rel(`case-${slug}-sem-rolagem-h-${w}`, sx <= 0, String(sx));
      if (w !== 360 && ['amott', 'prosup', 'heisuca'].includes(slug)) await cap(p, `case-${slug}-${w}.png`);
      const i = await info(p);
      if (w === 1440) {
        const f = await fimAlcancavel(p);
        rel(`case-${slug}-fim-do-texto-alcancavel-1440x900`, f.ok, f.r);
        if (i.unica) {
          rel(`case-${slug}-coluna-unica-sem-grade-nem-sticky`, !i.grade && i.pos !== 'sticky' && i.palcoW > 800 && i.palcoW <= 960, `grade=${i.grade} pos=${i.pos} palco=${i.palcoW}`);
        } else {
          rel(`case-${slug}-duas-colunas-com-grade`, i.grade);
          rel(`case-${slug}-texto-nunca-sticky-1440x900`, i.pos !== 'sticky', `pos=${i.pos}`);
          await provaTelas(p, slug, i);
        }
      }
      if (w === 430) rel(`case-${slug}-sem-sticky-430`, i.pos !== 'sticky' && i.telasPos !== 'sticky' && !i.grade);
    });
  }
  // janela alta (1440x1200): texto nunca sticky e o fim do texto alcançável; coluna única segue sem grade
  await abre(`/projetos/${slug}/`, { viewport: { width: 1440, height: 1200 } }, async (p) => {
    const i = await info(p);
    rel(`case-${slug}-texto-nunca-sticky-1440x1200`, i.pos !== 'sticky' && (i.unica ? !i.grade : i.grade), `pos=${i.pos} grade=${i.grade}`);
    const f = await fimAlcancavel(p);
    rel(`case-${slug}-fim-do-texto-alcancavel-1440x1200`, f.ok, f.r);
  });
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
