# Diário de laboratório: do formulário ao teste com Medusa

- **Data do exercício:** 24 de outubro de 2026
- **Alvo:** aplicação Flask criada para a aula, executada no Windows do próprio aluno
- **Cliente de teste:** Kali Linux em uma VM Oracle VirtualBox
- **Rede:** Host-Only, sem alvo público
**Objetivo:** compreender o fluxo HTTP de um formulário de login e observar uma tentativa controlada com o módulo `web-form` do Medusa.

> Este diário descreve o laboratório didático e não um acesso a uma conta do Windows ou a um sistema de terceiros.

## Resumo executivo

O ambiente de teste fornecido para a aula não estava utilizável naquele momento. Em vez de insistir em um alvo que não respondia, foi criada uma pequena aplicação Flask de login para observar todo o fluxo e reproduzir a atividade dentro de uma rede virtual controlada.

O exercício terminou com o Medusa lendo duas listas (quatro usuários e quatro senhas) e identificando a combinação de demonstração `aluno` / `Lab123!`. O resultado foi possível após corrigir o formato das listas e alinhar a configuração do módulo ao formulário Flask.

## Linha do tempo: problemas, hipóteses e correções

### 1. O alvo de aula não estava pronto para o exercício

**Problema:** não havia um formulário funcional acessível para observar e testar o fluxo de login no ambiente que estava disponível.

**Decisão:** criar uma aplicação mínima em Flask, controlada pelo aluno. Isso tornou o código, os campos do formulário e as respostas observáveis e evitou depender de um serviço externo.

### 2. Preparação do backend

O ambiente foi preparado no Windows usando um ambiente virtual Python e as dependências declaradas no `requirements.txt`:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

O terminal confirmou que Flask e pytest foram instalados e que o servidor de desenvolvimento iniciou. Como em qualquer servidor de desenvolvimento, isso é apropriado para treinamento local, não para implantação em produção.

### 3. `localhost` não era suficiente para a VM

**Problema:** quando o servidor escuta somente em `127.0.0.1`, ele aceita conexões destinadas ao próprio Windows; o Kali na VM é outra máquina lógica e não pode acessar esse loopback como se fosse o do host.

**Investigação:** foram conferidos os endereços dos adaptadores no Windows e no Kali. O exercício usou `192.168.219.1` no adaptador Host-Only do Windows e `192.168.219.10` no Kali.

**Correção:** o Flask foi iniciado ligado ao endereço Host-Only do Windows:

```bat
flask run --host=192.168.219.1 --port=5000
```

O log do Flask passou a registrar requisições originadas de `192.168.219.10` para `/` e, depois, para `/login`.

**Aprendizado:** um `ping` sem resposta não prova, por si só, que o serviço HTTP está inacessível. O teste de conectividade deve ser feito para o serviço e a porta realmente usados; regras de firewall podem bloquear ICMP enquanto o TCP funciona.

### 4. Inspeção do formulário com DevTools

No navegador, a aba **Network / Rede** mostrou uma requisição para `/login` com método `POST`. Em **Payload / Conteúdo**, foram identificados os campos `username` e `password`; em **Response / Resposta**, foi possível observar o marcador textual retornado pelo Flask.

Isso ligou três conceitos:

1. HTML constrói um formulário com `action="/login"` e `method="POST"`.
2. O navegador serializa os campos e envia uma requisição HTTP.
3. A rota Flask lê os dados, valida a combinação e produz a resposta.

### 5. Respostas HTTP durante a depuração

Inicialmente, o formulário devolvia `401` em uma falha de login e `200` em um login válido. Durante a depuração com o módulo `web-form`, a rota foi ajustada para responder `200` em ambos os casos e diferenciar o resultado pelo texto:

- Falha: `LOGIN_FAILED - Invalid username or password.`
- Sucesso: `LOGIN_OK - Access granted.`

