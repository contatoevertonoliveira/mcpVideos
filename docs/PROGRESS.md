# PROGRESS — Estado Atual do Projeto

> Este arquivo é o ponto de retomada entre sessões/chats. Sempre ler antes de continuar o trabalho. Sempre atualizar ao final de uma sessão relevante ou fase concluída.

Última atualização: 2026-08-20

---

## 1. Status Geral

**Fase atual:** ✅ **Fase 02 — Core Domain & Database implementada e validada** (models, schemas, repositories, services, migration aplicada num Postgres real, 25 testes passando incluindo o teste obrigatório de tenant isolation). Ver seção 4.2 para o relatório completo. Fase 01 permanece 100% validada (seção 4.1).

**Próximo passo:** commitar a Fase 02 (aguardando confirmação do usuário) e depois iniciar a **Fase 03 — Authentication & Security**.

---

## 2. Documentos Mestres — Checklist

Todos os **10 documentos** previstos já foram entregues e lidos.

| # | Documento | Status | Resumo de uma linha |
|---|-----------|--------|----------------------|
| 01 | Visão Geral | ✅ Lido | Produto, princípio central (esconder complexidade do usuário), stack, 20 fases de implementação |
| 02 | Diretrizes Arquiteturais Obrigatórias | ✅ Lido | Regras técnicas: estrutura de repo, camadas, multi-tenancy, Celery/Postgres, gateways, quality gate, naming, DoD por fase |
| 03 | Modelo de Dados e Entidades do Sistema | ✅ Lido | ~80+ tabelas mapeadas por domínio; regra de criar só o que cada fase precisa; mapeamento fase→entidades nas seções 110-129 |
| 04 | Workflows, Estados, Automações e Orquestração | ✅ Lido | Workflow engine, +20 workflows nomeados (onboarding, sync, ideas, production, quality gate, publishing, analytics, learning), modos de automação, policy engine, observabilidade |
| 05 | Agentes de IA, Responsabilidades, Contratos e Avaliação | ✅ Lido | ~30 agentes em 4 categorias (Intelligence/Production/Quality/Growth), contratos JSON de I/O, Agent Registry versionado, AgentRuntime, separação agente-propõe/service-executa, evaluator independence |
| 06 | MCPs, Providers, Media Gateway, Model Router, Custos e Fallbacks | ✅ Lido | MediaGateway/VoiceGateway/MusicGateway, Provider/Model Registry, ModelRouter com routing score configurável, budget/cost controller com reservation, fallback strategies, MVP com 1 provider real + fake provider |
| 07 | Channel Intelligence, Growth Engine, Tendências, SEO e Recomendações | ✅ Lido | Channel DNA versionado, Trend Intelligence, Opportunity Score (componentes+pesos, cálculo em código não em LLM), calendar balancing, SEO/Title/Thumbnail intelligence, Learning Engine com sample size/confidence/effect size |
| 08 | UX/UI, Jornada do Usuário e Control Center | ✅ Lido | User App simples (Ideia→Planejado→Produzindo→Pronto→Agendado→Publicado) vs Control Center técnico separado; nunca expor provider/model/MCP/tokens ao usuário comum; telas MVP obrigatórias listadas |
| 09 | Segurança, Governança, Custos, Billing e Operação SaaS | ✅ Lido | Auth própria + OAuth separado, tenant isolation, encryption de tokens, AutomationPolicy com limites, budget hard/soft limits com reservation, plans/subscriptions/entitlements, kill switches, "nenhuma automação sem limites claros" |
| 10 | Plano Definitivo de Implementação, Dependências e Critérios de Aceite | ✅ Lido | Transforma docs 01-09 em plano executivo: as 20 fases detalhadas (objetivo/escopo/critério de aceite cada uma), dependências entre fases, Definition of Done global, Phase Completion Report, exige Architecture Acknowledgement antes de codar |

Regra cumprida: todos os 10 documentos foram lidos antes de qualquer implementação, conforme exigido pelo Documento 10.

