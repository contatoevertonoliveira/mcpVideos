# Architecture Acknowledgement

> Exigido pelo Documento 10, seção 138, antes de qualquer linha de implementação. Confirma que a arquitetura definida nos Documentos 01–10 foi compreendida. Não substitui a implementação.

Data: 2026-08-20

---

## 1. Stack Understood

- **Frontend:** Next.js + TypeScript + React + Tailwind CSS + shadcn/ui, organizado por feature em `apps/web`.
- **Backend:** Python + FastAPI em `apps/api`, com camadas `api / core / db / models / schemas / repositories / services / domain / events / workflows / agents / gateways / providers / integrations / security / observability`.
- **Banco:** PostgreSQL (SQLAlchemy + Alembic) — fonte de verdade para todo estado de negócio.
- **Cache/Fila:** Redis — apenas cache, locks e suporte a fila; nunca fonte de verdade.
- **Processamento assíncrono:** Celery — apenas executa; o banco decide o quê.
- **Multimídia:** FFmpeg centralizado em `MediaProcessingService`.
- **Storage:** abstração S3-compatible (Cloudflare R2 / AWS S3 / MinIO local).
- **Infra:** Docker + Docker Compose, ambientes development/staging/production, `.env` nunca commitado.
- **Monorepo:** `apps/`, `services/`, `packages/`, `infra/`, `docs/`, `tests/`.

## 2. 20 Phases Understood

Cinco macroetapas, 20 fases sequenciais (ver `docs/PROGRESS.md` seção 3 para o mapa completo). Regra fundamental: nenhuma fase implementa funcionalidade de fase futura; cada fase deixa o sistema executável, testável, documentado e migrável. Marcos de produto reconhecidos: após F10 (Channel Intelligence SaaS utilizável sem produzir vídeo), após F18 (produto operacional completo, MVP comercial possível em Assisted/Semi-Auto), após F20 (SaaS fechado com Autopilot, billing e Control Center).

## 3. Main Domain Boundaries

- **User App vs Control Center:** usuário opera decisões editoriais (ideia → calendário → aprovação → resultado); toda infraestrutura técnica (providers, models, workflows, custos brutos, correlation IDs) fica reservada ao Control Center administrativo.
- **Agent Layer vs Services/Policies/Workflows:** agentes de IA (Intelligence, Production, Quality, Growth) sempre recomendam via output estruturado; nunca executam ação externa sensível diretamente. `AGENT → structured decision → Service → Policy Validation → Workflow → Execution`.
- **Gateways de abstração:** `LLMGateway`, `MediaGateway`, `VoiceGateway`, `MusicGateway`, `YouTubeGateway`/`PlatformGateway`, `SearchGateway` isolam toda lógica de negócio de qualquer provider específico. Provider Adapters nunca decidem conteúdo, orçamento ou prioridade editorial.
- **Model Router / Media Router:** decide provider+modelo por capability, budget, saúde e histórico de aprovação — não hardcoded, não escolhido pelo agente.
- **Content Core vs Intelligence vs Governance:** conteúdo/estratégia/projetos/workflow/qualidade/analytics são agnósticos de plataforma (YouTube é o primeiro `PlatformGateway`, não uma dependência do núcleo).
- **Multi-tenancy:** Organization → Users → Channels é a espinha dorsal; toda entidade relevante carrega `organization_id`, e nenhuma query de recurso privado pode ignorá-lo.

## 4. Main Security Constraints

- Autenticação própria da plataforma, separada da autorização OAuth do YouTube.
- Tenant isolation absoluto: usuário de uma organização nunca acessa recurso de outra, mesmo conhecendo o UUID.
- Tokens OAuth e credenciais de provider: sempre criptografados em repouso, nunca em log, nunca entregues a agentes.
- Agentes nunca recebem credenciais, nunca decidem autorização, nunca publicam/cobram/alteram policy diretamente.
- Toda operação paga precisa checar entitlement → budget → policy antes de executar, e registrar usage/cost/audit depois.
- Auto Publish e Autopilot começam sempre OFF; ativação exige confirmação explícita do usuário.
- Kill switches globais obrigatórios (auto-publish, provider, organização, canal) sem necessidade de deploy.
- Idempotência obrigatória em publicação, billing e geração crítica — nunca duplicar por retry.
- Nenhuma automação existe sem limites técnicos, financeiros e de autorização definidos (Documento 09, princípio central).

## 5. Main Rules That Must Never Be Violated

1. Nunca implementar funcionalidade de fase futura de forma improvisada em fase anterior.
2. Nunca recomeçar ou substituir arquitetura já implementada sem autorização explícita do usuário.
3. Nunca deixar o Celery/Redis ser fonte de verdade — sempre o PostgreSQL.
4. Nunca acoplar regra de negócio a um provider específico (LLM, mídia, YouTube) — sempre via gateway/router.
5. Nunca permitir que um agente publique, gaste, mude policy ou credencial diretamente.
6. Nunca criar placeholders enganosos (função que aparenta funcionar mas não funciona) — usar `NotImplementedError` ou feature flag.
7. Nunca alterar banco fora de migration versionada.
8. Nunca sobrescrever histórico de tentativas, custos, auditoria ou analytics — sempre novo registro.
9. Nunca ativar Autopilot/Auto-Publish por padrão para canal novo.
10. Nunca expor ao usuário comum: MCP, provider, modelo, tokens, prompt version, queue, correlation ID — isso é exclusivo do Control Center.

---

Este acknowledgement confirma o entendimento da arquitetura descrita nos Documentos 01–10. A implementação segue a partir da Fase 01, conforme `docs/PROGRESS.md`.
