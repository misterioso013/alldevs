/* Revelacao "por tras do produto" (ALL.dev v2): a frente (captura real) vira canvas 2D com um buraco que segue o ponteiro;
   por baixo fica o trecho real. Campo de densidade em grade pequena, advectado e com decaimento. window.AllDevsRevelar. */
(function () {
 var doc = document, estilo = getComputedStyle(doc.documentElement);
 var reduz = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
 var agoraMs = function () { return performance.now(); };
 var RAF = window.requestAnimationFrame.bind(window), CAF = window.cancelAnimationFrame.bind(window);
 var COLS = 144, LIN = 90, MIN = 48, SUP = 2, OCIOSO = 2000, CICLO = 7000, JANELA = 30;
 var tok = function (n) { return (estilo.getPropertyValue(n) || "").trim(); };
 var cor3 = function (n) {
  var h = tok(n).replace("#", "");
  if (h.length === 3) h = h.replace(/./g, "$&$&");
  var x = parseInt(h, 16);
  return h.length === 6 && x === x ? [(x >> 16) & 255, (x >> 8) & 255, x & 255] : [0, 0, 0];
 };
 var corItem = function (c) { return cor3(c === "laranja" ? "--laranja-claro" : "--roxo-claro"); };
 var suave = function (x) { x = x < 0 ? 0 : x > 1 ? 1 : x; return x * x * (3 - 2 * x); };
 var DUR = (function () {
  var s = tok("--dur-curta"), n = parseFloat(s);
  return n ? (/ms$/.test(s) || !/s$/.test(s) ? n : n * 1000) : 200;
 })();
 function montarHero(el) {
  var itens;
  try { itens = JSON.parse(doc.getElementById("ciclo").textContent); } catch (e) { return; }
  var q = function (s) { return el.querySelector(s); };
  var img = q(".hero-frente img"), frente = q(".hero-frente"), atras = q(".hero-por-tras"), cv = q(".hero-mascara"),
   botao = q(".hero-ver-por-tras"), frase = q(".hero-frase"), origem = q(".hero-origem");
  if (!itens || !itens.length || !img || !atras || !cv) return;
  var txt = function (x) { return x == null ? "" : String(x); };
  var nova = function (tag, pai, ref) { var n = doc.createElement(tag); n.hidden = true; pai.insertBefore(n, ref || null); return n; };
  var pre = atras.querySelector("pre") || nova("pre", atras, atras.firstChild);
  var cod = pre.querySelector("code") || pre.appendChild(doc.createElement("code"));
  var im = atras.querySelector("img") || nova("img", atras, origem);
  im.alt = ""; im.decoding = "async";
  var atual = itens[0].por_tras, W = 0, H = 0, R = { x: 0, y: 0, s: 0 };
  // trecho ou wireframe conforme o item (o que sobra fica hidden); trecho curto se repete ate cobrir o palco
  var poe = function (p) {
   var t = txt(p.texto), n = 1;
   atual = p;
   pre.hidden = !t; im.hidden = !!t || !p.src;
   if (t) {
    var lh = parseFloat(getComputedStyle(pre).lineHeight) || 19, ln = t.split("\n").length + 1;
    n = Math.min(12, Math.max(1, Math.ceil((el.clientHeight / lh) / ln)));
    cod.textContent = Array(n + 1).join(t + "\n\n").replace(/\s+$/, "");
   } else if (p.src) im.src = p.src;
   origem.textContent = txt(p.origem); origem.hidden = !p.origem;
  };
  var poeFrase = function (it) {
   frase.firstChild.textContent = txt(it.nome);
   frase.lastChild.nodeValue = it.frase ? " " + it.frase : "";
   frase.hidden = !it.nome && !it.frase;
  };
  var medida = function () {
   var r = el.getBoundingClientRect();
   R.x = r.left; R.y = r.top; R.s = window.scrollY; W = r.width; H = r.height;
  };
  var tamanho = function () {}, uw = 0;
  medida(); poe(atual);
  new ResizeObserver(function () {
   medida();
   var w = Math.round(W);
   if (w !== uw) { uw = w; poe(atual); tamanho(); }
  }).observe(el);
  if (reduz) {
   cv.parentNode.removeChild(cv);
   if (botao) {
    botao.hidden = false;
    botao.addEventListener("click", function () {
     var m = !el.classList.contains("mostrando");
     el.classList.toggle("mostrando", m);
     botao.setAttribute("aria-pressed", String(m));
     atras.setAttribute("aria-hidden", String(!m));
     frente.setAttribute("aria-hidden", String(m));
    });
   }
   return;
  }
  var indice = 0, trocando = false, cor = corItem(itens[0].cor), aoTrocar = function () {}, fonte = img;
  var irPara = function (i) {
   if (trocando || itens.length < 2) return;
   trocando = true;
   indice = (i + itens.length) % itens.length;
   var it = itens[indice], n = new Image(), k = 0;
   var fim = function () { el.classList.remove("trocando"); trocando = false; };
   var vai = function () {
    if (++k < 2) return;
    img.width = it.frente.w; img.height = it.frente.h;
    img.alt = "Captura de tela de " + it.nome;
    img.src = it.frente.src; fonte = n;
    poe(it.por_tras); poeFrase(it);
    el.setAttribute("data-cor", it.cor);
    cor = corItem(it.cor);
    aoTrocar();
    RAF(fim);
   };
   el.classList.add("trocando");
   setTimeout(vai, DUR);   // o fade-out corre enquanto a proxima frente carrega e decodifica
   n.src = it.frente.src;
   (n.decode ? n.decode() : new Promise(function (ok, no) { n.onload = ok; n.onerror = no; })).then(vai, fim);
  };
  var baixo = null;
  el.addEventListener("pointerdown", function (e) { baixo = { x: e.clientX, y: e.clientY, t: agoraMs() }; });
  el.addEventListener("click", function (e) {
   var b = baixo; baixo = null;
   if (b && (agoraMs() - b.t > 250 || Math.abs(e.clientX - b.x) + Math.abs(e.clientY - b.y) > 10)) return;
   irPara(indice + 1);
  });
  var ctx = cv.getContext("2d");
  if (!ctx) return;
  // arte: a frente na resolucao da tela, so por troca/resize; mc/rc: buraco e anel, no campo x SUP
  var arte = doc.createElement("canvas"), actx = arte.getContext("2d");
  var mc = doc.createElement("canvas"), rc = doc.createElement("canvas"), mx = mc.getContext("2d"), rx = rc.getContext("2d");
  var mi, ri, mw = 0, mh = 0, cols = COLS, lin = LIN, nivel = 0, d, d2, u, v, u2, v2, fmax = 0, massa = 0;
  var visivel = true, raf = 0, espera = 0, ultimo = 0, auto = true, lento = 0, sujo = true, acum = 0;
  var entrada = agoraMs(), pt = null, vp = null, seg = null, jI = [], jC = [];
  window.__revelarQuadros = 0;
  var pintaCor = function () {
   for (var k = 0; k < mw * mh; k++) { ri.data[k * 4] = cor[0]; ri.data[k * 4 + 1] = cor[1]; ri.data[k * 4 + 2] = cor[2]; }
  };
  var aloca = function () {
   var n = cols * lin;
   d = new Float32Array(n); d2 = new Float32Array(n); u = new Float32Array(n);
   v = new Float32Array(n); u2 = new Float32Array(n); v2 = new Float32Array(n);
   mw = cols * SUP; mh = lin * SUP;
   mc.width = rc.width = mw; mc.height = rc.height = mh;
   mi = mx.createImageData(mw, mh); ri = rx.createImageData(mw, mh);
   for (var k = 0; k < mw * mh * 4; k++) mi.data[k] = 255;
   pintaCor(); fmax = 0;
  };
  var suaviza = function (c) { c.imageSmoothingEnabled = true; c.imageSmoothingQuality = "low"; };
  var pintaArte = function () {
   if (!fonte.naturalWidth) return false;
   actx.fillStyle = tok("--fundo-2");
   actx.fillRect(0, 0, arte.width, arte.height);
   var s = Math.min(arte.width / fonte.naturalWidth, arte.height / fonte.naturalHeight);
   var w = fonte.naturalWidth * s, h = fonte.naturalHeight * s;
   actx.drawImage(fonte, (arte.width - w) / 2, (arte.height - h) / 2, w, h);
   return true;
  };
  tamanho = function () {
   if (!W || !H) return;
   var f = Math.min(window.devicePixelRatio || 1, 2);
   f *= Math.min(1, 1200 / (W * f));
   cv.width = arte.width = Math.max(2, Math.round(W * f));
   cv.height = arte.height = Math.max(2, Math.round(H * f));
   suaviza(ctx); suaviza(actx);
   if (pintaArte()) { sujo = true; desenha(); el.classList.add("vivo"); }   // a img so some depois do 1o quadro pronto
  };
  var splat = function (x, y, dx, dy, raio) {
   var gx = x / W * cols, gy = y / H * lin, r = raio / W * cols, R2 = Math.ceil(r * 1.8);
   var i0 = Math.max(0, (gx - R2) | 0), i1 = Math.min(cols - 1, (gx + R2) | 0);
   var j0 = Math.max(0, (gy - R2) | 0), j1 = Math.min(lin - 1, (gy + R2) | 0);
   for (var j = j0; j <= j1; j++) for (var i = i0; i <= i1; i++) {
    var q2 = ((i - gx) * (i - gx) + (j - gy) * (j - gy)) / (r * r);
    if (q2 > 3.2) continue;
    var w = Math.exp(-q2), k = j * cols + i;
    d[k] = Math.min(1.6, d[k] + w * 0.9);
    u[k] += dx / W * cols * w * 0.5;
    v[k] += dy / H * lin * w * 0.5;
   }
   if (fmax < 0.9) fmax = 0.9;
   sujo = true;
  };
  var traco = function (a, b) {
   var dx = b.x - a.x, dy = b.y - a.y, dist = Math.sqrt(dx * dx + dy * dy);
   var raio = Math.min(W * 0.14, W * 0.05 + dist * 0.9), n = Math.max(1, Math.ceil(dist / (raio * 0.45)));
   for (var s = 1; s <= n; s++) splat(a.x + dx * s / n, a.y + dy * s / n, dx / n, dy / n, raio);
  };
  var amostra = function (f, x, y) {
   x = x < 0 ? 0 : x > cols - 1.001 ? cols - 1.001 : x;
   y = y < 0 ? 0 : y > lin - 1.001 ? lin - 1.001 : y;
   var i = x | 0, j = y | 0, fx = x - i, fy = y - j, k = j * cols + i;
   return (f[k] * (1 - fx) + f[k + 1] * fx) * (1 - fy) + (f[k + cols] * (1 - fx) + f[k + cols + 1] * fx) * fy;
  };
  var passo = function (dt) {
   var dd = Math.pow(0.96, dt), vd = Math.pow(0.9, dt), mxv = 0, m = 0, t;
   for (var j = 0, k = 0; j < lin; j++) for (var i = 0; i < cols; i++, k++) {
    var x = i - u[k] * dt, y = j - v[k] * dt, val = amostra(d, x, y) * dd;
    d2[k] = val;
    if (val > mxv) mxv = val;
    if (val > 0.3) m++;
    u2[k] = amostra(u, x, y) * vd;
    v2[k] = amostra(v, x, y) * vd;
   }
   t = d; d = d2; d2 = t; t = u; u = u2; u2 = t; t = v; v = v2; v2 = t;
   fmax = mxv; massa = m / (cols * lin);
  };
  // por quadro: a arte sem escala + um drawImage do buraco e um do anel
  var desenha = function () {
   ctx.globalCompositeOperation = "copy";
   ctx.drawImage(arte, 0, 0);
   if (fmax < 0.05) return;
   var a = mi.data, r = ri.data;
   // campo interpolado SUP vezes antes do limiar: contorno liso, sem degrau de celula
   for (var j = 0, k = 0; j < mh; j++) for (var i = 0; i < mw; i++, k++) {
    var x = amostra(d, (i + 0.5) / SUP - 0.5, (j + 0.5) / SUP - 0.5), b = 1 - Math.abs(x - 0.34) / 0.035;
    a[k * 4 + 3] = suave((x - 0.3) / 0.12) * 255;
    r[k * 4 + 3] = b > 0 ? suave(b) * 235 : 0;
   }
   mx.putImageData(mi, 0, 0); rx.putImageData(ri, 0, 0);
   ctx.globalCompositeOperation = "destination-out";
   ctx.drawImage(mc, 0, 0, cv.width, cv.height);
   ctx.globalCompositeOperation = "source-over";
   ctx.drawImage(rc, 0, 0, cv.width, cv.height);
  };
  // qualidade: 2 intervalos seguidos > 40 ms desligam o cursor virtual; media de 30 quadros > 22 ms reduz so o campo
  var qualidade = function (iv, custo) {
   lento = iv > 40 ? lento + 1 : 0;
   if (lento >= 2) auto = false;
   jI.push(iv);
   if (jI.length < JANELA) return;
   for (var a = 0, i = 0; i < JANELA; i++) a += jI[i];
   jI = [];
   if (a / JANELA > 22 && cols > MIN) {
    nivel++; cols = Math.max(MIN, COLS >> nivel); lin = Math.max(30, LIN >> nivel);
    aloca();
   }
  };
  var quadro = function (agora) {
   raf = 0;
   if (!visivel || doc.hidden) return;
   var iv = ultimo ? agora - ultimo : 0, dt = Math.min(3, iv / 16.667 || 1);
   window.__revelarQuadros++;
   ultimo = agora;
   if (auto && agora - entrada > OCIOSO) {
    var s = agora / 1000, p = { x: W * (0.5 + 0.34 * Math.sin(s * 0.7)), y: H * (0.5 + 0.3 * Math.sin(s * 1.1 + 1)) };
    if (vp) traco(vp, p);
    vp = p;
   } else vp = null;
   if (seg) splat(seg.x, seg.y, 0, 0, W * 0.07);
   if (fmax > 0.004) passo(dt);
   if (sujo) { desenha(); sujo = fmax > 0.004; }
   if (massa > 0.02 && (acum += iv) >= CICLO) { acum = 0; irPara(indice + 1); }
   if (iv) qualidade(iv);
   continua(agora);
  };
  var continua = function (agora) {
   if (!visivel || doc.hidden) { ultimo = 0; return; }
   if (fmax > 0.004 || seg || sujo || (auto && agora - entrada > OCIOSO)) { if (!raf) raf = RAF(quadro); return; }
   ultimo = 0; jI = [];
   clearTimeout(espera);
   if (auto) espera = setTimeout(acorda, Math.max(0, OCIOSO - (agoraMs() - entrada)) + 20);
  };
  var acorda = function () {
   clearTimeout(espera);
   if (visivel && !doc.hidden && !raf) raf = RAF(quadro);
  };
  var pausa = function () {
   if (raf) { CAF(raf); raf = 0; }
   clearTimeout(espera); ultimo = 0;
  };
  // posicao do palco em cache (resize e ResizeObserver); o scroll entra por scrollY, sem listener de scroll
  window.addEventListener("resize", medida);
  var local = function (e) { return { x: e.clientX - R.x, y: e.clientY - R.y + window.scrollY - R.s }; };
  var alimenta = function (e, novo) {
   var p = local(e), agora = agoraMs();
   if (pt && !novo && agora - entrada < 120) traco(pt, p); else splat(p.x, p.y, 0, 0, W * 0.07);
   pt = p; if (seg) seg = p;
   entrada = agora; vp = null; acorda();
  };
  el.addEventListener("pointermove", function (e) { if (e.pointerType === "mouse" || seg) alimenta(e, false); });
  el.addEventListener("pointerdown", function (e) { medida(); seg = local(e); alimenta(e, true); });
  var solta = function () { seg = null; pt = null; };
  ["pointerup", "pointercancel", "pointerleave"].forEach(function (t) { el.addEventListener(t, solta); });
  aoTrocar = function () { pintaCor(); if (pintaArte()) { sujo = true; desenha(); } acorda(); };
  if ("IntersectionObserver" in window) {
   new IntersectionObserver(function (es) { visivel = es[es.length - 1].isIntersecting; if (visivel) acorda(); else pausa(); }).observe(el);
  }
  doc.addEventListener("visibilitychange", function () { if (doc.hidden) pausa(); else acorda(); });
  aloca();
  var inicia = function () { tamanho(); acorda(); };
  if (img.complete && img.naturalWidth) inicia(); else img.addEventListener("load", inicia, { once: true });
  window.__revelarEstado = function () { return { cols: cols, linhas: lin, nivel: nivel, auto: auto }; };
 }

 function montarCartao(el) {
  var vai = function (e, f) {
   var b = el.getBoundingClientRect(), st = el.style;
   st.setProperty("--mx", e.clientX - b.left + "px"); st.setProperty("--my", e.clientY - b.top + "px");
   st.setProperty("--r", f * Math.max(b.width, b.height) * 0.28 + "px");
  };
  el.addEventListener("pointermove", function (e) { if (e.pointerType !== "touch" || e.buttons) vai(e, 1); });
  el.addEventListener("pointerdown", function (e) { vai(e, 1.3); });
  ["pointerup", "pointercancel", "pointerleave"].forEach(function (t) {
   el.addEventListener(t, function (e) { vai(e, t === "pointerup" && e.pointerType !== "touch" ? 1 : 0); });
  });
 }

 window.AllDevsRevelar = { montarHero: montarHero, montarCartao: montarCartao };
 var palco = doc.querySelector(".hero-palco[data-ciclo]");
 if (palco) montarHero(palco);
})();