---

## 3. As 20 Fases de Implementação (referência rápida)

```text
MACROETAPA A — FOUNDATION
01 Project Foundation
02 Core Domain & Database
03 Authentication & Security
04 YouTube Integration

MACROETAPA B — CONTENT INTELLIGENCE
05 Channel Importer
06 Channel Intelligence
07 Channel DNA
08 Strategy Engine
09 Ideas & Opportunity Engine
10 Content Calendar

MACROETAPA C — CONTENT FACTORY
11 Workflow & Agent Engine
12 Script & Storyboard Engine
13 AI/MCP Media Gateway
14 Media Router & Cost Controller
15 Media Production Pipeline

MACROETAPA D — QUALITY & PUBLICATION
16 Quality Gate
17 SEO & Thumbnail Engine
18 Scheduler & YouTube Publisher

MACROETAPA E — OPTIMIZATION & AUTONOMY
19 Analytics & Learning Engine
20 Autopilot, Billing & Control Center
```

Nenhuma fase foi iniciada.

---

## 4. Decisões e Convenções Já Fixadas

- Monorepo (`apps/web`, `apps/api`, `services/*`, `packages/*`, `infra/*`, `docs/`, `tests/`).
- Frontend: Next.js 16 (App Router) + TypeScript + React 19 + Tailwind v4 + shadcn/ui.
- Backend: Python 3.12 + FastAPI + SQLAlchemy 2 (sync, psycopg2) + Alembic + Pydantic v2 + Celery 5.
- DB: PostgreSQL (SQLAlchemy + Alembic). Cache/fila: Redis. Async: Celery.
- Storage: abstração S3-compatible via `StorageGateway` (boto3), compatível com R2 / AWS S3 / MinIO local.
- Logging estruturado (structlog) com redaction automático de campos sensíveis (`authorization`, `*token*`, `password`, `secret`, `api_key`).
- Hierarquia de erros (`app/core/exceptions.py`): `ApplicationError` com `http_status` fixo por classe e `code` de negócio sobrescrevível por instância; resposta no formato `{"error": {"code", "message"}}` do Documento 02 §59.
- Worker Celery reutiliza o código/imagem de `apps/api` (ver `services/worker/README.md`) — decisão a revisitar nas Fases 13-15.
- `CLAUDE.md` criado na raiz apontando para este arquivo e para os documentos mestres.
- Repositório Git inicializado na raiz (`git init`), remote `origin` = `https://github.com/contatoevertonoliveira/mcpVideos.git`, branch `main`.
- Porta host da `api` fixada em `8002` (não `8000`) para não colidir com outros projetos locais do usuário — porta interna do container continua `8000`.
- Enums de domínio: sempre `native_enum=False` (VARCHAR + CHECK, não `ENUM` nativo do Postgres) — evita `ALTER TYPE ADD VALUE` a cada novo status em fases futuras.
- Senhas: hashing via `bcrypt` (`app/security/password.py`). E-mail validado via `pydantic[EmailStr]` + `email-validator`.
- Repositórios: duas variantes em `app/repositories/base.py` — `BaseRepository` (sem escopo, só para `Organization`/`User`, que são raízes do tenant) e `TenantScopedRepository` (exige `organization_id` em toda leitura, sem exceção).
- Testes de repository/service rodam contra PostgreSQL real (não mockado) desde a Fase 02, cada um dentro de uma transação revertida ao final — ver `apps/api/tests/conftest.py` e `README.md`.

### 4.1 Fase 01 — Relatório de Conclusão

