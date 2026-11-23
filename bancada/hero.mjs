// Bancada do hero "por trás do produto". Uso: node bancada/hero.mjs --url <base> [--capturas <pasta>]
// Um cenário por linha ("ok" ou "FALHA"); rc 1 se algum falhar. Cenários: mouse-revela, toque-rola, toque-revela, pausa,
// cpu4x, reduzido, sem-js, ciclo, lcp. Com --capturas, grava PNGs em 360, 430 e 1440 px (parado e no meio da revelação).
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { esperaPreloader } from './paleta.mjs';

const arg = (n) => { const i = process.argv.indexOf('--' + n); return i > 0 ? process.argv[i + 1] : null; };
const base = (arg('url') || '').replace(/\/+$/, '');
const capturas = arg('capturas');
if (!base) { console.error('uso: node bancada/hero.mjs --url <base> [--capturas <pasta>]'); process.exit(2); }

const envNav = { ...process.env };
if (process.env.BANCADA_LIBS) envNav.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');
const navegador = await chromium.launch({ env: envNav });

const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
const PALCO = '.hero-palco';
const DESK = { viewport: { width: 1440, height: 900 } };
const MOVEL = { viewport: { width: 430, height: 900 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 };

async function abre(opts, fn, { esperaCanvas = true } = {}) {
  const ctx = await navegador.newContext(opts);
  const p = await ctx.newPage();
  const erros = [];
  p.on('pageerror', (e) => erros.push(String(e.message || e)));
  try {
    await p.addInitScript(() => {
      window.__lcp = null;
      try {
        new PerformanceObserver((l) => {
          const e = l.getEntries().pop();
          window.__lcp = { tag: e.element ? e.element.tagName : null, cls: e.element ? e.element.className : null, t: e.startTime };
        }).observe({ type: 'largest-contentful-paint', buffered: true });
      } catch (x) { /* sem suporte */ }
    });
    await p.goto(base + '/', { waitUntil: 'networkidle' });
    await esperaPreloader(p);
    if (esperaCanvas) await p.waitForSelector(PALCO + '.vivo', { timeout: 5000 });
    await fn(p, ctx, erros);
    if (erros.length) throw new Error('erro de página: ' + erros[0]);
  } finally { await ctx.close(); }
}

const caixa = async (p) => { await p.locator(PALCO).scrollIntoViewIfNeeded(); return p.locator(PALCO).boundingBox(); };
// Alfa do canvas da máscara num ponto (px de CSS dentro do palco): 0 = buraco (mostra o código), 255 = frente.
const alfa = (p, x, y) => p.evaluate(([x, y]) => {
  const c = document.querySelector('.hero-mascara'), r = c.getBoundingClientRect();
  return c.getContext('2d').getImageData(Math.round(x / r.width * (c.width - 1)), Math.round(y / r.height * (c.height - 1)), 1, 1).data[3];
}, [x, y]);
const quadros = (p) => p.evaluate(() => window.__revelarQuadros || 0);
const frase = (p) => p.locator('.hero-frase').first().textContent();
const varre = async (p, b, ms, { passos = 40 } = {}) => {
  const t0 = Date.now(); let i = 0;
  while (Date.now() - t0 < ms) {
    const s = (Date.now() - t0) / 1000;
    await p.mouse.move(b.x + b.width * (0.5 + 0.38 * Math.sin(s * 2.1)), b.y + b.height * (0.5 + 0.34 * Math.sin(s * 3.3 + 1)), { steps: 2 });
    await dorme(16); i++;
  }
  return i;
};

// Cada cenário devolve uma linha de detalhe (string); lançar erro = FALHA.
const defs = [];
const cena = (nome, fn) => defs.push([nome, fn]);

cena('mouse-revela', (det) => abre(DESK, async (p) => {
  const b = await caixa(p);
  const cx = b.width * 0.5, cy = b.height * 0.5;
  await p.mouse.move(b.x + cx - 60, b.y + cy);
  for (let i = 0; i <= 12; i++) { await p.mouse.move(b.x + cx - 60 + i * 10, b.y + cy); await dorme(16); }
  const furo = await alfa(p, cx, cy), longe = await alfa(p, b.width * 0.03, b.height * 0.04);
  if (!(furo < 100)) throw new Error(`sob o ponteiro o alfa é ${furo} (esperava < 100)`);
  if (!(longe > 200)) throw new Error(`longe do ponteiro o alfa é ${longe} (esperava > 200)`);
  det(`alfa sob o ponteiro ${furo}, longe ${longe}`);
}));

cena('toque-rola', (det) => abre(MOVEL, async (p, ctx) => {
  await p.evaluate(() => window.scrollTo(0, 0));
  const b = await p.locator(PALCO).boundingBox(), alt = p.viewportSize().height;
  if (!(b.y + b.height / 2 < alt - 20)) throw new Error('palco baixo demais na tela de 430 px para o gesto');
  const cdp = await ctx.newCDPSession(p);
  const x = b.x + b.width / 2, y0 = b.y + b.height / 2;
  const antes = await p.evaluate(() => window.scrollY);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y: y0 }] });
  for (let i = 1; i <= 15; i++) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y: y0 - i * 20 }] }); await dorme(16); }
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await dorme(500);
  const depois = await p.evaluate(() => window.scrollY);
  if (!(depois - antes > 100)) throw new Error(`a página não rolou com o gesto sobre o palco (scrollY ${antes} -> ${depois})`);
  det(`scrollY ${antes} -> ${depois} com o arrasto vertical começando no palco`);
}));

