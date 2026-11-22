// Caso de bancada do inspetor do hero (js/inspetor.js). Mede o que só aparece com o tempo:
//  a) parado 12 s sem gesto: CLS (maior janela de sessão) < 0,05, o percurso anda e o LCP segue o <h1>;
//  b) gesto cedo (tecla) e 40 s aberto, com o mouse passando no palco: a tela troca e o CLS fica < 0,05;
//  c) reducedMotion: 2 caixas acesas e paradas, mesmo com hover e clique;
//  d) botão "próxima tela" com >= 44 px de altura e sem cobrir o selo.
// CLS e troca em 360, 430 e 1440 px; botão também em 412 px. Tudo em paralelo (~45 s).
// Uso solo: node bancada/inspetor.mjs --url http://127.0.0.1:8765/   (o rodar.mjs chama medeInspetor)
import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';

const LARGURAS_CLS = [360, 430, 1440];
const LARGURAS_BOTAO = [360, 412, 430, 1440];
const ALTURA = (w) => (w >= 960 ? 900 : 800);

// Observadores antes de qualquer script da página (buffered pega o que veio antes).
function observa() {
  window.__cls = []; window.__lcp = [];
  const nomeEl = (n) => !n || !n.tagName ? '?' : n.tagName + [...(n.classList || [])].map((c) => '.' + c).join('');
  new PerformanceObserver((l) => l.getEntries().forEach((e) => window.__cls.push({
    t: e.startTime, v: e.value, r: e.hadRecentInput, s: (e.sources || []).map((x) => nomeEl(x.node)).join(' '),
  }))).observe({ type: 'layout-shift', buffered: true });
  new PerformanceObserver((l) => l.getEntries().forEach((e) => window.__lcp.push({ t: e.startTime, el: nomeEl(e.element) })))
    .observe({ type: 'largest-contentful-paint', buffered: true });
}

// Maior janela de sessão (1 s entre mudanças, 5 s no máximo), sem as que vêm logo após entrada do usuário.
function janelaMax(lista) {
  let max = 0, cur = 0, ini = 0, ult = 0;
  for (const e of lista.filter((x) => !x.r).sort((a, b) => a.t - b.t)) {
    if (cur && e.t - ult < 1000 && e.t - ini < 5000) { cur += e.v; ult = e.t; } else { cur = e.v; ini = ult = e.t; }
    if (cur > max) max = cur;
  }
  return max;
}
const culpados = (lista) => [...new Set(lista.filter((x) => !x.r && x.v > 0.001).map((x) => x.s))].slice(0, 3).join('; ');

const estado = (p) => p.evaluate(() => {
  const img = document.querySelector('.inspetor-tela img');
  const code = document.querySelector('.inspetor-codigo code');
  const acesas = [...document.querySelectorAll('.inspetor-caixa')].filter((c) => +getComputedStyle(c).opacity > 0.5)
    .map((c) => { const r = c.getBoundingClientRect(); return [r.x, r.y, r.width, r.height].map(Math.round).join(','); });
  return { src: img && img.getAttribute('src'), code: code && code.textContent, acesas };
});

async function amostra(p, ms, passo, fn) {
  const fim = Date.now() + ms;
  while (Date.now() < fim) { await p.waitForTimeout(Math.min(passo, Math.max(0, fim - Date.now()))); await fn(); }
}

async function parado(nav, url, w) {
  const ctx = await nav.newContext({ viewport: { width: w, height: ALTURA(w) } });
  try {
    const p = await ctx.newPage(); await p.addInitScript(observa);
    await p.goto(url, { waitUntil: 'load' });
    const codes = new Set(), srcs = new Set();
    await amostra(p, 12000, 1000, async () => { const e = await estado(p); codes.add(e.code); srcs.add(e.src); });
    const { cls, lcp } = await p.evaluate(() => ({ cls: window.__cls, lcp: window.__lcp }));
    const jm = janelaMax(cls), soH1 = lcp.length > 0 && lcp.every((e) => e.el.startsWith('H1'));
    const falhas = [];
    if (!(jm < 0.05)) falhas.push(`CLS ${jm.toFixed(3)} (${culpados(cls)})`);
    if (codes.size < 3) falhas.push(`percurso parado (${codes.size} textos)`);
    if (srcs.size !== 1) falhas.push(`trocou de tela sem gesto (${srcs.size})`);
    if (!soH1) falhas.push('LCP fora do h1: ' + lcp.map((e) => e.el).join(','));
    return { falhas, det: `${w} parado: CLS ${jm.toFixed(3)} (${cls.length} mudanças), ${codes.size} passos, LCP ${lcp.map((e) => e.el).join('>')}` };
  } finally { await ctx.close(); }
}

