# Versão hardened — estrutura inicial

> [!WARNING]
> **Esta pasta ainda não contém uma implementação segura.** É somente um esqueleto de trabalho, preparado para manter a mesma direção visual da versão vulnerável. Não execute, não publique como app funcional e não considere suas proteções implementadas.

## Estado atual

- [x] Criar a pasta independente `hardened/`.
- [x] Copiar a base visual HTML/CSS para possibilitar uma interface consistente entre as versões.
- [x] Reservar um arquivo de dependências próprio.
- [ ] Implementar backend de autenticação com configuração segura e sem credenciais reais no código.
- [ ] Definir um fluxo de armazenamento/verificação de senha com hash seguro.
- [ ] Adicionar rate limiting e uma estratégia cuidadosa para tentativas repetidas.
- [ ] Configurar sessão, proteção CSRF e cookies de acordo com o fluxo escolhido.
- [ ] Revisar respostas de erro, logs sem senhas/tokens e tratamento de segredos.
- [ ] Criar testes automatizados próprios para os controles implementados.
- [ ] Validar manualmente e comparar os resultados com `vulnerable/`.

## Decisões que ainda precisam ser tomadas

Antes de implementar, definir se a versão protegida usará uma conta configurada por variáveis de ambiente ou uma persistência própria, qual biblioteca será usada para hashing de senha e como serão limitadas as tentativas. As dependências atuais são apenas a base Flask/pytest copiada do laboratório; **nenhuma dependência adicional de segurança foi escolhida ou validada ainda**.

## Interface

`templates/login.html` e `static/style.css` são cópias da camada visual da versão vulnerável na reorganização inicial. Podem evoluir separadamente, mas o objetivo é preservar a mesma aparência geral para que a comparação se concentre no comportamento de segurança.
