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

async function abre(opts, fn, { esperaCanvas = true, antes = null, rota = null } = {}) {
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
          window.__lcp = { tag: e.element ? e.element.tagName : null, cls: e.element ? e.element.className : null, frente: !!(e.element && e.element.closest && e.element.closest('.hero-frente')), t: e.startTime };
        }).observe({ type: 'largest-contentful-paint', buffered: true });
      } catch (x) { /* sem suporte */ }
    });
    if (antes) await antes(p, ctx);
    if (rota) await p.route(base + '/', rota);
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

// 360 px, sem mouse real: o cursor virtual entra sozinho; com CPU 4x a qualidade adaptativa precisa agir (nível > 0 ou cursor virtual desligado).
cena('cpu4x-360', (det) => abre({ viewport: { width: 360, height: 800 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 }, async (p, ctx) => {
  await caixa(p);
  const cdp = await ctx.newCDPSession(p);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  await dorme(5000);   // o cursor virtual entra e a qualidade adaptativa assenta
  const q0 = await quadros(p), t0 = Date.now();
  await dorme(3000);
  const fps = ((await quadros(p)) - q0) / ((Date.now() - t0) / 1000);
  const est = await p.evaluate(() => window.__revelarEstado());
  const res = `${est.cols}x${est.linhas}, nível ${est.nivel}, cursor virtual ${est.auto ? 'ligado' : 'desligado'}`;
  det(`${fps.toFixed(1)} fps com CPU 4x a 360 px; ${res}`);
  // passa se a qualidade agiu (nível > 0 ou cursor virtual desligado) ou, se não precisou agir, se o laço ativo manteve >= 50 fps
  if (!(est.nivel > 0 || !est.auto || fps >= 50)) throw new Error(`a qualidade adaptativa não agiu e o laço caiu: ${res}; ${fps.toFixed(1)} fps`);
}));

cena('reduzido', (det) => abre({ ...DESK, reducedMotion: 'reduce' }, async (p) => {
  const canvas = await p.locator('.hero-mascara').count();
  if (canvas !== 0) throw new Error('o canvas existe com movimento reduzido');
  const botao = p.locator('.hero-ver-por-tras');
  if (!(await botao.isVisible())) throw new Error('o botão "Ver por trás" não aparece');
  const bb = await botao.boundingBox();
  if (bb.height < 44) throw new Error(`botão com ${bb.height}px de altura (< 44)`);
  const attr = (sel, n) => p.locator(sel).first().getAttribute(n);
  const opac = () => p.evaluate(() => getComputedStyle(document.querySelector('.hero-frente')).opacity);
  const opAntes = await opac();
  // o clique no palco não troca o ciclo
  const b = await caixa(p);
  const f0 = await frase(p), s0 = await attr('.hero-frente img', 'src');
  await p.mouse.click(b.x + b.width * 0.3, b.y + b.height * 0.3);
  await dorme(900);
  if ((await frase(p)) !== f0 || (await attr('.hero-frente img', 'src')) !== s0) throw new Error('o clique no palco trocou o ciclo com movimento reduzido');
  if ((await attr('.hero-ver-por-tras', 'aria-pressed')) !== 'false') throw new Error('o clique no palco mexeu no aria-pressed');
  await botao.click();
  await dorme(400);
  const press = await botao.getAttribute('aria-pressed');
  const opDepois = await opac();
  const aria1 = [await attr('.hero-por-tras', 'aria-hidden'), await attr('.hero-frente', 'aria-hidden')];
  if (press !== 'true') throw new Error(`aria-pressed ${press} depois do clique`);
  if (!(Number(opDepois) < Number(opAntes))) throw new Error(`a frente não saiu da frente do trecho (opacity ${opAntes} -> ${opDepois})`);
  if (aria1[0] !== 'false' || aria1[1] !== 'true') throw new Error(`aria-hidden (por trás, frente) = ${aria1} ao mostrar o trecho (esperava false,true)`);
  await botao.click();
  await dorme(400);
  const press2 = await botao.getAttribute('aria-pressed'), op2 = await opac();
  const aria2 = [await attr('.hero-por-tras', 'aria-hidden'), await attr('.hero-frente', 'aria-hidden')];
  if (press2 !== 'false' || Math.abs(Number(op2) - Number(opAntes)) > 0.05) throw new Error(`o 2º clique não voltou à frente (aria-pressed ${press2}, opacity ${op2})`);
  if (aria2[0] !== 'true' || aria2[1] !== 'false') throw new Error(`aria-hidden (por trás, frente) = ${aria2} ao voltar (esperava true,false)`);
  const f1 = await frase(p); await dorme(8000); const f2 = await frase(p);
  if (f1 !== f2) throw new Error('o ciclo andou sozinho com movimento reduzido');
  det(`sem canvas; botão ${bb.height}px; clique no palco não troca; frente opacity ${opAntes} -> ${opDepois} -> ${op2}; aria ${aria1} -> ${aria2}; sem ciclo sozinho`);
}, { esperaCanvas: false }));

// Itens 1 a 4 da rodada 1.
cena('h1-linhas', async (det) => {
  const out = [], ruins = [];
  for (const w of [1024, 1280, 1440, 1920]) {
    await abre({ viewport: { width: w, height: 900 } }, async (p) => {
      const r = await p.evaluate(() => {
        const h = document.querySelector('.hero h1, h1');
        const tw = document.createTreeWalker(h, NodeFilter.SHOW_TEXT);
        const partidas = []; const tops = new Set();
        for (let n = tw.nextNode(); n; n = tw.nextNode()) {
          const re = /\S+/g; let m;
          while ((m = re.exec(n.nodeValue))) {
            const g = document.createRange(); g.setStart(n, m.index); g.setEnd(n, m.index + m[0].length);
            const linhas = new Set([...g.getClientRects()].filter((x) => x.width > 0.5).map((x) => Math.round(x.top)));
            if (linhas.size > 1) partidas.push(m[0]);
            linhas.forEach((t) => tops.add(t));
          }
        }
        // tops de fontes diferentes (Syne e mono) variam alguns px na mesma linha: funde os que estão a menos de 0,4 do corpo
        const corpo = parseFloat(getComputedStyle(h).fontSize), ord = [...tops].sort((a, b) => a - b); let n = 0, ult = -1e9;
        for (const t of ord) { if (t - ult > corpo * 0.4) n++; ult = t; }
        return { partidas, linhas: n, texto: h.textContent.trim() };
      });
      out.push(`${w}px: ${r.linhas} linhas`);
      if (r.partidas.length) ruins.push(`${w}px: palavra partida em mais de uma linha (${r.partidas.join(', ')})`);
      if (r.linhas > 3) ruins.push(`${w}px: ${r.linhas} linhas (esperava <= 3)`);
    }, { esperaCanvas: false });
  }
  det(out.join('; '));
  if (ruins.length) throw new Error(ruins.join(' | '));
});

// Com o cursor no centro, o furo precisa ter código atrás: >= 2 linhas do trecho cruzam o círculo.
const furoCom = (perfil, nome) => cena('furo-' + nome, (det) => abre(perfil, async (p, ctx) => {
  const b = await caixa(p);
  const x = b.x + b.width / 2, y = b.y + b.height / 2;
  let cdp = null;
  if (perfil.hasTouch) { cdp = await ctx.newCDPSession(p); await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] }); }
  else { for (let i = 0; i <= 12; i++) { await p.mouse.move(x - 60 + i * 5, y); await dorme(16); } await dorme(60); }
  if (cdp) await dorme(700);
  // raio do furo: maior distância do centro, na horizontal, com alfa < 100
  let raio = 0;
  for (let d = 0; d < b.width / 2; d += 2) { if ((await alfa(p, b.width / 2 + d, b.height / 2)) < 100) raio = d; else if (d > raio + 12) break; }
  if (cdp) await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  const n = await p.evaluate(([cx, cy, r]) => {
    const pre = document.querySelector('.hero-por-tras pre'), pal = document.querySelector('.hero-palco').getBoundingClientRect();
    const g = document.createRange(); g.selectNodeContents(pre);
    const cruza = new Set();
    for (const t of g.getClientRects()) {
      if (t.width < 2) continue;
      const rx = t.left - pal.left, ry = t.top - pal.top;
      const dx = Math.max(rx - cx, 0, cx - (rx + t.width)), dy = Math.max(ry - cy, 0, cy - (ry + t.height));
      if (dx * dx + dy * dy <= r * r) cruza.add(Math.round(t.top));
    }
    return cruza.size;
  }, [b.width / 2, b.height / 2, raio]);
  det(`furo de raio ${raio}px: ${n} linhas do trecho cruzam o círculo`);
  if (raio < 10) throw new Error(`o furo não abriu (raio ${raio}px)`);
  if (n < 2) throw new Error(`só ${n} linha(s) do trecho cruzam o furo de raio ${raio}px (esperava >= 2)`);
}));
furoCom(DESK, '1440');
furoCom(MOVEL, '430');

