# PROGRESS — Estado Atual do Projeto

> Este arquivo é o ponto de retomada entre sessões/chats. Sempre ler antes de continuar o trabalho. Sempre atualizar ao final de uma sessão relevante ou fase concluída.

Última atualização: 2026-08-20

---

## 1. Status Geral

**Fase atual:** ✅ **Fase 05 — Channel Importer implementada e validada de ponta a ponta**, inclusive testada manualmente no navegador (clicar "Sincronizar agora" → worker Celery real processa → vídeos aparecem). Ver seção 4.5 para o relatório completo. Fases 01-04 permanecem 100% validadas e commitadas (seções 4.1-4.4).

**Próximo passo:** commitar a Fase 05 (aguardando confirmação do usuário) e depois iniciar a **Fase 06 — Channel Intelligence**.

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
- Autenticação: sessões DB-backed com token opaco (hash SHA-256 persistido, nunca o token puro) — não JWT stateless, para permitir revogação real (Documento 09 §6). `AuthService` (`app/services/auth.py`) cobre register/login/logout/switch-organization.
- Autorização: `AuthorizationService` + `Permission` (`app/domain/permissions.py`) — mapeamento fixo role→permissão (owner/admin/editor/viewer), granularidade completa por recurso fica para o futuro (Documento 09 §17).
- Registro cria organização automaticamente e o usuário vira `owner` dela — sem fluxo de "entrar em organização existente" ainda.
- Rate limiting de login via Redis (`app/security/rate_limit.py`): 5 tentativas/e-mail em 15 min, depois HTTP 429.
- Frontend: sessão fica num cookie `httpOnly` (`mcp_session`), setado por Server Actions após chamar a API — nunca exposta ao JS do cliente. `proxy.ts` (renomeado de `middleware.ts` no Next 16) faz o redirect rápido de rota protegida; a validação real do token acontece sempre no servidor, olhando a API.
- `YouTubeGateway` (`app/gateways/youtube.py`) com duas implementações trocáveis via `Settings.youtube_fake_gateway`: `GoogleYouTubeGateway` (real, `httpx`) e `FakeYouTubeGateway` (determinística, sem rede — Documento 02 §71). Fica em `true` (fake) até o usuário configurar credenciais reais do Google Cloud.
- Tokens OAuth sempre criptografados em repouso (`app/security/encryption.py`, Fernet, chave em `TOKEN_ENCRYPTION_KEY`) — nunca devolvidos pela API.
- OAuth `state` assinado via HMAC (stdlib puro, `app/security/signed_state.py`) — sem storage server-side, carrega `organization_id`+`user_id`, expira em 10 min.
- Fluxo OAuth passa pelo frontend (Next.js Route Handlers `/oauth/youtube/{start,callback}`), nunca direto do navegador para a API — é o Next.js que tem o cookie de sessão do usuário e o repassa como Bearer token pra API.

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

### 4.3 Fase 03 — Relatório de Conclusão

