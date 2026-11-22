"""Moldes HTML: string.Template com escape automático (fonte/modelos/*.html)."""
import html
from pathlib import Path
from string import Template

PASTA = Path(__file__).resolve().parent.parent / "modelos"


class Seguro(str):
    """HTML já pronto: não passa pelo escape."""


def esc(v) -> Seguro:
    if isinstance(v, Seguro):
        return v
    return Seguro(html.escape(str(v), quote=True))


def render(modelo: str, /, **campos) -> Seguro:
    texto = (PASTA / f"{modelo}.html").read_text(encoding="utf-8")
    valores = {k: esc(v) for k, v in campos.items()}
    return Seguro(Template(texto).substitute(valores))
