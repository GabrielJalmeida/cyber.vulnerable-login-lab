from __future__ import annotations

from argon2 import Type, extract_parameters

from app.security.passwords import PASSWORD_HASHER
from tests.helpers import TEST_PASSWORD, TEST_USERNAME, csrf_token_from


def test_login_page_contains_labels_and_independence_notice(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Usuário de demonstração" in body
    assert "Senha de demonstração" in body
    assert "Não é um sistema oficial" in body
    assert 'name="csrf_token"' in body


def test_valid_credentials_create_temporary_session(client):
    token = csrf_token_from(client)
    response = client.post(
        "/login",
        data={
            "csrf_token": token,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 303
    assert response.headers["Location"].endswith("/success")
    assert client.get("/success").status_code == 200



def test_session_cookie_is_httponly_samesite_lax_and_temporary(client, app):
    token = csrf_token_from(client)
    response = client.post(
        "/login",
        data={"csrf_token": token, "username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    cookie = response.headers.get("Set-Cookie", "")
    assert response.status_code == 303
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Expires=" in cookie
    assert app.permanent_session_lifetime.total_seconds() == 900


def test_wrong_password_is_rejected(client):
    token = csrf_token_from(client)
    response = client.post(
        "/login",
        data={"csrf_token": token, "username": TEST_USERNAME, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert "Usuário ou senha inválidos" in response.get_data(as_text=True)



def test_failed_login_logs_result_without_password_or_username(client, caplog):
    token = csrf_token_from(client)
    password_marker = "senha-privada-marker"
    username_marker = "usuario-privado-marker"

    response = client.post(
        "/login",
        data={"csrf_token": token, "username": username_marker, "password": password_marker},
    )

    assert response.status_code == 401
    assert "resultado=failed" in caplog.text
    assert password_marker not in caplog.text
    assert username_marker not in caplog.text


def test_wrong_username_is_rejected(client):
    token = csrf_token_from(client)
    response = client.post(
        "/login",
        data={"csrf_token": token, "username": "outro-usuario", "password": TEST_PASSWORD},
    )

    assert response.status_code == 401
    assert "Usuário ou senha inválidos" in response.get_data(as_text=True)


def test_missing_authentication_configuration_returns_controlled_500(client, app):
    token = csrf_token_from(client)
    app.config["CYBER_LAB_USERNAME"] = None
    app.config["CYBER_LAB_PASSWORD_HASH"] = None

    response = client.post(
        "/login",
        data={"csrf_token": token, "username": "fake", "password": "fake-password"},
    )

    assert response.status_code == 500
    assert "Configuração de autenticação incompleta" in response.get_data(as_text=True)


def test_malformed_hash_returns_controlled_500_without_password_in_logs(client, app, caplog):
    token = csrf_token_from(client)
    app.config["CYBER_LAB_PASSWORD_HASH"] = "algoritmo-inexistente$salt$valor"
    marker = "senha-marker-nao-deve-aparecer"

    response = client.post(
        "/login",
        data={"csrf_token": token, "username": TEST_USERNAME, "password": marker},
    )

    assert response.status_code == 500
    assert "Configuração de autenticação inválida" in response.get_data(as_text=True)
    assert marker not in caplog.text
    assert "algoritmo-inexistente" not in response.get_data(as_text=True)


def test_csrf_token_is_required(client):
    response = client.post(
        "/login", data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    assert response.status_code == 400
    assert "requisição expirou" in response.get_data(as_text=True).lower()


def test_success_page_requires_authentication(client):
    response = client.get("/success")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_logout_requires_csrf_and_ends_session(client):
    token = csrf_token_from(client)
    login = client.post(
        "/login",
        data={"csrf_token": token, "username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    assert login.status_code == 303
    success_page = client.get("/success")
    assert success_page.status_code == 200
    token = csrf_token_from(client, "/success")

    logout = client.post("/logout", data={"csrf_token": token})
    assert logout.status_code == 303
    protected = client.get("/success")
    assert protected.status_code == 302


def test_argon2id_profile_uses_expected_minimum_parameters(test_password_hash):
    assert test_password_hash.startswith("$argon2id$")
    params = extract_parameters(test_password_hash)
    assert params.type is Type.ID
    assert params.memory_cost == 19_456
    assert params.time_cost == 2
    assert params.parallelism == 1
    assert PASSWORD_HASHER.check_needs_rehash(test_password_hash) is False
