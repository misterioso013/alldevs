"""Monta as páginas do site a partir dos dados e dos moldes."""
import html
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from . import contato, seo
from . import dados as dados_mod
from .dados import Dados, ErroDeDados
from .dados import TIPO_ROTULO, anos_de_estrada, ler_por_tras, visiveis
from .modelos import Seguro, esc, render

CABECALHO = "<!-- gerado por fonte/gerar.py — não editar -->"
ESTATICOS = ("css", "js", "assets", "icon.svg")

HOME_TITULO = "AllDevs — Estúdio de software: sites, apps e automações"
HOME_DESCRICAO = (
    "Estúdio de software com dois sócios. "
    "Sites, apps, bots e produtos próprios no ar."
)
PROJETOS_TITULO = "Projetos — AllDevs"
PROJETOS_DESCRICAO = "Os projetos da AllDevs: sites, apps, automações e produtos próprios, feitos pelo estúdio."
MARCADOR_CONTATO = "<!--contato-->"


@dataclass(frozen=True)
class Pagina:
    caminho: str
    titulo: str
    descricao: str
    corpo: Seguro
    atualizado: str
    json_ld: tuple
    indexar: bool = True


def og_slug(caminho: str) -> str:
    """Nome da imagem OG (assets/og/<slug>.png) de cada página: a home é `site`, o resto é a última pasta."""
    if caminho == "index.html":
        return "site"
    if caminho.endswith("/index.html"):
        return caminho[: -len("/index.html")].rsplit("/", 1)[-1]
    return caminho.rsplit("/", 1)[-1].removesuffix(".html")


def _documento(caminho, titulo, descricao, corpo, json_ld=(), previa=False, barra="", head_extra="") -> Seguro:
    if json_ld:
        bloco = f'\n<script type="application/ld+json">{seo.serializar(json_ld)}</script>'
    else:
        bloco = ""
    return render("base", titulo=titulo, descricao=descricao, canonical=seo.url_publica(caminho),
                  og_imagem=f"{seo.SITE}/assets/og/{og_slug(caminho)}.png", corpo=corpo, json_ld=Seguro(bloco),
                  robots_meta=Seguro(seo.META_NOINDEX if previa else ""), barra_wa=barra,
                  head_extra=Seguro(head_extra))


def _bloco_contato(estudio, tipo, alvo=None, slug=None, com_id=True, so_principal=False) -> Seguro:
    """com_id=False na home: o id "contato" é da seção, não do bloco. so_principal: só o botão do WhatsApp (o cartão do fim do
    texto de serviço); o trio WhatsApp / e-mail / Telegram aparece uma vez só por página, no bloco de contato."""
    codigo = contato.codigo_origem(tipo, slug)
    msg = contato.mensagem(estudio, tipo, alvo, slug)
    email = contato.link_email(estudio.email, codigo)
    secundarios = "" if so_principal else (
        f'\n  <a href="{esc(email)}" class="btn btn-linha">Enviar e-mail</a>'
        f'\n  <a href="{esc(estudio.telegram)}" target="_blank" rel="noopener" class="btn btn-linha">Telegram</a>\n')
    return render(
        "contato",
        whatsapp=contato.link_whatsapp(estudio.whatsapp, msg),
        secundarios=Seguro(secundarios),
        id_attr=Seguro(' id="contato"' if com_id else ""),
    )


def _barra_wa(estudio, tipo, alvo=None, slug=None) -> Seguro:
    """Barra fixa do WhatsApp (só no celular, via CSS) com a origem da página. /projetos/
    usa `home`, como o bloco de contato do v1."""
    msg = contato.mensagem(estudio, tipo, alvo, slug)
    return render("barra_wa", whatsapp=contato.link_whatsapp(estudio.whatsapp, msg))


def _ler_conteudo(raiz: Path, partes, contato_html: Seguro) -> Seguro:
    """Lê o conteúdo e põe o bloco de contato onde está o marcador."""
    texto = (Path(raiz) / "fonte" / "conteudo" / Path(*partes)).read_text(encoding="utf-8")
    if MARCADOR_CONTATO not in texto:
        raise ValueError(f"conteúdo {'/'.join(partes)} sem o marcador {MARCADOR_CONTATO}")
    return Seguro(texto.replace(MARCADOR_CONTATO, contato_html.rstrip("\n")))


def _cabecalho_e_rodape(dados: Dados) -> dict:
    itens = "\n".join(
        f'        <li><a href="/servicos/{esc(s.slug)}/">{esc(s.nome)}</a></li>' for s in dados.servicos)
    return {"cabecalho": render("cabecalho"), "rodape": render("rodape", servicos=Seguro(itens))}


def _com_ano(tipo, ano) -> list:
    return [str(tipo)] if ano is None else [str(tipo), str(ano)]


def _cartao_pessoa(p) -> str:
    # Foto em 4/5 (retrato inteiro), abaixo do hero: lazy, para não disputar banda com a frente (LCP). A única prioridade alta da home é a da frente do hero.
    # Só foto, nome e o mesmo texto nos dois (decisão do Caio, 24/11): nada que separe um sócio do outro.
    return (
        f'    <article class="cartao-pessoa" data-slug="{esc(p.slug)}">\n'
        f'      <img src="/{esc(p.foto)}" alt="Foto de {esc(p.nome)}" width="512" height="640" loading="lazy" decoding="async">\n'
        f'      <h3>{esc(p.nome)}</h3>\n'
        f'      <p>Sócio do estúdio.</p>\n'
        f'    </article>'
    )


CARTAO_PREENCHE = 18   # (sem uso desde a r3: o trecho não se repete mais; mantido só pela assinatura)
CARTAO_LINHAS = 9   # linhas do trecho de código na camada "por trás" do cartão


