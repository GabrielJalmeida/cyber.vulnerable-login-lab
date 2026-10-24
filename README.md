# Vulnerable Login Lab — Flask + Kali Linux + Medusa

> **Educational lab only.** This application is intentionally vulnerable and is designed to run on a local, isolated VirtualBox Host-Only network. Do not deploy it to the public internet, expose it to an untrusted network, or reuse its authentication design in a real application.

A small Flask login form created for a cybersecurity class exercise. The goal was to understand how an HTML form sends credentials using HTTP `POST`, inspect the request and response in browser DevTools, connect a Kali Linux virtual machine to a Flask service on a Windows host, and observe how Medusa's `web-form` module distinguishes a failed login from a successful one.

## What this project demonstrates

- Browser DevTools: inspecting `POST /login`, form fields, status codes and response content.
- Backend: a Flask route that receives `username` and `password` form fields.
- Networking: accessing a Windows-hosted service from Kali through a VirtualBox Host-Only adapter.
- Controlled security testing: two small text files used as input for a single, local training exercise with Medusa.
- Troubleshooting: shell quoting, one-value-per-line wordlists, `localhost` vs. a host-only IP, and HTTP response behavior.

## Lab topology used in the exercise

| Component | Example value | Purpose |
|---|---|---|
| Windows host-only IP | `192.168.219.1` | Hosts the Flask app |
| Kali VM host-only IP | `192.168.219.10` | Sends the lab requests |
| Flask port | `5000` | Login form service |
| Endpoint | `POST /login` | Accepts the form data |

Your VirtualBox network and adapter addresses may differ. Substitute your own **Host-Only** addresses. Do not aim the exercise at an internet host or a system you do not own or have explicit permission to test.

## Requirements

- Python 3.10+ (the original exercise ran on Windows with Python 3.14.6)
- Flask and pytest, installed from `requirements.txt`
- Oracle VirtualBox with Kali Linux
- Medusa compiled/installed in Kali with the `web-form` module available
- A Host-Only network configured between the host and VM

## 1. Install and run the Flask application on Windows

Open Command Prompt in the project directory:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

Set the fake lab credentials in the current CMD session. These values are for this local exercise only:

```bat
set LAB_USERNAME=aluno
set LAB_PASSWORD=Lab123!
```

For a host-only VM connection, start Flask bound specifically to the Windows Host-Only adapter's IPv4 address. The address below is the one used in the original exercise; check `ipconfig` on your own machine first.

```bat
flask --app app run --host=192.168.219.1 --port=5000
```

Keep this terminal open. For a quick first test, open `http://127.0.0.1:5000/` on Windows. To use the VM, browse to `http://192.168.219.1:5000/` from Kali, substituting your adapter address if different.

**Network safety:** do not use `--host=0.0.0.0` as a shortcut. Bind to the specific Host-Only adapter address. Keep the Host-Only subnet separate from public/bridged networks and stop the server when the exercise is finished.

## 2. Confirm the HTTP form behavior

Open the login page in a browser and press `F12` → **Network / Rede**. Submit a test login and inspect the `/login` request.

Expected request details:

- Method: `POST`
- URL: `/login`
- Form fields: `username` and `password`
- Content type: typically `application/x-www-form-urlencoded`
- Failed response marker: `LOGIN_FAILED - Invalid username or password.`
- Successful response marker: `LOGIN_OK - Access granted.`

The lab deliberately returns HTTP `200 OK` for both outcomes, so the experiment uses the response marker rather than the HTTP status alone. This was a debugging choice for the training exercise, **not** a production recommendation. Real applications should use appropriate status codes and implement robust authentication controls.

You can check the route with a single manual request from Kali:

```bash
curl -i -X POST --data-urlencode 'username=aluno' --data-urlencode 'password=Lab123!' http://192.168.219.1:5000/login
```

Use only the demo credentials configured for your own local instance. Do not paste real credentials into documentation, terminals that are recorded, or public issue trackers.

## 3. Prepare two wordlist files in Kali

Create one username per line:

```bash
printf '%s\n' admin gabriel aluno teste > users.txt
```

Create one password per line:

```bash
printf '%s\n' '123456' 'senha123' 'senha-incorreta-lab' 'Lab123!' > passwords.txt
```

Verify the shape of the files:

```bash
cat -n users.txt
cat -n passwords.txt
```

Each command should display **four numbered lines**, not one line containing backslashes. The two files contain four values each, which creates 4 × 4 = **16 possible username/password pairs**. These files are local test input and are excluded from Git by `.gitignore`; the repository contains example versions under `examples/` instead.

## 4. Run Medusa against the isolated lab form

First, `medusa -M web-form -q` displays the module's supported options. In the original exercise, the relevant options were `FORM`, `FORM-DATA`, and `DENY-SIGNAL`.

With the Flask service running on the Host-Only adapter, run:

```bash
medusa -h 192.168.219.1 -n 5000 -U users.txt -P passwords.txt -M web-form -m FORM:login -m 'FORM-DATA:POST?username=&password=' -m 'DENY-SIGNAL:LOGIN_FAILED' -t 1
```

The command is intentionally scoped to the example private Host-Only address and the form in this repository. Do not replace the target with a public website, campus service, or another person's system.

### What the options mean

| Option | Meaning |
|---|---|
| `-h 192.168.219.1` | Host-only IP where Flask is listening |
| `-n 5000` | TCP port of the Flask service |
| `-U users.txt` | File of usernames, one per line |
| `-P passwords.txt` | File of passwords, one per line |
| `-M web-form` | Select the module for web form authentication |
| `FORM:login` | Form endpoint path `/login` |
| `FORM-DATA:POST?username=&password=` | Submit a POST form with the two named fields |
| `DENY-SIGNAL:LOGIN_FAILED` | Marker text that identifies a failed login response |
| `-t 1` | Keep the lab run sequential and low-concurrency |

## 5. Successful result observed

The final successful run produced a line equivalent to:

```text
ACCOUNT FOUND: [web-form] Host: 192.168.219.1 User: aluno Password: Lab123! [SUCCESS]
```

This confirmed that the form accepted the demo pair configured for the lab. It did **not** compromise Windows, the Kali VM, or an operating-system account: the target was the deliberately vulnerable Flask web form running on the Windows host.

## Automated tests

Run these on the host with the virtual environment activated:

```bat
python -m pytest -q
```

The tests cover the landing page, valid demo credentials, the failure marker, and the rule that submitted passwords must not be written to application logs.

## Repository safety checklist

Before publishing, verify that you are not committing any of the following:

- `venv/` or `.venv/`
- `.env` or local environment files
- real API keys, tokens, passwords, cookies, or browser profiles
- private IP/network details beyond what you intentionally want to document
- terminal history, screenshots showing secrets, or unrelated files from Downloads
- locally generated `users.txt` and `passwords.txt`

The tracked `examples/` wordlists contain only disposable demo values. The root-level working lists are ignored. If a real secret was committed previously, removing the file in a later commit is not enough; revoke/rotate the secret and purge history when necessary.

## Further reading

- [MDN: Sending form data](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Sending_and_retrieving_form_data)
- [Flask documentation](https://flask.palletsprojects.com/)
- [Medusa project](https://github.com/jmk-foofus/medusa)

## License

MIT; see [LICENSE](LICENSE).