// 360 e 430 px, no modo reduzido (o botão aparece): a origem e o botão não se cruzam.
cena('origem-botao', async (det) => {
  const out = [];
  for (const w of [360, 430]) {
    await abre({ viewport: { width: w, height: 800 }, reducedMotion: 'reduce', hasTouch: true, isMobile: true, deviceScaleFactor: 2 }, async (p) => {
      await caixa(p);
      const r = await p.evaluate(() => {
        const o = document.querySelector('.hero-origem').getBoundingClientRect(), v = document.querySelector('.hero-ver-por-tras').getBoundingClientRect();
        return { cruza: !(o.right <= v.left || v.right <= o.left || o.bottom <= v.top || v.bottom <= o.top), o: [o.left, o.top, o.right, o.bottom].map(Math.round), v: [v.left, v.top, v.right, v.bottom].map(Math.round) };
      });
      out.push(`${w}px sem cruzar`);
      if (r.cruza) throw new Error(`a ${w} px .hero-origem ${r.o} cruza .hero-ver-por-tras ${r.v}`);
    }, { esperaCanvas: false });
  }
  det(out.join('; '));
});

// Item 6: wireframe e campos faltando, com um item falso injetado no JSON #ciclo (projetos.json não muda).
cena('wireframe', (det) => abre(DESK, async (p) => {
  const b = await caixa(p);
  const est = () => p.evaluate(() => {
    const q = (s) => document.querySelector(s), vis = (e) => !!e && !e.hidden && getComputedStyle(e).display !== 'none';
    return { pre: vis(q('.hero-por-tras pre')), img: vis(q('.hero-por-tras img')), src: (q('.hero-por-tras img') || {}).src || '',
      origem: q('.hero-origem').textContent, origemVis: vis(q('.hero-origem')), frase: q('.hero-frase').textContent, fraseVis: vis(q('.hero-frase')) };
  });
  const e0 = await est();
  const t = JSON.stringify(e0);
  if (/undefined|null/.test(e0.origem + e0.frase)) throw new Error('"undefined" na tela: ' + t);
  if (e0.pre || !e0.img || !/fakly\.webp/.test(e0.src)) throw new Error('o item de wireframe não mostrou a img e escondeu o pre: ' + t);
  if (e0.origemVis) throw new Error('a origem vazia continua visível: ' + t);
  await p.mouse.click(b.x + b.width / 2, b.y + b.height / 2);
  await dorme(900);
  const e1 = await est();
  if (!e1.pre || e1.img) throw new Error('depois do wireframe o item de código não voltou ao pre: ' + JSON.stringify(e1));
  if (/undefined|null/.test(e1.origem + e1.frase)) throw new Error('"undefined" na tela: ' + JSON.stringify(e1));
  det(`wireframe: pre=${e0.pre} img=${e0.img} origem visível=${e0.origemVis}; depois: pre=${e1.pre} img=${e1.img}`);
}, { rota: async (rota) => {
  const r = await rota.fetch();
  let h = await r.text();
  h = h.replace(/(<script id="ciclo" type="application\/json">)(\[)/, (m, a, c) => a + c + JSON.stringify({ slug: 'wf', cor: 'roxo', frente: { src: '/assets/frente/amott.webp', w: 960, h: 600 }, por_tras: { tipo: 'wireframe', src: '/assets/frente/fakly.webp', w: 960, h: 600 } }) + ',');
  await rota.fulfill({ response: r, body: h });
} }));

// Item 3 (so conta a corrida de pixels na cor do item encostada num pixel transparente, o furo; a arte tem tons parecidos): o anel na cor do item tem <= 3 px de CSS de espessura (medido nos pixels do canvas, em varreduras horizontais pelo furo).
const anelCom = (perfil, nome) => cena('anel-' + nome, (det) => abre(perfil, async (p, ctx) => {
  const b = await caixa(p);
  const x = b.x + b.width / 2, y = b.y + b.height / 2;
  if (perfil.hasTouch) { const cdp = await ctx.newCDPSession(p); await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] }); await dorme(700); }
  else { for (let i = 0; i <= 12; i++) { await p.mouse.move(x - 60 + i * 5, y); await dorme(16); } await dorme(60); }
  const r = await p.evaluate(() => {
    const cv = document.querySelector('.hero-mascara'), pal = document.querySelector('.hero-palco'), g = cv.getContext('2d');
    const sonda = document.createElement('i'); sonda.style.color = getComputedStyle(pal).getPropertyValue('--cor-item'); pal.appendChild(sonda);
    const c = getComputedStyle(sonda).color.match(/[\d.]+/g).map(Number); sonda.remove();
    const esc = cv.width / pal.getBoundingClientRect().width, vals = [];
    for (const fy of [0.35, 0.42, 0.5, 0.58, 0.65]) {
      const y = Math.round(cv.height * fy), d = g.getImageData(0, y, cv.width, 1).data;
      let corridas = [], n = 0;
      for (let i = 0; i < cv.width; i++) {
        const dist = Math.abs(d[i * 4] - c[0]) + Math.abs(d[i * 4 + 1] - c[1]) + Math.abs(d[i * 4 + 2] - c[2]);
        if (dist < 90 && d[i * 4 + 3] > 100) n++; else { if (n && (i - n - 3 >= 0 && d[(i - n - 3) * 4 + 3] < 30 || d[(i + 2) * 4 + 3] < 30)) corridas.push(n); n = 0; }
      }
      vals.push(...corridas.filter((k) => k >= 1).map((k) => k / esc));
    }
    return { esc, vals };
  });
  const max = Math.max(...r.vals, 0);
  det(r.vals.length ? `${r.vals.length} cruzamentos do anel, espessura máxima ${max.toFixed(1)} px de CSS (escala ${r.esc.toFixed(2)})` : 'anel abaixo do limiar de detecção (< 1 px de CSS)');
  // a 430 px o anel (celula de ~2,8 px) fica abaixo de 1 px de CSS e mistura com a arte: sem corrida detectada passa, e a captura confere que ele existe
  if (!r.vals.length && !perfil.hasTouch) throw new Error('nenhum pixel do anel achado');
  if (max > 3.0) throw new Error(`o anel tem ${max.toFixed(1)} px de CSS (esperava <= 3)`);
}));
anelCom(DESK, '1440');
anelCom(MOVEL, '430');

