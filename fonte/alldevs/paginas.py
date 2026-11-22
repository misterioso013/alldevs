"""Monta as páginas do site a partir dos dados e dos moldes."""
import shutil
from dataclasses import dataclass
from pathlib import Path

from . import contato
from .dados import Dados
from .modelos import Seguro, render

CABECALHO = "<!-- gerado por fonte/gerar.py — não editar -->"
SITE = "https://all.dev.br"
ESTATICOS = ("css", "js", "assets", "icon.svg")

HOME_TITULO = "AllDevs — Desenvolvimento Web, Mobile e Automações | Rosiel Victor"
HOME_DESCRICAO = (
    "Desenvolvedor full stack sênior disponível para freelas. Sites, apps, bots e MVPs entregues rápido. "
    "Engenheiro de software, fundador do ForjaDev."
)
HISTORIA_TITULO = "A história — AllDevs"
HISTORIA_DESCRICAO = (
    "Como um adolescente que programava no celular virou engenheiro sênior, mentor de desenvolvedores "
    "e fundador do ForjaDev."
)
FONTES = (
    "https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800"
    "&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500&display=swap"
)
FONTES_ITALICO = FONTES.replace("0,9..40,500&", "0,9..40,500;1,9..40,300&")
MARCADOR_CONTATO = "<!--contato-->"
GSAP_HOME = (
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>\n'
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>\n'
    '<link rel="stylesheet" href="/css/styles.css">'
)


@dataclass(frozen=True)
class Pagina:
    caminho: str
    titulo: str
    descricao: str
    corpo: Seguro
    atualizado: str
    json_ld: tuple


def _url(caminho: str) -> str:
    """URL pública da página (index.html some, como no site atual)."""
    if caminho == "index.html":
        return SITE + "/"
    if caminho.endswith("/index.html"):
        return f"{SITE}/{caminho[: -len('index.html')]}"
    return f"{SITE}/{caminho}"


def _documento(caminho, titulo, descricao, css, corpo, fontes=FONTES) -> Seguro:
    return render("base", titulo=titulo, descricao=descricao, canonical=_url(caminho),
                  fontes=Seguro(fontes), css=css, corpo=corpo)


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


def _home(dados: Dados, raiz: Path) -> Pagina:
    est = dados.estudio
    codigo = contato.codigo_origem("home")
    corpo = render(
        "home",
        wa_home=contato.link_whatsapp(est.whatsapp, contato.mensagem(est, "home")),
        wa_numero=est.whatsapp,
        email=est.email,
        email_link=contato.link_email(est.email, codigo),
        codigo=codigo,
    )
    caminho = "index.html"
    doc = _documento(caminho, HOME_TITULO, HOME_DESCRICAO, Seguro(GSAP_HOME), corpo, FONTES_ITALICO)
    return Pagina(caminho, HOME_TITULO, HOME_DESCRICAO, doc, est.atualizado, ())


def _historia(dados: Dados, raiz: Path) -> Pagina:
    corpo = render(
        "historia",
        conteudo=_ler_conteudo(raiz, ("historia.html",), _bloco_contato(dados.estudio, "home")),
    )
    caminho = "historia.html"
    doc = _documento(caminho, HISTORIA_TITULO, HISTORIA_DESCRICAO, render("historia_estilo"), corpo, FONTES_ITALICO)
    return Pagina(caminho, HISTORIA_TITULO, HISTORIA_DESCRICAO, doc, dados.estudio.atualizado, ())


def _servico(s, dados: Dados, raiz: Path) -> Pagina:
    corpo = render(
        "servico",
        nome=s.nome,
        quem_toca=Seguro(""),
        conteudo=_ler_conteudo(
            raiz, ("servicos", f"{s.slug}.html"),
            _bloco_contato(dados.estudio, "servico", alvo=s.nome, slug=s.slug)),
    )
    caminho = f"servicos/{s.slug}/index.html"
    css = Seguro('<link rel="stylesheet" href="/css/servico.css">')
    doc = _documento(caminho, s.titulo, s.descricao, css, corpo)
    return Pagina(caminho, s.titulo, s.descricao, doc, s.atualizado, ())


def montar_todas(dados: Dados, raiz: Path, previa: bool) -> list:
    """Todas as páginas, ordenadas por caminho. `previa` fica para o SEO (Tarefa 5)."""
    paginas = [_home(dados, raiz), _historia(dados, raiz)]
    paginas += [_servico(s, dados, raiz) for s in dados.servicos]
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
    if previa:
        raiz = Path(raiz) if raiz else Path(__file__).resolve().parent.parent.parent
        for nome in ESTATICOS:
            origem = raiz / nome
            if origem.is_dir():
                shutil.copytree(origem, saida / nome, dirs_exist_ok=True)
            elif origem.is_file():
                shutil.copy2(origem, saida / nome)
