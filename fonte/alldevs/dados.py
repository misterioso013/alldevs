"""Carrega e valida os dados do site (fonte/dados/*.json)."""
import json
import re
from dataclasses import MISSING, dataclass, fields
from pathlib import Path

TIPOS = {"site", "app", "automacao", "produto"}
TIPO_ROTULO = {"site": "Site", "app": "App", "automacao": "Automação", "produto": "Produto"}
POR_TRAS_TIPOS = {"codigo", "wireframe", "fluxo"}
GRUPOS_TECNOLOGIA = {"front", "mobile", "back", "nuvem", "dados"}
REMOVIDOS = {"autores", "quem_toca"}  # campos que não existem mais: citar o arquivo em vez de ignorar
PLAY_STORE = "https://play.google.com/store/apps/details?id="
POR_TRAS_MAX_LINHAS, POR_TRAS_MAX_COLUNAS, FRASE_MAX = 24, 72, 60
# Uma classe de segredo por padrão; o erro cita arquivo:linha e a classe, nunca o valor.
RE_SEGREDO = (
    ("chave sk-", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}")),
    ("chave AWS", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("token GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36}|\bgithub_pat_[A-Za-z0-9_]{22,}")),
    ("chave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Bearer", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}")),
    ("credencial", re.compile(r"""(token|password|passwd|senha|secret|api[_-]?key)[\w-]*["']?\s*[:=]""", re.I)),
    ("IP", re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")),
    ("e-mail", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")),
    ("host interno", re.compile(r"localhost|docaio\.com\.br", re.I)),
)
RE_LOJA = re.compile(re.escape(PLAY_STORE) + r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+$")
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
    ciclo: tuple
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
    faz: tuple = ()
    link_historia: bool = False


@dataclass(frozen=True)
class Projeto:
    slug: str
    nome: str
    tipo: str
    situacao: str
    ano: "int | None"
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
    rascunho: bool = False
    loja: str = ""
    por_tras: "dict | None" = None


@dataclass(frozen=True)
class Servico:
    slug: str
    nome: str
    titulo: str
    descricao: str
    resumo: str
    tipo: str
    atualizado: str


@dataclass(frozen=True)
class Tecnologia:
    nome: str
    grupo: str


@dataclass(frozen=True)
class Depoimento:
    nome: str
    papel: str
    texto: str
    autorizado: bool


@dataclass(frozen=True)
class Dados:
    estudio: Estudio
    pessoas: tuple
    projetos: tuple
    servicos: tuple
    tecnologias: tuple
    depoimentos: tuple


def _ler(caminho: Path):
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ErroDeDados(f"{caminho.name}: não foi possível ler ({e})") from e


def _montar(cls, obj, arquivo):
    if not isinstance(obj, dict):
        raise ErroDeDados(f"{arquivo}: item não é um objeto")
    for campo in sorted(REMOVIDOS & set(obj)):
        ref = f" (slug {obj['slug']})" if "slug" in obj else ""
        raise ErroDeDados(f"{arquivo}: campo removido não pode mais aparecer: {campo}{ref}")
    kw = {}
    for f in fields(cls):
        if f.name not in obj:
            if f.default is not MISSING:
                continue
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


def _simples(cls, raiz_dados, arquivo):
    obj = _ler(raiz_dados / arquivo)
    if not isinstance(obj, list):
        raise ErroDeDados(f"{arquivo}: esperado uma lista")
    return tuple(_montar(cls, o, arquivo) for o in obj)  # ordem editorial: a do JSON


def carregar(raiz: Path) -> Dados:
    d = Path(raiz) / "fonte" / "dados"
    estudio = _montar(Estudio, _ler(d / "estudio.json"), "estudio.json")
    return Dados(
        estudio=estudio,
        pessoas=_lista(Pessoa, d, "pessoas.json"),
        projetos=_lista(Projeto, d, "projetos.json"),
        servicos=_lista(Servico, d, "servicos.json"),
        tecnologias=_simples(Tecnologia, d, "tecnologias.json"),
        depoimentos=_simples(Depoimento, d, "depoimentos.json"),
    )


def visiveis(projetos):
    return [p for p in projetos if p.visivel]


def ler_por_tras(raiz: Path, proj: Projeto) -> "str | None":
    """Texto do .txt do "por trás" quando o tipo é código; nos outros casos, None."""
    pt = proj.por_tras
    if not pt or pt.get("tipo") != "codigo":
        return None
    return (Path(raiz) / pt["arquivo"]).read_text(encoding="utf-8")


def _por_tras(rot, pt, raiz, e):
    rot = f"{rot} por_tras"
    if not isinstance(pt, dict):
        e(f"{rot}: deve ser um objeto ou null")
        return
    ok = set()
    for k in ("tipo", "arquivo", "origem", "frente", "frase", "cor"):
        if isinstance(pt.get(k), str) and pt[k].strip():
            ok.add(k)
        else:
            e(f"{rot}: campo {k} ausente ou vazio")
    tipo, arq = pt.get("tipo"), pt.get("arquivo")
    if "tipo" in ok and tipo not in POR_TRAS_TIPOS:
        e(f"{rot}: tipo inválido: {tipo!r}")
    if "cor" in ok and pt["cor"] not in CORES:
        e(f"{rot}: cor inválida: {pt['cor']!r}")
    if isinstance(pt.get("frase"), str) and len(pt["frase"]) > FRASE_MAX:
        e(f"{rot}: frase com {len(pt['frase'])} caracteres (máximo {FRASE_MAX})")
    frente = pt.get("frente")
    if "frente" in ok:
        if not (frente.startswith("assets/frente/") and frente.endswith(".webp")) or ".." in Path(frente).parts:
            e(f"{rot}: frente deve ser .webp em assets/frente/ (veio {frente})")
        elif not (raiz / frente).is_file():
            e(f"{rot}: frente inexistente: {frente}")
    if "arquivo" not in ok or tipo not in POR_TRAS_TIPOS:
        return
    if ".." in Path(arq).parts or Path(arq).is_absolute():
        e(f"{rot}: arquivo não pode sair da pasta (veio {arq})")
        return
    prefixo, sufixo = ("fonte/conteudo/por-tras/", ".txt") if tipo == "codigo" else ("assets/por-tras/", ".webp")
    if not (arq.startswith(prefixo) and arq.endswith(sufixo)):
        e(f"{rot}: arquivo de {tipo} deve ser {sufixo} em {prefixo} (veio {arq})")
        return
    if not (raiz / arq).is_file():
        e(f"{rot}: arquivo inexistente: {arq}")
        return
    if tipo != "codigo":
        return
    linhas = (raiz / arq).read_text(encoding="utf-8").splitlines()
    if not any(l.strip() for l in linhas):
        e(f"{rot}: {arq} sem nenhuma linha com código")
    if len(linhas) > POR_TRAS_MAX_LINHAS:
        e(f"{rot}: {arq} com {len(linhas)} linhas (máximo {POR_TRAS_MAX_LINHAS} linhas)")
    for n, linha in enumerate(linhas, 1):
        if len(linha) > POR_TRAS_MAX_COLUNAS:
            e(f"{rot}: {arq}:{n} com {len(linha)} colunas (máximo {POR_TRAS_MAX_COLUNAS} colunas)")
        for classe, padrao in RE_SEGREDO:
            if padrao.search(linha):
                e(f"{rot}: {arq}:{n} parece conter {classe}")


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

    est = dados.estudio
    data("estudio", est.atualizado)
    https("estudio.telegram", est.telegram)
    for r in est.redes:
        https(f"estudio.redes {r.get('rotulo', '?')}", r.get("url"))
    por_slug = {p.slug: p for p in dados.projetos}
    for s in est.ciclo:
        if s not in por_slug:
            e(f"estudio.ciclo: projeto inexistente: {s}")
        elif not por_slug[s].por_tras:
            e(f"estudio.ciclo: '{s}' não tem por_tras")

    for p in dados.pessoas:
        rot = f"pessoa {p.slug}"
        if p.cor not in CORES:
            e(f"{rot}: cor inválida: {p.cor!r}")
        data(rot, p.atualizado)
        if len(p.faz) != 3 or not all(isinstance(x, str) and x for x in p.faz):
            e(f"{rot}: faz deve ter exatamente 3 textos (veio {len(p.faz)})")
        if not isinstance(p.link_historia, bool):
            e(f"{rot}: link_historia deve ser booleano")
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
        if p.ano is not None and (not isinstance(p.ano, int) or isinstance(p.ano, bool)):
            e(f"{rot}: ano deve ser inteiro ou null")
        data(rot, p.atualizado)
        for campo in ("visivel", "destaque", "rascunho"):
            if not isinstance(getattr(p, campo), bool):
                e(f"{rot}: {campo} deve ser booleano (veio {getattr(p, campo)!r})")
        if p.rascunho:
            a(f"{rot}: rascunho (texto aguarda o autor)")
        if p.link:
            https(rot, p.link)
        if not isinstance(p.loja, str) or (p.loja and not RE_LOJA.match(p.loja)):
            e(f"{rot}: loja deve ser {PLAY_STORE}<id do pacote> (ou ficar vazia)")
        if p.por_tras is not None:
            _por_tras(rot, p.por_tras, raiz, e)
        for img in p.imagens:
            if not (raiz / img).is_file():
                e(f"{rot}: imagem inexistente: {img}")
        if not p.imagens:
            a(f"{rot}: imagens vazias")
        if p.visivel and not (raiz / "assets" / "og" / f"{p.slug}.png").is_file():
            a(f"{rot}: falta assets/og/{p.slug}.png")

    n_destaques = sum(1 for p in dados.projetos if p.visivel and p.destaque)
    if not 4 <= n_destaques <= 6:
        a(f"destaques: {n_destaques} projetos visíveis em destaque (ideal 4 a 6)")

    for s in dados.servicos:
        rot = f"servico {s.slug}"
        data(rot, s.atualizado)
        n = len(s.descricao)
        if not 140 <= n <= 160:
            a(f"{rot}: descricao com {n} caracteres (ideal 140 a 160)")
        if s.tipo not in TIPOS:
            e(f"{rot}: tipo inválido: {s.tipo!r}")

    # A faixa de tecnologias só diz a verdade se cada item está num projeto visível e publicado.
    no_ar = {t for p in dados.projetos if p.visivel and not p.rascunho for t in p.stack}
    for t in dados.tecnologias:
        if t.grupo not in GRUPOS_TECNOLOGIA:
            e(f"tecnologia {t.nome}: grupo inválido: {t.grupo!r}")
        if t.nome not in no_ar:
            e(f"tecnologia {t.nome}: não aparece no stack de nenhum projeto visível e publicado")

    for d in dados.depoimentos:
        if d.autorizado is not True:
            e(f"depoimento {d.nome}: sem autorização (autorizado deve ser true)")

    if not (raiz / "assets" / "og" / "site.png").is_file():
        a("falta assets/og/site.png")
    return erros, avisos
