/* "Da ideia ao ar" (ALL.dev v2). Sem JS os 5 estagios ficam empilhados e legiveis.
   Desktop com movimento: a secao fica presa (pin) e a rolagem (scrub) troca o estagio; o codigo "digita" por clip-path.
   Celular com movimento: cada estagio entra ao aparecer (IntersectionObserver). Reduced-motion: nada se anima. */
(function () {
 var g = window.gsap, sec = document.getElementById("ideia");
 if (!g || !window.ScrollTrigger || !g.matchMedia || !sec) return;
 g.registerPlugin(window.ScrollTrigger);
 var est = [].slice.call(sec.querySelectorAll(".ideia-estagio")), n = est.length;
 if (!n) return;
 var linhas = function (e) {
  var c = e.querySelector(".ideia-codigo code");
  return c ? { el: c.parentNode, n: Math.max(1, c.textContent.split("\n").length) } : null;
 };
 var fecha = function () { return "inset(0 0 100% 0)"; };
 var abre = "inset(0 0 0% 0)";
 var mm = window.gsap.matchMedia();
 mm.add({
  desk: "(min-width: 1024px) and (prefers-reduced-motion: no-preference)",
  movel: "(max-width: 1023px) and (prefers-reduced-motion: no-preference)"
 }, function (ctx) {
  if (ctx.conditions.desk) {
   var barra = sec.querySelector(".ideia-trilho-barra"), ativo = -1, st;
   sec.classList.add("ideia-pin");
   var marca = function (i) {
    if (i === ativo) return;
    ativo = i;
    est.forEach(function (e, k) {
     e.classList.toggle("ativo", k === i);
     if (k === i) e.setAttribute("aria-current", "step"); else e.removeAttribute("aria-current");
    });
   };
   var tl = g.timeline({ defaults: { ease: "none" }, scrollTrigger: {
    trigger: sec, start: "top top", end: "+=" + n * 70 + "%", pin: true, scrub: 0.5, anticipatePin: 1,
    onUpdate: function (s) { marca(Math.min(n - 1, Math.floor(s.progress * n))); }
   } });
   st = tl.scrollTrigger;
   if (barra) tl.to(barra, { scaleX: 1, duration: n }, 0);
   est.forEach(function (e, i) {
    if (i) tl.fromTo(e, { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: 0.3 }, i); else g.set(e, { opacity: 1 });
    if (i < n - 1) tl.to(e, { opacity: 0, y: -28, duration: 0.25 }, i + 0.72);
    var c = linhas(e);
    if (c) tl.fromTo(c.el, { clipPath: fecha() }, { clipPath: abre, ease: "steps(" + c.n + ")", duration: 0.55 }, i + 0.15);
    e.addEventListener("focusin", function () {
     if (i !== ativo) window.scrollTo(0, st.start + (st.end - st.start) * ((i + 0.5) / n));
    });
   });
   marca(0);
   return function () {
    sec.classList.remove("ideia-pin");
    est.forEach(function (e) { e.classList.remove("ativo"); e.removeAttribute("aria-current"); });
   };
  }
  var io = new IntersectionObserver(function (lista) {
   lista.forEach(function (r) {
    if (!r.isIntersecting) return;
    var e = r.target, c = linhas(e);
    io.unobserve(e);
    e.classList.add("ideia-visto");
    if (c) g.fromTo(c.el, { clipPath: fecha() }, { clipPath: abre, ease: "steps(" + c.n + ")", duration: 0.9, clearProps: "clipPath" });
   });
  }, { threshold: 0.2 });
  est.forEach(function (e) {
   var c = linhas(e);
   e.classList.add("ideia-oculto");
   if (c) g.set(c.el, { clipPath: fecha() });
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