cena('toque-revela', (det) => abre(MOVEL, async (p, ctx) => {
  const b = await caixa(p);
  const cdp = await ctx.newCDPSession(p);
  const x = b.x + b.width / 2, y = b.y + b.height / 2;
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
  await dorme(500);   // segurar parado continua revelando
  const furo = await alfa(p, b.width / 2, b.height / 2);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  if (!(furo < 100)) throw new Error(`dedo parado: alfa sob o dedo ${furo} (esperava < 100)`);
  det(`alfa sob o dedo parado ${furo}`);
}));

cena('pausa', (det) => abre(DESK, async (p, ctx) => {
  const b = await caixa(p);
  await varre(p, b, 500);
  await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await dorme(400);
  const a = await quadros(p); await dorme(700); const c = await quadros(p);
  if (c - a > 1) throw new Error(`fora da tela o laço seguiu: ${c - a} quadros em 700 ms`);
  await p.evaluate(() => window.scrollTo(0, 0));
  await p.mouse.move(b.x + 100, b.y + 100); await dorme(50); await p.mouse.move(b.x + 160, b.y + 140);
  await dorme(400);
  const d = await quadros(p);
  if (!(d - c > 5)) throw new Error('o laço não voltou ao palco reaparecer');
  // aba escondida: dispara visibilitychange
  const ant = await quadros(p);
  await p.evaluate(() => { Object.defineProperty(document, 'hidden', { configurable: true, get: () => true }); document.dispatchEvent(new Event('visibilitychange')); });
  await dorme(200); const e1 = await quadros(p); await dorme(500); const e2 = await quadros(p);
  if (e2 - e1 > 1) throw new Error(`com a aba escondida o laço seguiu: ${e2 - e1} quadros em 500 ms`);
  det(`fora da tela ${c - a} quadros em 700 ms; aba escondida ${e2 - e1} em 500 ms; de volta ${d - c} em 400 ms`);
}));

cena('cpu4x', (det) => abre(DESK, async (p, ctx) => {
  const b = await caixa(p);
  const cdp = await ctx.newCDPSession(p);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  await varre(p, b, 4000);   // aquecimento: a qualidade adaptativa assenta
  const q0 = await quadros(p), t0 = Date.now();
  await varre(p, b, 3000);
  const q1 = await quadros(p), dt = (Date.now() - t0) / 1000;
  const fps = (q1 - q0) / dt;
  const est = await p.evaluate(() => (window.__revelarEstado ? window.__revelarEstado() : null));
  const res = est ? `${est.cols}x${est.linhas} (nível ${est.nivel})` : '?';
  det(`${fps.toFixed(1)} fps com CPU 4x; resolução final do campo ${res}`);
  if (!(fps >= 50)) throw new Error(`${fps.toFixed(1)} fps (esperava >= 50); resolução final ${res}`);
}));

cena('reduzido', (det) => abre({ ...DESK, reducedMotion: 'reduce' }, async (p) => {
  const canvas = await p.locator('.hero-mascara').count();
  if (canvas !== 0) throw new Error('o canvas existe com movimento reduzido');
  const botao = p.locator('.hero-ver-por-tras');
  if (!(await botao.isVisible())) throw new Error('o botão "Ver por trás" não aparece');
  const bb = await botao.boundingBox();
  if (bb.height < 44) throw new Error(`botão com ${bb.height}px de altura (< 44)`);
  const opAntes = await p.evaluate(() => getComputedStyle(document.querySelector('.hero-frente')).opacity);
  await botao.click();
  await dorme(400);
  const press = await botao.getAttribute('aria-pressed');
  const opDepois = await p.evaluate(() => getComputedStyle(document.querySelector('.hero-frente')).opacity);
  if (press !== 'true') throw new Error(`aria-pressed ${press} depois do clique`);
  if (!(Number(opDepois) < Number(opAntes))) throw new Error(`a frente não saiu da frente do trecho (opacity ${opAntes} -> ${opDepois})`);
  const f1 = await frase(p); await dorme(8000); const f2 = await frase(p);
  if (f1 !== f2) throw new Error('o ciclo andou sozinho com movimento reduzido');
  det(`sem canvas; botão ${bb.height}px; frente opacity ${opAntes} -> ${opDepois}; sem ciclo sozinho`);
}, { esperaCanvas: false }));