**Implementado:**
- Monorepo completo conforme Documento 02 §2 (`apps/web`, `apps/api`, `services/{worker,media,scheduler}`, `packages/{shared,schemas,ui}`, `infra/{docker,nginx,scripts}`, `tests/`), com README explicando a decisão em cada diretório ainda vazio.
- **Backend** (`apps/api`): FastAPI app (`app/main.py`) com lifespan, CORS, exception handler; camadas vazias mas presentes (`api, core, db, models, schemas, repositories, services, domain, events, workflows, agents, gateways, providers, integrations, security, observability, utils`) prontas para a Fase 02+; `StorageGateway` (S3-compatible); Celery app + task fake `foundation.ping`; Alembic configurado (lê `DATABASE_URL` de `Settings`, `target_metadata = Base.metadata`, ainda sem nenhuma migration real — correto por Documento 03 §110).
- **Endpoints:** `GET /health`, `GET /health/db`, `GET /health/redis` (não versionados, conforme Documento 02 §55). Nenhuma rota de negócio ainda (`/api/v1` só tem o router vazio).
- **Frontend** (`apps/web`): Next.js 16 + Tailwind v4 + shadcn/ui (`button`, `card`, `badge`); página inicial faz fetch server-side em `/health` da API e mostra status via Card/Badge (prova de conectividade frontend↔backend); cliente de API embrionário em `src/services/api/`.
- **Docker:** `docker-compose.yml` na raiz com `postgres`, `redis`, `minio`, `api`, `worker`, `web` (healthchecks, hot-reload via bind mount); `Dockerfile` em `apps/api` e `apps/web` (este último multi-stage `dev`/`builder`/`runner`).
- **Testes:** backend 7 testes (pytest) cobrindo health, config, hierarquia de erros e `StorageGateway` (mockado); frontend 3 testes (vitest) cobrindo `checkApiConnection`. Nenhum teste depende de infraestrutura real (Postgres/Redis/S3), conforme Documento 02 §54/71.
- **Lint/Typecheck:** `ruff` + `mypy` (backend), `eslint` + `tsc` (frontend) — todos limpos.
- **CI foundation:** `.github/workflows/ci.yml` rodando lint+typecheck+test (+build do frontend) em push/PR.
- **Documentação:** `README.md` raiz (requisitos, comandos, migrations), `apps/web/README.md` reescrito, `infra/scripts/smoke-test.sh` (curl em `/health`, `/health/db`, `/health/redis`, frontend).

**Validado nesta sessão:**
- `ruff check .`, `mypy app`, `pytest` (backend) — todos passando.
- `npm run lint`, `npm run typecheck`, `npm run test`, `npm run build` (frontend) — todos passando.
- `alembic heads` — confirma que `env.py` carrega `Settings`/`Base`/`app.models` sem erro (sem precisar de DB real).
- `docker-compose.yml` — validado sintaticamente via parser YAML (Python). **Não validado rodando de fato** (`docker compose up`), pois o Docker não está instalado no ambiente onde esta sessão rodou.

**Validado com Docker real (2026-08-20, após instalação do Docker Desktop pelo usuário):**
- `docker compose up --build -d`: as 6 imagens buildaram e os 6 containers subiram (`postgres`, `redis`, `minio` chegaram a `healthy`; `api`, `worker`, `web` em `Up`).
- `bash infra/scripts/smoke-test.sh`: os 4 checks passaram (`/health`, `/health/db`, `/health/redis`, frontend).
- `curl http://localhost:3000` retorna a página com o badge **"Conectado"** — confirma fetch server-side real do Next.js para a API dentro da rede Docker.
- Logs do `worker`: conectou ao Redis e ficou `celery@... ready.`, task `foundation.ping` registrada.
- Logs da `api`: sem erros, sem warning de `storage_bucket_check_failed` — o bucket MinIO foi criado no startup com sucesso.
- Ambiente rodando via WSL2 (o usuário já tinha WSL habilitado); Docker Desktop CLI precisou ser adicionado ao PATH da sessão do PowerShell manualmente (`C:\Program Files\Docker\Docker\resources\bin`) pois a instalação foi feita fora desta sessão.

