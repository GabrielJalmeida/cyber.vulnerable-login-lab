"""Application factory for the local Cyber Lab hardened login demonstration."""

from __future__ import annotations

import os
import time
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError, CSRFProtect

from app.security.rate_limit import LoginRateLimiter

csrf = CSRFProtect()
_BASE_DIR = Path(__file__).resolve().parents[1]


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def create_app(test_config: dict | None = None) -> Flask:
    """Create an app instance; environment configuration is never hard-coded."""
    load_dotenv(_BASE_DIR / ".env", override=False)

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY"),
        CYBER_LAB_USERNAME=os.getenv("CYBER_LAB_USERNAME"),
        CYBER_LAB_PASSWORD_HASH=os.getenv("CYBER_LAB_PASSWORD_HASH"),
        TESTING=False,
        WTF_CSRF_ENABLED=True,
        MAX_CONTENT_LENGTH=16 * 1024,
        MAX_USERNAME_LENGTH=128,
        MAX_PASSWORD_LENGTH=1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=_env_bool("SESSION_COOKIE_SECURE", False),
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=15),
        RATE_LIMIT_MAX_ATTEMPTS=5,
        RATE_LIMIT_WINDOW_SECONDS=60,
        RATE_LIMIT_BLOCK_SECONDS=60,
        RATE_LIMIT_CLOCK=time.monotonic,
        RATE_LIMIT_MAX_CLIENTS=4096,
    )
    if test_config:
        app.config.update(test_config)

    csrf.init_app(app)
    app.extensions["login_rate_limiter"] = LoginRateLimiter(
        max_attempts=app.config["RATE_LIMIT_MAX_ATTEMPTS"],
        window_seconds=app.config["RATE_LIMIT_WINDOW_SECONDS"],
        block_seconds=app.config["RATE_LIMIT_BLOCK_SECONDS"],
        clock=app.config["RATE_LIMIT_CLOCK"],
        max_clients=app.config["RATE_LIMIT_MAX_CLIENTS"],
    )

    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp)

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "form-action 'self'; base-uri 'self'; frame-ancestors 'none'; "
            "object-src 'none'",
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(CSRFError)
    def handle_csrf_error(_error):
        return (
            render_template(
                "login.html",
                message="A requisição expirou ou não pôde ser validada. Atualize a página e tente novamente.",
                message_type="error",
            ),
            400,
        )

    @app.errorhandler(413)
    def handle_request_too_large(_error):
        return (
            render_template(
                "error.html",
                title="Requisição muito grande",
                message="A requisição excedeu o tamanho permitido para este laboratório.",
            ),
            413,
        )

    @app.errorhandler(500)
    def handle_internal_error(_error):
        return (
            render_template(
                "error.html",
                title="Erro interno",
                message="O laboratório encontrou um problema interno. Confira a configuração local e os logs do processo.",
            ),
            500,
        )

    return app


def validate_startup_configuration(app: Flask) -> list[str]:
    """Return missing/invalid configuration names without exposing their values."""
    missing = [
        name
        for name in ("SECRET_KEY", "CYBER_LAB_USERNAME", "CYBER_LAB_PASSWORD_HASH")
        if not app.config.get(name)
    ]

    secret_key = app.config.get("SECRET_KEY")
    if secret_key and (len(str(secret_key)) < 32 or "REPLACE_WITH" in str(secret_key)):
        missing.append("SECRET_KEY (muito curta ou placeholder)")

    username = app.config.get("CYBER_LAB_USERNAME")
    if username and len(str(username)) > 64:
        missing.append("CYBER_LAB_USERNAME (deve ter até 64 caracteres)")

    configured_hash = app.config.get("CYBER_LAB_PASSWORD_HASH")
    if configured_hash:
        try:
            from argon2 import extract_parameters
            from app.security.passwords import PASSWORD_HASHER

            params = extract_parameters(configured_hash)
            if params.type.name != "ID":
                missing.append("CYBER_LAB_PASSWORD_HASH (deve usar Argon2id)")
            elif PASSWORD_HASHER.check_needs_rehash(configured_hash):
                missing.append("CYBER_LAB_PASSWORD_HASH (parâmetros fora do perfil atual)")
        except (ValueError, TypeError):
            missing.append("CYBER_LAB_PASSWORD_HASH (formato inválido)")
    return missing
