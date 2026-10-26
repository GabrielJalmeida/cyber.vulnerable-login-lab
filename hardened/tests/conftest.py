import pytest

from app import create_app
from app.security.passwords import hash_password
from tests.helpers import TEST_PASSWORD, TEST_USERNAME


@pytest.fixture(scope="session")
def test_password_hash() -> str:
    return hash_password(TEST_PASSWORD)


@pytest.fixture
def app(test_password_hash):
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-key-never-use-this-outside-pytest",
            "CYBER_LAB_USERNAME": TEST_USERNAME,
            "CYBER_LAB_PASSWORD_HASH": test_password_hash,
            "WTF_CSRF_ENABLED": True,
            "SESSION_COOKIE_SECURE": False,
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()
