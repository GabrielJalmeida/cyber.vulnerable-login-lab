# Segurança, limitações e possíveis correções

## Por que o projeto é deliberadamente vulnerável?

O objetivo é didático: observar um login sem limitação de tentativas, sem bloqueio temporário e sem atraso entre falhas. O Medusa é usado contra uma aplicação de demonstração criada e controlada para o exercício.

O projeto não deve ser implantado como serviço real. Ele usa credenciais simples de demonstração e retorna um marcador textual para facilitar a análise. Não representa uma arquitetura de autenticação adequada para produção.

## O que protegeria um sistema real?

1. **Armazenamento de senhas:** nunca armazenar senhas em texto puro. Usar uma biblioteca confiável com Argon2id, scrypt ou bcrypt configurado adequadamente.
2. **Limitação de tentativas:** implementar rate limits e atrasos progressivos; considerar limites por conta e por origem sem facilitar negação de serviço por bloqueio abusivo.
3. **Monitoramento:** registrar falhas e sucessos sem registrar senhas, tokens ou conteúdo sensível; alertar sobre padrões anormais.
4. **Autenticação multifator:** oferecer MFA, especialmente para contas de alto risco.
5. **Respostas HTTP corretas:** escolher códigos de status coerentes com a semântica do resultado. O `200` para ambos os caminhos é uma escolha didática deste laboratório, não uma prática de produção.
6. **Gestão de segredos:** não manter credenciais reais no código, versionamento, logs, capturas de tela ou listas de teste públicas.
7. **Ambiente e transporte:** usar HTTPS em aplicações reais; manter serviços de demonstração isolados e desativados quando não estiverem em uso.
8. **Testes automatizados:** incluir testes de autenticação, rate limiting, políticas de sessão e comportamento de erro.

## Limitações deste experimento

- Apenas quatro usuários e quatro senhas de demonstração; não é teste de desempenho nem de cobertura realista.
- A aplicação é um formulário Flask simples; não replica CSRF, sessões, banco de dados, MFA, proxies, WAF, SSO ou regras de autenticação de sistemas reais.
- O marcador de texto torna o resultado fácil de identificar; respostas reais podem ter mensagens, códigos, redirecionamentos e tokens mais complexos.
- O teste não autoriza reproduzir a técnica em outros sistemas. A autorização e o escopo devem ser explícitos.