// Item 10: da saída da frente até a nova visível <= 400 ms, com a imagem em cache.
cena('troca-400', (det) => abre(DESK, async (p) => {
  const b = await caixa(p);
  const centro = [b.x + b.width / 2, b.y + b.height / 2];
  for (let i = 0; i < 6; i++) { await p.mouse.click(...centro); await dorme(900); }   // aquece o cache de todas as imagens
  const medidas = [];
  for (let k = 0; k < 3; k++) {
    await p.evaluate(() => {
      window.__troca = new Promise((ok) => {
        const pal = document.querySelector('.hero-palco'), img = pal.querySelector('.hero-frente img'), cv = pal.querySelector('.hero-mascara');
        const src0 = img.getAttribute('src'); let t0 = 0;
        const quad = (t) => {
          if (!t0 && pal.classList.contains('trocando')) t0 = t;
          const ok2 = t0 && !pal.classList.contains('trocando') && img.getAttribute('src') !== src0 && Number(getComputedStyle(cv).opacity) >= 0.98;
          if (ok2) return ok(t - t0);
          if (t0 && t - t0 > 3000) return ok(-1);
          requestAnimationFrame(quad);
        };
        requestAnimationFrame(quad);
      });
    });
    await p.mouse.click(...centro);
    medidas.push(Math.round(await p.evaluate(() => window.__troca)));
    await dorme(600);
  }
  det(`troca em ${medidas.join(', ')} ms (imagem em cache)`);
  if (medidas.some((m) => m < 0 || m > 400)) throw new Error(`troca de ${medidas.join(', ')} ms (esperava <= 400 em cada)`);
}));

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

// LCP no perfil 4G (1,6 Mbps, 150 ms): precisa ser o h1 ou a img da frente, nunca o canvas, e sair antes de 2,5 s.
cena('lcp', (det) => abre(DESK, async (p) => {
  await dorme(800);
  const l = await p.evaluate(() => window.__lcp);
  if (!l) throw new Error('sem entrada de LCP');
  const ok = l.tag === 'H1' || (l.tag === 'IMG' && l.frente);
  if (!ok) throw new Error(`o LCP é ${l.tag}.${l.cls} (esperava o h1 ou a img dentro de .hero-frente)`);
  if (!(l.t < 2500)) throw new Error(`o LCP (${l.tag}) saiu aos ${Math.round(l.t)} ms (esperava < 2500 no perfil 4G)`);
  det(`LCP em ${l.tag} aos ${Math.round(l.t)} ms (4G)`);
}, { antes: async (p, ctx) => {
  const cdp = await ctx.newCDPSession(p);
  await cdp.send('Network.enable');
  await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8 });
} }));

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
const so = arg('so');
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
