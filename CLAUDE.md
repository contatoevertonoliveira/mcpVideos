# mcp_videos — Guia para Claude Code

Plataforma SaaS multiusuário/multicanal de automação de conteúdo para YouTube (Content Intelligence + Production + Growth Automation). Ver visão completa em `/docs`.

## Leitura obrigatória antes de qualquer trabalho

1. **[docs/PROGRESS.md](docs/PROGRESS.md)** — SEMPRE ler primeiro. Diz em que fase estamos, o que já foi feito, o que falta e quaisquer decisões pendentes. É o ponto de retomada entre sessões/chats.
2. **`/docs/Documento NN - *.md`** — os 10 documentos mestres do projeto (todos já entregues), a serem seguidos à risca:
   - Documento 01 — Visão Geral (produto, princípios, 20 fases)
   - Documento 02 — Diretrizes Arquiteturais Obrigatórias (regras técnicas)
   - Documento 03 — Modelo de Dados e Entidades do Sistema
   - Documento 04 — Workflows, Estados, Automações e Orquestração
   - Documento 05 — Agentes de IA, Responsabilidades, Contratos e Avaliação
   - Documento 06 — MCPs, Providers, Media Gateway, Model Router, Custos e Fallbacks
   - Documento 07 — Channel Intelligence, Growth Engine, Tendências, SEO e Recomendações
   - Documento 08 — UX/UI, Jornada do Usuário e Control Center
   - Documento 09 — Segurança, Governança, Custos, Billing e Operação SaaS
   - Documento 10 — Plano Definitivo de Implementação, Dependências e Critérios de Aceite
3. **[docs/ARCHITECTURE-ACKNOWLEDGEMENT.md](docs/ARCHITECTURE-ACKNOWLEDGEMENT.md)** — confirmação de entendimento da arquitetura, exigida pelo Documento 10 antes de qualquer código.

## Regras não-negociáveis (resumo — os documentos têm a versão completa)

- **20 fases sequenciais.** Nunca implementar funcionalidade de fase futura de forma improvisada em fase anterior. Nunca pular ou reordenar fases sem autorização explícita do usuário.
- **Nunca recomeçar/substituir arquitetura já implementada** sem autorização explícita.
- Multi-tenant desde o início: toda entidade relevante carrega `organization_id`; toda query de recurso privado deve ser escopada por ele.
- UUIDs para entidades de domínio; timestamps timezone-aware UTC no banco.
- Estado vive no PostgreSQL — Celery/Redis nunca são fonte de verdade, apenas executam/cacheiam.
- Nenhuma regra de negócio deve depender de um provider específico (LLM, mídia, voz) — sempre via Gateway (`LLMGateway`, `MediaGateway`, `VoiceGateway`, `MusicGateway`, `YouTubeGateway`).
- Agentes propõem, services validam, workflows executam. Agente nunca publica/cobra/altera credencial diretamente.
- Prompts, workflows e agentes são versionados (`short.production.v1`, etc.) — nunca alterar versão existente silenciosamente.
- Sem placeholders enganosos (função que aparenta funcionar mas não funciona) — usar `NotImplementedError` ou feature flag.
- Toda migration de schema é obrigatória — nunca alterar banco manualmente.
- Não criar todas as tabelas do Documento 03 de uma vez — cada fase cria só o que lhe pertence (ver seção "Fases e Criação das Entidades" desse documento).

## Antes de iniciar/continuar uma fase

Seguir o processo do Documento 02 (seção "Implementation Plan Before Coding"):
1. revisar Documento 02 e o Documento 01;
2. revisar código existente;
3. listar arquivos a criar/alterar;
4. indicar dependências e migrations;
5. implementar, testar, corrigir;
6. **atualizar `docs/PROGRESS.md`** ao final da sessão/fase (isso é obrigatório, não opcional — é o que permite continuar em outro chat).

## Ao terminar uma fase ou sessão relevante

Sempre atualizar `docs/PROGRESS.md` com: o que foi concluído, arquivos criados/alterados, migrations, pendências, e próximos passos — seguindo o "Feature Completion Report" descrito no Documento 02.
