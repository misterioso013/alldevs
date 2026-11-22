"""Monta as páginas do site a partir dos dados e dos moldes."""
import shutil
from dataclasses import dataclass
from pathlib import Path

from . import contato, seo
from .dados import Dados
from .dados import visiveis
from .modelos import Seguro, esc, render

CABECALHO = "<!-- gerado por fonte/gerar.py — não editar -->"
ESTATICOS = ("css", "js", "assets", "icon.svg")

HOME_TITULO = "AllDevs — Estúdio de software: sites, apps e automações"
HOME_DESCRICAO = (
    "Estúdio de software com dois sócios, Caio Guerras e Rosiel Victor. "
    "Sites, apps, bots e produtos próprios no ar."
)
PROJETOS_TITULO = "Projetos — AllDevs"
PROJETOS_DESCRICAO = "Os projetos da AllDevs: sites, apps, bots e produtos próprios, de cada sócio."
HISTORIA_TITULO = "A história — AllDevs"
HISTORIA_DESCRICAO = (
    "Como um adolescente que programava no celular virou engenheiro sênior, mentor de desenvolvedores "
    "e fundador do ForjaDev."
)
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


def _documento(caminho, titulo, descricao, corpo, json_ld=(), previa=False) -> Seguro:
    if json_ld:
        bloco = f'\n<script type="application/ld+json">{seo.serializar(json_ld)}</script>'
    else:
        bloco = ""
    return render("base", titulo=titulo, descricao=descricao, canonical=seo.url_publica(caminho),
                  og_imagem=f"{seo.SITE}/assets/og/{og_slug(caminho)}.png", corpo=corpo, json_ld=Seguro(bloco),
                  robots_meta=Seguro(seo.META_NOINDEX if previa else ""))


def _bloco_contato(estudio, tipo, alvo=None, slug=None) -> Seguro:
    codigo = contato.codigo_origem(tipo, slug)
    msg = contato.mensagem(estudio, tipo, alvo, slug)
    return render(
        "contato",
        whatsapp=contato.link_whatsapp(estudio.whatsapp, msg),
        email=contato.link_email(estudio.email, codigo),
        telegram=estudio.telegram,
    )


def _ler_conteudo(raiz: Path, partes, contato_html: Seguro) -> Seguro:
    """Lê o conteúdo e põe o bloco de contato onde está o marcador."""
    texto = (Path(raiz) / "fonte" / "conteudo" / Path(*partes)).read_text(encoding="utf-8")
    if MARCADOR_CONTATO not in texto:
        raise ValueError(f"conteúdo {'/'.join(partes)} sem o marcador {MARCADOR_CONTATO}")
    return Seguro(texto.replace(MARCADOR_CONTATO, contato_html.rstrip("\n")))


def _rosiel_primeiro(dados: Dados):
    return sorted(dados.pessoas, key=lambda p: (p.slug != "rosiel", p.slug))


def _cabecalho_e_rodape(dados: Dados) -> dict:
    itens = "\n".join(
        f'        <li><a href="/servicos/{esc(s.slug)}/">{esc(s.nome)}</a></li>' for s in dados.servicos)
    return {"cabecalho": render("cabecalho"), "rodape": render("rodape", servicos=Seguro(itens))}


def _nomes(dados: Dados, autores) -> str:
    por_slug = {p.slug: p.nome for p in dados.pessoas}
    return " e ".join(por_slug[a] for a in autores)


def _selos(dados: Dados, autores) -> Seguro:
    por_slug = {p.slug: p.nome for p in dados.pessoas}
    return Seguro("".join(
        f'<span class="selo selo-{esc(a)}">{esc(por_slug[a])}</span>' for a in autores))


def _com_ano(tipo, ano) -> list:
    return [str(tipo)] if ano is None else [str(tipo), str(ano)]


def _dupla(autores) -> str:
    """Classe do degradê violeta↔laranja: só no que os dois sócios fizeram juntos."""
    return " obra-dupla" if len(set(autores)) > 1 else ""


def _cartao_pessoa(p, prioridade: bool = False) -> str:
    # Foto em 4/5 (retrato inteiro); só a primeira do HTML ganha prioridade de LCP, nenhuma é lazy.
    prio = ' fetchpriority="high"' if prioridade else ""
    return (
        f'    <article class="cartao-pessoa" data-slug="{esc(p.slug)}">\n'
        f'      <img src="/{esc(p.foto)}" alt="Foto de {esc(p.nome)}" width="512" height="640"{prio}>\n'
        f'      <h3>{esc(p.nome)}</h3>\n'
        f'      <p class="rotulo-mono">{esc(p.papel_mono)}</p>\n'
        f'      <p>{esc(p.frase)}</p>\n'
        f'      <a href="/{esc(p.slug)}/" class="link-seta">Ver perfil de {esc(p.nome)}</a>\n'
        f'    </article>'
    )


