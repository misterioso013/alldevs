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

  /* ---------- Filtro de /projetos/ por tipo: o gerador o entrega hidden; sem JS a lista fica inteira ---------- */
  doc.querySelectorAll(".filtro-tipos").forEach(function (filtro) {
    var cartoes = doc.querySelectorAll("[data-lista-projetos] > article[data-tipo]");
    var botoes = filtro.querySelectorAll("button[data-tipo]");
    botoes.forEach(function (botao) {
      botao.addEventListener("click", function () {
        var tipo = botao.getAttribute("data-tipo");
        botoes.forEach(function (b) { b.setAttribute("aria-pressed", String(b === botao)); });
        cartoes.forEach(function (c) { c.hidden = tipo !== "todos" && c.getAttribute("data-tipo") !== tipo; });
      });
    });
    filtro.hidden = false;
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

  /* ---------- Preloader: quem decide é o script inline do <head> (classe pre-1a no <html>); o overlay e a animação de saída
     são do CSS, com os tempos dos tokens. Aqui só: grava a flag da sessão e remove o overlay quando a saída termina. ---------- */
  var DUR_MEDIA = tempo("--dur-media", 0.4);
  var noPreloader = raiz.classList.contains("pre-1a");
  var animPre = null;
  if (noPreloader) {
    try { window.sessionStorage.setItem("alldev-visto", "1"); } catch (erro) { /* sem storage: o inline já não mostrou */ }
    var pre = doc.querySelector(".preloader");
    var tirar = function () {
      raiz.classList.remove("pre-1a");
      if (pre && pre.parentNode) pre.parentNode.removeChild(pre);
    };
    if (pre) {
      // O CSS pode ter terminado antes deste script rodar (defer): getAnimations().finished já vem resolvido nesse caso.
      var anims = pre.getAnimations ? pre.getAnimations() : [];
      animPre = anims[0] || null;
      if (anims.length) Promise.all(anims.map(function (a) { return a.finished; })).then(tirar, tirar);
      else window.setTimeout(tirar, (DUR_MEDIA + 2 * DUR_CURTA) * 1000); // navegador sem getAnimations
    } else {
      tirar();
    }
  }
  /* Ms até o overlay começar a sumir (zero se já começou): o que estiver sob ele ainda está coberto. */
  var aindaCoberto = function () {
    if (!noPreloader) return -1;
    if (animPre && animPre.startTime !== null && doc.timeline) {
      return Math.max(0, animPre.startTime + animPre.effect.getTiming().delay - doc.timeline.currentTime);
    }
    return Math.max(0, DUR_CURTA * 1000 - window.performance.now());
  };

  /* ---------- Cursor próprio: só com mouse. O nativo continua; o anel acompanha e mostra o data-cursor ---------- */
  if (mq("(pointer: fine)") && !reduz) {
    var cursor = doc.createElement("div");
    cursor.className = "cursor";
    cursor.setAttribute("aria-hidden", "true");
    var anel = doc.createElement("span");
    anel.className = "cursor-anel";
    var rotulo = doc.createElement("span");
    rotulo.className = "cursor-texto";
    cursor.appendChild(anel);
    cursor.appendChild(rotulo);
    doc.body.appendChild(cursor);
    var alvoX = 0, alvoY = 0, quadro = 0;
    var desenha = function () {
      quadro = 0;
      cursor.style.transform = "translate3d(" + alvoX + "px," + alvoY + "px,0)";
    };
    var esconde = function () {
      cursor.classList.remove("cursor-ativo");
      cursor.classList.remove("cursor-com-texto");
    };
    var ehMouse = function (e) { return !e.pointerType || e.pointerType === "mouse"; };
    doc.addEventListener("pointermove", function (e) {
      if (!ehMouse(e)) return;
      if (!e.clientX && !e.clientY) return;   // (0,0) é evento sintético sem posição: o anel não nasce no canto
      alvoX = e.clientX;
      alvoY = e.clientY;
      cursor.classList.add("cursor-ativo");
      if (!quadro) quadro = window.requestAnimationFrame(desenha);
    });
    doc.addEventListener("pointerover", function (e) {
      if (!ehMouse(e)) return;
      var el = e.target.closest ? e.target.closest("[data-cursor]") : null;
      var texto = el ? el.getAttribute("data-cursor") : "";
      rotulo.textContent = texto || "";
      cursor.classList.toggle("cursor-com-texto", !!texto);
    });
    doc.addEventListener("pointerout", function (e) {
      if (!ehMouse(e)) return;
      if (!e.relatedTarget) { esconde(); return; } // saiu da janela
      cursor.classList.remove("cursor-com-texto");
    });
    doc.addEventListener("pointerdown", function (e) {
      if (!ehMouse(e)) esconde(); // um toque: some o anel, que é coisa de mouse
    });
    doc.documentElement.addEventListener("pointerleave", esconde);
  }

  var gsap = window.gsap;

  /* ---------- .titulo-revela: linhas com overflow: hidden, sobem em sequência (0,05 s) ----------
     Só esconde o que ainda não foi visto: título já na tela ao carregar fica como está; sob o preloader, esconde enquanto o
     overlay ainda cobre e a subida começa quando ele sai; fora da tela, sobe ao entrar (IntersectionObserver).
     As linhas se refazem quando a largura muda (autoSplit). Com reduced-motion, nada de split. */
  var titulos = doc.querySelectorAll(".titulo-revela");
  if (!reduz && titulos.length && gsap && window.SplitText) {
    gsap.registerPlugin(window.SplitText);
    var saida = curva("--curva-saida", [0.22, 1, 0.36, 1]);
    var fontes = doc.fonts && doc.fonts.ready ? doc.fonts.ready : Promise.resolve();
    fontes.then(function () {
      titulos.forEach(function (titulo) {
        // Título com link ou botão fica inteiro: dividido, o link perderia o nome acessível.
        if (titulo.querySelector("a, button")) return;
        var coberto = aindaCoberto();
        var esconder = !naTela(titulo) || coberto > 0; // sob o preloader (coberto >= 0) um título fora da tela também esconde: coberto vale -1 sem overlay
        var revelado = !esconder;
        var linhas = [];
        var anim = null;
        var revela = function (atraso) {
          anim = gsap.to(linhas, { yPercent: 0, duration: DUR_LONGA, delay: atraso, stagger: STAGGER, ease: saida,
            onComplete: function () { revelado = true; } });
        };
        try {
          var lido = (titulo.innerText || titulo.textContent).replace(/\s+/g, " ").trim();
          window.SplitText.create(titulo, {
            type: "lines", linesClass: "linha-revela", mask: "lines", aria: "auto", autoSplit: true,
            onSplit: function (self) {
              if (titulo.hasAttribute("aria-label")) titulo.setAttribute("aria-label", lido);
              self.masks.forEach(function (m) { m.classList.add("linha-mascara"); });
              linhas = self.lines;
              if (anim) { anim.kill(); anim = null; revelado = true; } // largura mudou no meio da subida: mostra tudo
              if (!revelado) gsap.set(linhas, { yPercent: 110 });
            }
          });
          if (esconder) {
            if (coberto >= 0 && naTela(titulo)) revela(coberto / 1000);
            else umaVez([titulo], function () { revela(0); });
          }
        } catch (erro) {
          if (window.console) console.warn("titulo-revela falhou em", titulo, erro);
        }
      });
    });
  }

  /* ---------- Barra do WhatsApp (celular): some enquanto um botão de WhatsApp da página ou o rodapé está na tela ---------- */
  function ligarBarraWa() {
    var barra = doc.querySelector(".barra-wa");
    if (!barra || !temIO) return;   // sem JS (ou sem IntersectionObserver) a barra fica como sempre
    var alvos = [].slice.call(doc.querySelectorAll('main a[href*="wa.me"], footer'));
    var vistos = new Set();
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) { if (e.isIntersecting) vistos.add(e.target); else vistos.delete(e.target); });
      var oculta = vistos.size > 0;
      barra.classList.toggle("barra-wa--oculta", oculta);
      if (oculta) barra.setAttribute("inert", ""); else barra.removeAttribute("inert");
    });
    alvos.forEach(function (a) { io.observe(a); });
  }
  ligarBarraWa();

  /* ---------- Lenis: só com mouse, tela larga e sem reduced-motion ---------- */
  function ligarLenis() {
    if (typeof window.Lenis !== "function" || !gsap) return;
    var lenis = new window.Lenis({ anchors: true, autoRaf: false });
    if (window.ScrollTrigger) {
      gsap.registerPlugin(window.ScrollTrigger);
      lenis.on("scroll", window.ScrollTrigger.update);
    }
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
  }
  if (!reduz && mq("(pointer: fine) and (min-width: 1024px)")) ligarLenis();
})();