def _imagem_do_cartao(proj, raiz: Path):
    """(src, largura, altura) da imagem do cartão: a frente do "por trás"; sem ela, a 1ª imagem do projeto se for WebP."""
    pt = proj.por_tras
    rel = pt["frente"] if pt else None
    if not rel:   # sem "por trás": o derivado do cartão (assets/frente/<slug>.webp, ≤ 540 px em retrato), senão a 1ª imagem
        der = f"assets/frente/{proj.slug}.webp"
        rel = der if (Path(raiz) / der).is_file() else next((i for i in proj.imagens if i.endswith(".webp")), None)
    if not rel:
        return None
    w, h = _tamanho_webp(Path(raiz) / rel)
    return "/" + rel, w, h


def _fechado(texto: str) -> str:
    """O trecho real, com os fechamentos que faltam no fim (chaves, colchetes, parênteses): cada cópia repetida fica completa."""
    pares, pilha = {"{": "}", "[": "]", "(": ")"}, []
    for c in texto:
        if c in pares:
            pilha.append(pares[c])
        elif c in pares.values() and pilha and pilha[-1] == c:
            pilha.pop()
    return texto.rstrip() + ("\n" + "".join(reversed(pilha)) if pilha else "")


def _camada_por_tras(proj, raiz: Path, preenche: int = CARTAO_PREENCHE, linhas_max: int = CARTAO_LINHAS) -> str:
    """A camada que a máscara do ponteiro revela no cartão e no palco do case (js/revelar.js monta; css/site.css desenha a máscara).
    O palco do case é maior: mostra mais linhas do mesmo trecho."""
    pt = proj.por_tras
    texto = ler_por_tras(raiz, proj)
    if texto is not None:
        linhas = _fechado(texto).splitlines() or [""]
        # o trecho real aparece UMA vez, fechado; o que não cabe na figura esmaece no corte vertical (css) e a camada é aria-hidden
        trecho = "\n".join(linhas)
        miolo = f'<pre><code>{re.sub(r"(?<!&)#", "&#35;", esc(trecho))}</code></pre>'
    else:
        w, h = _tamanho_webp(Path(raiz) / pt["arquivo"])
        miolo = f'<img src="/{esc(pt["arquivo"])}" width="{w}" height="{h}" alt="" loading="lazy" decoding="async">'
    return (f'\n      <div class="cartao-por-tras" aria-hidden="true">{miolo}'
            f'<span class="cartao-origem">{esc(pt["origem"])}</span></div>')


def _cartao_projeto(proj, raiz: Path, nivel: int = 3, acima_da_dobra: bool = False, prioridade: bool = False) -> Seguro:
    """Cartão de projeto da home e de /projetos/: a tela real, o rótulo (tipo · ano · situação), o link do case e o link para o ar.
    Com `por_tras`, a figura leva data-revela-cartao e uma camada aria-hidden com o trecho real.
    `acima_da_dobra`: a imagem sai sem `loading="lazy"` (o cartão já aparece na 1ª tela de /projetos/); `prioridade`: fetchpriority alto (o 1º)."""
    raiz = Path(raiz)
    nivel = int(nivel)
    carga = ('fetchpriority="high" ' if prioridade else "") + 'decoding="async"' if acima_da_dobra else 'loading="lazy" decoding="async"'
    img = _imagem_do_cartao(proj, raiz)
    camada = _camada_por_tras(proj, raiz) if proj.por_tras else ""
    marca = ' data-revela-cartao data-cursor="ver por trás"' if camada else ""
    figura = ""
    if img:   # a revelação mora na figura: a camada tem o tamanho dela e nunca cobre o texto nem os links
        retrato = " projeto-tela--retrato" if img[2] > img[1] else ""
        figura = (f'\n      <figure class="projeto-tela{retrato}"{marca}><img src="{esc(img[0])}" width="{img[1]}" height="{img[2]}" '
                  f'alt="Captura de tela de {esc(proj.nome)}" {carga}>{camada}\n      </figure>')
    ano = None if proj.ano is None else esc(str(proj.ano))
    rotulo = " · ".join([*_com_ano(esc(TIPO_ROTULO.get(proj.tipo, proj.tipo)), ano), esc(proj.situacao)])
    destino = proj.link or proj.loja
    no_ar = ""
    if destino:
        no_ar = (f'\n      <a class="link-seta" href="{esc(destino)}" target="_blank" rel="noopener">'
                 f'Ver {esc(proj.nome)} no ar<span class="so-leitor"> (abre em nova aba)</span></a>')
    return Seguro(
        f'    <article class="projeto-cartao" data-slug="{esc(proj.slug)}" data-tipo="{esc(proj.tipo)}" data-revela>{figura}\n'
        f'      <p class="rotulo-mono">{rotulo}</p>\n'
        f'      <h{nivel} class="projeto-titulo"><a href="/projetos/{esc(proj.slug)}/">{esc(proj.nome)}</a></h{nivel}>\n'
        f'      <p>{esc(proj.resumo)}</p>{no_ar}\n'
        f'    </article>')


def _tamanho_webp(arq: Path) -> tuple:
    """(largura, altura) de um WebP pelo cabeçalho RIFF (VP8, VP8L ou VP8X), sem dependência."""
    b = arq.read_bytes()[:30]
    if len(b) < 30:
        raise ValueError(f"{arq}: WebP curto demais")
    if b[:4] != b"RIFF" or b[8:12] != b"WEBP":
        raise ValueError(f"{arq}: não é WebP")
    tipo = b[12:16]
    if tipo == b"VP8 ":
        if b[23:26] != b"\x9d\x01\x2a":  # código de início do quadro-chave VP8
            raise ValueError(f"{arq}: VP8 sem assinatura de quadro-chave")
        return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
    if tipo == b"VP8L":
        if b[20] != 0x2F:  # assinatura do VP8L sem perda
            raise ValueError(f"{arq}: VP8L sem assinatura 0x2f")
        v = int.from_bytes(b[21:25], "little")
        return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    if tipo == b"VP8X":
        return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    raise ValueError(f"{arq}: bloco WebP desconhecido {tipo!r}")