async function comGesto(nav, url, w) {
  const ctx = await nav.newContext({ viewport: { width: w, height: ALTURA(w) } });
  try {
    const p = await ctx.newPage(); await p.addInitScript(observa);
    await p.goto(url, { waitUntil: 'load' });
    await p.waitForTimeout(500);
    await p.keyboard.press('Shift');
    const srcs = [], palco = await p.locator('.inspetor-palco').boundingBox();
    let k = 0;
    await amostra(p, 40000, 1000, async () => {
      const e = await estado(p);
      if (srcs[srcs.length - 1] !== e.src) srcs.push(e.src);
      // mouse passeia pelo palco a cada 5 s (pointermove não marca hadRecentInput: o CLS dele conta)
      if (palco && ++k % 5 === 0) {
        const f = (k / 5) % 4;
        await p.mouse.move(palco.x + palco.width * (0.3 + 0.12 * f), palco.y + palco.height * (0.25 + 0.15 * f), { steps: 6 });
        await p.waitForTimeout(400);
        await p.mouse.move(2, 2);
      }
    });
    const cls = await p.evaluate(() => window.__cls);
    const jm = janelaMax(cls), falhas = [];
    if (!(jm < 0.05)) falhas.push(`CLS ${jm.toFixed(3)} (${culpados(cls)})`);
    if (new Set(srcs).size < 3) falhas.push(`trocou pouco: ${srcs.length - 1} trocas`);
    return { falhas, det: `${w} gesto: CLS ${jm.toFixed(3)} (${cls.filter((x) => !x.r).length} mudanças), ${srcs.length - 1} trocas` };
  } finally { await ctx.close(); }
}

async function calmo(nav, url) {
  const ctx = await nav.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  try {
    const p = await ctx.newPage(); await p.addInitScript(observa);
    await p.goto(url, { waitUntil: 'load' });
    await p.waitForTimeout(1000);
    const a = await estado(p), falhas = [];
    if (a.acesas.length !== 2 || a.acesas[0] === a.acesas[1]) falhas.push(`acesas ${JSON.stringify(a.acesas)}`);
    // hover e clique em cima da 2ª caixa e fora dela; nada pode andar
    for (const r of a.acesas.slice().reverse()) {
      const [x, y, cw, ch] = r.split(',').map(Number);
      await p.mouse.move(x + cw / 2, y + ch / 2, { steps: 4 });
      await p.mouse.click(x + cw / 2, y + ch / 2);
    }
    await p.waitForTimeout(2500);
    const b = await estado(p);
    if (JSON.stringify(a.acesas) !== JSON.stringify(b.acesas)) falhas.push(`caixas mudaram: ${JSON.stringify(b.acesas)}`);
    if (a.src !== b.src) falhas.push('trocou de tela sozinho');
    return { falhas, det: `calmo: ${a.acesas.length} acesas, paradas após hover/clique` };
  } finally { await ctx.close(); }
}

async function botao(nav, url, w) {
  const ctx = await nav.newContext({ viewport: { width: w, height: ALTURA(w) } });
  try {
    const p = await ctx.newPage();
    await p.goto(url, { waitUntil: 'load' });
    const g = await p.evaluate(() => {
      const r = (s) => { const el = document.querySelector(s); if (!el) return null; const b = el.getBoundingClientRect(); return { x: b.x, y: b.y, r: b.right, b: b.bottom, h: b.height }; };
      return { bt: r('.inspetor-proximo'), selo: r('.inspetor-selo') };
    });
    const falhas = [];
    if (!g.bt || !g.selo) return { falhas: ['botão ou selo ausente'], det: '' };
    const sobre = Math.max(0, Math.min(g.bt.r, g.selo.r) - Math.max(g.bt.x, g.selo.x)) * Math.max(0, Math.min(g.bt.b, g.selo.b) - Math.max(g.bt.y, g.selo.y));
    if (g.bt.h < 44) falhas.push(`botão ${w}: ${g.bt.h.toFixed(0)} px`);
    if (sobre > 0) falhas.push(`botão cobre o selo a ${w} px (selo ${g.selo.x.toFixed(0)}–${g.selo.r.toFixed(0)}, botão ${g.bt.x.toFixed(0)}–${g.bt.r.toFixed(0)})`);
    return { falhas, det: `${w}: botão ${g.bt.h.toFixed(0)} px, selo ${g.selo.x.toFixed(0)}–${g.selo.r.toFixed(0)}, botão ${g.bt.x.toFixed(0)}–${g.bt.r.toFixed(0)}` };
  } finally { await ctx.close(); }
}

export async function medeInspetor(nav, url) {
  const casos = await Promise.all([
    ...LARGURAS_CLS.map((w) => parado(nav, url, w)),
    ...LARGURAS_CLS.map((w) => comGesto(nav, url, w)),
    calmo(nav, url),
    ...LARGURAS_BOTAO.map((w) => botao(nav, url, w)),
  ]);
  const falhas = casos.flatMap((c) => c.falhas);
  return { passou: falhas.length === 0, det: falhas.length ? falhas.join('; ') : casos.map((c) => c.det).join('; '), casos };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const i = process.argv.indexOf('--url');
  const url = i > 0 ? process.argv[i + 1] : null;
  if (!url) { console.error('uso: node bancada/inspetor.mjs --url <página com o inspetor>'); process.exit(2); }
  const env = { ...process.env };
  if (process.env.BANCADA_LIBS) env.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');
  const nav = await chromium.launch({ env });
  try {
    const r = await medeInspetor(nav, url);
    for (const c of r.casos) console.log((c.falhas.length ? 'FALHA ' : 'passa ') + c.det + (c.falhas.length ? ' :: ' + c.falhas.join('; ') : ''));
    console.log(r.passou ? 'inspetor: PASSA' : 'inspetor: FALHA');
    process.exitCode = r.passou ? 0 : 1;
  } finally { await nav.close(); }
}
