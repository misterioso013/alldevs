// Bancada da seção "Da ideia ao ar". Uso: node bancada/ideia.mjs --url <base> [--capturas <pasta>] [--so <regex>]
// Cenários: desktop-pin, estados-por-progresso, estado-inicial, foco-vaza, foco-teclado, cabe-1280x600, codigo-celular, celular-sem-pin, reduzido, sem-js, cls. Um por linha ("ok" ou "FALHA"); rc 1 se algum falhar.
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

// Rola até a fração (0..1) do percurso do pin (desktop) e espera o scrub assentar (timeline alcança o progresso do scroll).
const assenta = (p) => p.waitForFunction(() => {
  const st = window.ScrollTrigger.getAll().find((s) => s.pin);
  return Math.abs(st.animation.progress() - st.progress) < 0.004;
}, null, { timeout: 8000 });
const noPin = async (p, f) => {
  await p.evaluate((f) => {
    const st = window.ScrollTrigger.getAll().find((s) => s.pin);
    window.scrollTo({ top: st.start + (st.end - st.start) * f, behavior: 'instant' });
  }, f);
  await p.waitForTimeout(80);
  await assenta(p);
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

const clipAberto = (c) => !!c && /^inset\(/.test(c) && c.slice(6, -1).split(/\s+/).every((v) => /^0(px|%)?$/.test(v));
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

cena('estados-por-progresso', (det) => abre(DESK, async (p) => {
  const ativos = [], cod = [];
  for (const f of [0.1, 0.3, 0.5, 0.7, 0.9]) {
    await noPin(p, f);
    const i = await info(p);
    ativos.push(i.ativo);
    cod.push(await p.evaluate(() => {
      const c = document.querySelector('#ideia .ativo .ideia-codigo code');
      return c ? getComputedStyle(c).clipPath : null;
    }));
    const op = i.op[i.ativo];
    if (op !== '1.00') throw new Error(`estágio ${i.ativo} com opacidade ${op} em ${f}`);
  }
  if (ativos.join() !== '0,1,2,3,4') throw new Error('ativos por progresso: ' + ativos.join());
  const c3 = cod[3];
  if (!clipAberto(c3)) throw new Error('código não está 100% revelado no estágio do código: ' + c3);
  det(`ativo ${ativos.join('/')}; clip-path do código no estágio 3: ${c3}`);
}));

cena('estado-inicial', (det) => abre(DESK, async (p) => {
  await noPin(p, 0.9);
  await p.reload({ waitUntil: 'networkidle' });
  await esperaPreloader(p);
  await p.waitForFunction(() => document.querySelector('#ideia.ideia-pin'));
  await assenta(p);
  const r = await p.evaluate(() => {
    const lis = [...document.querySelectorAll('#ideia .ideia-estagio')];
    const a = document.querySelector('#ideia .ideia-estagio[data-chave="no-ar"] a');
    const b = a.getBoundingClientRect();
    const el = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
    return { ativo: lis.findIndex((e) => e.classList.contains('ativo')), noAr: lis[4].classList.contains('ativo'), link: el === a || a.contains(el), top: Math.round(b.top), y: Math.round(scrollY) };
  });
  if (!r.noAr || !r.link) throw new Error('reload rolado: estado inicial errado ' + JSON.stringify(r));
  det(`reload a 90%: ativo ${r.ativo}, elementFromPoint no link = link (scrollY ${r.y})`);
}));

cena('foco-vaza', (det) => abre(DESK, async (p) => {
  await p.waitForFunction(() => document.querySelector('#ideia.ideia-pin'));
  await p.setViewportSize({ width: 800, height: 900 });
  await p.waitForFunction(() => !document.querySelector('#ideia.ideia-pin'));
  const antes = await p.evaluate(() => scrollY);
  await p.evaluate(() => document.querySelector('#ideia .ideia-codigo').focus({ preventScroll: true }));
  await p.waitForTimeout(400);
  const depois = await p.evaluate(() => scrollY);
  if (Math.abs(antes - depois) > 1) throw new Error(`o foco rolou a página depois do cleanup (${antes} -> ${depois})`);
  det(`scrollY ${antes} -> ${depois} ao focar o pre a 800 px`);
}));

cena('foco-teclado', (det) => abre(DESK, async (p) => {
  await p.waitForFunction(() => document.querySelector('#ideia.ideia-pin'));
  // elemento focável imediatamente antes da seção
  await p.evaluate(() => {
    const sec = document.querySelector('#ideia');
    const todos = [...document.querySelectorAll('a[href], button, input, [tabindex]:not([tabindex="-1"])')];
    const ant = todos.filter((e) => !sec.contains(e) && (sec.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_PRECEDING) && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden').pop();
    ant.focus({ preventScroll: true });
    if (document.activeElement !== ant) throw new Error('não consegui focar o elemento anterior à seção');
    window.__ant = ant;
  });
  const estado = () => p.evaluate(() => {
    const a = document.activeElement, sec = document.querySelector('#ideia');
    const li = a && a.closest ? a.closest('.ideia-estagio') : null;
    const cod = li && li.querySelector('.ideia-codigo code');
    const vis = (() => {
      if (!li) return null;
      const r = a.getBoundingClientRect();
      return r.width > 0 && r.top >= 0 && r.bottom <= innerHeight + 1;
    })();
    return { tag: a.tagName.toLowerCase() + (a.className ? '.' + String(a.className).split(' ')[0] : ''), dentro: sec.contains(a),
      chave: li && li.dataset.chave, ativo: !!(li && li.classList.contains('ativo')), op: li ? getComputedStyle(li).opacity : null,
      clip: cod ? getComputedStyle(cod).clipPath : null, vis };
  });
  const visitas = [];
  let achouPre = null, achouLink = null;
  for (let t = 0; t < 20 && !(achouPre && achouLink); t++) {
    await p.keyboard.press('Tab');
    await p.waitForTimeout(80);
    await assenta(p);
    const e = await estado();
    visitas.push(`${e.chave || 'fora'}:${e.tag}`);
    if (e.tag === 'pre.ideia-codigo') achouPre = e;
    if (e.tag === 'a.ideia-ver' || (e.chave === 'no-ar' && e.tag.startsWith('a'))) achouLink = e;
  }
  if (!achouPre) throw new Error('Tab não alcançou o pre do código: ' + visitas.join(' > '));
  if (!achouPre.ativo || achouPre.op !== '1' || !clipAberto(achouPre.clip) || !achouPre.vis)
    throw new Error('pre focado sem estágio 100% legível: ' + JSON.stringify(achouPre));
  if (!achouLink) throw new Error('Tab não alcançou o link: ' + visitas.join(' > '));
  if (!achouLink.ativo || achouLink.op !== '1' || !achouLink.vis) throw new Error('link focado sem estágio legível: ' + JSON.stringify(achouLink));
  // Shift+Tab volta ao pre
  await p.keyboard.press('Shift+Tab'); await p.waitForTimeout(80); await assenta(p);
  const volta = await estado();
  det(`Tab: ${visitas.join(' > ')}; pre ativo, opacidade 1, clip ${achouPre.clip}; link ativo, opacidade 1; Shift+Tab volta a ${volta.chave}:${volta.tag}`);
}));

cena('cabe-1280x600', (det) => abre({ viewport: { width: 1280, height: 600 } }, async (p) => {
  await p.waitForFunction(() => document.querySelector('#ideia.ideia-pin'));
  await noPin(p, 0.9);
  const r = await p.evaluate(() => {
    const a = document.querySelector('#ideia .ideia-estagio[data-chave="no-ar"] a'), b = a.getBoundingClientRect();
    const f = document.querySelector('#ideia .ideia-estagio[data-chave="no-ar"] .ideia-frente');
    const fr = f ? f.getBoundingClientRect() : null;
    return { bottom: Math.round(b.bottom), alt: innerHeight, figTop: fr && Math.round(fr.top), figBottom: fr && Math.round(fr.bottom) };
  });
  if (r.bottom > r.alt || (r.figBottom !== null && r.figBottom > r.alt)) throw new Error('o estágio no-ar (link ou figura) passa do viewport: ' + JSON.stringify(r));
  det(`link bottom ${r.bottom} <= ${r.alt}; figura ${r.figTop}..${r.figBottom}`);
}));

cena('codigo-celular', async (det) => {
  const partes = [];
  for (const w of [430, 360]) {
    await abre(MOVEL(w), async (p) => {
      const r = await p.evaluate(() => {
        const pre = document.querySelector('#ideia .ideia-codigo');
        const c = getComputedStyle(pre);
        return { sw: pre.scrollWidth, cw: pre.clientWidth, tab: pre.getAttribute('tabindex'), rotulo: pre.getAttribute('aria-label'),
          grad: (c.backgroundImage.match(/gradient/g) || []).length, fonte: c.fontSize };
      });
      const cabe = r.sw <= r.cw;
      const indicador = r.grad >= 2 && r.tab === '0' && !!r.rotulo;
      if (!cabe && !indicador) throw new Error(`${w} px: código corta e sem indicador/foco: ` + JSON.stringify(r));
      partes.push(`${w} px: ${cabe ? 'cabe' : `rola (${r.sw}>${r.cw}), ${r.grad} gradientes de borda, tabindex ${r.tab}`}, fonte ${r.fonte}`);
    });
  }
  det(partes.join('; '));
});

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
  await p.evaluate(() => document.querySelector('#ideia').scrollIntoView({ behavior: 'instant' }));
  await p.waitForFunction(() => { const h = document.querySelector('#ideia h2'); return h && Number(getComputedStyle(h).opacity) === 1; }, null, { timeout: 5000 })
    .catch(() => { throw new Error('h2 da seção não chegou a opacidade 1 com reduced-motion'); });
  const cab = await p.evaluate(() => ['#ideia h2', '#ideia .ideia-intro'].map((q) => { const e = document.querySelector(q), c = getComputedStyle(e), b = e.getBoundingClientRect(); return [q, c.opacity, b.height > 0]; }));
  if (cab.some((x) => x[1] !== '1' || !x[2])) throw new Error('cabeçalho da seção invisível com reduced-motion: ' + JSON.stringify(cab));
  const i = await info(p);
  const r = await p.evaluate((SEC) => [...document.querySelectorAll(SEC + ' .ideia-estagio')].map((e) => {
    const c = getComputedStyle(e), cod = e.querySelector('.ideia-codigo'), b = e.getBoundingClientRect();
    return { op: c.opacity, tr: c.transform, vis: b.width > 0 && b.height > 0 && c.visibility !== 'hidden', clip: cod ? getComputedStyle(cod).clipPath : 'none' };
  }), SEC);
  if (i.pin || i.spacer || i.oculto || i.visto) throw new Error('animação ligada com reduced-motion: ' + JSON.stringify(i));
  if (r.length !== 5 || r.some((x) => !x.vis || x.op !== '1' || x.tr !== 'none' || x.clip !== 'none')) throw new Error('estágios não estão estáticos: ' + JSON.stringify(r));
  det('5 estágios, h2 e intro visíveis com opacidade 1, sem transform, sem clip-path, sem pin');
}));

