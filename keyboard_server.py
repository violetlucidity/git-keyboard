#!/usr/bin/env python3
"""
Git Keyboard Server
Serves a touch-friendly git command keyboard and executes whitelisted git commands.
Binds to 127.0.0.1 only — not reachable from the network.
"""

import json
import os
import subprocess
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CONFIG_FILE = Path(__file__).parent / "config-git-keyboard.json"

with CONFIG_FILE.open() as f:
    CONFIG = json.load(f)

REPO_PATH   = CONFIG["repo_path"]
PORT        = int(CONFIG.get("port", 5000))
REMOTE      = CONFIG.get("remote", "origin")
MAIN_BRANCH = CONFIG.get("main_branch", "main")
BRANCHES    = CONFIG.get("branches", [MAIN_BRANCH])
MESSAGES    = CONFIG.get("commit_messages", ["wip: checkpoint"])

# ---------------------------------------------------------------------------
# CSRF token (generated once at startup, embedded in HTML)
# ---------------------------------------------------------------------------

CSRF_TOKEN = str(uuid.uuid4())

# ---------------------------------------------------------------------------
# Command allowlist
# All entries are argv lists — shell=False, no string interpolation at runtime.
# Entries derived from config are expanded once here at startup.
# ---------------------------------------------------------------------------

def _build_allowlist():
    cmds = {
        # Info
        "status":      ["git", "status"],
        "log":         ["git", "log", "--oneline", "-20"],
        "branch_list": ["git", "branch"],
        "diff_stat":   ["git", "diff", f"HEAD...{REMOTE}/{MAIN_BRANCH}", "--stat"],

        # Sync
        "fetch":       ["git", "fetch", REMOTE],
        "pull":        ["git", "pull", REMOTE, MAIN_BRANCH],
        "merge":       ["git", "merge", f"{REMOTE}/{MAIN_BRANCH}"],

        # Stage & commit
        "add_all":     ["git", "add", "-A"],
        "push_main":   ["git", "push", REMOTE, MAIN_BRANCH],
        "push_u":      ["git", "push", "-u", REMOTE, MAIN_BRANCH],

        # Destructive
        "reset_soft":  ["git", "reset", "--soft", "HEAD~1"],
        "discard":     ["git", "checkout", "--", "."],
    }

    # One checkout entry per configured branch
    for branch in BRANCHES:
        key = f"checkout_{branch.replace('/', '_').replace('-', '_')}"
        cmds[key] = ["git", "checkout", branch]

    # One commit entry per configured message
    for i, msg in enumerate(MESSAGES):
        key = f"commit_{i}"
        cmds[key] = ["git", "commit", "-m", msg]

    return cmds


ALLOWLIST = _build_allowlist()

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__, static_folder="static")

STATIC_DIR = Path(__file__).parent / "static"


@app.route("/")
def index():
    """Serve index.html with CSRF token injected."""
    html = (STATIC_DIR / "index.html").read_text()
    html = html.replace("__CSRF_TOKEN__", CSRF_TOKEN)
    html = html.replace("__CONFIG_JSON__", json.dumps({
        "branches": BRANCHES,
        "commit_messages": MESSAGES,
        "main_branch": MAIN_BRANCH,
        "remote": REMOTE,
        "repo_path": REPO_PATH,
    }))
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


@app.route("/branch")
def current_branch():
    """Return the current git branch for the status bar."""
    _check_csrf()
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        shell=False,
    )
    return jsonify({"branch": result.stdout.strip(), "error": result.stderr.strip()})


@app.route("/run", methods=["POST"])
def run_command():
    """Execute a whitelisted git command and return its output."""
    _check_csrf()

    data = request.get_json(silent=True) or {}
    cmd_key = data.get("cmd", "")

    if cmd_key not in ALLOWLIST:
        return jsonify({"error": f"Unknown command key: {cmd_key!r}"}), 403

    argv = ALLOWLIST[cmd_key]

    try:
        result = subprocess.run(
            argv,
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            shell=False,
            timeout=60,
        )
        return jsonify({
            "cmd":        " ".join(argv),
            "stdout":     result.stdout,
            "stderr":     result.stderr,
            "returncode": result.returncode,
        })
    except FileNotFoundError:
        return jsonify({"error": "git not found — is git installed?"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timed out after 60 s"}), 500


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_csrf():
    """Abort with 403 if the CSRF token header is missing or wrong."""
    token = request.headers.get("X-CSRF-Token", "")
    if token != CSRF_TOKEN:
        from flask import abort
        abort(403)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Git Keyboard running at http://127.0.0.1:{PORT}")
    print(f"Repo: {REPO_PATH}")
    print(f"Commands available: {', '.join(sorted(ALLOWLIST))}")
    app.run(host="127.0.0.1", port=PORT, debug=False)
