"""Server lokal untuk mencoba halaman tanpa Vercel: menyajikan index.html dan meneruskan /api/* ke API_URL.
Pakai:  python serve_local.py        (buka http://localhost:3000)
Atur alamat server pencarian:  $env:API_URL="http://localhost:8000"  (bawaan)"""
import json, os, urllib.error, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

API = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
PORT = int(os.environ.get("PORT", "3000"))
HERE = Path(__file__).parent


class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            data = (HERE / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif u.path == "/api/health":
            try:
                with urllib.request.urlopen(API + "/health", timeout=15) as r:
                    b = json.load(r)
                self._json(200, {"ready": bool(b.get("ready")), "stage": b.get("stage"), "error": b.get("error")})
            except Exception:
                self._json(502, {"ready": False, "error": "Server pencarian tidak dapat dihubungi."})
        elif u.path == "/api/search":
            q = (qs.get("q", [""])[0] or "").strip()[:500]
            mode = "lexical" if qs.get("mode", [""])[0] == "lexical" else "hybrid"
            if len(q) < 2:
                return self._json(400, {"error": "Kueri terlalu pendek."})
            url = API + "/search?" + urllib.parse.urlencode({"q": q, "top": 10, "mode": mode})
            try:
                with urllib.request.urlopen(url, timeout=55) as r:
                    self._json(200, json.load(r))
            except urllib.error.HTTPError as e:
                try:
                    detail = json.load(e).get("detail")
                except Exception:
                    detail = None
                self._json(503 if e.code == 503 else 502, {"error": detail or "Server pencarian mengembalikan error."})
            except Exception:
                self._json(502, {"error": "Server pencarian tidak dapat dihubungi."})
        else:
            self._json(404, {"error": "Tidak ditemukan"})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"Buka http://localhost:{PORT}  (server pencarian: {API})")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
