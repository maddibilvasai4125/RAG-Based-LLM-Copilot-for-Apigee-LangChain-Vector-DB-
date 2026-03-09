# server.py – tiny HTTP server using Python std-lib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import json, mimetypes

import bot                                    # uses answer() from bot.py

PORT = 8000
STATIC_DIR = Path(__file__).parent / "static"

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/plain"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/ask":               # AJAX endpoint
            query = parse_qs(parsed.query).get("q", [""])[0]
            reply = bot.answer(query)
            self._send(200, json.dumps({"answer": reply}).encode(),
                    "application/json")
        else:                                   # serve static files
            target = STATIC_DIR / (parsed.path.lstrip("/") or "index.html")
            if target.exists():
                mime = mimetypes.guess_type(target.name)[0] or "text/html"
                self._send(200, target.read_bytes(), mime)
            else:
                self._send(404, b"Not found")

if __name__ == "__main__":
    print(f"Serving on http://localhost:{PORT}")
    HTTPServer(("", PORT), Handler).serve_forever()