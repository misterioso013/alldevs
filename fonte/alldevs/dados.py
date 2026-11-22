"""Carrega e valida os dados do site (fonte/dados/*.json)."""
import json
import re
from dataclasses import dataclass, fields
from pathlib import Path

TIPOS = {"app", "site", "bot", "produto", "ferramenta"}
SITUACOES = {"no ar", "beta", "encerrado"}
CORES = {"roxo", "laranja"}
RE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ErroDeDados(Exception):
    pass


@dataclass(frozen=True)
class Estudio:
    nome: str
    whatsapp: str
    email: str
    telegram: str
    mensagens: dict
    redes: tuple
    inspetor: tuple
    atualizado: str


@dataclass(frozen=True)
class Pessoa:
    slug: str
    nome: str
    papel: str
    papel_mono: str
    frase: str
    foto: str
    links: tuple
    cor: str
    atualizado: str


@dataclass(frozen=True)
class Projeto:
    slug: str
    nome: str
    autores: tuple
    tipo: str
    situacao: str
    ano: int
    resumo: str
    problema: str
    fizemos: tuple
    resultado: "str | None"
    stack: tuple
    link: str
    imagens: tuple
    destaque: bool
    visivel: bool
    atualizado: str


@dataclass(frozen=True)
class Servico:
    slug: str
    nome: str
    titulo: str
    descricao: str
    resumo: str
    quem_toca: tuple
    atualizado: str


@dataclass(frozen=True)
class Dados:
    estudio: Estudio
    pessoas: tuple
    projetos: tuple
    servicos: tuple
    inspecao: dict


def _ler(caminho: Path):
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ErroDeDados(f"{caminho.name}: não foi possível ler ({e})") from e


def _montar(cls, obj, arquivo):
    if not isinstance(obj, dict):
        raise ErroDeDados(f"{arquivo}: item não é um objeto")
    kw = {}
    for f in fields(cls):
        if f.name not in obj:
            ref = f" (slug {obj['slug']})" if "slug" in obj else ""
            raise ErroDeDados(f"{arquivo}: campo obrigatório ausente: {f.name}{ref}")
        v = obj[f.name]
        kw[f.name] = tuple(v) if isinstance(v, list) else v
    return cls(**kw)


def _lista(cls, raiz_dados, arquivo):
    obj = _ler(raiz_dados / arquivo)
    if not isinstance(obj, list):
        raise ErroDeDados(f"{arquivo}: esperado uma lista")
    return tuple(sorted((_montar(cls, o, arquivo) for o in obj), key=lambda x: x.slug))


def carregar(raiz: Path) -> Dados:
    d = Path(raiz) / "fonte" / "dados"
    estudio = _montar(Estudio, _ler(d / "estudio.json"), "estudio.json")
    insp = {}
    pasta = d / "inspecao"
    if pasta.is_dir():
        for arq in sorted(pasta.glob("*.json")):
            insp[arq.stem] = _ler(arq)
    return Dados(
        estudio=estudio,
        pessoas=_lista(Pessoa, d, "pessoas.json"),
        projetos=_lista(Projeto, d, "projetos.json"),
        servicos=_lista(Servico, d, "servicos.json"),
        inspecao=insp,
    )


def visiveis(projetos):
    return [p for p in projetos if p.visivel]


def validar(dados: Dados, raiz: Path):
    raiz = Path(raiz)
    erros, avisos = [], []
    e, a = erros.append, avisos.append

    def https(rotulo, url):
        if not isinstance(url, str) or not url.startswith("https://"):
            e(f"{rotulo}: link deve começar com https:// (veio {url!r})")

    def data(rotulo, v):
        if not isinstance(v, str) or not RE_DATA.match(v):
            e(f"{rotulo}: atualizado deve ser AAAA-MM-DD (veio {v!r})")

    for nome, lista in (("pessoas", dados.pessoas), ("projetos", dados.projetos), ("servicos", dados.servicos)):
        vistos = set()
        for x in lista:
            if x.slug in vistos:
                e(f"{nome}: slug duplicado: {x.slug}")
            vistos.add(x.slug)

    slugs_pessoas = {p.slug for p in dados.pessoas}

    est = dados.estudio
    data("estudio", est.atualizado)
    https("estudio.telegram", est.telegram)
    for r in est.redes:
        https(f"estudio.redes {r.get('rotulo', '?')}", r.get("url"))
    for s in est.inspetor:
        if s == "amott":
            e("estudio.inspetor: 'amott' não pode aparecer no inspetor")
        if s not in dados.inspecao:
            e(f"estudio.inspetor: '{s}' sem arquivo em fonte/dados/inspecao/{s}.json")

    for p in dados.pessoas:
        rot = f"pessoa {p.slug}"
        if p.cor not in CORES:
            e(f"{rot}: cor inválida: {p.cor!r}")
        data(rot, p.atualizado)
        if not (raiz / p.foto).is_file():
            e(f"{rot}: foto inexistente: {p.foto}")
        for l in p.links:
            https(f"{rot} link", l.get("url"))
        if not (raiz / "assets" / "og" / f"{p.slug}.png").is_file():
            a(f"{rot}: falta assets/og/{p.slug}.png")

    for p in dados.projetos:
        rot = f"projeto {p.slug}"
        if p.tipo not in TIPOS:
            e(f"{rot}: tipo inválido: {p.tipo!r}")
        if p.situacao not in SITUACOES:
            e(f"{rot}: situacao inválida: {p.situacao!r}")
        if not isinstance(p.ano, int) or isinstance(p.ano, bool):
            e(f"{rot}: ano deve ser inteiro")
        data(rot, p.atualizado)
        if p.link:
            https(rot, p.link)
        for au in p.autores:
            if au not in slugs_pessoas:
                e(f"{rot}: autor inexistente: {au}")
        for img in p.imagens:
            if not (raiz / img).is_file():
                e(f"{rot}: imagem inexistente: {img}")
        if not p.imagens:
            a(f"{rot}: imagens vazias")
        if p.visivel and not (raiz / "assets" / "og" / f"{p.slug}.png").is_file():
            a(f"{rot}: falta assets/og/{p.slug}.png")

    for s in dados.servicos:
        rot = f"servico {s.slug}"
        data(rot, s.atualizado)
        n = len(s.descricao)
        if not 140 <= n <= 160:
            a(f"{rot}: descricao com {n} caracteres (ideal 140 a 160)")
        for q in s.quem_toca:
            if q not in slugs_pessoas:
                e(f"{rot}: quem_toca inexistente: {q}")

    if not (raiz / "assets" / "og" / "site.png").is_file():
        a("falta assets/og/site.png")
    return erros, avisos
