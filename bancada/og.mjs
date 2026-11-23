// Gera as imagens OG (1200×630) do ALL.dev, uma por página do sitemap, a partir da prévia local.
// Uso: node bancada/og.mjs --base http://127.0.0.1:8765 [--saida assets/og]
// O nome de cada arquivo vem da própria página (<meta property="og:image">), o mesmo que o gerador escreve.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const arg = (n) => { const i = process.argv.indexOf('--' + n); return i > 0 ? process.argv[i + 1] : null; };
const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const base = (arg('base') || '').replace(/\/+$/, '');
if (!base) { console.error('uso: node bancada/og.mjs --base http://127.0.0.1:8765 [--saida assets/og]'); process.exit(2); }
const saida = path.resolve(arg('saida') || path.join(raiz, 'assets', 'og'));
const SITE = 'https://all.dev.br';

const molde = fs.readFileSync(path.join(raiz, 'fonte', 'modelos', 'og.html'), 'utf8');
const projetos = JSON.parse(fs.readFileSync(path.join(raiz, 'fonte', 'dados', 'projetos.json'), 'utf8'));
const porSlug = Object.fromEntries(projetos.map((p) => [p.slug, p]));

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const ACENTO = { caio: 'var(--caio)', rosiel: 'var(--rosiel)', dupla: 'linear-gradient(90deg, var(--caio), var(--rosiel))' };

// Tipo e acento pelo caminho. O degradê violeta↔laranja fica só para o que é dos dois sócios.
function classificar(caminho) {
  if (caminho === '/') return { tipo: 'estúdio de software', acento: ACENTO.dupla };
  if (caminho === '/historia.html') return { tipo: 'história', acento: ACENTO.rosiel };
  if (caminho === '/projetos/') return { tipo: 'projetos', acento: ACENTO.dupla };
  let m = caminho.match(/^\/projetos\/([a-z0-9-]+)\/$/);
  if (m) { const p = porSlug[m[1]]; return { tipo: p ? p.tipo : 'projeto', acento: ACENTO.dupla }; }
  if (/^\/servicos\/[a-z0-9-]+\/$/.test(caminho)) return { tipo: 'serviço', acento: ACENTO.dupla };
  m = caminho.match(/^\/(caio|rosiel)\/$/);
  if (m) return { tipo: 'perfil', acento: ACENTO[m[1]] };
  throw new Error(`página sem tipo de OG: ${caminho}`);
}

// BANCADA_LIBS (opcional): diretório de .so extras, junto ao LD_LIBRARY_PATH só do navegador (igual ao rodar.mjs).
const envNav = { ...process.env };
if (process.env.BANCADA_LIBS) envNav.LD_LIBRARY_PATH = [process.env.BANCADA_LIBS, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':');

const sitemap = await (await fetch(`${base}/sitemap.xml`)).text();
const caminhos = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].replace(SITE, '') || '/');
if (!caminhos.length) { console.error('sitemap sem páginas'); process.exit(1); }
// Cases em rascunho ficam fora do sitemap (noindex), mas também têm página e og:image.
for (const slug of projetos.filter((p) => p.visivel !== false).map((p) => p.slug)) {
  const c = `/projetos/${slug}/`;
  if (!caminhos.includes(c)) caminhos.push(c);
}

fs.mkdirSync(saida, { recursive: true });
const navegador = await chromium.launch({ env: envNav });
const pagina = await navegador.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
const usados = new Map();
let falhas = 0;
for (const caminho of caminhos) {
  try {
    const resp = await pagina.goto(base + caminho, { waitUntil: 'domcontentloaded' });
    if (!resp || resp.status() !== 200) throw new Error(`HTTP ${resp && resp.status()}`);
    const info = await pagina.evaluate(() => ({
      og: document.querySelector('meta[property="og:image"]')?.content || '',
      h1: (() => {
        const h = document.querySelector('h1')?.cloneNode(true);
        if (!h) return '';
        h.querySelectorAll('br').forEach((br) => br.replaceWith(' '));
        return h.textContent.replace(/\s+/g, ' ').trim();
      })(),
      titulo: document.title,
    }));
    const m = info.og.match(/\/assets\/og\/([a-z0-9-]+)\.png$/);
    if (!m) throw new Error(`og:image inesperada: ${info.og}`);
    const slug = m[1];
    if (usados.has(slug)) throw new Error(`colisão: ${slug} já usado por ${usados.get(slug)}`);
    usados.set(slug, caminho);
    const titulo = info.h1 || info.titulo.replace(/\s+—\s+AllDevs$/, '');
    const { tipo, acento } = classificar(caminho);
    const tamanho = titulo.length > 60 ? '58px' : titulo.length > 32 ? '72px' : '96px';
    const html = molde
      .replaceAll('$base', () => base)
      .replaceAll('$tamanho', () => tamanho)
      .replaceAll('$acento', () => acento)
      .replaceAll('$tipo', () => esc(tipo))
      .replaceAll('$titulo', () => esc(titulo));
    await pagina.setContent(html, { waitUntil: 'networkidle' });
    await pagina.evaluate(() => document.fonts.ready);
    const arq = path.join(saida, `${slug}.png`);
    await pagina.screenshot({ path: arq, clip: { x: 0, y: 0, width: 1200, height: 630 } });
    console.log(`ok  ${caminho} -> ${path.relative(raiz, arq)}  [${tipo}] ${titulo}`);
  } catch (e) {
    falhas++;
    console.error(`ERRO ${caminho}: ${e.message}`);
  }
}
await navegador.close();
process.exit(falhas ? 1 : 0);