Essa mudança foi uma decisão específica do experimento para destacar a análise do conteúdo da resposta. **Não deve ser generalizada como uma prática correta para aplicações reais**; o status HTTP precisa refletir o significado do resultado e o endpoint deve ter controles de autenticação adequados. O resultado observado demonstra a configuração usada no laboratório, não que todos os formulários ou todas as versões do Medusa precisem responder dessa forma.

### 6. O terminal entrou em `dquote>`

**Problema:** o shell exibiu `dquote>`, sinalizando que uma aspa dupla havia sido aberta e não encerrada. O comando foi cancelado com `Ctrl+C` e refeito com aspas corretamente balanceadas.

### 7. `curl` rejeitou a URL

**Problema:** foram usadas barras invertidas (`\`) e espaços em uma única linha. No Bash, a barra de continuação precisa estar no fim da linha, sem espaços depois dela.

**Correção:** executar o comando em uma linha única, sem barras invertidas:

```bash
curl -i -X POST --data-urlencode 'username=aluno' --data-urlencode 'password=Lab123!' http://192.168.219.1:5000/login
```

A resposta mostrou `HTTP/1.1 200 OK` e o marcador esperado para as credenciais fornecidas.

### 8. Os arquivos de usuários e senhas estavam malformados

**Problema:** foram escritos valores com barras invertidas como separadores. As barras não separaram os itens em linhas; em uma tentativa com `echo -e`, sequências como `\a` e `\t` ainda foram interpretadas como escapes. O Medusa recebeu um único usuário e uma única senha com vários valores concatenados.

**Correção:** cada valor passou a ocupar sua própria linha. Uma forma reproduzível é:

```bash
printf '%s\n' admin gabriel aluno teste > users.txt
printf '%s\n' '123456' 'senha123' 'senha-incorreta-lab' 'Lab123!' > passwords.txt
cat -n users.txt
cat -n passwords.txt
```

A conferência com `cat -n` mostrou quatro linhas em cada arquivo. Esse foi o motivo concreto pelo qual a execução seguinte passou a mostrar os quatro usuários e as quatro senhas separadamente.

### 9. A execução final do Medusa

Com o servidor Flask ativo, foram utilizados `-U` para a lista de usuários, `-P` para a lista de senhas, `-M web-form` para selecionar o módulo, e `FORM`, `FORM-DATA` e `DENY-SIGNAL` para descrever o formulário e identificar a resposta de falha.

A saída final incluiu:

```text
ACCOUNT FOUND: [web-form] Host: 192.168.219.1 User: aluno Password: Lab123! [SUCCESS]
```

O log do Flask também registrou o `POST /login` vindo de `192.168.219.10`. Em conjunto, as evidências confirmaram que o Kali alcançou o servidor e que o módulo identificou a combinação configurada no formulário.

## Resultado e limites da conclusão

**Concluído:**

- Aplicação Flask funcional para o exercício.
- Requisições HTTP entre a VM Kali e o host Windows via Host-Only.
- Inspeção manual dos campos e respostas com DevTools.
- Dois arquivos de entrada com quatro itens cada.
- Execução do Medusa e reconhecimento da credencial de demonstração.

**O que não aconteceu:**

- Não foi acessada a conta do Windows.
- Não foi comprometida a VM Kali.
- Não foi testado um serviço público ou de terceiros.
- Não foi demonstrado que a aplicação resistiria ou não a qualquer ataque em escala; o teste foi minúsculo e controlado.

## Lições aprendidas

- Frontend, HTTP, backend, redes, sistemas operacionais e segurança se complementam.
- DevTools permite observar o protocolo real, não apenas o que a interface aparenta fazer.
- Uma ferramenta pode alcançar o serviço e mesmo assim estar mal configurada; conectividade, conteúdo dos arquivos e interpretação de resposta são problemas diferentes.
- Os logs de acesso padrão mostram rota, origem e status HTTP, mas não necessariamente o resultado semântico da autenticação.
- A documentação reproduzível deve separar evidência observada de suposições.
