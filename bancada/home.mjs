// Bancada da home (cartão "por trás" dos projetos e capturas por seção). Uso: node bancada/home.mjs --url <base> [--capturas <pasta>] [--so <regex>]
// Cenários (1440 e 430 px, sobre o 1º cartão com camada): repouso, hover, link-visivel, alvos; 430 px com toque: toque-rolar, toque-segurar;
// reduzido, sem-js. Um por linha ("ok" ou "FALHA"); rc 1 se algum falhar.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { esperaPreloader } from './paleta.mjs';

const arg = (n) => { const i = process.argv.indexOf('--' + n); return i > 0 ? process.argv[i + 1] : null; };
const base = (arg('url') || '').replace(/\/+$/, '');
const capturas = arg('capturas');
const so = arg('so');
if (!base) { console.error('uso: node bancada/home.mjs --url <base> [--capturas <pasta>] [--so <regex>]'); process.exit(2); }

const envNav = { ...process.env };
if (process.env.BANCADA_LIBS) envNav.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');
const navegador = await chromium.launch({ env: envNav });

const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
const MOUSE = (w) => ({ viewport: { width: w, height: 900 } });
const TOQUE = { viewport: { width: 430, height: 900 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 };
const CARTAO = '.projeto-cartao:has(.cartao-por-tras)';
const LARGURAS = [1440, 430];

async function abre(opts, fn, { js = true } = {}) {
  const ctx = await navegador.newContext({ ...opts, javaScriptEnabled: js });
  const p = await ctx.newPage();
  const erros = [];
  p.on('pageerror', (e) => erros.push(String(e.message || e)));
  try {
    await p.goto(base + '/', { waitUntil: 'networkidle' });
    if (js) await esperaPreloader(p);
    await fn(p, erros);
    if (erros.length) throw new Error('erro de página: ' + erros[0]);
  } finally { await ctx.close().catch(() => {}); }
}

// Traz o 1º cartão com camada para o meio da janela e devolve os rects (relativos à janela).
const prepara = async (p) => {
  await p.evaluate((c) => document.querySelector(c).scrollIntoView({ block: 'center', behavior: 'instant' }), CARTAO);
  await p.waitForTimeout(500);
  return geo(p);
};
const geo = (p) => p.evaluate((c) => {
  const card = document.querySelector(c), fig = card.querySelector('.projeto-tela'), cam = card.querySelector('.cartao-por-tras');
  const R = (e) => { const r = e.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; };
  return { card: R(card), fig: R(fig), cam: R(cam), h3a: R(card.querySelector('h3 a')), link: R(card.querySelector('.link-seta')) };
}, CARTAO);

// Estado da camada: raio da máscara, centro, opacidade, e as linhas do código que o círculo sólido (70% do raio) alcança.
const estado = (p) => p.evaluate((c) => {
  const cam = document.querySelector(c + ' .cartao-por-tras'), cs = getComputedStyle(cam), cr = cam.getBoundingClientRect();
  const r = parseFloat(cs.getPropertyValue('--r')) || 0, mx = parseFloat(cs.getPropertyValue('--mx')), my = parseFloat(cs.getPropertyValue('--my'));
  const visivel = cs.display !== 'none' && r > 0 && Number(cs.opacity) > 0;
  const cx = cr.left + (isNaN(mx) ? cr.width / 2 : mx), cy = cr.top + (isNaN(my) ? cr.height / 2 : my);
  let linhas = 0, total = 0;
  const w = document.createTreeWalker(cam, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) {
    if (!n.parentElement.closest('pre')) continue;
    let o = 0;
    for (const l of n.textContent.split('\n')) {
      if (l.trim()) {
        const g = document.createRange(); g.setStart(n, o); g.setEnd(n, o + l.length);
        const b = g.getBoundingClientRect();
        const dentro = b.right > cr.left && b.left < cr.right && b.bottom > cr.top && b.top < cr.bottom;
        if (dentro) {
          total++;
          const dx = Math.max(b.left - cx, 0, cx - b.right), dy = Math.max(b.top - cy, 0, cy - b.bottom);
          if (Math.hypot(dx, dy) < r * 0.7) linhas++;
        }
      }
      o += l.length + 1;
    }
  }
  return { r, opacidade: Number(cs.opacity), visivel, linhas, total };
}, CARTAO);

const cruza = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
const centro = (g) => [g.x + g.w / 2, g.y + g.h / 2];
const fora = async (p) => { await p.mouse.move(2, 2); await p.waitForTimeout(250); };
const pixels = (p, g) => p.screenshot({ clip: { x: g.x, y: g.y, width: g.w, height: g.h } });

const defs = [];
const cena = (nome, fn) => defs.push([nome, fn]);

for (const w of LARGURAS) {
  cena(`repouso@${w}`, (det) => abre(MOUSE(w), async (p) => {
    const g = await prepara(p);
    await p.waitForTimeout(900);   // deixa a entrada do cartão (revelar) terminar antes de comparar pixels
    await fora(p);
    const e = await estado(p);
    if (e.visivel) throw new Error(`camada visível sem ponteiro: ${JSON.stringify(e)}`);
    const antes = await pixels(p, g.fig);
    await p.addStyleTag({ content: '.cartao-por-tras{visibility:hidden!important}' });
    const sem = await pixels(p, g.fig);
    if (!antes.equals(sem)) throw new Error('os pixels da figura em repouso diferem dos da frente (a camada vaza)');
    det(`--r ${e.r}, opacity ${e.opacidade}, pixels da figura iguais aos da frente`);
  }));

  cena(`hover@${w}`, (det) => abre(MOUSE(w), async (p) => {
    const g = await prepara(p);
    const pts = [['centro', 0.5, 0.5], ['canto-sup-esq', 0.15, 0.15], ['canto-inf-dir', 0.85, 0.85], ['canto-sup-dir', 0.85, 0.15], ['canto-inf-esq', 0.15, 0.85]];
    const out = [];
    for (const [nome, fx, fy] of pts) {
      await fora(p);
      await p.mouse.move(g.fig.x + g.fig.w * fx, g.fig.y + g.fig.h * fy, { steps: 4 });
      await p.waitForTimeout(350);
      const e = await estado(p);
      if (!e.visivel) throw new Error(`${nome}: a camada não abriu (${JSON.stringify(e)})`);
      if (e.linhas < 2) throw new Error(`${nome}: só ${e.linhas} linha(s) do código no círculo (de ${e.total} dentro da camada, r=${Math.round(e.r)})`);
      out.push(`${nome} ${e.linhas}`);
    }
    det('linhas no círculo: ' + out.join(', '));
  }));

  cena(`link-visivel@${w}`, (det) => abre(MOUSE(w), async (p) => {
    const g = await prepara(p);
    const partes = [];
    for (const [nome, alvo] of [['h3', g.h3a], ['ver-no-ar', g.link]]) {
      const [x, y] = centro(alvo);
      await fora(p);
      await p.mouse.move(x, y, { steps: 6 });
      await p.waitForTimeout(350);
      const c = await geo(p);
      const e = await estado(p);
      if (e.visivel && cruza(c.cam, alvo)) throw new Error(`${nome}: a camada (${Math.round(c.cam.w)}x${Math.round(c.cam.h)} em ${Math.round(c.cam.x)},${Math.round(c.cam.y)}) cobre o link (${Math.round(alvo.w)}x${Math.round(alvo.h)})`);
      if (cruza(c.cam, alvo)) throw new Error(`${nome}: o rect da camada cruza o do link`);
      const ok = await p.evaluate(([x, y, q]) => { const el = document.elementFromPoint(x, y); return !!el && !!el.closest(q); }, [x, y, nome === 'h3' ? CARTAO + ' h3 a' : CARTAO + ' .link-seta']);
      if (!ok) throw new Error(`${nome}: elementFromPoint no centro do link não devolve o link`);
      partes.push(`${nome} livre`);
    }
    det(partes.join(', '));
  }));

  cena(`alvos@${w}`, (det) => abre(MOUSE(w), async (p) => {
    const g = await prepara(p);
    const h = { 'h3 a': g.h3a.h, 'ver no ar': g.link.h };
    for (const [n, v] of Object.entries(h)) if (v < 44) throw new Error(`${n} com ${v.toFixed(1)} px de altura (mínimo 44)`);
    det(Object.entries(h).map(([n, v]) => `${n} ${v.toFixed(0)} px`).join(', '));
  }));

  cena(`reduzido@${w}`, (det) => abre({ ...MOUSE(w), reducedMotion: 'reduce' }, async (p) => {
    const g = await prepara(p);
    let vis = 0;
    for (const [fx, fy] of [[0.5, 0.5], [0.2, 0.3]]) {
      await p.mouse.move(g.fig.x + g.fig.w * fx, g.fig.y + g.fig.h * fy, { steps: 5 });
      await p.waitForTimeout(300);
      const e = await estado(p);
      if (e.visivel) vis++;
    }
    if (vis) throw new Error('a camada apareceu com movimento reduzido');
    det('a camada nunca apareceu');
  }));

  cena(`sem-js@${w}`, (det) => abre(MOUSE(w), async (p) => {
    // sem JS não há evaluate: a geometria sai dos locators
    await p.locator(CARTAO).first().scrollIntoViewIfNeeded();
    await p.waitForTimeout(500);
    const f = await p.locator(CARTAO + ' .projeto-tela').first().boundingBox();
    const g = { fig: { x: f.x, y: f.y, w: f.width, h: f.height } };
    await p.mouse.move(2, 2);
    await p.waitForTimeout(250);
    const repouso = await pixels(p, g.fig);
    await p.mouse.move(g.fig.x + g.fig.w / 2, g.fig.y + g.fig.h / 2, { steps: 4 });
    await p.waitForTimeout(400);
    const sobre = await pixels(p, g.fig);   // sem JS não há addStyleTag: compara repouso e ponteiro em cima
    if (!repouso.equals(sobre)) throw new Error('sem JS a camada aparece sobre a figura');
    const href = await p.evaluate((c) => document.querySelector(c + ' h3 a').getAttribute('href'), CARTAO);
    await p.click(CARTAO + ' h3 a');
    await p.waitForURL((u) => u.pathname === href, { timeout: 5000 }).catch(() => { throw new Error('o link do cartão não navegou para ' + href); });
    det('camada oculta e o link do cartão navega para ' + href);
  }, { js: false }));
}

// Toque de verdade pelo CDP (o Playwright só tem tap): pointerdown, parada e rolagem.
const comToque = (fn) => abre(TOQUE, async (p) => {
  const cdp = await p.context().newCDPSession(p);
  const t = (type, x, y) => cdp.send('Input.dispatchTouchEvent', { type, touchPoints: type === 'touchEnd' ? [] : [{ x, y, id: 1, radiusX: 4, radiusY: 4, force: 1 }] });
  await fn(p, t);
});
const monitora = (p) => p.evaluate((c) => {
  window.__quadros = 0; window.__vis = 0;
  const cam = document.querySelector(c + ' .cartao-por-tras');
  (function f() {
    const cs = getComputedStyle(cam);
    window.__quadros++;
    if (cs.display !== 'none' && (parseFloat(cs.getPropertyValue('--r')) || 0) > 0 && Number(cs.opacity) > 0) window.__vis++;
    requestAnimationFrame(f);
  })();
}, CARTAO);

cena('toque-rolar@430', (det) => comToque(async (p, t) => {
  const g = await prepara(p);
  const [x, y] = centro(g.fig);
  await monitora(p);
  const y0 = await p.evaluate(() => scrollY);
  await t('touchStart', x, y);
  await dorme(30);
  for (let i = 1; i <= 8; i++) { await t('touchMove', x, y - i * 14); await dorme(16); }
  await dorme(60);
  await t('touchEnd');
  await dorme(500);
  const r = await p.evaluate(() => ({ vis: window.__vis, q: window.__quadros, y: scrollY }));
  if (r.y === y0) throw new Error('a rolagem por toque não aconteceu: o cenário não prova nada');
  if (r.vis) throw new Error(`a camada apareceu em ${r.vis} de ${r.q} quadros durante a rolagem`);
  det(`rolou ${Math.round(r.y - y0)} px; a camada não apareceu em nenhum dos ${r.q} quadros`);
}));

cena('toque-segurar@430', (det) => comToque(async (p, t) => {
  const g = await prepara(p);
  const [x, y] = centro(g.fig);
  await t('touchStart', x, y);
  await dorme(300);
  const e1 = await estado(p);
  if (!e1.visivel) throw new Error(`o dedo parado por 300 ms não revelou: ${JSON.stringify(e1)}`);
  await t('touchEnd');
  await dorme(250);
  const e2 = await estado(p);
  if (e2.visivel) throw new Error('a camada não fechou ao soltar');
  det(`revelou (r ${Math.round(e1.r)}) e fechou ao soltar`);
}));

async function tiraCapturas(pasta) {
  fs.mkdirSync(pasta, { recursive: true });
  await abre(MOUSE(1440), async (p) => {
    const ids = await p.evaluate(() => [...document.querySelectorAll('main > section')].map((s) => s.id));
    for (const id of ids) {
      if (id === 'ideia') {   // seção presa: roda o pin até o fim e tira a janela
        await p.evaluate(() => { const st = window.ScrollTrigger.getAll().find((s) => s.pin); window.scrollTo({ top: st.start + (st.end - st.start) * 0.97, behavior: 'instant' }); });
        await p.waitForTimeout(900);
        await p.screenshot({ path: path.join(pasta, 'home-1440-ideia.png') });
        continue;
      }
      await p.evaluate((id) => document.getElementById(id).scrollIntoView({ block: 'start', behavior: 'instant' }), id);
      await p.waitForTimeout(900);
      await p.locator('#' + id).screenshot({ path: path.join(pasta, `home-1440-${id}.png`) });
    }
  });
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
