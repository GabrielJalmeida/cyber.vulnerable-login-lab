# Vulnerable Login Lab — Flask, Kali Linux & Medusa

> **Educational lab only.** This project intentionally contains a weak login flow for a controlled cybersecurity exercise. Run it only on a local machine or an isolated VirtualBox Host-Only/Internal network that you control. Do not expose it to the public internet or use it against systems without explicit authorization.

A small Flask login application built to study the full path from an HTML form to an HTTP request, backend authentication logic, virtual networking, and controlled testing with Medusa's `web-form` module. The exercise also documents the troubleshooting process, including mistakes and how they were diagnosed.

## Learning objectives

- Inspect a form submission using browser DevTools (Network/Rede, request payload, HTTP status and response body).
- Understand how `POST /login` sends the `username` and `password` fields to a Flask route.
- Connect a Kali Linux VM to a service running on a Windows host through VirtualBox Host-Only networking.
- Use a small, disposable username list and password list to test the lab form with Medusa.
- Interpret application logs, distinguish HTTP status codes from response markers, and document failures as well as successful results.
- Identify basic controls that a real authentication endpoint should implement.

## Lab topology

The original exercise used the following private Host-Only addresses. Your addresses may differ; use the values assigned to your own VirtualBox adapters.

| Component | Address / value | Role |
|---|---|---|
| Windows Host-Only adapter | `192.168.219.1` | Runs the Flask application |
| Kali VM Host-Only adapter | `192.168.219.10` | Sends requests from the lab VM |
| Flask port | `5000` | Web service |
| Endpoint | `POST /login` | Accepts the login form |

The target is **the Flask web form only**. The exercise did not compromise the Windows account, the Kali VM, or an operating-system login.

## Requirements

- Python and `pip`
- Flask and pytest (installed from `requirements.txt`)
- Oracle VirtualBox and Kali Linux
- Medusa with the `web-form` module available in Kali
- A Host-Only or Internal Network configured for the lab

## 1. Install dependencies on Windows

Open Command Prompt in the project directory:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

## 2. Start the Flask application

The demo credentials are intentionally fixed in `app.py`:

- Username: `aluno`
- Password: `Lab123!`

They are disposable lab credentials, not values to reuse on any real account. The application does not read `LAB_USERNAME` or `LAB_PASSWORD` environment variables.

Find the IPv4 address of the Windows Host-Only adapter with `ipconfig`. Then start the app bound to that specific address. The command below uses the address from the original exercise; replace it if your adapter uses a different IP:

```bat
python app.py --host 192.168.219.1 --port 5000
```

The app defaults to `127.0.0.1` if no host is specified and refuses `0.0.0.0` when started through `python app.py`. Keep the Flask server running during the exercise. Stop it with `Ctrl+C` when finished.

Do not bind this intentionally vulnerable app to a public or bridged interface. Keep the VM network isolated and do not expose port `5000` to untrusted networks.

## 3. Inspect the HTTP request in a browser

Open the login page in a browser and press `F12`. Select **Network / Rede**, submit a login attempt, and inspect the `/login` request.

Expected request details:

- Method: `POST`
- Path: `/login`
- Form fields: `username` and `password`
- Content type: usually `application/x-www-form-urlencoded`
- Failed-login response marker: `LOGIN_FAILED - Invalid username or password.`
- Successful-login response marker: `LOGIN_OK - Access granted.`

For compatibility with the particular Medusa module used in the exercise, this lab returns HTTP `200 OK` for both valid and invalid credentials and distinguishes the result by a marker in the response body. This is a deliberate test-lab choice, **not a production recommendation**. Real applications should have a clear HTTP contract and appropriate authentication protections.

You can make a single manual request from Kali to verify the endpoint. Use only the demo values configured in this project:

```bash
curl -i -X POST --data-urlencode 'username=aluno' --data-urlencode 'password=Lab123!' http://192.168.219.1:5000/login
```

## 4. Review the sample wordlists

The repository contains disposable demonstration lists:

- [`wordlists/usernames.txt`](wordlists/usernames.txt): 4 usernames, one per line
- [`wordlists/passwords.txt`](wordlists/passwords.txt): 6 passwords, one per line

That is up to **4 × 6 = 24 candidate pairs**. These lists are intentionally small and are only for this lab. The working lists created at the repository root (`users.txt` and `passwords.txt`) are local exercise files and should not be committed.

To use the repository's sample lists directly from Kali, clone the repository inside the VM and enter its directory:

```bash
git clone https://github.com/GabrielJalmeida/cyber.vulnerable-login-lab.git
cd cyber.vulnerable-login-lab
```

