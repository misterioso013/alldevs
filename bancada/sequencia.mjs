// Sequências de janela (rolagem real com mouse.wheel, um passo por ~0,8 janela). Uso:
// node bancada/sequencia.mjs --url <base> --saida <pasta> [--paginas /,/projetos/] [--larguras 1440,430,360]
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { esperaPreloader } from './paleta.mjs';

const arg = (n) => { const i = process.argv.indexOf('--' + n); return i > 0 ? process.argv[i + 1] : null; };
const base = (arg('url') || '').replace(/\/+$/, ''), saida = arg('saida');
if (!base || !saida) { console.error('uso: node bancada/sequencia.mjs --url <base> --saida <pasta> [--paginas ...] [--larguras ...]'); process.exit(2); }
const paginas = (arg('paginas') || '/').split(','), larguras = (arg('larguras') || '1440,430,360').split(',').map(Number);
const alt = { 1440: 900, 430: 932, 360: 780 };
fs.mkdirSync(saida, { recursive: true });
const envNav = { ...process.env };
if (process.env.BANCADA_LIBS) envNav.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');
const nav = await chromium.launch({ env: envNav });
const lista = [];
for (const pg of paginas) for (const w of larguras) {
  const h = alt[w] || 900;
  const ctx = await nav.newContext({ viewport: { width: w, height: h }, hasTouch: w < 1000, isMobile: w < 1000, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto(base + pg, { waitUntil: 'networkidle' });
  await esperaPreloader(p);
  const nome = (pg.replace(/^\/|\/$/g, '').replace(/[^\w.-]+/g, '_') || 'home') + '-' + w;
  const passo = Math.round(h * 0.8);
  let y = -1, i = 0, parado = 0;
  while (i < 80) {
    const f = path.join(saida, `${nome}-${String(i).padStart(2, '0')}.png`);
    await p.waitForTimeout(700);
    await p.screenshot({ path: f }); lista.push(path.resolve(f)); i++;
    const ant = await p.evaluate(() => scrollY);
    if (w >= 1000) await p.mouse.wheel(0, passo); else await p.evaluate((d) => scrollBy({ top: d, behavior: 'instant' }), passo);
    await p.waitForTimeout(400);
    const dep = await p.evaluate(() => scrollY), max = await p.evaluate(() => document.documentElement.scrollHeight - innerHeight);
    if (dep === ant) { if (++parado > 2 || dep >= max - 2) break; } else parado = 0;
    if (dep >= max - 2) { await p.waitForTimeout(500); const f2 = path.join(saida, `${nome}-${String(i).padStart(2, '0')}.png`); await p.screenshot({ path: f2 }); lista.push(path.resolve(f2)); break; }
  }
  await ctx.close();
}
await nav.close();
fs.writeFileSync(path.join(saida, 'lista_abs.txt'), lista.join('\n') + '\n');
console.log(lista.length + ' capturas');
