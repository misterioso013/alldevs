// Caso de bancada da paleta de comandos (js/paleta.js). Mede, em cada página:
//  a) 1440 px, teclado: sem pedido do paleta.json na carga; Ctrl K abre (foco no campo, 1 pedido, todos os itens);
//     seta muda a opção (aria-activedescendant), a busca ignora acento, Enter navega até o destino da opção;
//     Esc devolve o foco a quem o tinha (o logo); ⌘K (Meta+K) também abre; axe com a paleta aberta (0 serious/critical);
//  b) 412 px, toque: a pílula "> ir para…" tem >= 44 px, não há barra fixa embaixo, o toque abre, as opções têm
//     >= 44 px, Esc devolve o foco à pílula, tocar numa opção navega, axe com a paleta aberta;
//  c) reducedMotion: aberta, nenhum elemento com transform após 1 s e o diálogo termina opaco;
//  d) 412 px com o paleta.json bloqueado: a pílula segue como link e leva a /projetos/;
//  e) 412 px, clique sem foco (o que o toque faz no Safari/iOS e no Firefox/macOS: o <a> não ganha foco, o activeElement
//     é o body): aberta pela pílula, Esc devolve o foco à pílula.
// Uso solo: node bancada/paleta.mjs --url http://127.0.0.1:8765/   (o rodar.mjs chama medePaleta)
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import { fileURLToPath } from 'node:url';

const ARQ = '/assets/paleta.json';
const ABERTA = 'dialog.paleta[open]';
const ESPERA = { timeout: 6000 };

const contexto = (nav, w, extra = {}) => nav.newContext({ viewport: { width: w, height: 900 }, ...extra });

const estado = (p) => p.evaluate(() => {
  const d = document.querySelector('dialog.paleta');
  const campo = d && d.querySelector('input');
  const ops = [...document.querySelectorAll('dialog.paleta [role="option"]')];
  const sel = ops.findIndex((o) => o.getAttribute('aria-selected') === 'true');
  const a = document.activeElement;
  return {
    aberto: !!d && d.open, foco: !!campo && a === campo, n: ops.length, sel,
    ativo: campo ? campo.getAttribute('aria-activedescendant') : null,
    idSel: sel > -1 ? ops[sel].id : null, href: sel > -1 ? ops[sel].getAttribute('href') : null,
    rot: sel > -1 ? ops[sel].textContent : null, alturas: ops.map((o) => o.getBoundingClientRect().height),
    ativoEm: a ? (a.tagName.toLowerCase() + [...a.classList].map((c) => '.' + c).join('')) : null,
  };
});

const axeAberta = async (p, w, falhas) => {
  const r = await new AxeBuilder({ page: p }).analyze();
  const gr = r.violations.filter((v) => ['serious', 'critical'].includes(v.impact));
  if (gr.length) falhas.push(`axe com a paleta aberta a ${w} px: ` + gr.map((v) => `${v.id} (${v.impact}, ${v.nodes.length})`).join(', '));
  return `${r.violations.length} violações, ${gr.length} serious/critical`;
};

// Espera a página ser trocada por uma nova (a marca posta na antiga some). Devolve false se não trocou.
const marcaEEsperaTrocar = async (p, acao) => {
  await p.evaluate(() => { window.__marca = 1; });
  await acao();
  try { await p.waitForFunction(() => window.__marca === undefined, null, ESPERA); return true; } catch { return false; }
};

