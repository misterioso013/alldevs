/* "Da ideia ao ar" (ALL.dev v2). Sem JS os 3 estagios ficam empilhados e legiveis.
   Desktop com movimento: a secao fica presa (pin) e a rolagem (scrub) troca o estagio; o codigo "digita" por clip-path.
   Os estagios inativos ficam fora da arvore de acessibilidade e do foco (inert); o Tab anda de estagio em estagio.
   Celular com movimento: cada estagio entra ao aparecer (IntersectionObserver). Reduced-motion: nada se anima. */
(function () {
 var g = window.gsap, sec = document.getElementById("ideia");
 if (!g || !window.ScrollTrigger || !g.matchMedia || !sec) return;
 g.registerPlugin(window.ScrollTrigger);
 var est = [].slice.call(sec.querySelectorAll(".ideia-estagio")), n = est.length;
 if (!n) return;
 var linhas = function (e) {
  var c = e.querySelector(".ideia-codigo code");
  return c ? { el: c, n: Math.max(1, c.textContent.replace(/\n$/, "").split("\n").length) } : null;
 };
 var fecha = "inset(0 0 100% 0)", abre = "inset(0 0 0% 0)";
 var paradas = function (e) { return [e].concat([].slice.call(e.querySelectorAll("pre[tabindex], a[href]"))); };
 var mm = window.gsap.matchMedia();
 mm.add({
  desk: "(min-width: 1024px) and (prefers-reduced-motion: no-preference)",
  movel: "(max-width: 1023px) and (prefers-reduced-motion: no-preference)"
 }, function (ctx) {
  if (ctx.conditions.desk) {
   var barra = sec.querySelector(".ideia-trilho-barra"), ativo = -1, st, ac = new AbortController();
   sec.classList.add("ideia-pin");
   var marca = function (i) {
    if (i === ativo) return;
    ativo = i;
    est.forEach(function (e, k) {
     var on = k === i;
     e.classList.toggle("ativo", on);
     if (on) { e.setAttribute("aria-current", "step"); e.removeAttribute("inert"); e.removeAttribute("aria-hidden"); e.tabIndex = 0; }
     else { e.removeAttribute("aria-current"); e.setAttribute("inert", ""); e.setAttribute("aria-hidden", "true"); e.removeAttribute("tabindex"); }
    });
   };
   var doProgresso = function (p) { return Math.max(0, Math.min(n - 1, Math.floor(p * n))); };
   // Rola ate o ponto em que o estagio k esta 100% revelado (codigo inteiro, antes do fade-out).
   var vai = function (k) {
    marca(k);
    window.scrollTo({ top: st.start + (st.end - st.start) * ((k + 0.6) / n), behavior: "instant" });
   };
   var tl = g.timeline({ defaults: { ease: "none" }, scrollTrigger: {
    trigger: sec, start: "top top", end: "+=" + n * 70 + "%", pin: true, scrub: 0.5, anticipatePin: 1,
    onUpdate: function (s) { marca(doProgresso(s.progress)); },
    onRefresh: function (s) { marca(doProgresso(s.progress)); }
   } });
   st = tl.scrollTrigger;
   if (barra) tl.to(barra, { scaleX: 1, duration: n }, 0);
   est.forEach(function (e, i) {
    if (i) tl.fromTo(e, { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: 0.3 }, i); else g.set(e, { opacity: 1 });
    if (i < n - 1) tl.to(e, { opacity: 0, y: -28, duration: 0.25 }, i + 0.72);
    var c = linhas(e);
    // revela em saltos de uma linha (steps) e termina em i+0.45: do fim da revelacao ao fade-out sobram 0,27 de timeline
    if (c) tl.fromTo(c.el, { clipPath: fecha }, { clipPath: abre, ease: "steps(" + c.n + ")", duration: 0.3 }, i + 0.15);
   });
   marca(doProgresso(st.progress));
   // Foco: so o estagio ativo e focavel; foco que chega a ele (clique, script) leva a rolagem ao ponto 100% legivel.
   sec.addEventListener("focusin", function (ev) {
    var k = est.indexOf(ev.target.closest && ev.target.closest(".ideia-estagio"));
    if (k < 0) return;
    var p = st.progress * n - k;
    if (k !== ativo || p < 0.5 || p > 0.72) vai(k);
   }, { signal: ac.signal });
   // Tab/Shift+Tab: com os outros estagios inertes, o fim das paradas do ativo avanca o pin um estagio.
   sec.addEventListener("keydown", function (ev) {
    if (ev.key !== "Tab" || ev.altKey || ev.ctrlKey || ev.metaKey) return;
    var ps = paradas(est[ativo]), i = ps.indexOf(document.activeElement);
    if (i < 0) return;
    var j = ev.shiftKey ? i - 1 : i + 1, k = ativo + (ev.shiftKey ? -1 : 1);
    if (j >= 0 && j < ps.length) return;       // ainda ha parada dentro do estagio: Tab nativo
    if (k < 0 || k >= n) return;               // inicio/fim da secao: Tab nativo sai dela
    ev.preventDefault();
    vai(k);
    var alvo = paradas(est[k]);
    alvo[ev.shiftKey ? alvo.length - 1 : 0].focus({ preventScroll: true });
   }, { signal: ac.signal });
   return function () {
    ac.abort();
    sec.classList.remove("ideia-pin");
    est.forEach(function (e) {
     e.classList.remove("ativo");
     ["aria-current", "inert", "aria-hidden", "tabindex"].forEach(function (a) { e.removeAttribute(a); });
    });
   };
  }
  var io = new IntersectionObserver(function (lista) {
   lista.forEach(function (r) {
    if (!r.isIntersecting) return;
    var e = r.target, c = linhas(e);
    io.unobserve(e);
    e.classList.add("ideia-visto");
    if (c) g.fromTo(c.el, { clipPath: fecha }, { clipPath: abre, ease: "steps(" + c.n + ")", duration: 0.9, clearProps: "clipPath" });
   });
  }, { threshold: 0.2 });
  est.forEach(function (e) {
   var c = linhas(e);
   e.classList.add("ideia-oculto");
   if (c) g.set(c.el, { clipPath: fecha });
   io.observe(e);
  });
  return function () {
   io.disconnect();
   est.forEach(function (e) {
    e.classList.remove("ideia-oculto", "ideia-visto");
    var c = linhas(e);
    if (c) g.set(c.el, { clearProps: "clipPath" });
   });
  };
 });
})();
