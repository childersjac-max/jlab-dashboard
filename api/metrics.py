# api/metrics.py
from http.server import BaseHTTPRequestHandler
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from _github import fetch_json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = fetch_json("pipeline_output/backtest_metrics.json")
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