async function teclado(nav, url, total) {
  const falhas = [];
  const ctx = await contexto(nav, 1440);
  try {
    const p = await ctx.newPage();
    const pedidos = [];
    p.on('request', (r) => { if (new URL(r.url()).pathname === ARQ) pedidos.push(r.url()); });
    await p.goto(url, { waitUntil: 'networkidle' });
    if (pedidos.length) falhas.push(`paleta.json buscado na carga (${pedidos.length})`);
    const pilulaVisivel = await p.locator('.paleta-gatilho').first().isVisible();
    if (pilulaVisivel) falhas.push('a pílula aparece a 1440 px');

    await p.focus('a.nav-logo');
    await p.keyboard.press('Control+k');
    await p.waitForSelector(`${ABERTA} [role="option"]`, ESPERA);
    let e = await estado(p);
    if (!e.aberto || !e.foco) falhas.push(`Ctrl K: aberto ${e.aberto}, foco no campo ${e.foco}`);
    if (e.n !== total) falhas.push(`${e.n} opções, esperava ${total}`);
    if (pedidos.length !== 1) falhas.push(`paleta.json pedido ${pedidos.length}x (esperava 1)`);
    const nAxe = await axeAberta(p, 1440, falhas);

    await p.keyboard.press('ArrowDown');
    e = await estado(p);
    if (e.sel !== 1 || !e.idSel || e.ativo !== e.idSel) falhas.push(`seta: opção ${e.sel}, activedescendant ${e.ativo} (id ${e.idSel})`);
    await p.keyboard.press('ArrowUp');
    await p.keyboard.press('ArrowUp');
    e = await estado(p);
    if (e.sel !== total - 1) falhas.push(`seta para cima não volta ao fim da lista (opção ${e.sel})`);

    await p.keyboard.type('orcamento');
    e = await estado(p);
    if (e.n !== 1 || !/orçamento/i.test(e.rot || '')) falhas.push(`busca "orcamento": ${e.n} opção(ões), "${e.rot}"`);
    await p.keyboard.press('Control+a');
    await p.keyboard.press('Backspace');
    await p.keyboard.press('ArrowDown');
    e = await estado(p);
    if (e.n !== total || e.sel !== 1) falhas.push(`limpar a busca: ${e.n} opções, seleção ${e.sel}`);
    const destino = e.href;
    const foi = await marcaEEsperaTrocar(p, () => p.keyboard.press('Enter'));
    const chegou = new URL(p.url());
    if (!foi) falhas.push('Enter não navegou');
    else if (chegou.pathname !== new URL(destino, url).pathname) falhas.push(`Enter foi para ${chegou.pathname}, esperava ${destino}`);

    // Esc devolve o foco a quem o tinha; ⌘K (Meta+K) também abre
    await p.goto(url, { waitUntil: 'networkidle' });
    await p.focus('a.nav-logo');
    await p.keyboard.press('Control+k');
    await p.waitForSelector(`${ABERTA} [role="option"]`, ESPERA);
    await p.keyboard.press('ArrowDown');
    await p.keyboard.press('Escape');
    await p.waitForTimeout(150);
    e = await estado(p);
    if (e.aberto) falhas.push('Esc não fechou');
    if (!/nav-logo/.test(e.ativoEm || '')) falhas.push(`Esc: o foco foi para ${e.ativoEm}, esperava o logo`);
    await p.keyboard.press('Meta+k');
    await p.waitForSelector(ABERTA, ESPERA);
    await p.keyboard.press('Escape');
    e = await estado(p);
    if (e.aberto) falhas.push('Meta+K abriu e o Esc não fechou');
    return { falhas, det: `1440 px: Ctrl K, seta, Enter -> ${chegou.pathname}, Esc devolve o foco, ${total} opções, 1 pedido, axe ${nAxe}` };
  } finally { await ctx.close(); }
}

async function toque(nav, url, total) {
  const falhas = [];
  const ctx = await contexto(nav, 412, { hasTouch: true, isMobile: true });
  try {
    const p = await ctx.newPage();
    await p.goto(url, { waitUntil: 'networkidle' });
    const pilula = p.locator('.paleta-gatilho').first();
    const alt = (await pilula.boundingBox() || { height: 0 }).height;
    if (!(await pilula.isVisible()) || alt < 44) falhas.push(`pílula a 412 px: visível ${await pilula.isVisible()}, ${alt.toFixed(0)} px de altura`);
    const fixas = await p.evaluate(() => [...document.querySelectorAll('body *')]
      .filter((el) => getComputedStyle(el).position === 'fixed' && el.getBoundingClientRect().bottom >= innerHeight - 1 && el.getBoundingClientRect().height > 0)
      .map((el) => el.tagName.toLowerCase() + [...el.classList].map((c) => '.' + c).join('')));
    if (fixas.length) falhas.push('barra fixa embaixo: ' + fixas.join(', '));

    await pilula.tap();
    await p.waitForSelector(`${ABERTA} [role="option"]`, ESPERA);
    let e = await estado(p);
    if (!e.aberto || !e.foco || e.n !== total) falhas.push(`toque: aberto ${e.aberto}, foco no campo ${e.foco}, ${e.n} opções`);
    if (e.alturas.some((h) => h < 44)) falhas.push(`opção com ${Math.min(...e.alturas).toFixed(0)} px (< 44)`);
    const nAxe = await axeAberta(p, 412, falhas);
    await p.keyboard.press('Escape');
    await p.waitForTimeout(150);
    e = await estado(p);
    if (e.aberto || !/paleta-gatilho/.test(e.ativoEm || '')) falhas.push(`Esc a 412 px: aberto ${e.aberto}, foco em ${e.ativoEm}, esperava a pílula`);

    // tocar numa opção navega
    await pilula.tap();
    await p.waitForSelector(`${ABERTA} [role="option"]`, ESPERA);
    const alvo = p.locator(`${ABERTA} [role="option"]`).nth(1);
    const href = await alvo.getAttribute('href');
    const foi = await marcaEEsperaTrocar(p, () => alvo.tap());
    if (!foi) falhas.push('o toque na opção não navegou');
    else if (new URL(p.url()).pathname !== new URL(href, url).pathname) falhas.push(`toque na opção foi para ${new URL(p.url()).pathname}, esperava ${href}`);
    return { falhas, det: `412 px: pílula ${alt.toFixed(0)} px, toque abre, Esc devolve o foco, toque na opção -> ${new URL(p.url()).pathname}, sem barra fixa, axe ${nAxe}` };
  } finally { await ctx.close(); }
}

