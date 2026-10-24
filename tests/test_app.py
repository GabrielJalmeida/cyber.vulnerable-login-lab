"""
Basic automated tests for the vulnerable login lab.
Run with:  pytest -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402


def make_client():
    app.testing = True
    return app.test_client()


def test_index_loads():
    client = make_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Lab Login" in response.data
    assert b'action="/login"' in response.data


def test_valid_login_returns_login_ok():
    client = make_client()
    response = client.post(
        "/login", data={"username": "aluno", "password": "Lab123!"}
    )
    assert response.status_code == 200
    assert b"LOGIN_OK" in response.data
    assert b"LOGIN_FAILED" not in response.data


def test_invalid_password_returns_login_failed():
    client = make_client()
    response = client.post(
        "/login", data={"username": "aluno", "password": "wrong-password"}
    )
    assert response.status_code == 200
    assert b"LOGIN_FAILED" in response.data
    assert b"LOGIN_OK" not in response.data


def test_invalid_username_returns_login_failed():
    client = make_client()
    response = client.post(
        "/login", data={"username": "not-aluno", "password": "Lab123!"}
    )
    assert response.status_code == 200
    assert b"LOGIN_FAILED" in response.data


def test_missing_fields_returns_login_failed():
    client = make_client()
    response = client.post("/login", data={})
    assert response.status_code == 200
    assert b"LOGIN_FAILED" in response.data