cena('sem-js', async (det) => {
  const ctx = await navegador.newContext({ ...DESK, javaScriptEnabled: false });
  try {
    const p = await ctx.newPage();
    await p.goto(base + '/', { waitUntil: 'load' });
    const r = await p.evaluate(() => {
      const sec = document.querySelector('#ideia');
      const vis = (e) => { const c = getComputedStyle(e), b = e.getBoundingClientRect(); return c.visibility !== 'hidden' && c.display !== 'none' && b.height > 0 && Number(c.opacity) > 0.99; };
      return { estagios: [...sec.querySelectorAll('.ideia-estagio')].map((e) => vis(e) && !e.hasAttribute('inert') && e.getAttribute('aria-hidden') !== 'true'),
        h2: vis(sec.querySelector('h2')), intro: vis(sec.querySelector('.ideia-intro')), pin: sec.classList.contains('ideia-pin') };
    });
    if (r.estagios.length !== 5 || r.estagios.some((v) => !v) || !r.h2 || !r.intro || r.pin) throw new Error('sem JS a seção não ficou legível: ' + JSON.stringify(r));
    det('JS desligado: 5 estágios, h2 e intro visíveis, sem pin');
  } finally { await ctx.close(); }
});

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
    const chaves = ['conversa', 'encontro', 'prototipo', 'codigo', 'no-ar'];
    for (let i = 0; i < 5; i++) {
      await noPin(p, (i + 0.6) / 5);   // estágio i 100% revelado
      await p.screenshot({ path: path.join(pasta, `ideia-1440-${chaves[i]}.png`) });
    }
  });
  await abre({ viewport: { width: 1280, height: 600 } }, async (p) => {
    await p.waitForFunction(() => document.querySelector('#ideia.ideia-pin'));
    await noPin(p, 0.9);
    await p.screenshot({ path: path.join(pasta, 'ideia-1280x600-no-ar.png') });
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
