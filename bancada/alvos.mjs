// Controles (botões, CTAs, pílula, filtros, FAQ, menu) a 412 px: altura mínima por página.
// Uso: node bancada/alvos.mjs http://127.0.0.1:8765 / /historia.html /servicos/...   (V=1 lista os tipos; BANCADA_LIBS como no rodar.mjs)
import { chromium } from 'playwright';
const [base, ...paths] = process.argv.slice(2);
const env = { ...process.env, LD_LIBRARY_PATH: [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':') };
const SEL = 'button, summary, input, select, textarea, [role=button], .btn, .nav-cta, .paleta-gatilho, .nav-links a, .faq-question, .menu-toggle, .nav-toggle';
const b = await chromium.launch({ env });
let falhas = 0;
for (const p of paths) {
  const c = await b.newContext({ viewport: { width: 412, height: 900 }, hasTouch: true, isMobile: true });
  const pg = await c.newPage(); await pg.goto(base + p, { waitUntil: 'networkidle' });
  const r = await pg.evaluate((SEL) => {
    const out = [];
    for (const el of document.querySelectorAll(SEL)) {
      const s = getComputedStyle(el); const x = el.getBoundingClientRect();
      if (!x.width || !x.height || s.visibility === 'hidden' || s.display === 'none') continue;
      out.push({ sel: el.tagName.toLowerCase() + [...el.classList].map(c => '.' + c).join(''), t: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 24), w: Math.round(x.width * 10) / 10, h: Math.round(x.height * 10) / 10 });
    }
    return out;
  }, SEL);
  const menor = r.reduce((m, o) => Math.min(m, o.h), 999);
  const ruins = r.filter(o => o.h < 43.5);
  falhas += ruins.length;
  const tipos = [...new Set(r.map(o => o.sel))].join(' ');
  console.log(`${p}: ${r.length} controles, menor altura ${menor} px, abaixo de 44: ${ruins.length}`);
  if (process.env.V) console.log('   tipos:', tipos);
  for (const o of ruins) console.log('   ', JSON.stringify(o));
  await c.close();
}
await b.close();
console.log('total abaixo de 44:', falhas);
