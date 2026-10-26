"""Login, session, and logout routes for the local demo account."""

import hmac

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.security.passwords import PasswordHashConfigurationError, verify_password


auth_bp = Blueprint("auth", __name__)


def _client_key() -> str:
    # Do not trust X-Forwarded-For: this local lab has no configured trusted proxy.
    return request.remote_addr or "unknown"


def _login_message(message: str, message_type: str = "error", status: int = 200):
    return render_template(
        "login.html", message=message, message_type=message_type
    ), status


@auth_bp.get("/")
def login_page():
    if session.get("authenticated"):
        return redirect(url_for("auth.success"))
    return render_template("login.html", message=None, message_type="info")


@auth_bp.post("/login")
def login_submit():
    expected_username = current_app.config.get("CYBER_LAB_USERNAME")
    password_hash = current_app.config.get("CYBER_LAB_PASSWORD_HASH")
    if not expected_username or not password_hash:
        current_app.logger.error("Autenticação indisponível: configuração ausente.")
        return _login_message("Configuração de autenticação incompleta.", "error", 500)

    client_key = _client_key()
    limiter = current_app.extensions["login_rate_limiter"]
    allowed, retry_after = limiter.try_consume(client_key)
    if not allowed:
        current_app.logger.warning("Evento de autenticação: resultado=rate_limited")
        body, status = _login_message(
            f"Muitas tentativas. Aguarde {retry_after} segundos antes de tentar novamente.",
            "warning",
            429,
        )
        response = current_app.response_class(body, status=status)
        response.headers["Retry-After"] = str(retry_after)
        return response

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if (
        len(username) > current_app.config["MAX_USERNAME_LENGTH"]
        or len(password) > current_app.config["MAX_PASSWORD_LENGTH"]
    ):
        return _login_message(
            "Os dados enviados excedem o tamanho permitido.", "error", 400
        )

    try:
        # Verify the hash regardless of username to reduce obvious timing differences.
        password_matches = verify_password(password_hash, password)
    except PasswordHashConfigurationError:
        current_app.logger.error("Configuração de hash de senha inválida.")
        return _login_message(
            "Configuração de autenticação inválida.", "error", 500
        )

    try:
        username_matches = hmac.compare_digest(
            username.encode("utf-8"), expected_username.encode("utf-8")
        )
    except (UnicodeEncodeError, AttributeError):
        username_matches = False

    if not (password_matches and username_matches):
        current_app.logger.warning("Evento de autenticação: resultado=failed")
        return _login_message("Usuário ou senha inválidos.", "error", 401)

    current_app.logger.info("Evento de autenticação: resultado=success")
    limiter.clear(client_key)
    session.clear()  # Discard pre-authentication session values before login.
    session["authenticated"] = True
    session.permanent = True
    return redirect(url_for("auth.success"), code=303)


@auth_bp.get("/success")
def success():
    if not session.get("authenticated"):
        return redirect(url_for("auth.login_page"))
    return render_template("success.html")


@auth_bp.post("/logout")
def logout():
    session.clear()
    current_app.logger.info("Evento de sessão: resultado=logout")
    return redirect(url_for("auth.login_page"), code=303)