**Pendências / Known Limitations:**
- A imagem Docker do backend instala `requirements-dev.txt` (inclui ferramentas de lint/test) mesmo em runtime — simplificação deliberada para a Fase 01; separar imagem de produção enxuta fica para quando houver deploy real.
- Nenhuma entidade de domínio, autenticação, OAuth, agente ou billing foi implementada — está fora de escopo da Fase 01 por definição.
- Stack Docker deixada rodando ao final desta sessão (`docker compose down` quando não precisar mais).

**Como validar (já confirmado, comandos para reproduzir):**
```bash
cp .env.example .env && cp apps/api/.env.example apps/api/.env && cp apps/web/.env.example apps/web/.env
docker compose up --build -d
bash infra/scripts/smoke-test.sh
```
Ou sem Docker, rodando cada app localmente (ver `README.md`).

### 4.2 Fase 02 — Relatório de Conclusão

**Implementado:**
- **7 entidades** (Documento 03 §111): `organizations`, `users`, `organization_members`, `channels`, `jobs`, `feature_flags`, `audit_logs`. Mixins reutilizáveis em `app/db/mixins.py` (`UUIDPrimaryKeyMixin`, `TimestampMixin`, `SoftDeleteMixin`, `OrganizationScopedMixin`). Enums centralizados em `app/models/enums.py`.
- **Migration** `a2160f18014a_core_domain.py` (Alembic autogenerate) — cria as 7 tabelas, índices e constraints (unique `organizations.slug`, `users.email`, `organization_members(org_id,user_id)`, índice único parcial `channels(org_id,platform,external_channel_id) WHERE external_channel_id IS NOT NULL`).
- **Repositories** (`app/repositories/`): `base.py` com `BaseRepository`/`TenantScopedRepository` genéricos + um por entidade (`organization`, `user`, `organization_member`, `channel`, `job`, `audit_log`, `feature_flag`).
- **Schemas Pydantic** (`app/schemas/`): Create/Read para organization, user, organization_member, channel, job.
- **Services** (`app/services/`), exatamente os 5 nomeados pelo Documento 10 F02: `OrganizationService` (cria organização com slug único + `add_member`), `UserService` (cria usuário com senha hasheada), `ChannelService` (cria canal "placeholder", sempre `automation_mode=assisted`), `JobService` (ciclo de vida pending→running→completed/failed), `AuditService` (grava audit log).
- **Não implementado** (fora de escopo por definição): conexão OAuth real de canal (Fase 04), login/sessão (Fase 03) — `UserService` só cria o usuário, não autentica.
- Nenhum endpoint HTTP novo exposto ainda: como não há autenticação (Fase 03), expor `POST /organizations` ou `POST /users` publicamente seria um risco de segurança sem necessidade — a camada de serviço já está pronta para a Fase 03 chamar.

**Validado nesta sessão (com Postgres real, via Docker):**
- `alembic upgrade head` na dev DB (`mcp_videos`) e num banco limpo (`mcp_videos_test`), incluindo ciclo `upgrade → downgrade → upgrade` sem erro (Documento 10 §36).
- 25 testes (pytest) rodando contra PostgreSQL real (não mockado): CRUD de cada service, e um arquivo dedicado `test_tenant_isolation.py` provando que a Org A nunca enxerga recursos da Org B (canal, job, membership) — o critério de aceite explícito da Fase 02.
- `ruff check .` e `mypy app` limpos (60 arquivos).
- Rebuild das imagens Docker (`api`/`worker`) com as novas dependências (`bcrypt`, `email-validator`) e stack revalidada com `smoke-test.sh` — tudo OK.
- `.github/workflows/ci.yml` atualizado com um serviço `postgres` (16-alpine) + `alembic upgrade head` antes do `pytest`, para o CI também rodar os testes de integração.

**Pendências / Known Limitations:**
- `docs/database.md` criado com ERD Mermaid e decisões de modelagem — manter atualizado a cada fase que mudar o schema (Documento 03 §133).
- `channels.status` (`pending|active|disabled`) foi uma decisão desta fase — o Documento 03 não especifica os valores exatos.
- Autorização (quem pode fazer o quê) ainda não existe — isso é `AuthorizationService`, Fase 03.
- Testes de repository/service agora **exigem PostgreSQL real** (`mcp_videos_test`), diferente da Fase 01 onde nada dependia de infra. Documentado no `README.md`.

