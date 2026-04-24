import http.server
import socketserver
import urllib.request
import urllib.error

PORT = 8001
PROXY_DOMAIN = "https://www.v3painting.com"

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Forward requests to /scripts/ to the live Squarespace site
        if self.path.startswith('/scripts/') or self.path.startswith('/universal/') or self.path.startswith('/static/'):
            url = PROXY_DOMAIN + self.path
            print(f"Proxying: {url}")
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.status)
                    for key, value in response.getheaders():
                        self.send_header(key, value)
                    # Allow CORS
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response.read())
            except urllib.error.HTTPError as e:
                self.send_error(e.code, e.reason)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            super().do_GET()

with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
