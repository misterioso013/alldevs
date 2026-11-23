/* Base de movimento do ALL.dev v2. Script clássico com defer, carregado depois de js/vendor/.
   Sem JS o site fica inteiro: nada começa escondido, o FAQ abre, o contato funciona.
   Tempos e curva vêm de css/tokens.css. Visibilidade por IntersectionObserver; este arquivo não ouve "scroll". */
(function () {
  "use strict";

  var doc = document;
  var raiz = doc.documentElement;
  var mq = function (q) { return !!(window.matchMedia && window.matchMedia(q).matches); };
  var reduz = mq("(prefers-reduced-motion: reduce)");
  var temIO = "IntersectionObserver" in window;

  /* ---------- Tempos e curva únicos, lidos dos tokens ---------- */
  var estilo = getComputedStyle(raiz);
  var tempo = function (nome, padrao) {
    var v = parseFloat(estilo.getPropertyValue(nome));
    return isNaN(v) ? padrao : v / 1000;
  };
  var DUR_CURTA = tempo("--dur-curta", 0.2);
  var DUR_LONGA = tempo("--dur-longa", 0.8);
  var STAGGER = 0.05;

  var curva = function (nome, padrao) {
    var m = /cubic-bezier\(([^)]+)\)/.exec(estilo.getPropertyValue(nome));
    var p = m ? m[1].split(",").map(parseFloat) : padrao;
    var x1 = p[0], y1 = p[1], x2 = p[2], y2 = p[3];
    var bz = function (t, a, b) { return 3 * a * t * (1 - t) * (1 - t) + 3 * b * t * t * (1 - t) + t * t * t; };
    var dbz = function (t, a, b) { return 3 * a * (1 - t) * (1 - t) + 6 * (b - a) * t * (1 - t) + 3 * (1 - b) * t * t; };
    return function (x) {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      var t = x;
      for (var i = 0; i < 8; i++) {
        var d = dbz(t, x1, x2);
        if (Math.abs(d) < 1e-6) break;
        t -= (bz(t, x1, x2) - x) / d;
      }
      return bz(Math.min(1, Math.max(0, t)), y1, y2);
    };
  };

  var naTela = function (el) {
    var r = el.getBoundingClientRect();
    return r.top < window.innerHeight && r.bottom > 0;
  };

  /* Observa os elementos uma vez: chama aoEntrar(el) quando 15% aparece e para de observar. */
  var umaVez = function (els, aoEntrar) {
    if (!temIO) { els.forEach(aoEntrar); return; }
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        aoEntrar(e.target);
      });
    }, { threshold: 0.15 });
    els.forEach(function (el) { io.observe(el); });
  };

  /* ---------- Sorteio: a ordem dos cartões de [data-sortear] muda a cada visita ---------- */
  doc.querySelectorAll("[data-sortear]").forEach(function (lista) {
    var itens = Array.prototype.slice.call(lista.children);
    for (var i = itens.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = itens[i]; itens[i] = itens[j]; itens[j] = t;
    }
    itens.forEach(function (el) { lista.appendChild(el); });
  });

  /* ---------- FAQ dos serviços: aberto sem JS, sanfona com JS ---------- */
  doc.querySelectorAll(".faq-question").forEach(function (botao, n) {
    var resposta = botao.nextElementSibling;
    if (!resposta || !resposta.classList.contains("faq-answer")) return;
    resposta.id = resposta.id || "faq-resposta-" + (n + 1);
    botao.setAttribute("aria-controls", resposta.id);
    botao.setAttribute("aria-expanded", "false");
    botao.removeAttribute("disabled"); // vem desativado no HTML: sem JS a resposta fica aberta e o botão não engana
    resposta.hidden = true;
    botao.addEventListener("click", function () {
      var abrir = botao.getAttribute("aria-expanded") !== "true";
      botao.setAttribute("aria-expanded", String(abrir));
      resposta.hidden = !abrir;
    });
  });

  /* ---------- data-revela: entra subindo 24 px com opacidade (CSS faz a transição) ---------- */
  if (!reduz) {
    var reveladas = Array.prototype.filter.call(doc.querySelectorAll("[data-revela]"), function (el) { return !naTela(el); });
    reveladas.forEach(function (el) { el.classList.add("revela-oculto"); });
    umaVez(reveladas, function (el) { el.classList.add("revela-vista"); });
  }

  /* ---------- Preloader: só na 1ª visita da sessão, ≤ 1 s. Sobreposição com opacity sobre a página já pintada,
     então o h1 do LCP nunca fica escondido do navegador. ---------- */
  var primeiraVisita = function () {
    try {
      if (window.sessionStorage.getItem("alldev-visto")) return false;
      window.sessionStorage.setItem("alldev-visto", "1");
      return true;
    } catch (erro) {
      return false; // sem storage: nunca mostra, para não repetir a cada página
    }
  };
  if (!reduz && primeiraVisita()) {
    var pre = doc.createElement("div");
    pre.className = "preloader";
    pre.setAttribute("aria-hidden", "true");
    pre.innerHTML = "<span>all.dev</span>";
    doc.body.appendChild(pre);
    window.setTimeout(function () { pre.classList.add("preloader-saindo"); }, 500);
    window.setTimeout(function () { if (pre.parentNode) pre.parentNode.removeChild(pre); }, 500 + DUR_CURTA * 2000);
  }

  /* ---------- Cursor próprio: só com mouse. O nativo continua; a bolinha acompanha e mostra o data-cursor ---------- */
  if (mq("(pointer: fine)") && !reduz) {
    var cursor = doc.createElement("div");
    cursor.className = "cursor";
    cursor.setAttribute("aria-hidden", "true");
    var rotulo = doc.createElement("span");
    rotulo.className = "cursor-texto";
    cursor.appendChild(rotulo);
    doc.body.appendChild(cursor);
    var alvoX = 0, alvoY = 0, quadro = 0;
    var desenha = function () {
      quadro = 0;
      cursor.style.transform = "translate3d(" + alvoX + "px," + alvoY + "px,0)";
    };
    doc.addEventListener("pointermove", function (e) {
      if (e.pointerType && e.pointerType !== "mouse") return;
      alvoX = e.clientX;
      alvoY = e.clientY;
      cursor.classList.add("cursor-ativo");
      if (!quadro) quadro = window.requestAnimationFrame(desenha);
    });
    doc.addEventListener("pointerover", function (e) {
      var el = e.target.closest ? e.target.closest("[data-cursor]") : null;
      var texto = el ? el.getAttribute("data-cursor") : "";
      rotulo.textContent = texto || "";
      cursor.classList.toggle("cursor-com-texto", !!texto);
    });
    doc.documentElement.addEventListener("pointerleave", function () { cursor.classList.remove("cursor-ativo"); });
  }

  var gsap = window.gsap;

  /* ---------- .titulo-revela: linhas com overflow: hidden, sobem em sequência (0,05 s) ---------- */
  var titulos = doc.querySelectorAll(".titulo-revela");
  if (!reduz && titulos.length && gsap && window.SplitText) {
    gsap.registerPlugin(window.SplitText);
    var saida = curva("--curva-saida", [0.22, 1, 0.36, 1]);
    var fontes = doc.fonts && doc.fonts.ready ? doc.fonts.ready : Promise.resolve();
    fontes.then(function () {
      titulos.forEach(function (titulo) {
        // Título com link ou botão fica inteiro: dividido, o link perderia o nome acessível.
        if (titulo.querySelector("a, button")) return;
        try {
          var lido = (titulo.innerText || titulo.textContent).replace(/\s+/g, " ").trim();
          var partes = window.SplitText.create(titulo, {
            type: "lines", linesClass: "linha-revela", mask: "lines", aria: "auto"
          });
          if (titulo.hasAttribute("aria-label")) titulo.setAttribute("aria-label", lido);
          partes.masks.forEach(function (m) { m.classList.add("linha-mascara"); });
          gsap.set(partes.lines, { yPercent: 110 });
          umaVez([titulo], function () {
            gsap.to(partes.lines, { yPercent: 0, duration: DUR_LONGA, stagger: STAGGER, ease: saida });
          });
        } catch (erro) {
          if (window.console) console.warn("titulo-revela falhou em", titulo, erro);
        }
      });
    });
  }

  /* ---------- Lenis: só com mouse, tela larga e sem reduced-motion ---------- */
  if (!reduz && mq("(pointer: fine) and (min-width: 1024px)") && typeof window.Lenis === "function" && gsap) {
    var lenis = new window.Lenis({ anchors: true, autoRaf: false });
    if (window.ScrollTrigger) {
      gsap.registerPlugin(window.ScrollTrigger);
      lenis.on("scroll", window.ScrollTrigger.update);
    }
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
  }
})();
