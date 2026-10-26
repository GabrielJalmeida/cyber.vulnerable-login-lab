"""Local-only entry point for the Cyber Lab hardened version."""

from app import create_app, validate_startup_configuration

app = create_app()


if __name__ == "__main__":
    problems = validate_startup_configuration(app)
    if problems:
        print("Configuração incompleta ou inválida. Execute 'python setup_lab.py' primeiro.")
        print("Itens para revisar: " + ", ".join(problems))
        raise SystemExit(1)

    print("Cyber Lab iniciado apenas em http://127.0.0.1:5001")
    print("Não exponha este laboratório à Internet nem use credenciais reais.")
    app.run(host="127.0.0.1", port=5001, debug=False)