**Implementado:**
- **Entidade nova:** `sessions` (modelo `UserSession` — nome escolhido para não colidir com `sqlalchemy.orm.Session`, usado em todo o resto do código). Campos exatamente conforme Documento 09 §6. Migration `373efef0edb5`.
- **`app/security/tokens.py`:** token opaco de alta entropia (`secrets.token_urlsafe(32)`); só o hash SHA-256 é persistido.
- **`app/services/auth.py` (`AuthService`):** `register` (cria user + org + membership OWNER + sessão + audit log), `login` (verifica senha, cria sessão, usa a primeira organização do usuário como contexto ativo, audit log), `logout` (revoga sessão, audit log), `get_valid_session` (rejeita token inválido/expirado/revogado), `switch_organization` (exige ser membro), `revoke_all_sessions` (pronto para um futuro "sair de todos os dispositivos").
- **`app/domain/permissions.py` + `app/services/authorization.py`:** `Permission` enum e `AuthorizationService.require_permission()` — mapeamento fixo role→permissões (Documento 09 §12-17).
- **`app/api/deps.py`:** dependencies FastAPI compostas — `get_bearer_token`, `get_current_session`, `get_current_user`, `get_current_organization_id`, `require_permission(permission)` (factory) — para qualquer endpoint futuro proteger com uma linha.
- **Endpoints** (`/api/v1/auth/*`): `POST /register`, `POST /login` (com rate limit), `POST /logout`, `GET /me`, `POST /organization` (trocar organização ativa).
- **Rate limiting:** `app/security/rate_limit.py`, Redis, 5 tentativas/e-mail/15min → 429.
- **Fix de correção encontrado via teste:** `get_db()` (`app/db/session.py`) não fazia `commit()` — funcionava por acidente nas Fases 01-02 porque nenhum endpoint escrevia dados ainda. Corrigido para `commit()` no sucesso / `rollback()` na exceção.
- **Fix de correção encontrado via teste:** `request.client.host` do FastAPI podia não ser um IP válido (ex.: `"testclient"` do TestClient, ou proxies mal configurados em produção) e quebrava o insert na coluna `INET`. Agora validado com `ipaddress.ip_address()` antes de gravar, com fallback `None`.
- **Frontend** (`apps/web`): `/login`, `/register` (Server Actions + `useActionState` para exibir erro), `/dashboard` (Authenticated Shell: usuário, organização ativa, lista de organizações, botão sair). Sessão num cookie `httpOnly` `mcp_session` setado só em Server Actions. `proxy.ts` (Next 16 renomeou `middleware.ts` → `proxy.ts`) redireciona `/dashboard` sem sessão → `/login`, e `/login`/`/register` com sessão → `/dashboard`.
- **Não implementado** (fora de escopo por definição): MFA (Documento 09 §8, opcional), convite de membros para organização existente, granularidade completa de permissões por recurso, "logout de todos os dispositivos" na UI (a capacidade existe no service).

**Validado nesta sessão:**
- 60 testes de backend (pytest) contra Postgres+Redis reais: `test_auth_service.py`, `test_authorization_service.py` (matriz completa role×permission), `test_rate_limit.py`, `test_auth_endpoints.py` (HTTP via TestClient), `test_deps.py` (wiring das dependencies do FastAPI). `ruff`/`mypy` limpos.
- Migration validada com ciclo `upgrade → downgrade → upgrade` num banco limpo.
- Stack Docker reconstruída (backend + frontend) e **testada manualmente no navegador de ponta a ponta**: cadastro → dashboard mostrando dados corretos → logout → tentativa de acessar `/dashboard` sem sessão (bloqueada, redirecionada) → login com senha errada (mensagem de erro exibida) → login correto → dashboard → acessar `/login` autenticado (redirecionado pro dashboard). Rate limit confirmado via `curl` (6ª tentativa errada = 429).
- Frontend: `eslint`, `tsc --noEmit`, `vitest`, `next build` — todos limpos; todas as rotas novas aparecem como dinâmicas (`ƒ`), como esperado (usam cookies/redirect).

**Pendências / Known Limitations:**
- MFA, convite de membros, permissões granulares por recurso — adiados por definição de escopo (ver Documento 09 §8/§17).
- `docs/database.md` atualizado com `sessions` no ERD e as decisões desta fase.

**Como validar:**
```bash
cd apps/api && pytest -v
cd apps/web && npm run lint && npm run typecheck && npm run test && npm run build
docker compose up -d --build
bash infra/scripts/smoke-test.sh
# depois, testar manualmente: http://localhost:3000/register
```

### 4.4 Fase 04 — Relatório de Conclusão