def _tamanho_png(arq: Path) -> tuple:
    """(largura, altura) de um PNG pelo bloco IHDR (inteiros big-endian nos bytes 16 a 24), sem dependência."""
    b = arq.read_bytes()[:24]
    if len(b) < 24:
        raise ValueError(f"{arq}: PNG curto demais")
    if b[:8] != b"\x89PNG\r\n\x1a\n" or b[12:16] != b"IHDR":
        raise ValueError(f"{arq}: não é PNG")
    return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")


def _tamanho_imagem(arq: Path) -> tuple:
    """(largura, altura) de uma imagem de caso: PNG ou WebP, escolhido pela extensão; outra coisa é erro."""
    sufixo = arq.suffix.lower()
    if sufixo == ".png":
        return _tamanho_png(arq)
    if sufixo == ".webp":
        return _tamanho_webp(arq)
    raise ValueError(f"{arq}: imagem de caso precisa ser PNG ou WebP")


def _item_ciclo(proj, raiz: Path) -> dict:
    """Um item do ciclo do hero: o que o JS precisa para trocar frente, trecho e frase."""
    pt = proj.por_tras
    w, h = _tamanho_webp(raiz / pt["frente"])
    atras = {"tipo": pt["tipo"], "origem": pt["origem"]}
    texto = ler_por_tras(raiz, proj)
    if texto is not None:
        atras["texto"] = _fechado(texto)
    else:
        atras["src"] = "/" + pt["arquivo"]
    return {"slug": proj.slug, "nome": proj.nome, "frase": pt["frase"], "cor": pt["cor"],
            "frente": {"src": "/" + pt["frente"], "w": w, "h": h}, "por_tras": atras}