def _cartao_projeto(proj, dados: Dados, classe: str, com_autores: bool, nivel: int = 3) -> str:
    attr = f' data-autores="{esc(" ".join(proj.autores))}"' if com_autores else ""
    return (
        f'    <article class="{classe}{_dupla(proj.autores)}" data-slug="{esc(proj.slug)}"{attr}>\n'
        f'      <p class="rotulo-mono">{esc(" · ".join(_com_ano(proj.tipo, proj.ano)))}</p>\n'
        f'      <h{nivel}><a href="/projetos/{esc(proj.slug)}/">{esc(proj.nome)}</a></h{nivel}>\n'
        f'      <p>{esc(proj.resumo)}</p>\n'
        f'      <p>{_selos(dados, proj.autores)}</p>\n'
        f'    </article>'
    )


def _home(dados: Dados, raiz: Path, previa: bool) -> Pagina:
    est = dados.estudio
    cartoes = "\n".join(_cartao_pessoa(p, prioridade=(i == 0))
                         for i, p in enumerate(sorted(dados.pessoas, key=lambda p: p.slug)))
    destaques = "\n".join(
        _cartao_projeto(p, dados, "cartao-destaque", False) for p in visiveis(dados.projetos) if p.destaque)
    servicos = "\n".join(
        f'    <article class="cartao-servico{_dupla(s.quem_toca)}">\n'
        f'      <h3><a href="/servicos/{esc(s.slug)}/">{esc(s.nome)}</a></h3>\n'
        f'      <p>{esc(s.resumo)}</p>\n'
        + (f'      <p>{_selos(dados, s.quem_toca)}</p>\n' if s.quem_toca else "")
        + '    </article>'
        for s in dados.servicos)
    corpo = render(
        "home", **_cabecalho_e_rodape(dados),
        cartoes=Seguro(cartoes), destaques=Seguro(destaques), servicos=Seguro(servicos),
        contato=_bloco_contato(est, "home"),
    )
    caminho = "index.html"
    ld = (seo.json_ld_home(dados), *(seo.json_ld_pessoa(p) for p in _rosiel_primeiro(dados)))
    doc = _documento(caminho, HOME_TITULO, HOME_DESCRICAO, corpo, ld, previa)
    return Pagina(caminho, HOME_TITULO, HOME_DESCRICAO, doc, est.atualizado, ld)


def _perfil(p, dados: Dados, previa: bool) -> Pagina:
    meus = [x for x in visiveis(dados.projetos) if p.slug in x.autores]
    projetos = "\n".join(_cartao_projeto(x, dados, "cartao-projeto", False) for x in meus)
    if not projetos:
        projetos = '    <p class="vazio">Em breve.</p>'
    links = ""
    if p.links:
        itens = "\n".join(
            f'    <li><a href="{esc(l["url"])}" rel="noopener">{esc(l.get("rotulo", l["url"]))}</a></li>' for l in p.links)
        links = f'  <ul class="perfil-links">\n{itens}\n  </ul>'
    faz = "\n".join(f"    <li>{esc(x)}</li>" for x in p.faz)
    historia = ""
    if p.link_historia:
        historia = '\n  <p><a class="link-seta perfil-historia" href="/historia.html">Leia a história</a></p>'
    corpo = render(
        "perfil", **_cabecalho_e_rodape(dados), faz=Seguro(faz), historia=Seguro(historia),
        nome=p.nome, papel=p.papel, papel_mono=p.papel_mono, frase=p.frase, foto=p.foto,
        links=Seguro(links), projetos=Seguro(projetos),
        contato=_bloco_contato(dados.estudio, "perfil", alvo=p.nome, slug=p.slug),
    )
    caminho = f"{p.slug}/index.html"
    titulo = f"{p.nome} — AllDevs"
    descricao = f"{p.nome}, sócio da AllDevs: {p.papel.lower()}."
    ld = (seo.json_ld_pessoa(p),)
    doc = _documento(caminho, titulo, descricao, corpo, json_ld=ld, previa=previa)
    return Pagina(caminho, titulo, descricao, doc, p.atualizado, ld)


def _projetos(dados: Dados, previa: bool) -> Pagina:
    vis = visiveis(dados.projetos)
    cartoes = "\n".join(_cartao_projeto(x, dados, "cartao-projeto", True, 2) for x in vis)
    corpo = render(
        "projetos", **_cabecalho_e_rodape(dados), cartoes=Seguro(cartoes),
        contato=_bloco_contato(dados.estudio, "home"),
    )
    caminho = "projetos/index.html"
    atualizado = max([x.atualizado for x in vis] + [dados.estudio.atualizado])
    doc = _documento(caminho, PROJETOS_TITULO, PROJETOS_DESCRICAO, corpo, previa=previa)
    return Pagina(caminho, PROJETOS_TITULO, PROJETOS_DESCRICAO, doc, atualizado, ())