**Implementado:**
- **2 entidades novas** (Documento 03 §10-11, Documento 10 F04): `channel_connections` (modelo `ChannelConnection`) e `channel_sync_runs` (modelo `ChannelSyncRun`). Migration `59037a0445d8`.
- **`app/gateways/youtube.py` (`YouTubeGateway`)**: abstração com `get_authorization_url`, `exchange_code`, `refresh_access_token`, `get_channel_info`, `revoke_token`. Duas implementações: `GoogleYouTubeGateway` (real, via `httpx`, endpoints OAuth2 + YouTube Data API v3 do Google) e `FakeYouTubeGateway` (determinística — sempre resolve para o mesmo `external_channel_id` fixo, simulando reconectar a mesma conta). Selecionada por `Settings.youtube_fake_gateway` (`YOUTUBE_FAKE_GATEWAY`, default `true`).
- **`app/security/encryption.py`**: Fernet, chave via `TOKEN_ENCRYPTION_KEY` (nunca no banco). **`app/security/signed_state.py`**: state HMAC-assinado stateless (sem nova dependência).
- **`ChannelConnectionService`** (`app/services/channel_connection.py`): `start_connection` (valida membership, gera state assinado, retorna a `authorization_url`), `complete_connection` (verifica state, troca código por tokens, busca info do canal, faz upsert de `Channel`+`ChannelConnection`, grava `ChannelSyncRun` tipo `INITIAL`, audit log `channel.connected`), `disconnect` (revoga token best-effort no Google, marca `DISCONNECTED`/`DISABLED`, audit log `channel.disconnected`).
- **Endpoints** (`/api/v1/channels/*`): `GET` (listar, qualquer membro), `POST /connect` (requer `Permission.CHANNEL_MANAGE`), `POST /callback` (troca code+state por canal conectado), `POST /{id}/disconnect` (requer `Permission.CHANNEL_MANAGE`).
- **Frontend**: Route Handlers `GET /oauth/youtube/start` e `GET /oauth/youtube/callback` (BFF — o Next.js tem o cookie de sessão, a API nunca vê o browser diretamente nesse fluxo); página `/channels` (lista canais, badge de status, conectar/desconectar); link "Canais" adicionado ao dashboard; `proxy.ts` protegendo `/channels` também.
- **Não implementado** (fora de escopo por definição): importação de vídeos/playlists (`source_videos` etc. — Fase 05), refresh automático de token expirado (o método existe no gateway mas nada ainda o chama de forma agendada — chega com o Scheduler da Fase 18/Celery Beat), UI de credenciais Google reais (usuário decidiu seguir só com `FakeYouTubeGateway` por enquanto).

**Dois bugs reais encontrados e corrigidos:**
1. `TenantScopedRepository.add()`/`BaseRepository.add()` fazem `session.flush()` imediatamente. Em `complete_connection`, o código criava `Channel`/`ChannelConnection` "vazios" e só preenchia os campos `NOT NULL` *depois* de chamar `.add()` — flush prematuro quebrava com `IntegrityError`. Corrigido usando `session.add()` cru (sem flush) nesses dois pontos; documentado em `docs/database.md` como padrão a lembrar em fases futuras.
2. **Só apareceu no teste manual no navegador, não nos testes automatizados**: o `FakeYouTubeGateway.get_channel_info` gerava `external_channel_id` a partir de um hash do `access_token`, que muda a cada clique em "Conectar" (código OAuth aleatório novo). Resultado: reconectar sempre criava um canal duplicado em vez de atualizar o existente — o upsert por `external_channel_id` nunca disparava de verdade. Os testes de serviço não pegaram isso porque usavam o mesmo `code` literal nas duas chamadas. Corrigido tornando o `external_channel_id` do fake gateway uma constante fixa (simula reconectar a mesma conta Google de verdade). Ficou registrado como lição: **um "fake" tem que simular identidade estável entre chamadas, não só evitar rede.**

