# api/index.py
# Single entrypoint for all API routes on Vercel.

import os
import json
import csv
import io
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

GITHUB_USER   = os.environ.get("GITHUB_USER",   "childersjac-max")
GITHUB_REPO   = os.environ.get("GITHUB_REPO",   "Line-Tracker-Model")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"


def fetch_raw(path):
    url = f"{RAW_BASE}/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "jlab-dashboard"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        print(f"fetch_raw error: {e}")
        return None


def fetch_csv(path):
    raw = fetch_raw(path)
    if not raw:
        return []
    return list(csv.DictReader(io.StringIO(raw)))


def fetch_json_file(path):
    raw = fetch_raw(path)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def cast_numeric(rows, fields):
    for r in rows:
        for f in fields:
            if f in r and r[f] not in ("", None):
                try:
                    r[f] = float(r[f])
                except ValueError:
                    pass
    return rows


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")

        if path == "/api/slate":
            rows = fetch_csv("pipeline_output/bet_slate_latest.csv")
            rows = cast_numeric(rows, [
                "model_prob","fair_prob","edge_pct","ev_pct",
                "bet_pct","bet_usd","american_odds","line",
                "pin_move_full","money_vs_tickets","n_signals"
            ])
            body = json.dumps({"bets": rows, "n_bets": len(rows)})

        elif path == "/api/metrics":
            data = fetch_json_file("pipeline_output/backtest_metrics.json")
            body = json.dumps(data)

        elif path == "/api/history":
            rows = fetch_csv("pipeline_output/backtest_results.csv")
            rows = cast_numeric(rows, [
                "bet_usd","pnl","edge","model_prob",
                "american_odds","clv","outcome"
            ])
            body = json.dumps({"records": rows})

        elif path == "/api/status":
            from datetime import datetime, timezone
            body = json.dumps({
                "status": "ok",
                "repo": f"{GITHUB_USER}/{GITHUB_REPO}",
                "time": datetime.now(timezone.utc).isoformat(),
            })

        else:
            body = json.dumps({"error": f"Unknown route: {path}"})

        encoded = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
