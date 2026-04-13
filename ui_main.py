from __future__ import annotations

import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


def run_ui() -> None:
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)
    server = ThreadingHTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
    print("Static UI available at http://localhost:8000")
    server.serve_forever()


if __name__ == "__main__":
    run_ui()
