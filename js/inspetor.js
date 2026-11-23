/* Inspetor do hero: percorre as caixas da tela (~1,2 s cada) e troca de tela (~8 s), na ordem de
   estudio.inspetor. Sem dependência. As caixas não andam: cada tela ganha um alvo novo com uma caixa por item, já no lugar,
   e o percurso só acende e apaga (opacidade); a caixa salta, nada desliza, sem CLS.
   Para fora da tela e com a aba escondida. Com reduced-motion: 2 caixas acesas e paradas.
   A troca de tela só começa depois do 1º gesto do visitante (toque, clique, tecla, roda): uma imagem nova
   pintada antes disso viraria um LCP tardio (~9 s) para quem só olha; depois do gesto o LCP já fechou.
   Sem JS fica só a 1ª imagem (o botão "próxima tela" nasce com hidden). */
(function () {
  "use strict";
  var doc = document;
  var raiz = doc.querySelector(".inspetor");
  var fonte = doc.getElementById("inspecao");
  if (!raiz || !fonte) return;
  var telas;
  try { telas = JSON.parse(fonte.textContent).telas; } catch (e) { return; }
  if (!telas || !telas.length) return;

  var palco = raiz.querySelector(".inspetor-palco");
  var tela = raiz.querySelector(".inspetor-tela");
  var img = tela && tela.querySelector("img");
  var selo = raiz.querySelector(".inspetor-selo");
  var codigo = raiz.querySelector(".inspetor-codigo code");
  var botao = doc.querySelector(".inspetor-proximo");
  if (!palco || !img || !codigo) return;

  var calmo = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var PASSO = 1200, POR_TELA = 8000;
  var atual = 0, indice = 0, tempo = 0, visivel = false, mouse = false, trocando = false, mexeu = false;
  var timer = null, alvo = null, caixas = [], carregadas = {};
  carregadas[telas[0].imagem] = true;

  // Mesmo token de movimento do resto do site (css/tokens.css).
  function duracao() {
    if (calmo) return 0;
    var v = parseFloat(getComputedStyle(doc.documentElement).getPropertyValue("--t-medio"));
    return isFinite(v) ? v : 450;
  }

  // Alvo da tela t: mesma proporção da imagem, na mesma célula da grade (ver css/site.css), com todas as
  // caixas já posicionadas e apagadas. Trocar o alvo inteiro (nó novo) não conta como mudança de layout.
  function montaAlvo(t) {
    if (alvo) tela.removeChild(alvo);
    alvo = doc.createElement("div");
    alvo.className = "inspetor-alvo";
    alvo.style.setProperty("--w", t.w);
    alvo.style.setProperty("--h", t.h);
    caixas = [];
    for (var i = 0; i < t.caixas.length; i++) {
      var c = t.caixas[i], el = doc.createElement("div"), rot = doc.createElement("span");
      el.className = "inspetor-caixa" + (c.y < 8 ? " embaixo" : "") + (c.x > 50 ? " direita" : "");
      el.style.left = c.x + "%";
      el.style.top = c.y + "%";
      el.style.width = c.w + "%";
      el.style.height = c.h + "%";
      rot.className = "inspetor-rotulo";
      rot.textContent = c.tag + "." + c.classe + " · " + c.medida;
      el.appendChild(rot);
      alvo.appendChild(el);
      caixas.push(el);
    }
    tela.appendChild(alvo);
  }

  // Acende a caixa i (e, no modo calmo, também a 1) e apaga as outras.
  function mostra(i) {
    var lista = telas[atual].caixas;
    indice = (i + lista.length) % lista.length;
    for (var j = 0; j < caixas.length; j++) caixas[j].classList.toggle("aceso", j === indice || (calmo && j === 1));
    codigo.textContent = lista[indice].codigo;
  }

  function carrega(n, pronto) {
    var t = telas[n];
    if (carregadas[t.imagem]) { if (pronto) pronto(true); return; }
    var pre = new Image();
    pre.onload = function () { carregadas[t.imagem] = true; if (pronto) pronto(true); };
    pre.onerror = function () { if (pronto) pronto(false); };
    pre.src = t.imagem;
  }

  function depois(fn) {
    function vai() { setTimeout(fn, 1500); }
    if (doc.readyState === "complete") vai(); else window.addEventListener("load", vai);
  }

  function vaiTela(n) {
    if (trocando || telas.length < 2) return;
    var prox = (n + telas.length) % telas.length;
    trocando = true;
    carrega(prox, function (ok) {
      if (!ok) { trocando = false; tempo = 0; return; }
      tela.classList.add("trocando");
      setTimeout(function () {
        var t = telas[prox];
        atual = prox;
        img.src = t.imagem;
        img.alt = "Tela do " + t.nome;
        img.width = t.w;
        img.height = t.h;
        montaAlvo(t);
        raiz.className = "inspetor ativo inspetor-" + t.cor;
        if (selo) selo.textContent = t.nome + " · " + t.autor;
        mostra(0);
        tela.classList.remove("trocando");
        trocando = false;
        tempo = 0;
        para(); // a caixa 0 da tela nova fica um passo inteiro
        agenda();
        // Já busca a seguinte enquanto esta fica no ar.
        carrega((prox + 1) % telas.length);
      }, duracao());
    });
  }

  function rodando() { return visivel && !doc.hidden && !calmo; }
  function para() { clearTimeout(timer); timer = null; }
  function agenda() { if (!timer && rodando()) timer = setTimeout(tique, PASSO); }
  function tique() {
    timer = null;
    if (!rodando()) return;
    if (!mouse && !trocando) {
      // Sem gesto, o tempo fica preso em POR_TELA: o 1º gesto depois dos 8 s troca já no próximo tique.
      tempo = Math.min(tempo + PASSO, POR_TELA);
      if (tempo >= POR_TELA && mexeu) vaiTela(atual + 1);
      else mostra(indice + 1);
    }
    agenda();
  }

  // Caixa sob o ponteiro: a menor que contém o ponto (em % da imagem).
  function sob(ev) {
    var r = alvo.getBoundingClientRect();
    if (!r.width || !r.height) return -1;
    var px = (ev.clientX - r.left) / r.width * 100, py = (ev.clientY - r.top) / r.height * 100;
    var lista = telas[atual].caixas, melhor = -1, area = Infinity;
    for (var i = 0; i < lista.length; i++) {
      var c = lista[i];
      if (px >= c.x && px <= c.x + c.w && py >= c.y && py <= c.y + c.h && c.w * c.h < area) {
        melhor = i;
        area = c.w * c.h;
      }
    }
    return melhor;
  }

  palco.addEventListener("pointermove", function (ev) {
    if (calmo || ev.pointerType !== "mouse" || trocando) return;
    mouse = true;
    var i = sob(ev);
    if (i >= 0 && i !== indice) mostra(i);
  });
  palco.addEventListener("pointerleave", function (ev) {
    if (ev.pointerType === "mouse") mouse = false;
  });
  // Toque (ou clique) inspeciona a caixa; não chama preventDefault, então não prende a rolagem.
  palco.addEventListener("click", function (ev) {
    if (calmo || trocando) return;
    var i = sob(ev);
    if (i < 0) return;
    mostra(i);
    tempo = 0;
    para();
    agenda();
  });

  if (botao) {
    botao.hidden = false;
    botao.addEventListener("click", function () {
      tempo = 0;
      vaiTela(atual + 1);
    });
  }

  // Modo calmo: 2 caixas acesas e paradas (hover e clique não as movem; o botão ainda troca a tela).
  montaAlvo(telas[0]);
  raiz.classList.add("ativo");
  mostra(0);

  var GESTOS = ["pointerdown", "keydown", "wheel", "touchstart"];
  function acorda() {
    if (mexeu) return;
    mexeu = true;
    for (var g = 0; g < GESTOS.length; g++) window.removeEventListener(GESTOS[g], acorda, true);
    // Só agora busca a 2ª tela (quem sai sem mexer não gasta banda com ela).
    if (!calmo) depois(function () { carrega(1 % telas.length); });
  }
  for (var g = 0; g < GESTOS.length; g++) window.addEventListener(GESTOS[g], acorda, { capture: true, passive: true });

  doc.addEventListener("visibilitychange", function () {
    if (doc.hidden) para(); else agenda();
  });
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (es) {
      visivel = es[es.length - 1].isIntersecting;
      if (visivel) {
        agenda();
      } else {
        para();
      }
    }).observe(raiz);
  } else {
    visivel = true;
    agenda();
  }
})();
