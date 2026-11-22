#!/usr/bin/env python3
"""Gera o site a partir de fonte/dados, fonte/modelos e fonte/conteudo.

Uso: python3 fonte/gerar.py [--previa] [--raiz R] [--saida S]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from alldevs import dados as mod_dados  # noqa: E402
from alldevs import paginas  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Gera o site AllDevs.")
    ap.add_argument("--previa", action="store_true", help="gera numa pasta à parte (exige --saida)")
    ap.add_argument("--raiz", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--saida")
    args = ap.parse_args(argv)

    if args.previa and not args.saida:
        print("erro: --previa exige --saida", file=sys.stderr)
        return 2
    raiz = Path(args.raiz)
    saida = Path(args.saida) if args.saida else raiz

    try:
        dados = mod_dados.carregar(raiz)
    except mod_dados.ErroDeDados as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    erros, avisos = mod_dados.validar(dados, raiz)
    for a in avisos:
        print(f"aviso: {a}")
    if erros:
        for e in erros:
            print(f"erro: {e}", file=sys.stderr)
        return 1

    lista = paginas.montar_todas(dados, raiz, args.previa)
    paginas.escrever(lista, saida, args.previa, raiz, {"assets/paleta.json": paginas.paleta_json(dados)})
    print(f"{len(lista)} páginas em {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