**Como validar:**
```bash
cd apps/api
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/mcp_videos alembic upgrade head
pytest -v
```
(requer `docker compose up -d` rodando para o Postgres em `localhost:5432`, e o banco `mcp_videos_test` criado uma vez — ver `README.md`).

## 5. Pendências / Perguntas em Aberto

- Fase 02 implementada e validada nesta sessão — **ainda não commitada/enviada** (aguardando pedido explícito, igual fizemos na Fase 01).
- Documento 10 (seção 137) sugere organizar os documentos em `/docs/master/` com slugs (`01-product-brief.md`, etc.) — não feito; usuário optou implicitamente por manter o padrão atual `Documento NN - Titulo.md` ao pedir para seguir direto para a Fase 01.
- Ainda não definido: nome comercial do produto, provedor de IA/mídia real a integrar primeiro na Fase 13 (Documento 10 §71 pede benchmark atualizado antes de decidir — não assumir Higgsfield/Kie/fal.ai/WaveSpeed/Replicate como escolha final), moeda/plano de billing.

---

## 6. Log de Sessões

### 2026-08-20 — Sessão de briefing inicial
- Lidos Documentos 01, 02 e 03 (nomes ainda não renumerados nesse momento).
- Usuário renomeou os arquivos para o padrão `Documento NN - Titulo.md` e avisou que serão ~10 documentos ao todo.
- Lido Documento 04 assim que apareceu em `/docs`.
- Criado `CLAUDE.md` (raiz) e `docs/PROGRESS.md` (este arquivo) para garantir continuidade entre chats/sessões.

### 2026-08-20 — Leitura completa da spec mestre (mesma data, sessão seguinte)
- Lidos Documentos 05, 06, 07, 08, 09 e 10 — spec mestre 100% completa.
- Criado [docs/ARCHITECTURE-ACKNOWLEDGEMENT.md](ARCHITECTURE-ACKNOWLEDGEMENT.md), exigido pelo Documento 10 §138: confirma entendimento de stack, 20 fases, domain boundaries, security constraints e regras invioláveis, antes de qualquer implementação.
- Nenhum código implementado ainda. Próximo passo: usuário decide se inicia a Fase 01 — Project Foundation.

### 2026-08-20 — Fase 01 — Project Foundation (mesma data, sessão seguinte)
- Usuário pediu para seguir os documentos e iniciar a Fase 01.
- Monorepo criado por completo; backend FastAPI + frontend Next.js/shadcn scaffolded e validados (lint, typecheck, testes — ver seção 4.1 para o relatório completo).
- `docker-compose.yml` e Dockerfiles escritos e validados estaticamente, mas **não executados** (Docker indisponível no ambiente desta sessão) — ver pendência na seção 5.
- `git init` executado na raiz; nenhum commit criado ainda.
- Próximo passo: usuário valida `docker compose up` e decide sobre iniciar a Fase 02.