cena('sem-js', async (det) => {
  const ctx = await navegador.newContext({ ...DESK, javaScriptEnabled: false });
  try {
    const p = await ctx.newPage();
    await p.goto(base + '/', { waitUntil: 'networkidle' });
    const h1 = p.locator('h1').first();
    if (!(await h1.isVisible())) throw new Error('h1 invisível sem JS');
    const img = p.locator('.hero-frente img').first();
    if (!(await img.isVisible())) throw new Error('a frente (img) não aparece sem JS');
    const ok = await img.evaluate((i) => i.complete && i.naturalWidth > 0);
    if (!ok) throw new Error('a imagem da frente não carregou sem JS');
    const pre = await p.locator('.hero-por-tras pre').first().isVisible();
    if (pre) throw new Error('o trecho aparece sem JS (deveria ficar escondido)');
    const cv = await p.locator('.hero-mascara').first().isVisible();
    if (cv) throw new Error('o canvas aparece sem JS');
    const oc = await p.evaluate(() => getComputedStyle(document.querySelector('h1')).opacity);
    det(`h1 e frente legíveis; trecho e canvas escondidos; h1 opacity ${oc}`);
  } finally { await ctx.close(); }
});

cena('ciclo', (det) => abre(DESK, async (p) => {
  const b = await caixa(p);
  const f0 = await frase(p);
  const s0 = await p.locator('.hero-frente img').first().getAttribute('src');
  const c0 = await p.locator('.hero-por-tras code').first().textContent();
  await p.mouse.click(b.x + b.width / 2, b.y + b.height / 2);   // clique curto: próximo item
  await dorme(900);
  const f1 = await frase(p), s1 = await p.locator('.hero-frente img').first().getAttribute('src');
  const c1 = await p.locator('.hero-por-tras code').first().textContent();
  if (f1 === f0 || s1 === s0 || c1 === c0) throw new Error('o clique não trocou frente, trecho e frase');
  const cor1 = await p.locator(PALCO).getAttribute('data-cor');
  // 7 s de revelação acumulada trocam sozinhos
  await varre(p, b, 10500);
  const f2 = await frase(p);
  if (f2 === f1) throw new Error('7 s de revelação não trocaram de item');
  det(`clique: "${f0.trim().slice(0, 14)}" -> "${f1.trim().slice(0, 14)}" (cor ${cor1}); revelação contínua: -> "${f2.trim().slice(0, 14)}"`);
}));

cena('lcp', (det) => abre(DESK, async (p) => {
  await dorme(800);
  const l = await p.evaluate(() => window.__lcp);
  if (!l) throw new Error('sem entrada de LCP');
  const ok = l.tag === 'H1' || (l.tag === 'IMG' && /hero-frente|^$/.test(l.cls || '')) || l.tag === 'IMG';
  if (l.tag === 'CANVAS' || !ok) throw new Error(`o LCP é ${l.tag}.${l.cls} (esperava h1 ou a img da frente)`);
  det(`LCP em ${l.tag} aos ${Math.round(l.t)} ms`);
}));

// Capturas: parado e no meio de uma revelação, em 360, 430 e 1440 px.
async function tiraCapturas(dir) {
  fs.mkdirSync(dir, { recursive: true });
  for (const w of [360, 430, 1440]) {
    const touch = w < 1000;
    await abre({ viewport: { width: w, height: w < 1000 ? 900 : 900 }, hasTouch: touch, isMobile: touch, deviceScaleFactor: 1 }, async (p, ctx) => {
      await p.evaluate(() => window.scrollTo(0, 0));
      await dorme(300);
      await p.screenshot({ path: path.join(dir, `hero-${w}-parado.png`) });
      const b = await caixa(p);
      if (touch) {
        const cdp = await ctx.newCDPSession(p);
        const x = b.x + b.width * 0.5, y = b.y + b.height * 0.5;
        await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
        for (let i = 1; i <= 14; i++) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: x + i * 6, y: y - i * 2 }] }); await dorme(16); }
        await dorme(120);
        await p.screenshot({ path: path.join(dir, `hero-${w}-revelando.png`) });
        await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
      } else {
        for (let i = 0; i <= 30; i++) { await p.mouse.move(b.x + b.width * (0.25 + i * 0.015), b.y + b.height * (0.45 + 0.1 * Math.sin(i / 4))); await dorme(16); }
        await p.screenshot({ path: path.join(dir, `hero-${w}-revelando.png`) });
      }
    });
  }
}

let falhou = 0;
for (const [nome, fn] of defs) {
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
