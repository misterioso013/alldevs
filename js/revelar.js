/* Revelacao "por tras do produto" (ALL.dev v2): a frente (captura real) vira canvas 2D com um buraco que segue o ponteiro;
   por baixo fica o trecho real. Campo de densidade em grade pequena, advectado e com decaimento. window.AllDevsRevelar. */
(function () {
 var doc = document, estilo = getComputedStyle(doc.documentElement);
 var reduz = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
 var agoraMs = function () { return performance.now(); };
 var RAF = window.requestAnimationFrame.bind(window), CAF = window.cancelAnimationFrame.bind(window);
 var COLS = 144, LIN = 90, MIN = 48, OCIOSO = 2000, CICLO = 7000, JANELA = 30;
 var tok = function (n) { return (estilo.getPropertyValue(n) || "").trim(); };
 var cor3 = function (n) {
  var h = tok(n).replace("#", "");
  if (h.length === 3) h = h.replace(/./g, "$&$&");
  var x = parseInt(h, 16);
  return h.length === 6 && x === x ? [(x >> 16) & 255, (x >> 8) & 255, x & 255] : [0, 0, 0];
 };
 var corItem = function (c) { return cor3(c === "laranja" ? "--laranja-claro" : "--roxo-claro"); };
 var suave = function (x) { x = x < 0 ? 0 : x > 1 ? 1 : x; return x * x * (3 - 2 * x); };
 var DUR = parseFloat(tok("--dur-curta")) || 200;
 function montarHero(el) {
  var itens;
  try { itens = JSON.parse(doc.getElementById("ciclo").textContent); } catch (e) { return; }
  var q = function (s) { return el.querySelector(s); };
  var img = q(".hero-frente img"), atras = q(".hero-por-tras"), cv = q(".hero-mascara"),
   botao = q(".hero-ver-por-tras"), frase = q(".hero-frase"), origem = q(".hero-origem");
  if (!itens || !itens.length || !img || !atras || !cv) return;
  var pre = atras.querySelector("pre");
  if (pre) pre.hidden = false;
  var indice = 0, trocando = false, cor = corItem(itens[0].cor), aoTrocar = function () {};
  var irPara = function (i) {
   if (trocando || itens.length < 2) return;
   trocando = true;
   indice = (i + itens.length) % itens.length;
   var it = itens[indice];
   el.classList.add("trocando");
   setTimeout(function () {
    var n = new Image();
    var fim = function () { el.classList.remove("trocando"); trocando = false; };
    n.onerror = fim;
    n.onload = function () {
        img.width = it.frente.w; img.height = it.frente.h;
     img.alt = "Captura de tela de " + it.nome;
     img.src = it.frente.src;
     if (pre) pre.firstChild.textContent = it.por_tras.texto;
     origem.textContent = it.por_tras.origem;
     frase.firstChild.textContent = it.nome;
     frase.lastChild.nodeValue = " " + it.frase;
     el.setAttribute("data-cor", it.cor);
     cor = corItem(it.cor);
     aoTrocar();
     RAF(fim);
    };
    n.src = it.frente.src;
   }, DUR);
  };
  var baixo = null;
  el.addEventListener("pointerdown", function (e) { baixo = { x: e.clientX, y: e.clientY, t: agoraMs() }; });
  el.addEventListener("click", function (e) {
   if (botao && botao.contains(e.target)) return;
   var b = baixo; baixo = null;
   if (b && (agoraMs() - b.t > 250 || Math.abs(e.clientX - b.x) + Math.abs(e.clientY - b.y) > 10)) return;
   irPara(indice + 1);
  });
  if (reduz) {
   cv.parentNode.removeChild(cv);
   if (botao) {
    botao.hidden = false;
    botao.addEventListener("click", function () {
     var m = !el.classList.contains("mostrando");
     el.classList.toggle("mostrando", m);
     botao.setAttribute("aria-pressed", String(m));
    });
   }
   return;
  }
  var ctx = cv.getContext("2d");
  if (!ctx) return;
  var arte = doc.createElement("canvas"), actx = arte.getContext("2d");
  var mc = doc.createElement("canvas"), rc = doc.createElement("canvas"), mx = mc.getContext("2d"), rx = rc.getContext("2d");
  var mi, ri, cols = COLS, lin = LIN, nivel = 0, d, d2, u, v, u2, v2, W = 0, H = 0, fmax = 0, massa = 0;
  var visivel = true, raf = 0, espera = 0, ultimo = 0, auto = true, lento = 0, sujo = true, acum = 0;
  var entrada = agoraMs(), pt = null, vp = null, seg = null, jI = [], jC = [];
  window.__revelarQuadros = 0;
  var pintaCor = function () {
   for (var k = 0; k < cols * lin; k++) { ri.data[k * 4] = cor[0]; ri.data[k * 4 + 1] = cor[1]; ri.data[k * 4 + 2] = cor[2]; }
  };
  var aloca = function () {
   var n = cols * lin;
   d = new Float32Array(n); d2 = new Float32Array(n); u = new Float32Array(n);
   v = new Float32Array(n); u2 = new Float32Array(n); v2 = new Float32Array(n);
   mc.width = rc.width = cols; mc.height = rc.height = lin;
   mi = mx.createImageData(cols, lin); ri = rx.createImageData(cols, lin);
   for (var k = 0; k < n * 4; k++) mi.data[k] = 255;
   pintaCor();
  };
  var pintaArte = function () {
   if (!img.naturalWidth) return false;
   actx.fillStyle = tok("--fundo-2");
   actx.fillRect(0, 0, arte.width, arte.height);
   var s = Math.min(arte.width / img.naturalWidth, arte.height / img.naturalHeight);
   var w = img.naturalWidth * s, h = img.naturalHeight * s;
   actx.drawImage(img, (arte.width - w) / 2, (arte.height - h) / 2, w, h);
   return true;
  };
  var tamanho = function () {
   var r = el.getBoundingClientRect();
   W = r.width; H = r.height;
   if (!W || !H) return;
   var f = Math.min(window.devicePixelRatio || 1, 2) / (1 << nivel);
   f *= Math.min(1, 1200 / (W * f));
   cv.width = arte.width = Math.max(2, Math.round(W * f));
   cv.height = arte.height = Math.max(2, Math.round(H * f));
   if (pintaArte()) { el.classList.add("vivo"); sujo = true; }
  };
  var splat = function (x, y, dx, dy, raio) {
   var gx = x / W * cols, gy = y / H * lin, r = raio / W * cols, R = Math.ceil(r * 1.8);
   var i0 = Math.max(0, (gx - R) | 0), i1 = Math.min(cols - 1, (gx + R) | 0);
   var j0 = Math.max(0, (gy - R) | 0), j1 = Math.min(lin - 1, (gy + R) | 0);
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
  var desenha = function () {
   ctx.globalCompositeOperation = "source-over";
   ctx.clearRect(0, 0, cv.width, cv.height);
   ctx.drawImage(arte, 0, 0);
   if (fmax < 0.05) return;
   var a = mi.data, r = ri.data;
   for (var k = 0, n = cols * lin; k < n; k++) {
    var x = d[k], t = suave((x - 0.3) / 0.3);
    a[k * 4 + 3] = t * 255;
    r[k * 4 + 3] = suave((x - 0.08) / 0.2) * (1 - t) * 220;
   }
   mx.putImageData(mi, 0, 0); rx.putImageData(ri, 0, 0);
   ctx.globalCompositeOperation = "destination-out";
   ctx.drawImage(mc, 0, 0, cv.width, cv.height);
   ctx.globalCompositeOperation = "source-over";
   ctx.drawImage(rc, 0, 0, cv.width, cv.height);
  };
  var qualidade = function (iv, custo) {
   jI.push(iv); jC.push(custo);
   if (jI.length < JANELA) return;
   var a = 0, b = 0, i;
   for (i = 0; i < JANELA; i++) { a += jI[i]; b += jC[i]; }
   a /= JANELA; b /= JANELA; jI = []; jC = [];
   if (a <= 22) { lento = 0; return; }
   if (b > 6 && cols > MIN) {
    nivel++; cols = Math.max(MIN, COLS >> nivel); lin = Math.max(30, LIN >> nivel);
    aloca(); tamanho();
   }
   if (a > 40) { if (++lento >= 2) auto = false; } else lento = 0;
  };
  var quadro = function (agora) {
   raf = 0;
   if (!visivel || doc.hidden) return;
   var t0 = agoraMs(), iv = ultimo ? agora - ultimo : 0, dt = Math.min(3, iv / 16.667 || 1);
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
   if (iv) qualidade(iv, agoraMs() - t0);
   continua(agora);
  };
  var continua = function (agora) {
   if (!visivel || doc.hidden) { ultimo = 0; return; }
   if (fmax > 0.004 || seg || sujo || (auto && agora - entrada > OCIOSO)) { if (!raf) raf = RAF(quadro); return; }
   ultimo = 0; jI = []; jC = [];
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
  var local = function (e) { var r = el.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; };
  var alimenta = function (e, novo) {
   var p = local(e), agora = agoraMs();
   if (pt && !novo && agora - entrada < 120) traco(pt, p); else splat(p.x, p.y, 0, 0, W * 0.07);
   pt = p; if (seg) seg = p;
   entrada = agora; vp = null; acorda();
  };
  el.addEventListener("pointermove", function (e) { if (e.pointerType === "mouse" || seg) alimenta(e, false); });
  el.addEventListener("pointerdown", function (e) { seg = local(e); alimenta(e, true); });
  var solta = function () { seg = null; pt = null; };
  ["pointerup", "pointercancel", "pointerleave"].forEach(function (t) { el.addEventListener(t, solta); });
  aoTrocar = function () {
   pintaCor();
   var f = function () { if (pintaArte()) sujo = true; acorda(); };
   if (img.complete && img.naturalWidth) f(); else img.addEventListener("load", f, { once: true });
  };
  if ("IntersectionObserver" in window) {
   new IntersectionObserver(function (es) { visivel = es[es.length - 1].isIntersecting; if (visivel) acorda(); else pausa(); }).observe(el);
  }
  doc.addEventListener("visibilitychange", function () { if (doc.hidden) pausa(); else acorda(); });
  {
   var uw = 0;
   new ResizeObserver(function () {
    var w = Math.round(el.getBoundingClientRect().width);
    if (w !== uw) { uw = w; tamanho(); acorda(); }
   }).observe(el);
  }
  aloca();
  var inicia = function () { tamanho(); acorda(); };
  if (img.complete && img.naturalWidth) inicia(); else img.addEventListener("load", inicia, { once: true });
  window.__revelarEstado = function () { return { cols: cols, linhas: lin, nivel: nivel }; };
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