Inspect the sample files with:

```bash
cat -n wordlists/usernames.txt
cat -n wordlists/passwords.txt
```

The historical exercise used two local files containing four entries each. The public sample files were later adjusted to four usernames and six passwords, so reproducing the run with the current repository lists tests up to 24 combinations rather than 16.

## 5. Run the controlled Medusa exercise

First inspect the installed module's supported options:

```bash
medusa -M web-form -q
```

With the Flask service running on the Windows Host-Only address, run the test **only against this lab target**:

```bash
medusa -h 192.168.219.1 -n 5000 -U wordlists/usernames.txt -P wordlists/passwords.txt -M web-form -m FORM:login -m 'FORM-DATA:POST?username=&password=' -m 'DENY-SIGNAL:LOGIN_FAILED' -t 1
```

Replace `192.168.219.1` if your own Host-Only adapter has a different address. Do not replace the target with a public website, campus service, or another person's system.

| Option | Purpose |
|---|---|
| `-h` | Address of the lab server |
| `-n 5000` | TCP port of the Flask service |
| `-U` | Username file, one entry per line |
| `-P` | Password file, one entry per line |
| `-M web-form` | Selects Medusa's web-form module |
| `FORM:login` | Targets the `/login` path |
| `FORM-DATA:POST?username=&password=` | Sends a POST with the expected form fields |
| `DENY-SIGNAL:LOGIN_FAILED` | Text used by this test to identify an unsuccessful login |
| `-t 1` | Keeps the test sequential with low concurrency |

### Result observed during the exercise

The successful run reported a result equivalent to:

```text
ACCOUNT FOUND: [web-form] Host: 192.168.219.1 User: aluno Password: Lab123! [SUCCESS]
```

The Windows Flask log also showed a `POST /login` request from the Kali Host-Only address. Together, these observations confirmed that the VM reached the local service and Medusa recognized the demo credential configured in the form.

## 6. Run automated tests

With the virtual environment activated on Windows, run:

```bat
python -m pytest -q
```

The current test suite contains five tests covering page loading, valid credentials, invalid passwords, invalid usernames, and missing form fields. The recorded local result was `5 passed`.

## Troubleshooting diary

The project includes a detailed account of issues encountered and how they were diagnosed:

- The original classroom target was not usable, so a controlled Flask target was created.
- The VM could not reach a service bound only to Windows `127.0.0.1`; the Flask server was then bound to the Windows Host-Only adapter IP.
- A shell `dquote>` prompt indicated an unclosed double quote; the incomplete command was cancelled and re-entered.
- `curl` rejected malformed URLs when line-continuation backslashes were placed in a single-line command; running the request on one line fixed it.
- The first wordlists accidentally stored multiple values on one line with backslashes. `cat -n` exposed the issue; rewriting one item per line allowed Medusa to process each value separately.
- Tests initially expected HTTP `401`, but the lab's Medusa-compatible behavior returned `200` for both outcomes. The tests were updated to assert the intended status and the response marker.

For detail, see:

- [Lab diary: problems, hypotheses and fixes](diario-do-laboratorio.md)
- [Reproduction guide](guia-de-reproducao.md)
- [Security notes and limitations](seguranca-e-limitacoes.md)

## Security notes and limitations

This is intentionally insecure training code, not a production authentication system. It uses one hard-coded demonstration credential pair, has no rate limiting, no temporary lockout, no delay between failures, no MFA, and no session-backed authentication flow. The application writes a local `login_attempts.log`; it records timestamps, usernames, and success/failure, but does not log submitted passwords. The log is excluded by `.gitignore`.

For real applications, consider:

- Rate limiting and progressive delays, designed to avoid abusive account lockouts.
- Password hashing with a dedicated password-hashing algorithm such as Argon2id, scrypt, or bcrypt, with sensible parameters.
- Multi-factor authentication where appropriate.
- Monitoring and alerts for unusual authentication attempts.
- Correct HTTP semantics and consistent response behavior.
- Secure session management, CSRF protections when relevant, HTTPS, and careful secret handling.
- Automated tests for controls such as rate limiting, session behavior, and error handling.

The lab does not model a real database, production session management, MFA, a WAF, SSO, or the many other controls used by real applications. The small wordlists make this an educational functionality test, not a performance benchmark or a measure of real-world password strength.

## Authorization and responsible use

Use the commands only against this application in an isolated environment that you own or are explicitly authorized to test. Do not reuse these commands or credentials against third-party services. Stop the server after the exercise.
