"""Links de contato com código de origem [site·…] (sem cookies, sem rastreio)."""
from urllib.parse import quote

from .dados import Estudio

TELEGRAM = "https://t.me/m/PYdcFSXtNjZh"

_EXIGE_SLUG = ("servico", "case")


def codigo_origem(tipo: str, slug: str | None = None) -> str:
    if tipo == "home":
        return "site·home"
    if tipo not in _EXIGE_SLUG:
        raise ValueError(f"tipo de origem desconhecido: {tipo!r}")
    if not slug:
        raise ValueError(f"origem '{tipo}' exige slug")
    return f"site·{tipo}·{slug}"


def mensagem(estudio: Estudio, tipo: str, alvo: str | None = None, slug: str | None = None) -> str:
    codigo = codigo_origem(tipo, slug)
    if tipo in _EXIGE_SLUG and not alvo:
        raise ValueError(f"mensagem '{tipo}' exige alvo")
    return estudio.mensagens[tipo].replace("{alvo}", alvo or "").replace("{codigo}", codigo)


def link_whatsapp(numero: str, msg: str) -> str:
    return f"https://wa.me/{numero}?text={quote(msg, safe='')}"


def link_email(email: str, codigo: str) -> str:
    return f"mailto:{email}?subject={quote('Orçamento [' + codigo + ']', safe='')}"
