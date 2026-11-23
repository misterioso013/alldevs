// Captura só a primeira dobra (1440x900). Uso: node bancada/dobra.mjs <url> <arquivo.png>
import { chromium } from 'playwright';
const env = { ...process.env, LD_LIBRARY_PATH: [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':') };
const [url, saida] = process.argv.slice(2);
const b = await chromium.launch({ env });
const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
await p.goto(url, { waitUntil: 'networkidle' });
await p.waitForTimeout(1500);
await p.screenshot({ path: saida, fullPage: false });
await b.close();
