#!/usr/bin/env python3
import os, sys
os.chdir('/Users/ardittrikshiqi/Desktop/pricing-v2')
import http.server, socketserver
PORT = int(os.environ.get('PORT', 8003))
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}", flush=True)
    httpd.serve_forever()
