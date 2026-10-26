from __future__ import annotations

from app import create_app
from tests.helpers import TEST_PASSWORD, TEST_USERNAME, csrf_token_from


class FakeClock:
    def __init__(self):
        self.value = 1000.0

    def __call__(self):
        return self.value

    def advance(self, seconds: float):
        self.value += seconds


def test_sixth_login_attempt_is_throttled_and_recovers(test_password_hash):
    clock = FakeClock()
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-key-never-use-this-outside-pytest",
            "CYBER_LAB_USERNAME": TEST_USERNAME,
            "CYBER_LAB_PASSWORD_HASH": test_password_hash,
            "WTF_CSRF_ENABLED": True,
            "SESSION_COOKIE_SECURE": False,
            "RATE_LIMIT_MAX_ATTEMPTS": 5,
            "RATE_LIMIT_WINDOW_SECONDS": 60,
            "RATE_LIMIT_BLOCK_SECONDS": 30,
            "RATE_LIMIT_CLOCK": clock,
        }
    )
    client = app.test_client()
    token = csrf_token_from(client)

    for _ in range(5):
        response = client.post(
            "/login",
            data={"csrf_token": token, "username": TEST_USERNAME, "password": "wrong-password"},
        )
        assert response.status_code == 401

    throttled = client.post(
        "/login",
        data={"csrf_token": token, "username": TEST_USERNAME, "password": "wrong-password"},
    )
    assert throttled.status_code == 429
    assert throttled.headers["Retry-After"] == "30"

    clock.advance(31)
    after_cooldown = client.post(
        "/login",
        data={"csrf_token": token, "username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    assert after_cooldown.status_code == 303
    assert after_cooldown.headers["Location"].endswith("/success")


def test_security_headers_are_added(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_long_credentials_are_rejected(client):
    token = csrf_token_from(client)
    response = client.post(
        "/login",
        data={
            "csrf_token": token,
            "username": "u" * 129,
            "password": "wrong-password",
        },
    )
    assert response.status_code == 400
    assert "excedem o tamanho permitido" in response.get_data(as_text=True)