def _json_script(valor) -> str:
    """JSON para dentro de <script type=application/json>: todo "<" vira \\u003c, então nem "</script>" nem "<!--" passam."""
    return json.dumps(valor, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("#", "\\u0023")


def _preload_frente(dados: Dados, raiz: Path) -> str:
    """<link rel=preload> da 1ª frente do ciclo, para o <head> da home (vazio sem ciclo)."""
    por_slug = {p.slug: p for p in dados.projetos}
    if not dados.estudio.ciclo:
        return ""
    frente = _item_ciclo(por_slug[dados.estudio.ciclo[0]], Path(raiz))["frente"]
    return f'\n<link rel="preload" as="image" href="{esc(frente["src"])}" type="image/webp" fetchpriority="high">'


def _hero(dados: Dados, raiz: Path) -> Seguro:
    """Hero: h1 fixo, palco com a captura real (frente) e, por trás, o trecho real do projeto (revelado por js/revelar.js)."""
    raiz = Path(raiz)
    por_slug = {p.slug: p for p in dados.projetos}
    itens = [_item_ciclo(por_slug[s], raiz) for s in dados.estudio.ciclo]
    palco = ""
    if itens:   # sem ciclo (nenhum projeto com por_tras) o hero fica só com o texto
        pri = itens[0]
        atras = pri["por_tras"]
        if "texto" in atras:
            camada = f"<pre hidden><code>{re.sub(r"(?<!&)#", "&#35;", esc(atras['texto']))}</code></pre>"
        else:
            camada = f'<img src="{esc(atras["src"])}" alt="" decoding="async" hidden>'
        frente = pri["frente"]
        palco = f'''
 <div class="hero-palco" data-ciclo data-cor="{esc(pri["cor"])}">
  <figure class="hero-frente"><img src="{esc(frente["src"])}" width="{frente["w"]}" height="{frente["h"]}" alt="Captura de tela de {esc(pri["nome"])}" fetchpriority="high" decoding="async"></figure>
  <div class="hero-por-tras" aria-hidden="true">{camada}<span class="hero-origem">{esc(atras["origem"])}</span></div>
  <canvas class="hero-mascara" aria-hidden="true"></canvas>
  <button type="button" class="hero-ver-por-tras" aria-pressed="false" hidden>Ver por trás</button>
  <p class="hero-frase" aria-live="off"><span class="hero-frase-nome">{esc(pri["nome"])}</span> {esc(pri["frase"])}</p>
  <script id="ciclo" type="application/json">{_json_script(itens)}</script>
  <script src="/js/revelar.js" defer></script>
 </div>'''
    return Seguro(
        f'''<section id="hero" class="hero" data-secao="hero">
 <div class="hero-texto">
  <p class="rotulo-mono">// estúdio de software</p>
  <h1 class="hero-headline">Fazemos <span class="titulo-mono">software</span> <span class="hero-fecho">que vive.</span></h1>
  <p class="hero-sub">Um estúdio de software. Sites, apps, bots e produtos próprios no ar.</p>
  <div class="hero-ctas">
    <a href="/projetos/" class="btn btn-cheio">Ver projetos</a>
    <a href="#contato" class="btn btn-linha">Pedir orçamento</a>
  </div>
 </div>{palco}
</section>''')


# Wireframe do estágio "protótipo": blocos que lembram a tela de um player, sem título, pôster ou marca.
WIREFRAME = (
    '<div class="ideia-wire" aria-hidden="true">'
    '<span class="wire-barra"></span>'
    '<span class="wire-tela"><span class="wire-play"></span></span>'
    '<span class="wire-prog"><span></span></span>'
    '<span class="wire-fileira"><span></span><span></span><span></span></span>'
    '</div>')


def _est_codigo(raiz: Path, e: dict) -> str:
    texto = (Path(raiz) / e["arquivo"]).read_text(encoding="utf-8")
    # "#" vira entidade: o checar.py varre o HTML atrás de cor solta (#fff) e um comentário de código não é cor.
    return (f'<pre class="ideia-codigo" role="region" aria-label="Trecho do código" tabindex="0">'
            f'<code>{re.sub(r"(?<!&)#", "&#35;", esc(texto))}</code></pre>')


def _est_no_ar(proj, e: dict, raiz: Path) -> str:
    frente = (proj.por_tras or {}).get("frente")   # sem "por trás" o projeto não tem captura: fica só o resultado e o link
    fig = ""
    if frente:
        w, h = _tamanho_webp(Path(raiz) / frente)
        fig = (f'<figure class="ideia-frente"><img src="/{esc(frente)}" width="{w}" height="{h}" '
               f'alt="Captura de tela de {esc(proj.nome)}" loading="lazy" decoding="async"></figure>\n   ')
    return (f'{fig}<div class="ideia-fecho">\n'
            f'    <p class="ideia-resultado">{esc(e["resultado"])}</p>\n'
            f'    <a class="btn btn-cheio" href="{esc(e["link"])}" target="_blank" rel="noopener" data-cursor="Abrir">'
            f'Ver {esc(proj.nome)} na loja<span class="so-leitor"> (abre em nova aba)</span></a>\n'
            f'   </div>')


def _ideia(dados: Dados, raiz: Path) -> Seguro:
    """Seção #ideia, "Da ideia ao ar": a história de um projeto em 3 estágios (ideia.json). Legível sem JS; js/ideia.js só anima."""
    ideia = dados.ideia
    if not ideia:
        return Seguro("")
    erros = dados_mod.validar_ideia(dados, raiz)
    if erros:
        raise ErroDeDados("; ".join(erros))
    proj = next(p for p in dados.projetos if p.slug == ideia["projeto"])
    itens = []
    for e in ideia["estagios"]:
        chave = e["chave"]
        if chave == "prototipo":
            visual = f'{WIREFRAME}\n   <p class="ideia-fonte">{esc(e["fonte"])}</p>'
        elif chave == "codigo":
            visual = _est_codigo(raiz, e)
        elif chave == "no-ar":
            visual = _est_no_ar(proj, e, raiz)
        else:
            raise ValueError(f"ideia.json: estágio desconhecido: {chave}")
        itens.append(
            f'  <li class="ideia-estagio" data-chave="{esc(chave)}">\n'
            f'   <div class="ideia-texto">\n'
            f'    <h3>{esc(e["titulo"])}</h3>\n'
            f'    <p>{esc(e["texto"])}</p>\n'
            f'   </div>\n'
            f'   <div class="ideia-visual">\n   {visual}\n   </div>\n'
            f'  </li>')
    return Seguro(
        '<section id="ideia" class="ideia" data-secao="ideia">\n'
        ' <header class="ideia-cab">\n'
        '  <p class="rotulo-mono">// um projeto de ponta a ponta</p>\n'
        '  <h2 class="titulo-revela">Da ideia ao ar</h2>\n'
        f'  <p class="ideia-intro" data-revela>A história de um projeto real do estúdio, do primeiro papo ao app na loja: '
        f'{esc(proj.nome)}.</p>\n'
        '  <div class="ideia-trilho" aria-hidden="true"><span class="ideia-trilho-barra"></span></div>\n'
        ' </header>\n'
        ' <ol class="ideia-estagios">\n' + "\n".join(itens) + '\n </ol>\n'
        ' <script src="/js/ideia.js" defer></script>\n'
        '</section>')


def _faixa_prova(dados: Dados, raiz: Path) -> Seguro:
    """Faixa de prova logo abaixo do hero: três números, todos calculados (anos lidos do texto do serviço; falha alto se sumir)."""
    no_ar = [p for p in visiveis(dados.projetos) if not p.rascunho and p.situacao == "no ar" and (p.link or p.loja)]
    itens = ((f"{anos_de_estrada(raiz)}+", "anos de experiência"), (str(len(no_ar)), "produtos no ar"),
             (str(len(dados.tecnologias)), "tecnologias em uso"))
    lis = "\n".join(f'  <li><strong class="faixa-num">{esc(n)}</strong> <span class="faixa-rotulo">{esc(r)}</span></li>'
                    for n, r in itens)
    return Seguro('<section id="faixa" class="faixa" data-secao="faixa" aria-label="O estúdio em números">\n'
                  f' <ul class="faixa-lista">\n{lis}\n </ul>\n</section>')


GRUPOS_ROTULO = (("front", "front-end"), ("mobile", "mobile"), ("back", "back-end"), ("nuvem", "nuvem"), ("dados", "dados"))


def _tecnologias(dados: Dados) -> Seguro:
    """#tecnologias: as de dados.tecnologias (cada uma já provada no stack de um projeto no ar), agrupadas, em mono."""
    grupos = []
    for chave, rotulo in GRUPOS_ROTULO:
        lis = "\n".join(f'    <li class="tecnologia">{esc(x.nome)}</li>' for x in dados.tecnologias if x.grupo == chave)
        if lis:
            grupos.append(f'  <div class="tec-grupo" data-grupo="{esc(chave)}" data-revela>\n'
                          f'   <h3 class="rotulo-mono">{esc(rotulo)}</h3>\n   <ul class="tec-lista">\n{lis}\n   </ul>\n  </div>')
    return Seguro(
        '<section id="tecnologias" class="tecnologias" data-secao="tecnologias">\n'
        ' <p class="rotulo-mono">// tecnologias</p>\n'
        ' <h2 class="titulo-revela">Com o que construímos</h2>\n'
        ' <p class="secao-intro">As ferramentas dos projetos que estão no ar.</p>\n'
        ' <div class="tec-grupos">\n' + "\n".join(grupos) + '\n </div>\n</section>')


def _como_trabalhamos(dados: Dados) -> Seguro:
    """#como-trabalhamos: os 4 passos de fonte/conteudo/como-trabalhamos.json, em lista ordenada."""
    lis = "\n".join(
        f'  <li class="passo" data-revela>\n   <span class="passo-num">{n:02d}</span>\n'
        f'   <h3>{esc(x["titulo"])}</h3>\n   <p>{esc(x["texto"])}</p>\n  </li>'
        for n, x in enumerate(dados.passos, 1))
    return Seguro(
        '<section id="como-trabalhamos" class="como-trabalhamos" data-secao="como-trabalhamos">\n'
        ' <p class="rotulo-mono">// como trabalhamos</p>\n'
        ' <h2 class="titulo-revela">Do briefing à entrega</h2>\n'
        f' <ol class="passos">\n{lis}\n </ol>\n</section>')


def _depoimentos(dados: Dados) -> Seguro:
    """#depoimentos: só existe com ao menos um depoimento autorizado."""
    deps = [d for d in dados.depoimentos if d.autorizado]
    if not deps:
        return Seguro("")
    itens = "\n".join(
        f'  <figure class="depoimento" data-revela>\n   <blockquote><p>{esc(d.texto)}</p></blockquote>\n'
        f'   <figcaption>{esc(d.nome)}, <span class="rotulo-mono">{esc(d.papel)}</span></figcaption>\n  </figure>'
        for d in deps)
    return Seguro(
        '<section id="depoimentos" class="depoimentos" data-secao="depoimentos">\n'
        ' <p class="rotulo-mono">// depoimentos</p>\n'
        ' <h2 class="titulo-revela">Quem já trabalhou com a gente</h2>\n'
        f' <div class="depoimentos-lista">\n{itens}\n </div>\n</section>')


# 4 perguntas das páginas de serviço, no máximo uma por serviço e nenhuma de um só entregável (serviço, pergunta); a resposta é lida do HTML do serviço, palavra por palavra.
FAQ_HOME = (("landing-page-conversao", "Quantas revisões estão incluídas?"),
            ("desenvolvimento-mvp-startups", "Vocês dão suporte após o lançamento?"),
            ("automacoes-integracoes-api", "Quais sistemas vocês conseguem integrar?"),
            ("aplicativo-mobile-react-native", "Vocês publicam o app na App Store e Google Play?"))
FAQ_SETA = '<svg class="faq-chevron" aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>'


FAQ_TAGS = ("strong", "em", "a", "code")   # marcação aceita na resposta copiada (HTML do próprio repo, sem escape)


def _ler_texto(arq: Path, quem: str) -> str:
    try:
        return Path(arq).read_text(encoding="utf-8")
    except OSError as e:
        raise ErroDeDados(f"{quem}: não consegui ler {arq}: {e.strerror or e}") from e


def _faq_home(raiz: Path) -> Seguro:
    """#faq: as respostas saem dos HTML dos serviços (fonte única). Botão desativado e aberto sem JS; o site.js vira sanfona."""
    itens = []
    for slug, pergunta in FAQ_HOME:
        arq = Path(raiz) / "fonte" / "conteudo" / "servicos" / f"{slug}.html"
        texto = _ler_texto(arq, "FAQ da home")
        m = re.search(r'faq-question[^>]*>\s*' + re.escape(pergunta) + r'\s*<svg.*?<div class="faq-answer"><p>(.*?)</p></div>',
                      texto, re.S)
        if not m:
            raise ErroDeDados(f"FAQ da home: a pergunta {pergunta!r} sumiu de servicos/{slug}.html")
        fora = sorted({t for t in re.findall(r"</?\s*([A-Za-z][\w-]*)", m.group(1)) if t.lower() not in FAQ_TAGS})
        if fora:
            raise ErroDeDados(f"FAQ da home: a resposta de {pergunta!r} tem tag fora de {', '.join(FAQ_TAGS)}: {', '.join(fora)}")
        itens.append(
            '   <div class="faq-item">\n'
            f'    <button type="button" class="faq-question" aria-expanded="true" disabled>\n     {esc(pergunta)}\n     {FAQ_SETA}\n    </button>\n'
            f'    <div class="faq-answer"><p>{m.group(1)}</p></div>\n   </div>')
    return Seguro(
        '<section id="faq" class="faq-home" data-secao="faq">\n'
        ' <p class="rotulo-mono">// perguntas frequentes</p>\n'
        ' <h2 class="titulo-revela">O que mais perguntam</h2>\n'
        ' <div class="faq-section">\n' + "\n".join(itens) + '\n </div>\n</section>')


def _home(dados: Dados, raiz: Path, previa: bool) -> Pagina:
    est = dados.estudio
    cartoes = "\n".join(_cartao_pessoa(p)
                         for p in sorted(dados.pessoas, key=lambda p: p.slug))
    projetos = "\n".join(
        str(_cartao_projeto(p, raiz)) for p in visiveis(dados.projetos) if p.destaque)
    servicos = "\n".join(
        f'    <article class="cartao-servico" data-revela>\n'
        f'      <h3><a href="/servicos/{esc(s.slug)}/">{esc(s.nome)}</a></h3>\n'
        f'      <p>{esc(s.resumo)}</p>\n'
        '    </article>'
        for s in dados.servicos)
    bloco = _bloco_contato(est, "home", com_id=False)   # na home o id "contato" é da seção
    corpo = render(
        "home", **_cabecalho_e_rodape(dados), hero=_hero(dados, raiz), faixa=_faixa_prova(dados, raiz),
        ideia=_ideia(dados, raiz), projetos=Seguro(projetos), servicos=Seguro(servicos),
        como=_como_trabalhamos(dados), tecnologias=_tecnologias(dados), cartoes=Seguro(cartoes),
        depoimentos=_depoimentos(dados), faq=_faq_home(raiz), contato=bloco,
    )
    caminho = "index.html"
    ld = (seo.json_ld_home(dados), *(seo.json_ld_pessoa(p) for p in sorted(dados.pessoas, key=lambda p: p.slug)))
    doc = _documento(caminho, HOME_TITULO, HOME_DESCRICAO, corpo, ld, previa, _barra_wa(est, "home"),
                     head_extra=_preload_frente(dados, raiz))
    return Pagina(caminho, HOME_TITULO, HOME_DESCRICAO, doc, est.atualizado, ld)


def _filtro_tipos(vis) -> Seguro:
    """Filtro de /projetos/ por tipo: Todos e um botão por tipo (ordem de TIPO_ROTULO) que tenha projeto visível.
    Sai `hidden`: sem JS a lista fica inteira e o filtro não aparece; js/site.js o abre e o liga."""
    tipos = [t for t in TIPO_ROTULO if any(p.tipo == t for p in vis)]
    botoes = [("todos", "Todos"), *((t, TIPO_ROTULO[t]) for t in tipos)]
    itens = "\n".join(
        f'    <button type="button" data-tipo="{esc(t)}" aria-pressed="{"true" if t == "todos" else "false"}">{esc(r)}</button>'
        for t, r in botoes)
    return Seguro(f'  <div class="filtro-tipos" role="group" aria-label="Filtrar por tipo" hidden>\n{itens}\n  </div>')


def _projetos(dados: Dados, raiz: Path, previa: bool) -> Pagina:
    vis = visiveis(dados.projetos)
    cartoes = "\n".join(str(_cartao_projeto(x, raiz, 2, i < 3, i == 0)) for i, x in enumerate(vis))
    revelar = '\n<script src="/js/revelar.js" defer></script>' if any(x.por_tras for x in vis) else ""
    corpo = render(
        "projetos", **_cabecalho_e_rodape(dados), filtro=_filtro_tipos(vis), cartoes=Seguro(cartoes),
        revelar=Seguro(revelar), contato=_bloco_contato(dados.estudio, "home"),
    )
    caminho = "projetos/index.html"
    atualizado = max([x.atualizado for x in vis] + [dados.estudio.atualizado])
    doc = _documento(caminho, PROJETOS_TITULO, PROJETOS_DESCRICAO, corpo, previa=previa,
                     barra=_barra_wa(dados.estudio, "home"))
    return Pagina(caminho, PROJETOS_TITULO, PROJETOS_DESCRICAO, doc, atualizado, ())


def _lista(itens) -> str:
    return "\n".join(f"      <li>{esc(i)}</li>" for i in itens)


def _img_case(proj, rel: str, numero: int, raiz: Path, primeira: bool = False) -> str:
    """`<img>` de uma captura do case com width/height reais (evita salto de layout) e classe pela orientação:
    retrato (celular) fica estreito, paisagem ocupa a coluna. Sem recorte forçado: a imagem aparece inteira."""
    w, h = _tamanho_imagem(Path(raiz) / rel)
    classe = "img-icone" if h == w else ("img-retrato" if h > w else "img-captura")
    legenda = f"Captura {numero} de {proj.nome}" if len(proj.imagens) > 1 else f"Captura de {proj.nome}"
    carga = 'fetchpriority="high" decoding="async"' if primeira else 'loading="lazy" decoding="async"'
    return (f'    <img class="{classe}" src="/{esc(rel)}" alt="{esc(legenda)}" width="{w}" height="{h}" {carga}>')


CASE_COLUNA_CAPTURAS = 714   # px: coluna 7fr do case a 1440 (contêiner 1280, gap 56)
CASE_TELAS_TOP = 24          # px: o `top` do sticky (o cabeçalho não é fixo)
CASE_ICONE = 120             # px: lado do ícone quadrado (.img-icone)
CASE_JANELA_MIN = 760        # px: altura de janela a partir da qual o CSS liga o sticky


def _altura_telas(tamanhos, loja: bool = False, largura: int = CASE_COLUNA_CAPTURAS) -> int:
    """Estimativa (px) da altura da coluna de capturas a 1440 px: mesmas regras do CSS (`.img-captura` ocupa a
    linha; `.img-retrato` tem calc(50% - 8px) até 240 px; `.case-loja img` na largura da coluna; `.img-icone` 120 px; gap 16;
    padding 24 em cima e embaixo; legenda da loja 24 px). Usada só para decidir a classe `case-telas-fixa`."""
    gap = 16
    linhas, atual, usado = [], 0, 0   # linha = altura do maior item; `usado` = largura ocupada
    def novo_item(w, h):
        nonlocal atual, usado
        if usado and usado + gap + w > largura + 0.5:
            linhas.append(atual); atual, usado = 0, 0
        usado += w + (gap if usado else 0); atual = max(atual, h)
    for w, h in tamanhos:
        if h == w:   # ícone quadrado: `.img-icone`, 120 px
            novo_item(CASE_ICONE, CASE_ICONE)
        elif loja:
            lw = largura; novo_item(lw, lw * h / w)
        elif h > w:
            lw = min(240, (largura - gap) / 2); novo_item(lw, lw * h / w)
        else:
            novo_item(largura, largura * h / w); linhas.append(atual); atual, usado = 0, 0
    if atual:
        linhas.append(atual)
    return round(sum(linhas) + gap * max(len(linhas) - 1, 0) + 48 + (24 + gap if loja else 0))


PALCO_PREENCHE = 28   # linhas da camada no palco do case (o cartão usa CARTAO_PREENCHE)
PALCO_LINHAS = 14


def _palco_do_case(proj, raiz: Path, imagem=None, primeira: bool = False) -> str:
    """Bloco "Por trás" do case: a mesma revelação do cartão (data-revela-cartao), maior. Só com `por_tras`.
    `primeira`: sem capturas na outra coluna, o palco leva a 1ª imagem do case (sem lazy, com prioridade)."""
    img = imagem or _imagem_do_cartao(proj, raiz)
    if not proj.por_tras or not img:
        return ""
    carga = 'fetchpriority="high" decoding="async"' if primeira else 'loading="lazy" decoding="async"'
    camada = _camada_por_tras(proj, raiz, PALCO_PREENCHE, PALCO_LINHAS)
    retrato = " case-palco--retrato" if img[2] > img[1] else ""
    return (f'\n  <section data-secao="por-tras">\n    <h2>Por trás</h2>\n'
            f'    <figure class="projeto-tela case-palco{retrato}" data-revela-cartao data-cursor="ver por trás">'
            f'<img src="{esc(img[0])}" width="{img[1]}" height="{img[2]}" '
            f'alt="Captura de tela de {esc(proj.nome)}" {carga}>{camada}\n    </figure>\n  </section>\n')


def _case(proj, dados: Dados, raiz: Path, previa: bool) -> Pagina:
    raiz = Path(raiz)
    linha = " · ".join([*_com_ano(proj.tipo, proj.ano), proj.situacao])
    frente = _imagem_do_cartao(proj, raiz) if proj.por_tras else None
    # o palco não repete uma imagem que a coluna de capturas já mostra: ela fica com as demais
    capturas = [i for i in proj.imagens if not (frente and "/" + i == frente[0])]
    palco = _palco_do_case(proj, raiz, frente, primeira=not capturas)
    resultado = ""
    if proj.resultado is not None:
        resultado = (f'\n  <section data-secao="resultado">\n    <h2>Resultado</h2>\n'
                     f'    <p>{esc(proj.resultado)}</p>\n  </section>\n')
    stack = ""
    if proj.stack:
        etiquetas = "".join(f'<li class="etiqueta-mono">{esc(s)}</li>' for s in proj.stack)
        stack = f'\n  <section data-secao="stack">\n    <h2>Stack</h2>\n    <ul class="etiquetas">{etiquetas}</ul>\n  </section>\n'
    imagens = ""
    fixa = ""
    if capturas:
        alt = _altura_telas([_tamanho_imagem(raiz / i) for i in capturas], bool(proj.loja))
        if alt <= CASE_JANELA_MIN - CASE_TELAS_TOP:
            fixa = " case-telas-fixa"
        figuras = "\n".join(_img_case(proj, i, n, raiz, n == 1) for n, i in enumerate(capturas, 1))
        if proj.loja:   # capturas da loja: uma legenda só para o conjunto
            figuras = f'  <figure class="case-loja">\n{figuras}\n    <figcaption>Na Google Play</figcaption>\n  </figure>'
        imagens = f'\n<section class="case-telas{fixa}" data-secao="imagens">\n{figuras}\n</section>\n'
    link = ""
    # no case a loja vem primeiro (a legenda "Na Google Play" está na coluna ao lado); no cartão, o link do site vem antes.
    # Com os dois iguais (Heisuca) sai um botão só.
    destino = proj.loja or proj.link
    if destino:
        link = (f'\n  <p class="case-link" data-secao="link"><a href="{esc(destino)}" target="_blank" rel="noopener" '
                f'class="btn btn-cheio">Ver {esc(proj.nome)} no ar<span class="so-leitor"> (abre em nova aba)</span></a></p>\n')
    revelar = '\n<script src="/js/revelar.js" defer></script>' if palco else ""
    corpo = render(
        "case", **_cabecalho_e_rodape(dados),
        classe="case" if capturas else "case case-unica", linha=linha, nome=proj.nome, resumo=proj.resumo, problema=proj.problema,
        fizemos=Seguro(_lista(proj.fizemos)), palco=Seguro(palco), resultado=Seguro(resultado), stack=Seguro(stack),
        imagens=Seguro(imagens), link=Seguro(link), revelar=Seguro(revelar),
        contato=_bloco_contato(dados.estudio, "case", alvo=proj.nome, slug=proj.slug),
    )
    caminho = f"projetos/{proj.slug}/index.html"
    titulo = f"{proj.nome}: {proj.tipo} — AllDevs"
    ld = (seo.json_ld_case(proj, dados),)
    doc = _documento(caminho, titulo, proj.resumo, corpo, json_ld=ld, previa=previa or proj.rascunho,
                     barra=_barra_wa(dados.estudio, "case", alvo=proj.nome, slug=proj.slug))
    return Pagina(caminho, titulo, proj.resumo, doc, proj.atualizado, ld, indexar=not proj.rascunho)


REDIRECIONA_TITULO = "Quem somos — AllDevs"


def _historia(dados: Dados, raiz: Path, previa: bool) -> Pagina:
    """/historia.html saiu do site (24/11), mas existe no site de hoje: fica só um redirecionamento para /#quem-somos
    (meta refresh, canonical na seção, noindex, um link visível). Fora do sitemap."""
    destino = f"{seo.SITE}/#quem-somos"
    doc = (
        '<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{REDIRECIONA_TITULO}</title>\n'
        '<meta http-equiv="refresh" content="0; url=/#quem-somos">\n'
        f'<link rel="canonical" href="{destino}">\n'
        '<meta name="robots" content="noindex">\n</head>\n<body>\n'
        '<p><a href="/#quem-somos">Quem somos</a></p>\n</body>\n</html>\n'
    )
    return Pagina("historia.html", REDIRECIONA_TITULO, "", doc, dados.estudio.atualizado, (), indexar=False)


CHEVRON_DO_FAQ = '<svg class="faq-chevron" '   # o conteúdo traz a seta sem aria-hidden; o gerador a marca como decorativa


def _projetos_do_tipo(s, dados: Dados, raiz: Path) -> tuple:
    """(HTML, há cartão com revelação) do fim do serviço: os cartões dos projetos visíveis do mesmo tipo;
    sem nenhum, só o link para /projetos/ (nada de frase inventada)."""
    vis = [p for p in visiveis(dados.projetos) if p.tipo == s.tipo]
    if not vis:
        return Seguro('\n  <p><a href="/projetos/" class="link-seta">Ver todos os projetos</a></p>'), False
    cartoes = "\n".join(str(_cartao_projeto(p, raiz, 3)) for p in vis)
    return Seguro(f'\n  <div class="grade-projetos">\n{cartoes}\n  </div>'), any(p.por_tras for p in vis)


def _servico(s, dados: Dados, raiz: Path, previa: bool) -> Pagina:
    projetos, revela = _projetos_do_tipo(s, dados, raiz)
    conteudo = _ler_conteudo(
        raiz, ("servicos", f"{s.slug}.html"),
        _bloco_contato(dados.estudio, "servico", alvo=s.nome, slug=s.slug, com_id=False, so_principal=True))
    conteudo = Seguro(conteudo.replace(CHEVRON_DO_FAQ, CHEVRON_DO_FAQ + 'aria-hidden="true" focusable="false" '))
    corpo = render(
        "servico", **_cabecalho_e_rodape(dados),
        nome=s.nome, conteudo=conteudo,
        rotulo_tipo=TIPO_ROTULO[s.tipo].lower(), projetos=projetos,
        contato=_bloco_contato(dados.estudio, "servico", alvo=s.nome, slug=s.slug),
        revelar=Seguro('\n<script src="/js/revelar.js" defer></script>' if revela else ""),
    )
    caminho = f"servicos/{s.slug}/index.html"
    ld = (seo.json_ld_servico(s),)
    doc = _documento(caminho, s.titulo, s.descricao, corpo, json_ld=ld, previa=previa,
                     barra=_barra_wa(dados.estudio, "servico", alvo=s.nome, slug=s.slug))
    return Pagina(caminho, s.titulo, s.descricao, doc, s.atualizado, ld)


def montar_todas(dados: Dados, raiz: Path, previa: bool) -> list:
    """Todas as páginas, ordenadas por caminho. Na `previa` cada uma leva a meta noindex."""
    paginas = [_home(dados, raiz, previa), _historia(dados, raiz, previa), _projetos(dados, raiz, previa)]
    paginas += [_case(x, dados, raiz, previa) for x in visiveis(dados.projetos)]
    paginas += [_servico(s, dados, raiz, previa) for s in dados.servicos]
    return sorted(paginas, key=lambda p: p.caminho)


def paleta(dados: Dados) -> list:
    """Entradas da paleta de comandos (assets/paleta.json), nesta ordem: projetos visíveis (a ordem de /projetos/),
    serviços e contato (as páginas dos sócios saíram do site em 24/11). Só o que tem página ou link real; o contato vem dos campos do `Estudio`.
    `termos` só entra quando o rótulo não cobre a busca ("email" não está em "E-mail"); o tipo também é buscável no JS."""
    est = dados.estudio
    itens = [{"rotulo": x.nome, "tipo": "projeto", "url": f"/projetos/{x.slug}/"} for x in visiveis(dados.projetos)]
    itens += [{"rotulo": x.nome, "tipo": "servico", "url": f"/servicos/{x.slug}/"} for x in dados.servicos]
    itens += [
        {"rotulo": "Pedir orçamento", "tipo": "contato", "url": "/#contato"},
        {"rotulo": "WhatsApp", "tipo": "contato",
         "url": contato.link_whatsapp(est.whatsapp, contato.mensagem(est, "home"))},
        {"rotulo": "Telegram", "tipo": "contato", "url": est.telegram},
        {"rotulo": "E-mail", "tipo": "contato", "termos": "email",
         "url": contato.link_email(est.email, contato.codigo_origem("home"))},
    ]
    return itens


def paleta_json(dados: Dados) -> str:
    return json.dumps(paleta(dados), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _com_cabecalho(corpo: str) -> str:
    primeira, _, resto = corpo.partition("\n")
    if not primeira.lower().startswith("<!doctype html>"):
        raise ValueError("página sem <!doctype html> na primeira linha")
    return f"{primeira}\n{CABECALHO}\n{resto}"


def _gerado(arq: Path) -> bool:
    try:
        return CABECALHO in arq.read_text(encoding="utf-8")[:300]
    except (OSError, UnicodeDecodeError):
        return False


def escrever(paginas, saida: Path, previa: bool, raiz: Path | None = None, extras: dict | None = None) -> None:
    """Grava as páginas em `saida`. Na prévia copia os estáticos de `raiz` (sem o CNAME).
    `extras` ({caminho: texto}) são arquivos gerados que não são páginas (assets/paleta.json); vão por último,
    para a cópia dos estáticos da prévia não pôr por cima a versão velha do repo."""
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    novos = {p.caminho for p in paginas}
    for arq in sorted(saida.rglob("*.html")):
        rel = arq.relative_to(saida).as_posix()
        if rel not in novos and _gerado(arq):
            arq.unlink()
    for p in paginas:
        destino = saida / p.caminho
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(_com_cabecalho(p.corpo), encoding="utf-8")
    (saida / "sitemap.xml").write_text(seo.sitemap(paginas), encoding="utf-8")
    if previa:
        (saida / "robots.txt").write_text(seo.robots_previa(), encoding="utf-8")
        (saida / "_headers").write_text(seo.headers_previa(), encoding="utf-8")
        raiz = Path(raiz) if raiz else Path(__file__).resolve().parent.parent.parent
        for nome in ESTATICOS:
            origem = raiz / nome
            if origem.is_dir():
                shutil.copytree(origem, saida / nome, dirs_exist_ok=True)
            elif origem.is_file():
                shutil.copy2(origem, saida / nome)
    for caminho, texto in sorted((extras or {}).items()):
        destino = saida / caminho
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