### 2026-08-20 — Repositório GitHub + Docker instalado e validado (mesma data, sessão seguinte)
- Usuário informou o repositório de destino: `https://github.com/contatoevertonoliveira/mcpVideos.git`. Remote `origin` adicionado localmente; nenhum commit/push feito ainda (aguardando pedido explícito).
- Usuário perguntou se instalávamos Docker ou seguíamos só com a `.venv`; perguntei de volta como queria rodar Postgres/Redis/MinIO e ele escolheu **instalar Docker Desktop**.
- Confirmei que esta sessão do Claude Code não tem privilégios administrativos no Windows e não pode instalar Docker Desktop sozinha (exigiria habilitar WSL2/Virtual Machine Platform via terminal elevado) — passei o passo a passo para o usuário instalar manualmente.
- Usuário instalou o Docker Desktop e rodou `wsl` + `docker compose version` — Docker Desktop já estava rodando no Windows, só faltava integração/PATH. Confirmei via PowerShell que o Docker Desktop estava instalado e o daemon respondendo (`docker ps` funcionando pelo caminho completo do executável).
- Rodei `docker compose up --build -d` de verdade: as 6 imagens buildaram, todos os containers subiram (`postgres`/`redis`/`minio` chegaram a `healthy`). Rodei `infra/scripts/smoke-test.sh`: os 4 checks passaram. Confirmei via `curl` que o frontend mostra "Conectado" (fetch real via rede Docker) e via logs que o worker Celery conectou ao Redis (`ready`) e a API criou o bucket MinIO no startup sem erro.
- **Fase 01 agora está 100% validada**, incluindo o critério de aceite que antes só tinha sido checado estaticamente.
- Usuário pediu para commitar e dar push. Commit único `b3041ae` ("feat(F01): project foundation", 107 arquivos) criado e enviado para `main` em `https://github.com/contatoevertonoliveira/mcpVideos.git`. Working tree limpo, branch `main` rastreando `origin/main`.
- Usuário pediu para não usar a porta 8000 no host (outro projeto já ocupa essa porta). Porta do host da `api` alterada para **8002** (`API_PORT:-8002` em `docker-compose.yml`, `.env.example`, `.env`, `infra/scripts/smoke-test.sh`, `README.md`); a porta **interna** do container continua 8000 (não afeta a comunicação `web` → `api` via rede Docker). Stack recriado (`docker compose up -d`) e revalidado com `smoke-test.sh` + `curl` no `localhost:3000` — tudo OK na nova porta. Commit `ed9b437` ("fix(F01): move API host port to 8002...") criado e enviado para `main`.
- Próximo passo: iniciar a Fase 02 — Core Domain & Database.

### 2026-08-20 — Fase 02 — Core Domain & Database (mesma data, sessão seguinte)
- Usuário pediu para seguir para a Fase 02.
- Criadas as 7 entidades (organizations, users, organization_members, channels, jobs, feature_flags, audit_logs), repositories (com `TenantScopedRepository` genérico exigindo `organization_id` sempre), schemas Pydantic, e os 5 services nomeados pelo Documento 10 (Organization/User/Channel/Job/Audit).
- Migration `a2160f18014a` gerada via `alembic revision --autogenerate`, aplicada na dev DB e validada com ciclo `upgrade → downgrade → upgrade` num banco limpo (`mcp_videos_test`).
- Criado banco `mcp_videos_test` no Postgres do Docker; testes de integração agora rodam contra Postgres real (25 testes, incluindo `test_tenant_isolation.py` — o critério de aceite obrigatório da fase, provando que Org A nunca acessa recurso de Org B).
- `ruff`/`mypy` limpos. Rebuild das imagens Docker (novas deps `bcrypt`/`email-validator`) e stack revalidado com `smoke-test.sh`.
- `.github/workflows/ci.yml` ganhou um serviço Postgres para rodar os testes de integração no CI também.
- Criado `docs/database.md` com ERD Mermaid (Documento 03 §133).
- Próximo passo: usuário decide se commita/envia a Fase 02 agora.

---

## 7. Como Continuar em um Novo Chat

1. Ler este arquivo (`docs/PROGRESS.md`) inteiro.
2. Ler `docs/ARCHITECTURE-ACKNOWLEDGEMENT.md`.
3. Ler todos os `docs/Documento NN - *.md` existentes (checklist na seção 2) — todos os 10 já estão presentes.
4. Conferir a seção 5 (pendências) e perguntar ao usuário se algo mudou.
5. Seguir o processo do Documento 02 ("Implementation Plan Before Coding") / Documento 10 (§33 "Claude Deve Planejar Antes de Codar") para iniciar ou continuar a fase corrente.
6. Ao final da sessão, atualizar as seções 1, 4, 5 e 6 deste arquivo — e a seção "Fase atual" sempre que uma fase avançar ou for concluída.