**Validado nesta sessão:**
- 82 testes de backend (pytest) contra Postgres+Redis reais, incluindo: round-trip de criptografia, `signed_state` (válido/adulterado/expirado/malformado), `FakeYouTubeGateway` determinístico, `ChannelConnectionService` completo (conectar, reconectar sem duplicar, desconectar, state de usuário errado rejeitado, state inválido rejeitado), endpoints HTTP (conectar, callback, listar, desconectar, viewer sem permissão → 403, nunca vaza token na resposta). `ruff`/`mypy` limpos.
- Migration validada com ciclo `upgrade → downgrade → upgrade`.
- Stack Docker reconstruída; **fluxo completo testado manualmente no navegador**: clicar "Conectar YouTube" → passa pelo loop OAuth fake → volta pra `/channels` com "Canal conectado com sucesso" → canal aparece com badge "Conectado" → desconectar → badge muda pra "Desconectado" e botão some → reconectar → confirmado que **não duplica** (foi isso que revelou o bug #2 acima).
- Frontend: `eslint`, `tsc --noEmit` (precisou rodar `next typegen` pra reconhecer a rota nova `/channels`), `vitest`, `next build` — todos limpos.

**Pendências / Known Limitations:**
- Credenciais reais do Google Cloud não configuradas — `GoogleYouTubeGateway` implementada mas nunca exercida de ponta a ponta contra o Google de verdade. Trocar `YOUTUBE_FAKE_GATEWAY=false` + preencher `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` quando o usuário tiver o projeto no Google Cloud Console.
- Refresh automático de token expirado: método pronto no gateway, sem chamador agendado ainda.
- `docs/database.md` atualizado com `channel_connections`/`channel_sync_runs` no ERD e as decisões desta fase.

**Como validar:**
```bash
cd apps/api && pytest -v
cd apps/web && npm run lint && npm run typecheck && npm run test && npm run build
docker compose up -d --build
bash infra/scripts/smoke-test.sh
# depois, testar manualmente: http://localhost:3000/channels (logado) → Conectar YouTube
```

### 4.5 Fase 05 — Relatório de Conclusão

**Implementado:**
- **3 entidades novas** (Documento 03 §12-14, Documento 10 F05): `source_videos`, `source_playlists`, `source_video_metrics`. Migration `93a5b4b81649`.
- **`YouTubeGateway` estendido** com `list_playlists`, `list_videos`, `get_video_metrics`. `GoogleYouTubeGateway` implementa a sequência real do YouTube Data API v3 (uploads playlist → playlistItems → videos.list em lotes de 50, paginação limitada a 5 páginas como cap de segurança do MVP); `FakeYouTubeGateway` devolve sempre os mesmos 5 vídeos determinísticos (2 Shorts + 3 vídeos longos) e 1 playlist.
- **`ChannelSyncService`** (`app/services/channel_sync.py`): implementa o fluxo do Documento 04 §18 (VALIDATE TOKEN → REFRESH IF REQUIRED → FETCH CHANNEL/CONTENT/METRICS → NORMALIZE → UPSERT → UPDATE LAST_SYNC → COMPLETE). Classifica `short`/`long_form`/`live`/`unknown` centralmente (heurística de duração ≤60s), faz upsert por `external_video_id`/`external_playlist_id` (idempotente — re-sync nunca duplica), grava métricas como histórico append-only.
- **Primeira task Celery real do projeto** (`app/tasks/channel_sync.py`, nome lógico `channel.sync.v1`): `run_channel_sync_task`, com retry controlado (`max_retries=3`, backoff exponencial+jitter) para erros de rede. `dispatch_channel_sync` cria um `Job` (entidade genérica da Fase 02, usada pela primeira vez) e enfileira a task.
- **Conectar canal dispara import automaticamente** (critério de aceite do Documento 10): `ChannelConnectionService.complete_connection` agora despacha um sync `INITIAL` (canal novo) ou `INCREMENTAL` (reconexão) ao final do fluxo OAuth.
- **Endpoints novos** em `/api/v1/channels/*`: `POST /{id}/sync` (trigger manual, `sync_type=MANUAL`, requer `Permission.CHANNEL_MANAGE`), `GET /{id}/videos`, `GET /{id}/sync-runs`.
- **Frontend**: página `/channels` ganhou contagem de vídeos importados, timestamp da última sincronização e botão "Sincronizar agora" por canal conectado.
- **Não implementado** (fora de escopo por definição): `watch_time_minutes`/`average_view_duration`/`subscribers_gained-lost`/`impressions`/`impressions_ctr` ficam `NULL` — exigem a YouTube Analytics API (escopo/fluxo próprios), que é explicitamente Fase 19 (Analytics & Learning Engine) no Documento 10, não Fase 05; sincronização agendada automática (Celery Beat) é Fase 18 (Scheduler & YouTube Publisher) — nesta fase o trigger é só conectar canal ou pedido manual.

**Bug real encontrado e corrigido (só apareceu testando manualmente contra a stack Docker real, não nos testes automatizados):**
`dispatch_channel_sync` cria a linha `Job` e chama `.delay()` dentro da mesma transação HTTP que ainda não tinha commitado. O worker Celery, rodando em processo/conexão separada, às vezes lia o Postgres *antes* do commit da API terminar e falhava com `NotFoundError: Job not found`. Reproduzido de forma determinística disparando `POST /channels/{id}/sync` contra a stack real. Corrigido com um retry curto e limitado (`_mark_running_with_retry`, até 5 tentativas / 1.5s) na primeira leitura do Job dentro da task — uma race condition clássica entre broker e commit de banco, resolvida de forma pragmática em vez de um outbox transacional completo (mais mecanismo do que esta fase precisa). Validado disparando 3 syncs concorrentes reais sem nenhuma falha.

**Validado nesta sessão:**
- 97 testes de backend (pytest) contra Postgres+Redis reais: gateway determinístico (playlists/vídeos/métricas estáveis entre chamadas), `ChannelSyncService` completo (import inicial, re-sync sem duplicar, refresh de token expirado, canal sem conexão rejeitado, canal desconhecido rejeitado, falha do gateway marca o run como `FAILED` e reverte o status da conexão), retry de visibilidade do Job, endpoints HTTP (trigger/videos/sync-runs, 404 para canal desconhecido, dispatch do Celery mockado via fixture autouse). `ruff`/`mypy` limpos.
- Migration validada com ciclo `upgrade → downgrade → upgrade` no banco de dev e aplicada ao banco de teste.
- Stack Docker reconstruída (api+worker); **fluxo completo validado contra infraestrutura real**: canal conectado via `curl` → worker Celery pegou a task automaticamente → 5 vídeos + 1 playlist importados corretamente classificados (2 shorts, 3 longos) → disparo manual de re-sync 3x concorrente sem duplicar nem falhar.
- Frontend: `eslint`, `tsc --noEmit` (com `next typegen` para a rota `/channels` atualizada), `vitest`, `next build` — todos limpos. **Validado clicando "Sincronizar agora" no navegador real**: contagem de vídeos foi de 0 para 5 e o timestamp de última sincronização atualizou, confirmando o clique → Server Action → API → Celery → Postgres → nova renderização.

**Pendências / Known Limitations:**
- Métricas de Analytics (watch time, impressões, CTR, subscribers ganhos/perdidos) aguardando Fase 19.
- Sincronização agendada automática aguardando Fase 18 (Scheduler).
- `docs/database.md` atualizado com `source_videos`/`source_playlists`/`source_video_metrics` no ERD e as decisões desta fase.

**Como validar:**
```bash
cd apps/api && pytest -v
cd apps/web && npm run lint && npm run typecheck && npm run test && npm run build
docker compose up -d --build
bash infra/scripts/smoke-test.sh
# depois, testar manualmente: conectar um canal em http://localhost:3000/channels
# e clicar em "Sincronizar agora" - a contagem de vídeos deve atualizar em poucos segundos
```

## 5. Pendências / Perguntas em Aberto

- Fases 01-04 commitadas e enviadas para `main` (`b3041ae`, `ed9b437`, `7b54b9c`, `4e5ecdc`, `7675039`). **Fase 05 implementada e validada nesta sessão, ainda não commitada** — aguardando confirmação do usuário.
- Documento 10 (seção 137) sugere organizar os documentos em `/docs/master/` com slugs (`01-product-brief.md`, etc.) — não feito; usuário optou implicitamente por manter o padrão atual `Documento NN - Titulo.md` ao pedir para seguir direto para a Fase 01.
- Ainda não definido: nome comercial do produto, provedor de IA/mídia real a integrar primeiro na Fase 13 (Documento 10 §71 pede benchmark atualizado antes de decidir — não assumir Higgsfield/Kie/fal.ai/WaveSpeed/Replicate como escolha final), moeda/plano de billing.
- Credenciais reais do Google Cloud (`GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`) ainda não configuradas — usuário optou por seguir só com `FakeYouTubeGateway` por enquanto (Fase 04). `GoogleYouTubeGateway` está implementada e pronta (incluindo os métodos de import da Fase 05), mas nunca exercitada contra o Google real.
- Direção visual: usuário pediu explicitamente uma estética moderna, típica de produto de IA para vídeo, quando chegarmos na fase de UX/UI (Documento 08) — a aparência atual é esqueleto funcional deliberado, não uma pendência de bug.

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

### 2026-08-20 — Fase 03 — Authentication & Security (mesma data, sessão seguinte)
- Usuário pediu para seguir para a Fase 03.
- Implementados: entidade `sessions` (`UserSession`), `AuthService` (register/login/logout/switch-organization/revoke-all), `AuthorizationService` + `Permission` (role→permissão fixo), dependencies FastAPI compostas (`app/api/deps.py`), endpoints `/api/v1/auth/*`, rate limiting de login via Redis.
- Dois bugs reais encontrados e corrigidos graças aos testes: `get_db()` não commitava (funcionava por acaso até agora, sem endpoints que escreviam); `request.client.host` podia não ser um IP válido e quebrava o insert na coluna `INET` da tabela `sessions`.
- Frontend: `/login`, `/register`, `/dashboard` (Server Actions, cookie `httpOnly`, `proxy.ts` para redirect de rota protegida).
- 60 testes de backend passando; `ruff`/`mypy`/`eslint`/`tsc`/`vitest`/`next build` limpos.
- Stack Docker reconstruída e o fluxo completo testado manualmente no navegador (registro → dashboard → logout → proteção de rota → erro de senha → login → redirect de página de auth já autenticado) e o rate limit confirmado via `curl`.
- Próximo passo: usuário decide se commita/envia a Fase 03 agora.

### 2026-08-20 — Fase 04 — YouTube Integration (mesma data, sessão seguinte)
- Usuário pediu para seguir para a Fase 04; ao ser perguntado sobre credenciais reais do Google Cloud, optou por seguir só com `FakeYouTubeGateway` por enquanto.
- Implementados: `channel_connections`/`channel_sync_runs`, `YouTubeGateway` (real + fake), criptografia de tokens (Fernet), state OAuth assinado (HMAC stateless), `ChannelConnectionService`, endpoints `/api/v1/channels/*`, fluxo OAuth via Route Handlers do Next.js (BFF), página `/channels`.
- Dois bugs reais corrigidos: flush prematuro do repositório quebrando `IntegrityError`; `FakeYouTubeGateway` não-determinístico causando duplicação de canal ao reconectar (só apareceu testando manualmente no navegador).
- 82 testes de backend passando; `ruff`/`mypy`/`eslint`/`tsc`/`vitest`/`next build` limpos. Fluxo completo validado manualmente no navegador.
- Commit `7675039` ("feat(F04): YouTube integration") criado e enviado para `main`.

### 2026-08-20 — Fase 05 — Channel Importer (mesma data, sessão seguinte)
- Usuário pediu para seguir para a Fase 05.
- Implementadas as 3 entidades (`source_videos`, `source_playlists`, `source_video_metrics`), extensão do `YouTubeGateway` (`list_playlists`/`list_videos`/`get_video_metrics`), `ChannelSyncService` (fluxo completo do Documento 04 §18, idempotente), e a primeira task Celery real do projeto (`app/tasks/channel_sync.py`).
- Conectar canal agora dispara import automaticamente (critério de aceite do Documento 10); endpoint manual `POST /channels/{id}/sync` e leitura via `GET /{id}/videos`/`GET /{id}/sync-runs` também implementados.
- **Bug real de concorrência encontrado e corrigido via teste manual contra a stack Docker real** (não pego pelos testes automatizados): race condition entre o commit da transação HTTP e o worker Celery pegando a task, causando `Job not found` intermitente. Corrigido com retry curto e limitado na primeira leitura do Job.
- 97 testes de backend passando; `ruff`/`mypy`/`eslint`/`tsc`/`vitest`/`next build` limpos. Fluxo completo validado com curl (incluindo 3 syncs concorrentes) e no navegador real (clicar "Sincronizar agora" → contagem de vídeos atualiza).
- Próximo passo: usuário decide se commita/envia a Fase 05 agora.

---

## 7. Como Continuar em um Novo Chat

1. Ler este arquivo (`docs/PROGRESS.md`) inteiro.
2. Ler `docs/ARCHITECTURE-ACKNOWLEDGEMENT.md`.
3. Ler todos os `docs/Documento NN - *.md` existentes (checklist na seção 2) — todos os 10 já estão presentes.
4. Conferir a seção 5 (pendências) e perguntar ao usuário se algo mudou.
5. Seguir o processo do Documento 02 ("Implementation Plan Before Coding") / Documento 10 (§33 "Claude Deve Planejar Antes de Codar") para iniciar ou continuar a fase corrente.
6. Ao final da sessão, atualizar as seções 1, 4, 5 e 6 deste arquivo — e a seção "Fase atual" sempre que uma fase avançar ou for concluída.
