#!/usr/bin/env python3
"""Confere o site publicado. rc 0 = limpo, rc 1 = há problemas.

Uso: python3 fonte/checar.py [--raiz R]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from alldevs import checagens  # noqa: E402
from alldevs import dados as mod_dados  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Checagens do site AllDevs.")
    ap.add_argument("--raiz", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args(argv)
    try:
        problemas = checagens.checar(Path(args.raiz))
    except (mod_dados.ErroDeDados, OSError, ValueError) as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    for p in problemas:
        print(p)
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
