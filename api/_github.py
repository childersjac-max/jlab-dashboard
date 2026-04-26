# api/_github.py
# Shared helper — imported by all API endpoint files.

import os
import json
import csv
import io
import urllib.request

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
        print(f"fetch_raw({path}): {e}")
        return None


def fetch_csv(path):
    raw = fetch_raw(path)
    if not raw:
        return []
    return list(csv.DictReader(io.StringIO(raw)))


def fetch_json(path):
    raw = fetch_raw(path)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}
