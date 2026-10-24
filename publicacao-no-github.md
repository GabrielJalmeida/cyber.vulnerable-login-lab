# Publicar este projeto no GitHub com segurança

O diretório está preparado para publicação. Antes de enviar, faça uma auditoria visual do que será versionado.

## 1. Crie um repositório vazio

No GitHub, escolha **New repository**, use o nome `vulnerable-login-lab` e escolha a visibilidade desejada. Para portfólio, normalmente faz sentido ser público, mas confira todo o conteúdo antes. Como este pacote já contém README e licença, não peça para o GitHub adicionar outro README, `.gitignore` ou licença no momento da criação.

## 2. Abra o terminal no diretório extraído

Execute:

```bash
git init -b main
git status --short
git add .
git diff --cached --check
git diff --cached --name-only
```

Leia a lista de arquivos staged. O esperado é incluir o código da aplicação, templates, CSS, testes, exemplos e documentação. **Não** deve incluir `venv/`, `.env`, `users.txt`, `passwords.txt`, logs nem arquivos de configuração pessoais.

Se você já tiver criado as listas locais, confira que o Git as ignora:

```bash
git check-ignore -v users.txt passwords.txt
```

O comando deve apontar para as regras correspondentes no `.gitignore`. Se os arquivos já tiverem sido adicionados ao índice anteriormente, remova-os do índice antes do commit com `git rm --cached users.txt passwords.txt` (isso preserva os arquivos locais).

## 3. Faça o primeiro commit

Depois de revisar a lista:

```bash
git commit -m "docs: publish isolated Flask login security lab"
```

## 4. Configure o remoto e publique

Substitua `GabrielJalmeida` caso o dono do repositório seja outro:

```bash
git remote add origin https://github.com/GabrielJalmeida/vulnerable-login-lab.git
git push -u origin main
```

Se o Git informar que `origin` já existe, rode `git remote -v` antes de alterar qualquer coisa. Não sobrescreva o remoto de outro projeto.

## 5. Verificação depois de publicar

- Abra o README diretamente no GitHub e confira a renderização dos comandos e tabelas.
- Confirme que os exemplos são claramente descritos como credenciais descartáveis do laboratório.
- Verifique a lista de arquivos publicados e confira novamente se não houve envio de `.env`, `venv/`, logs ou listas locais.
- Se algum segredo real tiver sido incluído por engano, revogue/rotacione-o. Apagar o arquivo em um commit posterior não remove o segredo do histórico do Git.
