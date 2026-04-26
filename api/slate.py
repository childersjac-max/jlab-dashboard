# api/slate.py
from http.server import BaseHTTPRequestHandler
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from _github import fetch_csv

NUMERIC = ["model_prob","fair_prob","edge_pct","ev_pct",
           "bet_pct","bet_usd","american_odds","line",
           "pin_move_full","money_vs_tickets","n_signals"]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        rows = fetch_csv("pipeline_output/bet_slate_latest.csv")
        for r in rows:
            for f in NUMERIC:
                if f in r and r[f] not in ("", None):
                    try: r[f] = float(r[f])
                    except ValueError: pass

        body = json.dumps({"bets": rows, "n_bets": len(rows)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
