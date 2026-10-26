"""Interactive one-time setup for a synthetic local Cyber Lab account."""

from __future__ import annotations

import re
import secrets
import sys
from pathlib import Path
from getpass import getpass

from app.security.passwords import hash_password

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def main() -> int:
    if ENV_FILE.exists():
        print("O arquivo .env já existe. Ele não foi sobrescrito.")
        print("Apague-o manualmente somente se quiser refazer a configuração do laboratório.")
        return 1

    print("Configuração local do Cyber Lab — use uma conta sintética exclusiva.\n")
    username = input("Usuário de demonstração [lab-demo]: ").strip() or "lab-demo"
    if not USERNAME_PATTERN.fullmatch(username):
        print("Use de 1 a 64 caracteres: letras, números, ponto, hífen ou sublinhado.")
        return 1

    password = getpass("Senha nova para o laboratório (mínimo 12 caracteres): ")
    confirmation = getpass("Repita a senha: ")
    if len(password) < 12:
        print("A senha precisa ter pelo menos 12 caracteres.")
        return 1
    if len(password) > 1024:
        print("A senha excede o limite permitido.")
        return 1
    if password != confirmation:
        print("As senhas não coincidem.")
        return 1

    password_hash = hash_password(password)
    session_secret = secrets.token_urlsafe(48)
    env_content = (
        f'FLASK_SECRET_KEY="{session_secret}"\n'
        f'CYBER_LAB_USERNAME="{username}"\n'
        f'CYBER_LAB_PASSWORD_HASH="{password_hash}"\n'
        'SESSION_COOKIE_SECURE=0\n'
    )
    try:
        ENV_FILE.write_text(env_content, encoding="utf-8", newline="\n")
    except OSError:
        print("Não foi possível criar o arquivo .env. Confira as permissões da pasta.")
        return 1
    try:
        ENV_FILE.chmod(0o600)
    except OSError:
        # Windows permissions are handled by the user account / filesystem ACL.
        pass

    print("\nConfiguração criada em .env.")
    print("A senha em texto claro não foi gravada; foi armazenado somente o hash Argon2id.")
    print("Não compartilhe, anexe nem versione esse arquivo.")
    print("Agora execute: python run.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
