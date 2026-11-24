// Bancada da seção "Da ideia ao ar". Uso: node bancada/ideia.mjs --url <base> [--capturas <pasta>] [--so <regex>]
// Cenários: desktop-pin, celular-sem-pin, reduzido, cls. Um por linha ("ok" ou "FALHA"); rc 1 se algum falhar.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { esperaPreloader } from './paleta.mjs';

const arg = (n) => { const i = process.argv.indexOf('--' + n); return i > 0 ? process.argv[i + 1] : null; };
const base = (arg('url') || '').replace(/\/+$/, '');
const capturas = arg('capturas');
const so = arg('so');
if (!base) { console.error('uso: node bancada/ideia.mjs --url <base> [--capturas <pasta>] [--so <regex>]'); process.exit(2); }

const envNav = { ...process.env };
if (process.env.BANCADA_LIBS) envNav.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');
const navegador = await chromium.launch({ env: envNav });

const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
const DESK = { viewport: { width: 1440, height: 900 } };
const MOVEL = (w) => ({ viewport: { width: w, height: 800 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
const SEC = '#ideia';

async function abre(opts, fn) {
  const ctx = await navegador.newContext(opts);
  const p = await ctx.newPage();
  const erros = [];
  p.on('pageerror', (e) => erros.push(String(e.message || e)));
  try {
    await p.addInitScript(() => {
      window.__cls = 0;
      try {
        new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
          .observe({ type: 'layout-shift', buffered: true });
      } catch (x) { /* sem suporte */ }
    });
    await p.goto(base + '/', { waitUntil: 'networkidle' });
    await esperaPreloader(p);
    await fn(p, erros);
    if (erros.length) throw new Error('erro de página: ' + erros[0]);
  } finally { await ctx.close(); }
}

// Rola até a fração (0..1) do percurso do pin (desktop) e espera o scrub assentar.
const noPin = async (p, f) => {
  await p.evaluate((f) => {
    const st = window.ScrollTrigger.getAll().find((s) => s.pin);
    window.scrollTo(0, st.start + (st.end - st.start) * f);
  }, f);
  await dorme(1200);
};
const info = (p) => p.evaluate((SEC) => {
  const s = document.querySelector(SEC), r = s.getBoundingClientRect();
  const lis = [...s.querySelectorAll('.ideia-estagio')];
  return {
    pos: getComputedStyle(s).position, top: Math.round(r.top), pin: s.classList.contains('ideia-pin'),
    spacer: !!document.querySelector('.pin-spacer'),
    ativo: lis.findIndex((e) => e.classList.contains('ativo')),
    op: lis.map((e) => Number(getComputedStyle(e).opacity).toFixed(2)),
    visto: lis.filter((e) => e.classList.contains('ideia-visto')).length,
    oculto: lis.filter((e) => e.classList.contains('ideia-oculto')).length,
  };
}, SEC);

const defs = [];
const cena = (nome, fn) => defs.push([nome, fn]);

cena('desktop-pin', (det) => abre(DESK, async (p) => {
  const a = await (async () => { await noPin(p, 0.05); return info(p); })();
  if (!a.pin || !a.spacer) throw new Error('a seção não ganhou o pin no desktop: ' + JSON.stringify(a));
  if (a.pos !== 'fixed' || Math.abs(a.top) > 2) throw new Error(`seção não está presa (position ${a.pos}, top ${a.top})`);
  const b = await (async () => { await noPin(p, 0.5); return info(p); })();
  const c = await (async () => { await noPin(p, 0.95); return info(p); })();
  if (b.pos !== 'fixed' || c.pos !== 'fixed') throw new Error('a seção soltou no meio do percurso');
  if (!(a.ativo === 0 && b.ativo > a.ativo && c.ativo > b.ativo)) throw new Error(`estágio ativo não avança: ${a.ativo}, ${b.ativo}, ${c.ativo}`);
  det(`presa (fixed, top ${a.top}); ativo ${a.ativo} -> ${b.ativo} -> ${c.ativo}; opacidades no meio ${b.op.join('/')}`);
}));

cena('celular-sem-pin', (det) => abre(MOVEL(360), async (p) => {
  const total = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < total; y += 300) { await p.evaluate((y) => window.scrollTo(0, y), y); await dorme(120); }
  await dorme(900);
  const i = await info(p);
  const fixos = await p.evaluate((SEC) => [...document.querySelectorAll(SEC + ', ' + SEC + ' *')].filter((e) => getComputedStyle(e).position === 'fixed').length, SEC);
  if (i.pin || i.spacer || i.pos === 'fixed' || fixos) throw new Error('há pin no celular: ' + JSON.stringify({ ...i, fixos }));
  if (i.visto !== 5) throw new Error(`entraram ${i.visto} de 5 estágios ao rolar`);
  det(`sem pin-spacer, ${fixos} elementos fixed na seção; ${i.visto} estágios entraram pelo IntersectionObserver`);
}));

cena('reduzido', (det) => abre({ ...DESK, reducedMotion: 'reduce' }, async (p) => {
  const i = await info(p);
  const r = await p.evaluate((SEC) => [...document.querySelectorAll(SEC + ' .ideia-estagio')].map((e) => {
    const c = getComputedStyle(e), cod = e.querySelector('.ideia-codigo'), b = e.getBoundingClientRect();
    return { op: c.opacity, tr: c.transform, vis: b.width > 0 && b.height > 0 && c.visibility !== 'hidden', clip: cod ? getComputedStyle(cod).clipPath : 'none' };
  }), SEC);
  if (i.pin || i.spacer || i.oculto || i.visto) throw new Error('animação ligada com reduced-motion: ' + JSON.stringify(i));
  if (r.length !== 5 || r.some((x) => !x.vis || x.op !== '1' || x.tr !== 'none' || x.clip !== 'none')) throw new Error('estágios não estão estáticos: ' + JSON.stringify(r));
  det('5 estágios visíveis, opacidade 1, sem transform, sem clip-path, sem pin');
}));

cena('cls', async (det) => {
  const medidas = [];
  for (const [nome, o] of [['1440', DESK], ['430', MOVEL(430)]]) {
    await abre(o, async (p) => {
      const total = await p.evaluate(() => document.documentElement.scrollHeight);
      for (let y = 0; y < total + 3000; y += 250) { await p.evaluate((y) => window.scrollTo(0, y), y); await dorme(60); }
      await dorme(800);
      medidas.push([nome, await p.evaluate(() => window.__cls)]);
    });
  }
  const pior = Math.max(...medidas.map((m) => m[1]));
  const txt = medidas.map(([n, v]) => `${n} px: ${v.toFixed(4)}`).join('; ');
  if (!(pior < 0.05)) throw new Error('CLS da home >= 0,05 (' + txt + ')');
  det('CLS da home ' + txt);
});

async function tiraCapturas(pasta) {
  fs.mkdirSync(pasta, { recursive: true });
  await abre(DESK, async (p) => {
    await noPin(p, 0.7);   // estágio do código, no meio da digitação
    await p.screenshot({ path: path.join(pasta, 'ideia-1440.png') });
  });
  for (const w of [430, 360]) {
    await abre(MOVEL(w), async (p) => {
      await p.evaluate(() => document.querySelector('#ideia').scrollIntoView());
      const alt = await p.evaluate(() => document.querySelector('#ideia').offsetHeight);
      for (let y = 0; y < alt + 800; y += 300) { await p.evaluate((d) => window.scrollBy(0, d), 300); await dorme(150); }
      await dorme(900);
      const b = await p.evaluate(() => { const r = document.querySelector('#ideia').getBoundingClientRect(); return { y: r.top + scrollY, h: r.height }; });
      await p.screenshot({ path: path.join(pasta, `ideia-${w}.png`), fullPage: true, clip: { x: 0, y: b.y, width: w, height: b.h } });
    });
  }
}

let falhou = 0;
for (const [nome, fn] of defs) {
  if (so && !new RegExp(so).test(nome)) continue;
  let det = '';
  try { await fn((d) => { det = d; }); console.log(`ok     ${nome}: ${det}`); }
  catch (e) { falhou++; console.log(`FALHA  ${nome}: ${String(e && e.message || e).split('\n')[0]}`); }
}
if (capturas) {
  try { await tiraCapturas(capturas); console.log('capturas em ' + capturas); }
  catch (e) { falhou++; console.log('FALHA  capturas: ' + String(e && e.message || e).split('\n')[0]); }
}
await navegador.close();
process.exit(falhou ? 1 : 0);
