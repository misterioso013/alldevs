/* Movimento e interação do ALL.dev. Script clássico com defer, carregado depois de js/vendor/.
   Sem JS o site fica inteiro: filtro escondido, todos os projetos e respostas visíveis.
   Tempos e curva vêm de css/tokens.css (--t-curto, --t-medio, --t-longo, --curva). */
(function () {
  "use strict";

  var doc = document;
  var raiz = doc.documentElement;
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var temGsap = typeof window.gsap !== "undefined";

  /* ---------- Sorteio: a ordem dos cartões de [data-sortear] muda a cada visita ---------- */
  doc.querySelectorAll("[data-sortear]").forEach(function (lista) {
    var itens = Array.prototype.slice.call(lista.children);
    for (var i = itens.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = itens[i]; itens[i] = itens[j]; itens[j] = t;
    }
    itens.forEach(function (el) { lista.appendChild(el); });
  });

  /* ---------- Filtro de /projetos/ por data-autores ---------- */
  var botoes = doc.querySelectorAll(".filtro-botao[data-filtro]");
  if (botoes.length) {
    var cartoes = doc.querySelectorAll("[data-autores]");
    var filtrar = function (slug) {
      botoes.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.filtro === slug)); });
      cartoes.forEach(function (c) {
        var autores = (c.getAttribute("data-autores") || "").split(/\s+/);
        c.hidden = !(slug === "todos" || autores.indexOf(slug) !== -1);
      });
      if (window.ScrollTrigger) window.ScrollTrigger.refresh();
    };
    botoes.forEach(function (b) {
      b.hidden = false;
      b.addEventListener("click", function () { filtrar(b.dataset.filtro); });
    });
    filtrar("todos");
  }

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
      if (window.ScrollTrigger) window.ScrollTrigger.refresh();
    });
  });

  if (!temGsap) return;
  var gsap = window.gsap;
  var ST = window.ScrollTrigger;
  var Split = window.SplitText;
  if (ST) gsap.registerPlugin(ST);
  if (Split) gsap.registerPlugin(Split);

  /* ---------- Tempos e curva únicos, lidos dos tokens ---------- */
  var estilo = getComputedStyle(raiz);
  var tempo = function (nome, padrao) {
    var v = parseFloat(estilo.getPropertyValue(nome));
    return isNaN(v) ? padrao : v / 1000;
  };
  var T_CURTO = tempo("--t-curto", 0.2);
  var T_MEDIO = tempo("--t-medio", 0.45);
  var T_LONGO = tempo("--t-longo", 0.9);

  // cubic-bezier(x1, y1, x2, y2) de --curva, resolvido por Newton (igual ao CSS)
  var curva = (function () {
    var m = /cubic-bezier\(([^)]+)\)/.exec(estilo.getPropertyValue("--curva"));
    var p = m ? m[1].split(",").map(parseFloat) : [0.22, 1, 0.36, 1];
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
  })();
  gsap.defaults({ ease: curva, duration: T_MEDIO });

  var naTela = function (el) {
    var r = el.getBoundingClientRect();
    return r.top < window.innerHeight && r.bottom > 0;
  };

  /* ---------- Laços: só rodam com o elemento na tela e a aba visível ---------- */
  var lacos = [];
  var atualizarLacos = function () {
    lacos.forEach(function (l) {
      if (l.visivel && !doc.hidden) l.tl.play(); else l.tl.pause();
    });
  };
  var laco = function (el, tl) {
    var l = { tl: tl.pause(), visivel: false };
    lacos.push(l);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entradas) {
        l.visivel = entradas[entradas.length - 1].isIntersecting;
        atualizarLacos();
      }).observe(el);
    } else {
      l.visivel = true;
      atualizarLacos();
    }
  };
  doc.addEventListener("visibilitychange", atualizarLacos);

  /* ---------- Títulos: digitação mono → serif, sem mudar a geometria ---------- */
  var digitar = function (letras) {
    if (!letras.length) return;
    letras.forEach(function (c) { c.classList.add("em-mono"); });
    var passo = T_LONGO / letras.length;
    var tl = gsap.timeline();
    letras.forEach(function (c, i) {
      tl.call(function () { c.classList.remove("em-mono"); }, null, i * passo);
    });
  };

  /* Divide depois das fontes carregadas (quebra de linha certa) e guarda o texto lido,
     com <br> virando espaço, no aria-label que o SplitText põe no título. */
  if (!reduz && Split) {
    var fontes = doc.fonts && doc.fonts.ready ? doc.fonts.ready : Promise.resolve();
    fontes.then(function () {
      doc.querySelectorAll("main h1, main h2").forEach(function (titulo) {
        // Título com link ou botão fica inteiro: dividido, o link perderia o nome acessível.
        if (titulo.querySelector("a, button")) return;
        // Erro num título não derruba os outros nem o caret/refresh abaixo; o título fica como veio.
        try {
          var lido = (titulo.innerText || titulo.textContent).replace(/\s+/g, " ").trim();
          var partes = Split.create(titulo, { type: "words,chars", wordsClass: "palavra", charsClass: "letra", tag: "span" });
          if (titulo.hasAttribute("aria-label")) titulo.setAttribute("aria-label", lido);
          partes.chars.forEach(function (c) { c.setAttribute("data-c", c.textContent); });
          if (naTela(titulo) || !ST) {
            digitar(partes.chars);
          } else {
            ST.create({ trigger: titulo, start: "top 85%", once: true, onEnter: function () { digitar(partes.chars); } });
          }
        } catch (erro) {
          if (window.console) console.warn("SplitText falhou em", titulo, erro);
        }
      });
      try { poeCaret(); } catch (erro) { if (window.console) console.warn("caret falhou", erro); }
      if (ST) ST.refresh();
    });
  }

  /* Barra de digitação piscando no título da home (laço controlado), posta depois da divisão */
  var poeCaret = function () {
    var hero = doc.querySelector(".hero-headline");
    if (!hero || reduz) return;
    var caret = doc.createElement("span");
    caret.className = "caret";
    caret.setAttribute("aria-hidden", "true");
    hero.appendChild(caret);
    laco(hero, gsap.timeline({ repeat: -1 })
      .to(caret, { opacity: 0, duration: T_MEDIO, ease: "steps(1)" })
      .to(caret, { opacity: 1, duration: T_MEDIO, ease: "steps(1)" }));
  };

  /* ---------- Cartões sobem 24 px ao entrar (com reduced-motion: só aparecem) ---------- */
  if (ST) {
    var seletor = ".cartao-pessoa, .cartao-projeto, .cartao-destaque, .cartao-servico, .relacionado-card, " +
      ".step-item, .tl-content, .servico-cta, .closing-inner";
    doc.querySelectorAll(seletor).forEach(function (el) {
      if (naTela(el)) return;
      var de = reduz ? { opacity: 0 } : { opacity: 0, y: 24 };
      var para = reduz
        ? { opacity: 1, duration: T_CURTO, clearProps: "opacity" }
        : { opacity: 1, y: 0, duration: T_LONGO, clearProps: "opacity,transform" };
      gsap.set(el, de);
      ST.create({ trigger: el, start: "top 92%", once: true, onEnter: function () { gsap.to(el, para); } });
    });
  }

  /* ---------- Lenis: rolagem suave só sem reduced-motion ---------- */
  if (!reduz && typeof window.Lenis === "function") {
    var lenis = new window.Lenis({ anchors: true, autoRaf: false });
    if (ST) lenis.on("scroll", ST.update);
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
  }
})();
