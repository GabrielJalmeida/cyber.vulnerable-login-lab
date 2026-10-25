"""
Vulnerable Login Lab — Flask application
=========================================
Educational target application for an isolated, authorized
penetration-testing lab (Medusa on Kali Linux vs. this app on
Ubuntu Server, connected only over a VirtualBox Host-Only or
Internal Network).

INTENDED WEAKNESS (and only this one):
    No rate limiting, no lockout, and no CAPTCHA on /login.
    This is what the Medusa brute-force exercise is meant to find.

NOT present, on purpose:
    No SQL injection, no command injection, no file access flaws,
    no remote code execution. Credentials are fixed in this file;
    there is no database.

SAFETY:
    This server defaults to 127.0.0.1 (localhost only) and refuses
    to bind to 0.0.0.0. Do not change that refusal, and do not run
    this anywhere but an isolated lab network you control.
"""

import argparse
import logging
from datetime import datetime, timezone

from flask import Flask, render_template, request

app = Flask(__name__)

# --- Fictional demo credentials (lab use only) ------------------------------
VALID_USERNAME = "aluno"
VALID_PASSWORD = "Lab123!"

# --- Logging ------------------------------------------------------------
# Only timestamp, submitted username, and result are ever logged.
# Passwords are never written to the log file. This logger has its own
# handler and does not propagate to the root logger, so Werkzeug's own
# startup/access logs never end up mixed into login_attempts.log.
logger = logging.getLogger("login_lab")
logger.setLevel(logging.INFO)
logger.propagate = False
_file_handler = logging.FileHandler("login_attempts.log")
_file_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(_file_handler)


def log_attempt(username: str, success: bool) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    result = "SUCCESS" if success else "FAILURE"
    logger.info("%s | username=%s | result=%s", timestamp, username, result)


@app.route("/", methods=["GET"])
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    # Intentionally: no rate limiting, no lockout counter, no CAPTCHA,
    # no delay between attempts. This is the vulnerability the lab
    # is designed to demonstrate.
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    success = username == VALID_USERNAME and password == VALID_PASSWORD
    log_attempt(username, success)

    if success:
        # LOGIN_FAILED must never appear anywhere in this response.
        return (
            render_template("login.html", message="LOGIN_OK - Access granted.", success=True),
            200,
        )

    return (
        render_template(
            "login.html",
            message="LOGIN_FAILED - Invalid username or password.",
            success=False,
        ),
        200,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Vulnerable login lab target (isolated testing only)."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help=(
            "Interface to bind to. Default: 127.0.0.1 (localhost only). "
            "To let the Kali VM reach this app, pass your VirtualBox "
            "Host-Only/Internal adapter IP instead, e.g. "
            "--host 192.168.56.10. Never pass 0.0.0.0 or a bridged/public IP."
        ),
    )
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000).")
    args = parser.parse_args()

    if args.host == "0.0.0.0":
        raise SystemExit(
            "Refusing to bind to 0.0.0.0.\n"
            "This lab must stay on an isolated Host-Only/Internal VirtualBox "
            "network. Pass your host-only adapter's own IP explicitly, e.g.:\n"
            "    python3 app.py --host 192.168.56.10"
        )

    print(f"Starting vulnerable login lab on http://{args.host}:{args.port}")
    print("Isolated lab target only — do not expose this to any network you do not control.")
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
