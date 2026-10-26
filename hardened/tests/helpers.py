"""Shared synthetic test data and small HTTP test helpers."""

import re

TEST_USERNAME = "lab-demo"
TEST_PASSWORD = "Senha-Sintetica-de-Teste-123!"


def csrf_token_from(client, path: str = "/") -> str:
    response = client.get(path)
    assert response.status_code == 200
    match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
    assert match is not None, "CSRF token input was not rendered"
    return match.group(1).decode("ascii")
