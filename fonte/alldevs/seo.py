"""SEO: JSON-LD, sitemap e modo prévia (noindex)."""
import json
import unicodedata
from xml.sax.saxutils import escape

SITE = "https://all.dev.br"
ID_ORGANIZACAO = f"{SITE}/#organizacao"
TIPOS_APLICATIVO = {"app", "produto"}
META_NOINDEX = '<meta name="robots" content="noindex">'


def url_publica(caminho: str) -> str:
    """URL pública da página (index.html some, como no site atual)."""
    if caminho == "index.html":
        return SITE + "/"
    if caminho.endswith("/index.html"):
        return f"{SITE}/{caminho[: -len('index.html')]}"
    return f"{SITE}/{caminho}"


def _fragmento(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return "-".join(sem_acento.lower().split())


def _id_pessoa(p) -> str:
    return f"{SITE}/#{_fragmento(p.nome)}"


def json_ld_pessoa(p) -> dict:
    ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": _id_pessoa(p),
        "name": p.nome,
        "worksFor": {"@id": ID_ORGANIZACAO},
    }
    return ld


def json_ld_home(dados) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": ID_ORGANIZACAO,
        "name": dados.estudio.nome,
        "url": SITE + "/",
        "member": [{"@id": _id_pessoa(p)} for p in dados.pessoas],
    }


def json_ld_case(proj, dados) -> dict:
    ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication" if proj.tipo in TIPOS_APLICATIVO else "WebSite",
        "name": proj.nome,
        "description": proj.resumo,
        "creator": {"@id": ID_ORGANIZACAO},
    }
    if proj.link:
        ld["url"] = proj.link
    return ld


def json_ld_servico(s) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": s.nome,
        "description": s.descricao,
        "provider": {"@id": ID_ORGANIZACAO},
    }


def serializar(blocos) -> str:
    """Lista em JSON, segura para dentro de <script> (`</` vira `<\\/`)."""
    return json.dumps(list(blocos), sort_keys=True, ensure_ascii=False).replace("</", "<\\/")


def sitemap(paginas) -> str:
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              "<!-- gerado por fonte/gerar.py — não editar -->",
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in (p for p in paginas if p.indexar):
        linhas += ["  <url>",
                   f"    <loc>{escape(url_publica(p.caminho))}</loc>",
                   f"    <lastmod>{escape(p.atualizado)}</lastmod>",
                   "  </url>"]
    linhas += ["</urlset>", ""]
    return "\n".join(linhas)


def robots_previa() -> str:
    return "User-agent: *\nDisallow: /\n"


def headers_previa() -> str:
    return "/*\n  X-Robots-Tag: noindex\n"
