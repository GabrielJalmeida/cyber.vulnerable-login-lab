# Cyber Lab — versão hardened

Aplicação didática Flask para demonstrar autenticação local com hash de senha, sessão temporária, proteção CSRF, headers defensivos e limitação de tentativas. Este pacote contém **somente a versão hardened**; a aplicação deliberadamente vulnerável não está incluída.

> **Escopo e honestidade:** este é um laboratório local, não um sistema de autenticação para produção. O limitador mantém estado em memória, por endereço de origem, e funciona somente dentro de um processo. Não há banco de dados, conta real, integração com a DIO nem autenticação externa. Não exponha a aplicação à Internet e nunca use credenciais de outros serviços.

## Interface

A tela usa uma estética tech/gamer com grafite, ciano, azul e magenta neon. O formulário fica dentro de um painel com silhueta de cadeado; os textos são curtos e os efeitos respeitam `prefers-reduced-motion`. A interface é local e independente, sem recursos externos ou JavaScript de terceiros.

## O que está implementado

- Conta local sintética configurada em `.env`; o assistente de configuração gera um hash e um segredo aleatório de sessão.
- Hash de senha Argon2id por `argon2-cffi`, com `m=19456 KiB`, `t=2`, `p=1`.
- Respostas distintas para credenciais inválidas (`401`), excesso de tentativas (`429`) e configuração ausente/malformada (`500`), sem exibir hash ou traceback ao navegador.
- Rate limit single-process: até cinco requisições de login por endereço de origem dentro da janela de 60 segundos; novas requisições ficam bloqueadas por 60 segundos. Um login bem-sucedido limpa o estado daquele endereço.
- CSRF nos formulários de login e logout com Flask-WTF.
- Sessão assinada, marcada como `HttpOnly` e `SameSite=Lax`, com expiração permanente de 15 minutos. O cookie `Secure` fica desativado na configuração HTTP local; deve ser ativado quando HTTPS estiver realmente configurado.
- `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy`, `Permissions-Policy` e `Cache-Control: no-store`.
- Limites de tamanho de requisição e de campos; mensagens de erro sem detalhes de configuração.
- Testes automatizados para os principais caminhos, CSRF, rate limit, recuperação e headers.

## Requisitos

- Python 3.10 ou superior.
- Dependências declaradas em `requirements.txt`.

## Instalação no Windows

Abra o CMD ou PowerShell nesta pasta (`hardened/`):

```bat
py -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe setup_lab.py
.venv\Scripts\python.exe run.py
```

O assistente pede um nome de usuário fictício e uma senha nova, solicita confirmação e cria `.env` com o hash Argon2id e uma chave aleatória para a sessão. A senha em texto claro não é gravada no arquivo. O assistente não sobrescreve um `.env` existente.

Abra `http://127.0.0.1:5001`. O servidor faz bind exclusivamente em `127.0.0.1`, com `debug=False`.

**Não compartilhe nem versione `.env`.** O arquivo já está coberto pelo `.gitignore`. Para refazer a configuração, faça backup apenas se necessário, remova o `.env` local com cuidado e execute `setup_lab.py` novamente; a conta anterior deixará de autenticar.

## Testes

Na pasta `hardened/`, execute:

```bat
.venv\Scripts\python.exe -m pytest -q
```

O teste de rate limit usa um relógio falso; não precisa aguardar 60 segundos em tempo real. Os testes criam credenciais sintéticas próprias e não dependem das credenciais no `.env`.

Opcionalmente, meça o custo de hashing/verificação na máquina em que o aplicativo será executado:

```bat
.venv\Scripts\python.exe benchmark_hash.py
```

A ferramenta gera dados aleatórios temporários, não imprime senha/hash e apresenta mediana e média de cinco gerações e cinco verificações.

## Política do rate limit

O limitador permite cinco submissões por IP dentro de 60 segundos. A partir da sexta tentativa, retorna `429 Too Many Requests` com `Retry-After`, bloqueando novas tentativas por 60 segundos. Uma autenticação válida antes de o bloqueio ser ativado limpa o contador; durante o período de bloqueio, a rota retorna `429` mesmo que as credenciais estejam corretas. O endereço é obtido de `request.remote_addr`; cabeçalhos como `X-Forwarded-For` não são confiáveis neste projeto e são ignorados.

A política usa memória local. Reiniciar o processo limpa os contadores, workers separados não compartilham estado e requisições originadas do mesmo IP compartilham o limite. Essas propriedades são limitações conhecidas e tornam o controle inadequado, isoladamente, para um serviço de produção distribuído.

## Armazenamento de senha

O projeto usa Argon2id com os parâmetros `m=19456 KiB`, `t=2`, `p=1`, alinhados à configuração mínima indicada na OWASP Password Storage Cheat Sheet. Os parâmetros têm custo de CPU/memória; se o ambiente mudar, faça benchmark e ajuste com critério antes de aumentar o custo. O valor em `.env` é um hash verificável, não a senha em texto claro, mas ainda deve ser tratado como informação sensível.

Referência: [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

## Respostas esperadas

| Cenário | Resposta |
|---|---:|
| Página do formulário | `200` |
| Login válido | `303` para `/success` |
| Senha ou usuário incorreto | `401` |
| CSRF ausente/inválido | `400` |
| Tentativas acima do limite | `429` e `Retry-After` |
| Configuração de autenticação ausente/malformada | `500` com mensagem controlada |
| Acesso a `/success` sem sessão | `302` para `/` |
| Logout com CSRF válido | `303` para `/` |

## Estrutura

```text
hardened/
├── app/
│   ├── routes/auth.py
│   ├── security/passwords.py
│   ├── security/rate_limit.py
│   ├── static/css/
│   └── templates/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
├── benchmark_hash.py
├── run.py
└── setup_lab.py
```

## Limitações e risco residual

- Não é auditado, certificado nem avaliado como serviço de produção.
- Sem HTTPS, conta de usuário persistente, recuperação de senha, MFA, banco de dados ou integração externa.
- O limitador não é distribuído, não persiste após reinício e agrupa pessoas pelo mesmo IP.
- A sessão é assinada no cookie do Flask; como não há armazenamento de sessão no servidor, um cookie de sessão roubado não pode ser revogado individualmente antes de expirar. O prazo curto reduz, mas não elimina, esse risco residual.
- A sessão é limitada pela expiração configurada, mas o projeto não trata todos os cenários operacionais de uma aplicação real.
- Os headers são uma camada defensiva básica, não prova de conformidade geral com um padrão.
- A aparência e os testes não demonstram, por si sós, ausência de vulnerabilidades.
