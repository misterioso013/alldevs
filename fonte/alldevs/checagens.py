"""Checagens do site publicado: o que não pode aparecer na saída."""
import json
import re
from pathlib import Path

from . import dados as mod_dados

# Arquivos ainda no visual antigo; a tarefa de limpeza esvazia esta tupla.
EXCECOES_TEMPORARIAS = ("css/styles.css", "css/servico.css", "historia.html", "index.html", "js/servico-gsap.js")

IGNORAR = {".git", ".superpowers", ".github", "docs", "fonte", "bancada", "inspecao"}
EXTENSOES = {".css", ".js", ".html"}
RE_COR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(", re.I)
RE_WA = re.compile(r"wa\.me/(\d*)(\?text=)?")


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
            if not cor_livre and (m := RE_COR.search(linha)):
                problemas.append(f"{rel}:{n}: cor fora dos tokens ({m.group(0)})")
            if caminho.suffix == ".html" and "Olá Rosiel" in linha:
                problemas.append(f"{rel}:{n}: 'Olá Rosiel' proibido")
            for m in RE_WA.finditer(linha):
                if not m.group(2):
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
