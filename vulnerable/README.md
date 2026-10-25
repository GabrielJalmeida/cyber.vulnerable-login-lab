# Versão vulnerable — linha de base

Esta pasta preserva a aplicação Flask deliberadamente vulnerável usada nos exercícios. Ela serve como referência comparativa e **não deve ser implantada em produção nem exposta à Internet**.

## Executar a partir da raiz do repositório

Ative o ambiente virtual e instale as dependências desta versão:

```bat
python -m pip install -r vulnerable/requirements.txt
venv\Scripts\python.exe -m pytest vulnerable/tests -q
venv\Scripts\python.exe vulnerable/app.py
```

Por padrão, o servidor escuta em `127.0.0.1:5000`. Para reproduzir o cenário Host-Only, confirme primeiro o endereço do adaptador privado e passe esse IP explicitamente a `--host`. Não use `0.0.0.0` nem uma interface pública.

A vulnerabilidade didática intencional é a ausência de limitação de tentativas/bloqueio no login. Os marcadores `LOGIN_OK` e `LOGIN_FAILED` e o status HTTP `200` nos dois resultados são convenções do exercício, não padrões de produção.
