"""Serve a prévia com gzip nos arquivos de texto, como o GitHub Pages. Só para a bancada local.

Uso: python3 bancada/gzserver.py <porta> <pasta>   (escuta só em 127.0.0.1)

O http.server puro não comprime: o JS de vendor chega inteiro e o Lighthouse (Lantern)
divide a banda simulada entre ele e a foto do LCP, o que não acontece em produção.
"""
import functools
import gzip
import http.server
import io
import os
import sys

TEXTO = (".html", ".css", ".js", ".mjs", ".json", ".xml", ".svg", ".txt")


class ComGzip(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        caminho = self.translate_path(self.path)
        if os.path.isdir(caminho):
            if not self.path.split("?", 1)[0].endswith("/"):
                return super().send_head()  # deixa o http.server mandar o 301 para a barra final
            caminho = os.path.join(caminho, "index.html")
        aceita = "gzip" in self.headers.get("Accept-Encoding", "")
        if not (aceita and caminho.endswith(TEXTO) and os.path.isfile(caminho)):
            return super().send_head()
        with open(caminho, "rb") as f:
            dados = gzip.compress(f.read(), mtime=0)
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(caminho))
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("Vary", "Accept-Encoding")
        self.end_headers()
        return io.BytesIO(dados)

    def log_message(self, *args):
        pass


def main(argv):
    if len(argv) != 3:
        sys.exit("uso: python3 bancada/gzserver.py <porta> <pasta>")
    porta, pasta = int(argv[1]), argv[2]
    if not os.path.isdir(pasta):
        sys.exit(f"pasta não existe: {pasta}")
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", porta), functools.partial(ComGzip, directory=pasta))
    servidor.serve_forever()


if __name__ == "__main__":
    main(sys.argv)