async function calmo(nav, url) {
  const falhas = [];
  const ctx = await contexto(nav, 1440, { reducedMotion: 'reduce' });
  try {
    const p = await ctx.newPage();
    await p.goto(url, { waitUntil: 'networkidle' });
    await p.keyboard.press('Control+k');
    await p.waitForSelector(`${ABERTA} [role="option"]`, ESPERA);
    await p.waitForTimeout(1000);
    const r = await p.evaluate(() => ({
      op: getComputedStyle(document.querySelector('dialog.paleta')).opacity,
      tr: [...document.querySelectorAll('*')].filter((el) => { const t = getComputedStyle(el).transform; return t && t !== 'none'; })
        .map((el) => el.tagName.toLowerCase() + [...el.classList].map((c) => '.' + c).join('')),
    }));
    if (r.tr.length) falhas.push(`reducedMotion com a paleta aberta: transform em ${r.tr.slice(0, 4).join(', ')}`);
    if (r.op !== '1') falhas.push(`reducedMotion: diálogo termina com opacidade ${r.op}`);
    return { falhas, det: 'reducedMotion: aberta, sem transform, opaca' };
  } finally { await ctx.close(); }
}

async function semRede(nav, url) {
  const falhas = [];
  const ctx = await contexto(nav, 412, { hasTouch: true, isMobile: true });
  try {
    const p = await ctx.newPage();
    await p.route('**' + ARQ, (r) => r.abort());
    await p.goto(url, { waitUntil: 'networkidle' });
    const foi = await marcaEEsperaTrocar(p, () => p.locator('.paleta-gatilho').first().tap());
    const caminho = new URL(p.url()).pathname;
    if (!foi) falhas.push('sem o paleta.json a pílula não navegou');
    else if (caminho !== '/projetos/') falhas.push(`sem o paleta.json a pílula foi para ${caminho}, esperava /projetos/`);
    return { falhas, det: `sem o paleta.json: a pílula leva a ${caminho}` };
  } finally { await ctx.close(); }
}

async function semFoco(nav, url) {
  const falhas = [];
  const ctx = await contexto(nav, 412, { hasTouch: true, isMobile: true });
  try {
    const p = await ctx.newPage();
    await p.goto(url, { waitUntil: 'networkidle' });
    // click() por script não dá foco ao <a>, como o toque do Safari; o tap()/click() do Playwright daria (Chromium)
    const antes = await p.evaluate(() => {
      document.activeElement && document.activeElement.blur();
      const a = document.activeElement;
      return a ? a.tagName.toLowerCase() : null;
    });
    if (antes !== 'body') falhas.push(`preparo: o foco inicial está em ${antes}, esperava body`);
    await p.evaluate(() => document.querySelector('.paleta-gatilho').click());
    await p.waitForSelector(`${ABERTA} [role="option"]`, ESPERA);
    let e = await estado(p);
    if (!e.aberto || !e.foco) falhas.push(`clique sem foco: aberto ${e.aberto}, foco no campo ${e.foco}`);
    await p.keyboard.press('Escape');
    await p.waitForTimeout(150);
    e = await estado(p);
    if (e.aberto || !/paleta-gatilho/.test(e.ativoEm || '')) falhas.push(`clique sem foco, Esc: aberto ${e.aberto}, foco em ${e.ativoEm}, esperava a pílula`);
    return { falhas, det: `clique sem foco no link: Esc devolve o foco à pílula (${e.ativoEm})` };
  } finally { await ctx.close(); }
}

export async function medePaleta(nav, url) {
  const total = (await (await fetch(new URL(ARQ, url))).json()).length;
  const casos = await Promise.all([teclado(nav, url, total), toque(nav, url, total), calmo(nav, url), semRede(nav, url), semFoco(nav, url)]
    .map((c) => c.catch((e) => ({ falhas: [String(e && e.message || e).split('\n')[0]], det: '' }))));
  const falhas = casos.flatMap((c) => c.falhas);
  return { passou: falhas.length === 0, det: falhas.length ? falhas.join('; ') : casos.map((c) => c.det).join('; '), casos };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const i = process.argv.indexOf('--url');
  const url = i > 0 ? process.argv[i + 1] : null;
  if (!url) { console.error('uso: node bancada/paleta.mjs --url <página>'); process.exit(2); }
  const env = { ...process.env };
  if (process.env.BANCADA_LIBS) env.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');
  const nav = await chromium.launch({ env });
  try {
    const r = await medePaleta(nav, url);
    for (const c of r.casos) console.log((c.falhas.length ? 'FALHA ' : 'passa ') + c.det + (c.falhas.length ? ' :: ' + c.falhas.join('; ') : ''));
    console.log(r.passou ? 'paleta: PASSA' : 'paleta: FALHA');
    process.exitCode = r.passou ? 0 : 1;
  } finally { await nav.close(); }
}
