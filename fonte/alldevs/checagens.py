"""Checagens do site publicado: o que não pode aparecer na saída."""
import json
import re
from pathlib import Path

from . import dados as mod_dados

# Visual antigo removido na tarefa 10: nenhum arquivo tem passe livre para cor fora dos tokens.
EXCECOES_TEMPORARIAS = ()

IGNORAR = {".git", ".superpowers", ".github", "docs", "fonte", "bancada", "dist-previa"}
EXTENSOES = {".css", ".js", ".html"}
# hex de 3, 4, 6 ou 8 dígitos; ignora entidades (&#160;) e âncoras (href="#x", id="#x", url(#x))
RE_COR = re.compile(
    r"""(?<![&\w])(?<!href=")(?<!id=")(?<!url\()#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4})\b"""
    r"|\brgba?\(|\bhsla?\(",
    re.I,
)
RE_WA = re.compile(r"""wa\.me/\+?([^\s?"'<>#/]*)(\?text=([^\s"'<>&#]*))?""", re.I)
RE_OLA = re.compile(r"Ol(?:á|%C3%A1|a\u0301)[\s+]*(?:%20)*Rosiel", re.I)


def _arquivos(raiz: Path):
    for p in sorted(raiz.rglob("*")):
        rel = p.relative_to(raiz)
        if rel.parts[0] in IGNORAR or not p.is_file() or p.suffix not in EXTENSOES:
            continue
        yield p, rel.as_posix()


def _linhas(texto: str):
    return enumerate(texto.splitlines(), 1)


def checar(raiz: Path) -> list:
    raiz = Path(raiz)
    dados = mod_dados.carregar(raiz)
    proibidos = json.loads((raiz / "fonte" / "dados" / "proibidos.json").read_text(encoding="utf-8"))
    proibidos = [(re.compile(x["padrao"], re.I), x["motivo"]) for x in proibidos]
    numero = dados.estudio.whatsapp
    problemas = []

    for caminho, rel in _arquivos(raiz):
        texto = caminho.read_text(encoding="utf-8", errors="replace")
        cor_livre = rel == "css/tokens.css" or rel.startswith("js/vendor/") or rel in EXCECOES_TEMPORARIAS
        for n, linha in _linhas(texto):
            if not cor_livre:
                for m in RE_COR.finditer(linha):
                    problemas.append(f"{rel}:{n}: cor fora dos tokens ({m.group(0)})")
            if caminho.suffix == ".html" and RE_OLA.search(linha):
                problemas.append(f"{rel}:{n}: 'Olá Rosiel' proibido")
            for m in RE_WA.finditer(linha):
                if not m.group(3):
                    problemas.append(f"{rel}:{n}: wa.me sem ?text=")
                if m.group(1) != numero:
                    problemas.append(f"{rel}:{n}: número wa.me diferente do estúdio ({m.group(1)})")
            for rx, motivo in proibidos:
                if rx.search(linha):
                    problemas.append(f"{rel}:{n}: {motivo}")

    sitemap = raiz / "sitemap.xml"
    sm = sitemap.read_text(encoding="utf-8") if sitemap.is_file() else ""
    for p in dados.projetos:
        if p.visivel:
            continue
        rel = f"projetos/{p.slug}/index.html"
        if (raiz / rel).exists():
            problemas.append(f"{rel}:1: projeto invisível presente na saída")
        for n, linha in _linhas(sm):
            if f"/projetos/{p.slug}/" in linha:
                problemas.append(f"sitemap.xml:{n}: projeto invisível no sitemap ({p.slug})")
    return sorted(problemas)
