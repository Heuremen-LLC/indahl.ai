import http.server, sys, os, urllib.parse
D = os.path.dirname(os.path.abspath(__file__))
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('content-length', 0)); b = self.rfile.read(n)
        name = os.path.basename(urllib.parse.urlparse(self.path).path)
        open(os.path.join(D, name), 'wb').write(b)
        self.send_response(200); self.send_header('access-control-allow-origin', '*'); self.end_headers(); self.wfile.write(b'ok')
    def do_OPTIONS(self):
        self.send_response(200); self.send_header('access-control-allow-origin', '*'); self.send_header('access-control-allow-methods', 'POST'); self.send_header('access-control-allow-headers', '*'); self.end_headers()
    def log_message(self, *a): pass
http.server.HTTPServer(('127.0.0.1', 18765), H).serve_forever()
