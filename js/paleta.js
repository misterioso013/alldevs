/* Paleta de comandos do ALL.dev: Ctrl K / ⌘K, ou a pílula "> ir para…" do cabeçalho (celular).
   Script clássico com defer, carregado depois de js/site.js. Sem JS, ou se o paleta.json não carregar,
   o gatilho continua sendo o link para /projetos/. O paleta.json só é buscado na 1ª abertura.
   Tempos e curva do esmaecer vêm de css/tokens.css (só opacidade, também com reduced-motion). */
(function () {
  "use strict";

  var doc = document;
  var gatilho = doc.querySelector(".paleta-gatilho");
  if (!gatilho || typeof doc.createElement("dialog").showModal !== "function") return;

  var TIPOS = { projeto: "projeto", servico: "serviço", pessoa: "pessoa", contato: "contato" };
  var itens = null;
  var carga = null;
  var falhou = false;
  var ativo = -1;
  var antes = null;
  var dialogo, campo, lista, aviso;

  // minúsculas e sem acento: "orçamento" casa com "orcamento"
  var limpar = function (s) {
    return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  };

  var criar = function (tag, atributos) {
    var el = doc.createElement(tag);
    for (var nome in atributos) el.setAttribute(nome, atributos[nome]);
    return el;
  };

  var marcar = function (n) {
    var opcoes = lista.children;
    if (!opcoes.length) {
      ativo = -1;
      campo.removeAttribute("aria-activedescendant");
      return;
    }
    ativo = (n + opcoes.length) % opcoes.length;
    for (var k = 0; k < opcoes.length; k++) opcoes[k].setAttribute("aria-selected", String(k === ativo));
    campo.setAttribute("aria-activedescendant", opcoes[ativo].id);
    opcoes[ativo].scrollIntoView({ block: "nearest" });
  };

  var mostrar = function (texto) {
    aviso.textContent = texto;
    aviso.hidden = !texto;
  };

  var filtrar = function () {
    var palavras = limpar(campo.value).split(/\s+/).filter(Boolean);
    var achados = (itens || []).filter(function (i) {
      var alvo = limpar(i.rotulo + " " + (i.termos || "") + " " + (TIPOS[i.tipo] || i.tipo));
      return palavras.every(function (p) { return alvo.indexOf(p) !== -1; });
    });
    lista.textContent = "";
    achados.forEach(function (i, n) {
      var a = criar("a", { id: "paleta-" + n, href: i.url, role: "option", tabindex: "-1" });
      if (/^https?:/.test(i.url)) {
        a.target = "_blank";
        a.rel = "noopener";
      }
      var tipo = criar("span", { class: "paleta-tipo" });
      tipo.textContent = TIPOS[i.tipo] || i.tipo;
      a.appendChild(doc.createTextNode(i.rotulo));
      a.appendChild(tipo);
      lista.appendChild(a);
    });
    lista.hidden = !achados.length;
    mostrar(achados.length || !itens ? "" : "Nada encontrado.");
    marcar(0);
  };

  var montar = function () {
    dialogo = criar("dialog", { class: "paleta", role: "dialog", "aria-modal": "true", "aria-label": "Ir para", "data-lenis-prevent": "" });
    campo = criar("input", {
      type: "text", role: "combobox", autocomplete: "off", spellcheck: "false", placeholder: "> ir para…",
      "aria-label": "Buscar página ou contato", "aria-autocomplete": "list", "aria-expanded": "true", "aria-controls": "paleta-lista"
    });
    lista = criar("div", { id: "paleta-lista", role: "listbox", "aria-label": "Resultados" });
    aviso = criar("p", { class: "paleta-aviso", role: "status" });
    dialogo.appendChild(campo);
    dialogo.appendChild(lista);
    dialogo.appendChild(aviso);
    doc.body.appendChild(dialogo);

    campo.addEventListener("input", filtrar);
    campo.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        marcar(ativo + (e.key === "ArrowDown" ? 1 : -1));
      } else if (e.key === "Enter" && ativo > -1) {
        e.preventDefault();
        var destino = lista.children[ativo];
        dialogo.close();
        destino.click();
      } else if (e.key === "Escape") {
        e.preventDefault();
        dialogo.close();
      }
    });
    // clique no fundo (no próprio <dialog>) fecha; clique numa opção fecha e deixa o link seguir
    dialogo.addEventListener("click", function (e) {
      if (e.target === dialogo || e.target.closest('[role="option"]')) dialogo.close();
    });
    // o foco volta para quem o tinha antes de abrir (a pílula, se foi ela)
    dialogo.addEventListener("close", function () {
      var atual = doc.activeElement;
      if (antes && antes.isConnected && (!atual || atual === doc.body)) antes.focus({ preventScroll: true });
    });
  };

  var carregar = function () {
    if (!carga) {
      carga = fetch("/assets/paleta.json")
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          return r.json();
        })
        .then(function (dados) { itens = dados; });
    }
    return carga;
  };

  var abrir = function (peloGatilho) {
    if (falhou) return;
    if (!dialogo) montar();
    if (dialogo.open) {
      campo.focus();
      return;
    }
    antes = peloGatilho ? gatilho : doc.activeElement;
    campo.value = "";
    filtrar();
    if (!itens) mostrar("Carregando…");
    dialogo.showModal();
    carregar().then(filtrar, function () {
      falhou = true;
      gatilho.removeAttribute("role");
      gatilho.removeAttribute("aria-haspopup");
      dialogo.close();
      if (peloGatilho) window.location.assign(gatilho.href);
    });
  };

  gatilho.setAttribute("role", "button");
  gatilho.setAttribute("aria-haspopup", "dialog");
  gatilho.addEventListener("click", function (e) {
    if (falhou) return;
    e.preventDefault();
    abrir(true);
  });
  gatilho.addEventListener("keydown", function (e) {
    if (e.key === " " && !falhou) {
      e.preventDefault();
      abrir(true);
    }
  });
  doc.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey && e.key && e.key.toLowerCase() === "k" && !falhou) {
      e.preventDefault();
      abrir(false);
    }
  });
})();