def _lista(itens) -> str:
    return "\n".join(f"      <li>{esc(i)}</li>" for i in itens)


def _case(proj, dados: Dados, previa: bool) -> Pagina:
    linha = " · ".join([*_com_ano(proj.tipo, proj.ano), _nomes(dados, proj.autores), proj.situacao])
    resultado = ""
    if proj.resultado is not None:
        resultado = (f'\n  <section data-secao="resultado">\n    <h2>Resultado</h2>\n'
                     f'    <p>{esc(proj.resultado)}</p>\n  </section>\n')
    stack = ""
    if proj.stack:
        etiquetas = "".join(f'<li class="etiqueta-mono">{esc(s)}</li>' for s in proj.stack)
        stack = f'\n  <section data-secao="stack">\n    <h2>Stack</h2>\n    <ul class="etiquetas">{etiquetas}</ul>\n  </section>\n'
    imagens = ""
    if proj.imagens:
        figuras = "\n".join(
            f'    <img class="img-16-10" src="/{esc(i)}" alt="Captura de {esc(proj.nome)}" loading="lazy">'
            for i in proj.imagens)
        imagens = f'\n  <section data-secao="imagens">\n{figuras}\n  </section>\n'
    link = ""
    if proj.link:
        link = (f'\n  <p class="case-link"><a href="{esc(proj.link)}" rel="noopener" class="btn-ghost">'
                f'Ver {esc(proj.nome)} no ar</a></p>\n')
    corpo = render(
        "case", **_cabecalho_e_rodape(dados),
        linha=linha, nome=proj.nome, resumo=proj.resumo, problema=proj.problema,
        fizemos=Seguro(_lista(proj.fizemos)), resultado=Seguro(resultado), stack=Seguro(stack),
        imagens=Seguro(imagens), link=Seguro(link),
        contato=_bloco_contato(dados.estudio, "case", alvo=proj.nome, slug=proj.slug),
    )
    caminho = f"projetos/{proj.slug}/index.html"
    titulo = f"{proj.nome}: {proj.tipo} — AllDevs"
    ld = (seo.json_ld_case(proj, dados),)
    doc = _documento(caminho, titulo, proj.resumo, corpo, json_ld=ld, previa=previa or proj.rascunho)
    return Pagina(caminho, titulo, proj.resumo, doc, proj.atualizado, ld, indexar=not proj.rascunho)


def _historia(dados: Dados, raiz: Path, previa: bool) -> Pagina:
    corpo = render(
        "historia", **_cabecalho_e_rodape(dados),
        conteudo=_ler_conteudo(raiz, ("historia.html",), _bloco_contato(dados.estudio, "home")),
    )
    caminho = "historia.html"
    doc = _documento(caminho, HISTORIA_TITULO, HISTORIA_DESCRICAO, corpo, (), previa)
    return Pagina(caminho, HISTORIA_TITULO, HISTORIA_DESCRICAO, doc, dados.estudio.atualizado, ())


def _servico(s, dados: Dados, raiz: Path, previa: bool) -> Pagina:
    corpo = render(
        "servico", **_cabecalho_e_rodape(dados),
        nome=s.nome,
        quem_toca=Seguro(""),
        conteudo=_ler_conteudo(
            raiz, ("servicos", f"{s.slug}.html"),
            _bloco_contato(dados.estudio, "servico", alvo=s.nome, slug=s.slug)),
    )
    caminho = f"servicos/{s.slug}/index.html"
    ld = (seo.json_ld_servico(s),)
    doc = _documento(caminho, s.titulo, s.descricao, corpo, json_ld=ld, previa=previa)
    return Pagina(caminho, s.titulo, s.descricao, doc, s.atualizado, ld)


def montar_todas(dados: Dados, raiz: Path, previa: bool) -> list:
    """Todas as páginas, ordenadas por caminho. Na `previa` cada uma leva a meta noindex."""
    paginas = [_home(dados, raiz, previa), _historia(dados, raiz, previa), _projetos(dados, previa)]
    paginas += [_perfil(p, dados, previa) for p in dados.pessoas]
    paginas += [_case(x, dados, previa) for x in visiveis(dados.projetos)]
    paginas += [_servico(s, dados, raiz, previa) for s in dados.servicos]
    return sorted(paginas, key=lambda p: p.caminho)


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


def escrever(paginas, saida: Path, previa: bool, raiz: Path | None = None) -> None:
    """Grava as páginas em `saida`. Na prévia copia os estáticos de `raiz` (sem o CNAME)."""
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
