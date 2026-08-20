# Documento 10 — Plano Definitivo de Implementação, Dependências e Critérios de Aceite

## 1. Objetivo

Este documento encerra a documentação mestre do projeto.

Ele transforma os Documentos 01–09 em um plano executivo de construção para o Claude Code.

A partir deste ponto, o projeto deverá ser implementado em 20 fases sequenciais, cada uma com:

- objetivo claro;
- escopo fechado;
- dependências;
- entregáveis;
- critérios de aceite;
- testes;
- documentação;
- regras de não implementação antecipada;
- Definition of Done.

A regra principal é:

**nenhuma fase deverá tentar implementar o produto inteiro; cada fase deverá expandir uma base estável e funcional.**

---

# 2. Documentos Mestres de Referência

Antes de iniciar qualquer fase, o Claude Code deverá considerar como fonte de verdade:

```text id="doc10_refs"
Documento 01
Briefing Mestre

Documento 02
Diretrizes Arquiteturais

Documento 03
Modelo de Dados

Documento 04
Workflows e Orquestração

Documento 05
Agentes de IA

Documento 06
MCPs, Providers e Media Router

Documento 07
Channel Intelligence e Growth

Documento 08
UX/UI e Control Center

Documento 09
Segurança, Billing e Governança
```

Este Documento 10 define:

```text id="doc10_exec"
QUANDO
e
EM QUAL ORDEM
```

cada parte será construída.

---

# 3. Estratégia Geral de Implementação

O desenvolvimento deverá ocorrer em cinco macroetapas:

```text id="macro_etapas"
A — Foundation
B — Content Intelligence
C — Content Factory
D — Quality & Publication
E — Optimization & SaaS
```

---

# 4. As 20 Fases

```text id="20_fases"
01 Project Foundation
02 Core Domain & Database
03 Authentication & Security
04 YouTube Integration
05 Channel Importer
06 Channel Intelligence
07 Channel DNA
08 Strategy Engine
09 Ideas & Opportunity Engine
10 Content Calendar
11 Workflow & Agent Engine
12 Script & Storyboard Engine
13 MCP / AI Media Gateway
14 Model Router & Cost Controller
15 Media Production Pipeline
16 Quality Gate
17 SEO & Thumbnail Engine
18 Scheduler & YouTube Publisher
19 Analytics & Learning Engine
20 Autopilot, Billing & Control Center
```

---

# 5. Regra de Dependência

Nenhuma fase deverá assumir como pronta uma dependência ainda não implementada.

Exemplo:

```text id="dep_example"
Fase 16 Quality Gate
```

depende de:

```text id="dep_example2"
Fase 11 Workflow Engine
Fase 12 Content Project
Fase 15 Media Assets
```

Logo não deverá ser implementada antes.

---

# 6. Regra de Continuidade

Cada fase deverá deixar o sistema:

```text id="continuity"
executável
testável
documentado
migrável
```

Mesmo que várias features ainda sejam incompletas.

---

# 7. FASE 01 — Project Foundation

## Objetivo

Criar a fundação física e operacional do projeto.

---

## Escopo

Criar:

```text id="f01_scope"
monorepo
frontend
backend
Docker
Docker Compose
PostgreSQL
Redis
Celery
storage local/S3 abstraction
environment configuration
logging
health checks
test foundation
lint/typecheck
CI foundation
```

---

## Frontend

Criar:

```text id="f01_frontend"
Next.js
TypeScript
Tailwind
shadcn/ui
```

Estrutura conforme Documento 02.

---

## Backend

Criar:

```text id="f01_backend"
FastAPI
SQLAlchemy
Alembic
Pydantic
Celery
Redis client
```

---

## Infraestrutura Local

`docker compose up` deverá iniciar:

```text id="f01_docker"
web
api
worker
postgres
redis
minio ou storage equivalente local
```

---

## Health

Implementar:

```text id="f01_health"
/health
/health/db
/health/redis
```

---

## Não Implementar

Ainda não criar:

```text id="f01_not"
YouTube OAuth
agentes
Channel DNA
media generation
billing
autopilot
```

---

## Critério de Aceite

```text id="f01_acceptance"
docker compose up
```

sobe toda a stack.

Frontend consegue falar com backend.

Backend consegue:

```text id="f01_acceptance2"
conectar PostgreSQL
conectar Redis
executar migration
executar Celery task fake
```

---

## Testes

```text id="f01_tests"
health
database connection
redis
basic frontend build
backend tests
```

---

# 8. FASE 02 — Core Domain & Database

## Objetivo

Criar a fundação SaaS multi-tenant.

---

## Entidades

Criar inicialmente:

```text id="f02_entities"
organizations
users
organization_members
channels
jobs
audit_logs
feature_flags
```

---

## Implementar

```text id="f02_impl"
models
schemas
repositories
services
migrations
UUIDs
timestamps
soft delete where needed
tenant isolation patterns
```

---

## Services

Criar:

```text id="f02_services"
OrganizationService
UserService
ChannelService
JobService
AuditService
```

---

## Não Implementar

Não implementar ainda conexão externa de canal.

---

## Critério de Aceite

Dever ser possível:

```text id="f02_acceptance"
create organization
create user
associate user
create placeholder channel
retrieve tenant-scoped resources
```

Teste deve provar que:

```text id="f02_isolation"
Org A não acessa recurso da Org B
```

---

# 9. FASE 03 — Authentication & Security

## Objetivo

Implementar autenticação, sessão e autorização.

---

## Escopo

```text id="f03_scope"
registration
login
logout
session/token management
password hashing
roles
permissions
organization context
audit events
rate limiting foundation
```

---

## Roles

```text id="f03_roles"
owner
admin
editor
viewer
```

---

## UI

Criar:

```text id="f03_ui"
Login
Register
Authenticated Shell
Organization context
```

---

## Critério de Aceite

```text id="f03_acceptance"
usuário cria conta
faz login
entra na organização
rotas privadas protegidas
permissions enforced server-side
```

---

# 10. FASE 04 — YouTube Integration

## Objetivo

Permitir que o usuário conecte um canal real.

---

## Implementar

```text id="f04_scope"
Google OAuth
YouTubeGateway
channel_connections
secure encrypted token storage
token refresh
connection status
disconnect
reauthorization
```

---

## UI

Fluxo:

```text id="f04_ui"
Dashboard vazio
↓
Conectar YouTube
↓
OAuth
↓
Canal conectado
```

---

## Segurança

OAuth tokens nunca aparecem:

```text id="f04_security"
frontend
logs
agent context
```

---

## Critério de Aceite

Usuário consegue:

```text id="f04_acceptance"
conectar
visualizar canal
desconectar
reconectar
```

---

# 11. FASE 05 — Channel Importer

## Objetivo

Importar o histórico do canal.

---

## Criar

```text id="f05_entities"
channel_sync_runs
source_videos
source_playlists
source_video_metrics
```

---

## Workflow

Implementar:

```text id="f05_workflow"
channel.sync.v1
```

---

## Sync Types

```text id="f05_types"
initial
incremental
full
manual
```

---

## Processo

```text id="f05_process"
channel
↓
playlists
↓
videos
↓
metadata
↓
available metrics
↓
normalize
↓
persist
```

---

## Critério de Aceite

Conectar canal dispara import.

Sistema identifica:

```text id="f05_acceptance"
vídeos
Shorts
datas
títulos
descrições
durações
playlists
métricas disponíveis
```

sem duplicação em re-sync.

---

# 12. FASE 06 — Channel Intelligence

## Objetivo

Fazer a plataforma começar a “entender” o canal.

---

## Implementar

```text id="f06_agents"
Channel Analyst
Audience Analyst
```

---

## Criar

```text id="f06_entities"
channel_profiles
audience_profiles
```

---

## Infraestrutura Inicial de IA

Pode criar versão mínima de:

```text id="f06_llm"
LLMGateway
AgentRuntime foundation
```

somente o necessário.

A arquitetura completa chega na Fase 11.

---

## Output

Identificar:

```text id="f06_output"
nicho
subnicho
idioma
formatos
público
padrões
frequência
principais temas
```

---

## UI

Tela:

```text id="f06_ui"
Analisando canal...
↓
Diagnóstico encontrado
```

---

## Critério de Aceite

Canal importado produz:

```text id="f06_acceptance"
Channel Profile
Audience Profile
confidence
evidence
```

---

# 13. FASE 07 — Channel DNA

## Objetivo

Criar a memória editorial estruturada e versionada.

---

## Criar

```text id="f07_entities"
channel_dna_versions
brand_profiles
```

---

## DNA

Estruturar:

```text id="f07_dna"
classification
audience
formats
content pillars
patterns
brand
restrictions
publishing behavior
performance
```

---

## Versioning

Implementar:

```text id="f07_versions"
draft
active
superseded
```

---

## UI

Mostrar DNA traduzido em cards.

Nunca JSON cru.

---

## Critério de Aceite

Cada canal possui:

```text id="f07_acceptance"
1 active DNA version
version history
confidence
evidence
```

---

# 14. FASE 08 — Strategy Engine

## Objetivo

Transformar Channel DNA em estratégia editorial.

---

## Criar

```text id="f08_entities"
content_strategies
content_pillars
strategy_rules
```

---

## Agent

```text id="f08_agent"
Strategy Agent
```

---

## Strategy Output

```text id="f08_output"
objectives
content mix
Shorts ratio
long-form ratio
frequency
experimental ratio
content pillars
```

---

## Approval

No modo inicial:

```text id="f08_assisted"
user approval required
```

---

## Critério de Aceite

Usuário visualiza:

```text id="f08_acceptance"
estratégia atual
recomendação
pilares
frequência
```

e pode aprovar.

---

# 15. FASE 09 — Ideas & Opportunity Engine

## Objetivo

Criar sistema inteligente de sugestões.

---

## Criar

```text id="f09_entities"
content_ideas
content_opportunities
opportunity_scores
content_clusters
idea_relationships
```

---

## Agents

```text id="f09_agents"
Idea Agent
Opportunity Evaluator
```

---

## Implementar

```text id="f09_impl"
generation
deduplication
scoring
ranking
confidence
evidence
```

---

## Opportunity Score

Cálculo final deve ocorrer em código.

---

## UI

Tela:

```text id="f09_ui"
Ideas
```

com:

```text id="f09_cards"
score
title
summary
format
reason
```

---

## Critério de Aceite

Sistema gera ideias coerentes com o canal e consegue rejeitar tendência irrelevante.

---

# 16. FASE 10 — Content Calendar

## Objetivo

Transformar oportunidades em plano editorial.

---

## Criar

```text id="f10_entities"
calendar_items
publishing_slots
calendar_recommendations
```

---

## Agent

```text id="f10_agent"
Calendar Planner
```

---

## Considerar

```text id="f10_consider"
pillar balance
format balance
topic saturation
series
frequency
slots
```

---

## UI

Criar:

```text id="f10_ui"
Week
Month
List
```

---

## Critério de Aceite

Usuário consegue:

```text id="f10_acceptance"
ver calendário sugerido
aprovar item
rejeitar
mover
```

---

# 17. Marco de Produto após Fase 10

Após Fase 10 a plataforma já deverá entregar valor sem produzir vídeos.

Fluxo:

```text id="milestone10"
Conectar canal
↓
Analisar
↓
Entender
↓
Criar estratégia
↓
Gerar ideias
↓
Criar calendário
```

Este será o primeiro grande milestone funcional.

---

# 18. FASE 11 — Workflow & Agent Engine

## Objetivo

Construir a infraestrutura completa de agentes e workflows.

---

## Criar

```text id="f11_entities"
agents
agent_versions
agent_prompts
agent_runs

workflow_definitions
workflow_versions
workflow_runs
workflow_steps
workflow_events
```

---

## Implementar

```text id="f11_impl"
AgentRuntime
AgentContextBuilder
structured outputs
prompt registry
workflow engine
step execution
retry
resume
pause
human review
events
correlation IDs
```

---

## Migrar

Agentes anteriores devem passar para essa infraestrutura.

---

## Critério de Aceite

Deve ser possível:

```text id="f11_acceptance"
execute versioned agent
validate JSON
record run
execute workflow
fail step
retry
resume
trace operation
```

---

# 19. FASE 12 — Script & Storyboard Engine

## Objetivo

Transformar pauta em projeto audiovisual estruturado.

---

## Criar

```text id="f12_entities"
content_projects
project_versions
scripts
script_versions
storyboards
scenes
scene_states
scene_transitions
characters
character_references
character_voices
locations
brand_assets
```

---

## Agents

```text id="f12_agents"
Research Agent
Hook Agent
Script Writer
Script Critic
Storyboard Director
Scene Planner
```

---

## Workflows

```text id="f12_workflows"
short.production.v1
longform.production.v1
```

até etapa de planejamento de mídia.

---

## UI

Content Project Detail:

```text id="f12_ui"
overview
script
storyboard
scenes
history
```

---

## Critério de Aceite

Ideia aprovada consegue virar:

```text id="f12_acceptance"
Project
↓
Script
↓
Storyboard
↓
Scenes
```

---

# 20. FASE 13 — MCP / AI Media Gateway

## Objetivo

Conectar geração multimídia real.

---

## Criar

```text id="f13_entities"
providers
provider_connections
ai_models
model_capabilities
provider_model_prices
provider_health_snapshots
generations
generation_attempts
```

---

## Implementar

```text id="f13_impl"
MediaGateway
Provider Adapter interface
MCP adapter foundation
FakeMediaProvider
one real provider
async job tracking
storage result
```

---

## Agents

```text id="f13_agents"
Media Director
Prompt Engineer
```

---

## Critério de Aceite

Uma cena consegue solicitar mídia e receber asset real.

---

# 21. FASE 14 — Model Router & Cost Controller

## Objetivo

Transformar múltiplos providers em uma infraestrutura inteligente.

---

## Criar

```text id="f14_entities"
cost_events
usage_events
budgets
budget reservations if required
```

---

## Implementar

```text id="f14_impl"
ModelRouter
PricingNormalizer
BudgetController
Provider health
Routing score
Fallback
Cost tracking
```

---

## Providers

Adicionar pelo menos:

```text id="f14_providers"
primary real provider
fallback real provider
fake provider
```

---

## Critério de Aceite

Simulação:

```text id="f14_case"
Provider A unavailable
```

deve resultar:

```text id="f14_case2"
Provider B selected
cost tracked
workflow continues
```

---

# 22. FASE 15 — Media Production Pipeline

## Objetivo

Produzir conteúdo audiovisual completo.

---

## Criar

```text id="f15_entities"
media_assets
asset_relationships
project_assets
```

---

## Implementar

```text id="f15_impl"
image generation
video generation
image-to-video
voice
audio
media storage
FFmpeg assembly
subtitles
final render
```

---

## Agents

```text id="f15_agents"
Voice Director
Audio Director
Editor Agent
```

---

## Critério de Aceite

Um Short simples consegue ir de:

```text id="f15_acceptance"
script
↓
scenes
↓
assets
↓
voice
↓
assembly
↓
rendered MP4
```

---

# 23. FASE 16 — Quality Gate

## Objetivo

Impedir que conteúdo defeituoso avance automaticamente.

---

## Criar

```text id="f16_entities"
quality_reviews
quality_scores
quality_issues
repair_actions
```

---

## Agents

```text id="f16_agents"
Script QA
Visual QA
Audio QA
Continuity QA
Brand Guardian
Audience QA
Safety QA
Technical QA
Retention QA
Final QA
```

---

## Implementar

```text id="f16_impl"
score policies
critical failures
repair
regenerate
human review
retry limits
```

---

## Critério de Aceite

Teste deve simular:

```text id="f16_case"
wrong character
```

e impedir publicação/avanço.

Também:

```text id="f16_case2"
audio-only problem
```

deve gerar repair direcionado.

---

# 24. FASE 17 — SEO & Thumbnail Engine

## Objetivo

Preparar pacote final de publicação.

---

## Criar

```text id="f17_entities"
seo_packages
title_candidates
thumbnail_candidates
metadata_versions
```

---

## Agents

```text id="f17_agents"
SEO Agent
Title Agent
Thumbnail Strategist
Thumbnail Evaluator
```

---

## Implementar

```text id="f17_impl"
titles
description
keywords
hashtags
chapters
thumbnail concepts
thumbnail generation
title-thumbnail pair score
```

---

## UI

Usuário poderá comparar candidatos.

---

## Critério de Aceite

Projeto pronto possui:

```text id="f17_acceptance"
video
title
description
thumbnail
metadata
quality approval
```

---

# 25. FASE 18 — Scheduler & YouTube Publisher

## Objetivo

Publicar conteúdo de maneira segura e agendada.

---

## Criar

```text id="f18_entities"
publications
publication_schedules
publication_attempts
publication_events
idempotency_keys
```

---

## Workflows

```text id="f18_workflows"
publication.readiness.v1
publication.schedule.v1
youtube.publish.v1
```

---

## Implementar

```text id="f18_impl"
scheduler
locks
idempotency
upload
metadata
thumbnail
schedule
retry
reconciliation
```

---

## Critério de Aceite

Projeto aprovado consegue:

```text id="f18_acceptance"
schedule
↓
upload once
↓
set metadata
↓
set thumbnail
↓
persist external video ID
```

sem duplicação mesmo após retry.

---

# 26. Marco de Produto após Fase 18

Nesse ponto já existe um produto operacional completo:

```text id="milestone18"
Conecta canal
↓
Analisa
↓
Planeja
↓
Produz
↓
Avalia
↓
Prepara SEO
↓
Agenda
↓
Publica
```

Ainda faltará otimização contínua e SaaS completo.

---

# 27. FASE 19 — Analytics & Learning Engine

## Objetivo

Fechar o feedback loop.

---

## Criar

```text id="f19_entities"
analytics_snapshots
video_metric_snapshots
channel_metric_snapshots
performance_baselines
performance_insights
learning_events
learned_rules
learning_evidence
```

---

## Agents

```text id="f19_agents"
Performance Analyst
Learning Analyst
Growth Strategist
```

---

## Workflows

```text id="f19_workflows"
analytics.collect.v1
performance.evaluate.v1
learning.evaluate.v1
channel.intelligence.refresh.v1
```

---

## Implementar

```text id="f19_impl"
snapshots
baselines
performance index
breakout detection
underperformance detection
learning candidates
confidence
sample size
effect size
validated rules
```

---

## Critério de Aceite

Conteúdo publicado gera:

```text id="f19_acceptance"
analytics
↓
baseline comparison
↓
insight
↓
learning candidate
```

e regras validadas podem influenciar novas ideias.

---

# 28. FASE 20 — Autopilot, Billing & Control Center

## Objetivo

Transformar a aplicação em SaaS autônomo operacional.

---

## Autopilot

Implementar:

```text id="f20_autopilot"
Manual
Assisted
Semi-Auto
Autopilot
```

---

## Policies

```text id="f20_policies"
publication limits
cost limits
quality minimum
format limits
time windows
human escalation
```

---

## Billing

Criar/completar:

```text id="f20_billing"
plans
subscriptions
entitlements
usage aggregation
billing gateway
billing reconciliation
```

---

## Control Center

Implementar:

```text id="f20_control"
overview
organizations
workflows
jobs
agents
providers
models
costs
quality
publications
errors
feature flags
audit
```

---

## Kill Switches

Obrigatórios:

```text id="f20_kill"
global auto-publish off
provider disable
organization pause
channel pause
```

---

## Critério de Aceite

Um canal em Autopilot consegue:

```text id="f20_acceptance"
detect content need
↓
generate idea
↓
score
↓
schedule
↓
produce
↓
QA
↓
publish
↓
measure
↓
learn
```

sem intervenção, dentro das policies.

---

# 29. Dependências entre Fases

Mapa resumido:

```text id="dependencies_map"
01
↓
02
↓
03
↓
04
↓
05
↓
06
↓
07
↓
08
↓
09
↓
10
↓
11
↓
12
↓
13
↓
14
↓
15
↓
16
↓
17
↓
18
↓
19
↓
20
```

Essa é a ordem principal.

---

# 30. Dependências Funcionais

Algumas dependências específicas:

```text id="functional_deps"
Channel DNA
requires Channel Intelligence

Ideas
requires Strategy

Calendar
requires Opportunities

Production
requires Projects + Workflows

Media Router
requires Provider Registry

Quality
requires Media Assets

Publishing
requires Quality + SEO

Learning
requires Published Analytics

Autopilot
requires almost all previous layers
```

---

# 31. Não Paralelizar Prematuramente

É possível paralelizar frontend/backend dentro da mesma fase.

Evitar trabalhar simultaneamente em:

```text id="bad_parallel"
Fase 04
e
Fase 17
```

sem a base intermediária.

---

# 32. Prompt de Implementação por Fase

Após estes 10 documentos, cada fase deverá receber seu próprio prompt executivo.

Estrutura padrão:

```text id="phase_prompt"
PHASE XX

Objective
Dependencies
Files to inspect
Required changes
Entities
Endpoints
Services
UI
Workers
Tests
Documentation
Out of scope
Acceptance criteria
```

---

# 33. Claude Deve Planejar Antes de Codar

Antes de modificar arquivos:

```text id="claude_plan"
1. Read master docs
2. Inspect repository
3. State current phase
4. List files to create/change
5. Identify migrations
6. Identify risks
7. Implement
8. Run tests
9. Fix
10. Report
```

---

# 34. Scope Lock

Durante uma fase:

```text id="scope_lock"
do not implement unrelated future features
```

Se detectar dependência futura:

```text id="future_todo"
create interface/TODO reference
```

somente quando necessário.

---

# 35. Definition of Done Global

Toda fase deve concluir:

```text id="global_dod"
implementation complete
tests passing
lint passing
typecheck passing
build passing
migrations working
Docker working
docs updated
no exposed secrets
no tenant isolation regression
existing tests passing
```

---

# 36. Migration Validation

Para fases com banco:

```text id="migration_validation"
fresh DB migration
existing DB upgrade
rollback when safe/required
```

---

# 37. API Validation

Endpoints devem possuir:

```text id="api_validation"
auth
authorization
tenant scope
input schema
response schema
errors
OpenAPI documentation
```

---

# 38. Async Validation

Processos assíncronos devem possuir:

```text id="async_validation"
job record
status
correlation ID
timeout
retry
failure path
```

---

# 39. External Integration Validation

Toda integração deve possuir:

```text id="external_validation"
mock
timeout
normalized error
credentials protection
rate limit awareness
reconciliation strategy
```

---

# 40. AI Feature Validation

Todo agente:

```text id="ai_validation"
registered
versioned
prompt versioned
structured input
structured output
validation
cost tracking
run tracking
tests
```

---

# 41. Quality Validation

Toda feature que produz conteúdo externo deverá definir:

```text id="quality_validation"
what means pass
what means fail
repair strategy
maximum retries
```

---

# 42. Security Validation

Antes de concluir qualquer fase:

```text id="security_validation"
tenant access tested
permissions tested
sensitive logging checked
credentials checked
```

---

# 43. UX Validation

Toda tela deve possuir:

```text id="ux_validation"
loading
empty
success
error
permission
mobile basics
```

---

# 44. Performance Validation

Evitar:

```text id="perf_avoid"
N+1 queries
unpaginated huge endpoints
blocking long operations
large media through API memory
```

---

# 45. Cost Validation

A partir da Fase 13:

```text id="cost_validation"
all paid operations attributable
```

---

# 46. Audit Validation

Ações críticas deverão possuir AuditLog.

---

# 47. Testing Pyramid

Prioridade:

```text id="testing_pyramid"
many unit tests
↓
integration tests
↓
selected E2E
```

---

# 48. Unit Tests

Focar em:

```text id="unit_focus"
scores
policies
state machines
router
budget
services
```

---

# 49. Integration Tests

Focar em:

```text id="integration_focus"
DB
repositories
API
workers
workflows
```

---

# 50. E2E Tests

Fluxos principais:

```text id="e2e_main"
login
connect channel
onboarding
ideas
calendar
content production
review
schedule
publish
autopilot pause
```

crescendo conforme fases.

---

# 51. Fake Providers

Nunca depender de custos reais para suite comum.

---

# 52. Test Environments

```text id="test_envs"
local
CI
staging
production
```

---

# 53. Staging

Antes de publicação real automática, manter ambiente staging com canais de teste quando possível.

---

# 54. Production Flags

Features perigosas começam:

```text id="prod_flags"
OFF
```

Exemplos:

```text id="danger_flags"
AUTO_PUBLISH
AUTOPILOT
MULTI_PROVIDER_ROUTING
```

---

# 55. Rollout Progressivo

Exemplo:

```text id="rollout"
internal
↓
test users
↓
limited beta
↓
general
```

---

# 56. Auto-Publish Rollout

Especialmente conservador.

---

# 57. Architecture Decision Records

Decisões importantes:

```text id="adr_rule"
/docs/adr/
```

---

# 58. ADR Triggers

Criar ADR quando:

```text id="adr_triggers"
changing DB architecture
changing auth strategy
changing orchestration
changing provider abstraction
changing tenancy model
```

---

# 59. No Silent Architecture Changes

Claude não deverá substituir componente central sem documentar.

---

# 60. Documentation Update Rule

Cada fase deverá atualizar documentos correspondentes.

Exemplo F13:

```text id="docs_f13"
/docs/providers.md
/docs/database.md
/docs/workflows.md
```

---

# 61. Phase Completion Report

Ao terminar cada fase, Claude deverá entregar:

```text id="completion_report"
Phase
Status

Implemented
Files Created
Files Modified
Migrations
Endpoints
Workers
UI
Tests
Documentation
Architecture Decisions
Known Limitations
Deferred Items
How to Validate
```

---

# 62. Known Limitations

Devem ser explícitas.

Não fingir feature completa.

---

# 63. Technical Debt

Se inevitável:

```text id="tech_debt"
record clearly
assign future phase
```

---

# 64. No Untracked TODO

TODO deve apontar para:

```text id="todo_format"
TODO(F14)
```

ou issue equivalente.

---

# 65. Phase Gate

Não iniciar próxima fase se:

```text id="phase_gate_fail"
tests failing
migrations broken
Docker broken
critical security bug
```

---

# 66. Acceptance Sign-Off

Idealmente cada fase será validada por:

```text id="acceptance_signoff"
automated tests
+
manual smoke test
```

---

# 67. Smoke Test

Claude deverá fornecer comandos exatos.

Exemplo:

```text id="smoke_example"
docker compose up
pytest
npm test
curl /health
```

conforme fase.

---

# 68. Project Milestones

## Milestone A — Foundation

Após Fase 04:

```text id="milestone_a"
conta
organização
login
canal conectado
```

---

## Milestone B — Intelligence

Após Fase 10:

```text id="milestone_b"
canal entendido
strategy
ideas
calendar
```

---

## Milestone C — Factory

Após Fase 15:

```text id="milestone_c"
roteiro
storyboard
media
render
```

---

## Milestone D — Autonomous Publishing

Após Fase 18:

```text id="milestone_d"
QA
SEO
schedule
publish
```

---

## Milestone E — Closed Loop SaaS

Após Fase 20:

```text id="milestone_e"
analytics
learning
autopilot
billing
control center
```

---

# 69. MVP Comercial Possível

Uma primeira versão comercial controlada pode existir antes da Fase 20.

Ponto sugerido:

```text id="commercial_mvp"
Fase 18
```

com:

```text id="commercial_mvp_mode"
Assisted / Semi-Auto
```

Sem Autopilot irrestrito.

---

# 70. Early Internal MVP

Após Fase 10 já existe:

```text id="internal_mvp"
Channel Intelligence SaaS
```

útil para validar:

```text id="internal_mvp_validate"
onboarding
recommendations
strategy
calendar
```

antes dos custos pesados de mídia.

---

# 71. Fase 13 — Provider Decision

Antes de integrar provider real, realizar benchmark atualizado.

Não assumir que provider escolhido na documentação continuará ideal.

---

# 72. Provider Benchmark

Comparar:

```text id="provider_benchmark"
capabilities
pricing
quality
API/MCP stability
terms
latency
rate limits
```

---

# 73. Provider Configurability

A escolha inicial não deve virar lock-in.

---

# 74. AI Model Decision

Mesmo princípio.

---

# 75. Security Review Points

Revisões específicas:

```text id="security_review_points"
after F03
after F04
after F13
before F18
before F20
```

---

# 76. Cost Review Points

```text id="cost_review_points"
F13
F14
F15
F20
```

---

# 77. UX Review Points

```text id="ux_review_points"
F04
F07
F10
F12
F18
F20
```

---

# 78. Database Review Points

```text id="db_review_points"
F02
F07
F11
F13
F18
F20
```

---

# 79. Load Testing

Não necessário inicialmente.

Adicionar antes de escala comercial significativa.

---

# 80. Load Test Areas

```text id="load_test_areas"
API
jobs
scheduler
provider routing
publication
analytics
```

---

# 81. Failure Injection

A partir da Fase 14 testar:

```text id="failure_injection"
provider timeout
Redis restart
worker crash
publication timeout
```

---

# 82. Recovery Testing

Sistema deve continuar ou reconciliar.

---

# 83. Data Integrity

Nunca aceitar consistência eventual em:

```text id="critical_integrity"
billing
budget
publication idempotency
tenant access
```

sem design explícito.

---

# 84. Source of Truth Rules

```text id="truth_rules"
PostgreSQL
→ business state

Redis
→ cache/locks/queue support

Object Storage
→ media

External platforms
→ external publication state
```

---

# 85. Reconciliation Rule

Quando nosso banco e provider discordarem:

```text id="reconcile_rule"
reconcile
```

nunca assumir silenciosamente.

---

# 86. Code Ownership Boundaries

Mesmo com Claude construindo tudo, manter módulos claramente separados.

---

# 87. No God Service

Evitar:

```text id="god_service"
ContentService
```

com milhares de linhas fazendo tudo.

---

# 88. No God Workflow

Mesmo princípio.

---

# 89. No God Agent

Especialização conforme Documento 05.

---

# 90. No Frontend Business Logic

Frontend apresenta e envia comandos.

Backend valida regras.

---

# 91. No LLM Business Logic

LLM recomenda.

Código aplica policies.

---

# 92. No Provider Business Logic

Adapters integram.

Services decidem.

---

# 93. Code Review Rule

Antes de concluir fase, Claude deverá revisar:

```text id="code_review_rule"
duplication
security
layer violations
future-phase leakage
tests
```

---

# 94. Layer Violation Example

Proibido:

```text id="bad_layer"
API route
↓
Fal.ai SDK
```

Correto:

```text id="good_layer"
API
↓
Service
↓
MediaGateway
↓
Adapter
```

---

# 95. Naming Consistency

Seguir Documento 02.

---

# 96. Phase Numbering

Todos os documentos, TODOs e relatórios devem manter referência:

```text id="phase_numbering"
F01
F02
...
F20
```

---

# 97. Git Commits

Preferir:

```text id="git_commit_example"
feat(F04): add YouTube OAuth flow
```

---

# 98. Branches

Sugestão:

```text id="branches"
phase/f01-foundation
phase/f02-core-domain
```

quando workflow de Git permitir.

---

# 99. Versioning da Aplicação

Pode iniciar:

```text id="app_version"
0.x
```

até produto atingir maturidade.

---

# 100. API Version

```text id="api_version"
/api/v1
```

desde início.

---

# 101. Database Naming

Consistente em snake_case.

---

# 102. User-Facing Terminology

Evitar termos técnicos.

Internamente:

```text id="internal_terms"
WorkflowRun
AgentRun
GenerationAttempt
```

Externamente:

```text id="external_terms"
Produzindo
Revisando
Pronto
```

---

# 103. Localization

UI preparada para i18n.

---

# 104. Default Locale

Inicial:

```text id="default_locale"
pt-BR
```

quando definido no produto.

---

# 105. Timezone

Persistência:

```text id="utc_storage"
UTC
```

Display:

```text id="local_timezone"
user/channel timezone
```

---

# 106. Data Volume

Paginar:

```text id="paginate"
videos
ideas
projects
audit logs
agent runs
workflow runs
```

---

# 107. Raw Data Retention

Não manter raw provider responses eternamente sem necessidade.

---

# 108. Media Lifecycle

Preparar policies futuras:

```text id="media_lifecycle"
draft assets
failed attempts
final assets
```

podem possuir retenções diferentes.

---

# 109. Cost Optimization Review

Após dados reais suficientes:

```text id="cost_opt_review"
identify expensive steps
retry waste
model inefficiency
```

---

# 110. Agent Optimization Review

Analisar:

```text id="agent_opt_review"
token use
approval rate
latency
cost
```

---

# 111. Workflow Optimization Review

Medir:

```text id="workflow_opt"
time per step
failure rate
human intervention
```

---

# 112. UX Optimization Review

Medir:

```text id="ux_opt"
approval friction
rejection rate
drop-off
```

---

# 113. Growth Optimization Review

Medir:

```text id="growth_opt"
idea approval
content performance
learning usefulness
```

---

# 114. Business Metrics Após Lançamento

```text id="business_metrics"
activation rate
channels connected
content published
autonomy rate
retention
COGS
gross margin
```

---

# 115. Product North Star

Possível métrica:

```text id="north_star"
High-quality content published successfully per active channel
```

não apenas número de gerações.

---

# 116. Reliability North Star

```text id="reliability_star"
successful publication rate
```

---

# 117. Quality North Star

```text id="quality_star"
first-pass approval rate
```

---

# 118. Efficiency North Star

```text id="efficiency_star"
cost per approved published content
```

---

# 119. Autonomy North Star

```text id="autonomy_star"
content completed without human intervention
```

---

# 120. Claude Code Não Deve

```text id="claude_must_not"
rebuild whole repository without reason
change stack casually
skip migrations
disable tests
hardcode credentials
hardcode providers
mix tenant data
allow agent direct publication
enable autopilot by default
implement fake placeholders as production-ready
```

---

# 121. Claude Code Deve

```text id="claude_must"
follow phases
reuse architecture
inspect before changing
test
document
preserve compatibility
report limitations
keep user UI simple
keep backend robust
```

---

# 122. Escopo Mudando Durante o Projeto

Se novo requisito aparecer:

```text id="scope_change"
identify which master document it affects
identify phase
update docs
then implement
```

Não implementar de forma isolada.

---

# 123. Breaking Changes

Se necessário:

```text id="breaking_change"
document
migration plan
compatibility plan
tests
```

---

# 124. Master Document Amendments

Documentos 01–10 podem evoluir.

Mudança importante deve registrar:

```text id="doc_amendment"
version
date
reason
affected phases
```

---

# 125. Projeto Como Sistema Evolutivo

A arquitetura não deve assumir que:

```text id="evolution"
YouTube será a única plataforma
Higgsfield será permanente
modelo X continuará melhor
LLM Y continuará disponível
```

---

# 126. Plataforma Agnóstica

Core:

```text id="agnostic_core"
content
strategy
projects
workflow
quality
analytics
```

deve ser independente da plataforma.

---

# 127. YouTube Como Primeiro Adapter

Inicialmente:

```text id="youtube_adapter"
YouTubePlatformGateway
```

---

# 128. Futuro

```text id="future_platforms"
TikTokPlatformGateway
InstagramPlatformGateway
```

sem reconstruir core.

---

# 129. Final Architecture Map

```text id="final_architecture"
                    USER APP
                       │
                       ↓
                 APPLICATION API
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   CONTENT CORE   INTELLIGENCE    GOVERNANCE
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                WORKFLOW ENGINE
                       │
                 AGENT RUNTIME
                       │
                 MEDIA GATEWAY
                       │
                 MODEL ROUTER
                       │
             PROVIDERS / MCPs
                       │
                   QUALITY
                       │
                     SEO
                       │
                  PUBLISHER
                       │
                    YOUTUBE
                       │
                  ANALYTICS
                       │
                   LEARNING
                       │
                  STRATEGY
                       ↺
```

---

# 130. Final Product Flow

```text id="final_flow"
CONNECT CHANNEL
      ↓
UNDERSTAND
      ↓
PLAN
      ↓
CREATE
      ↓
REVIEW
      ↓
PUBLISH
      ↓
MEASURE
      ↓
LEARN
      ↓
IMPROVE
      ↺
```

---

# 131. Final User Experience

O usuário deverá perceber:

```text id="final_user"
Conectei meu canal.
O sistema entendeu o que eu publico.
Ele encontrou novas oportunidades.
Montou um calendário.
Produziu.
Revisou.
Publicou.
Mediu.
E as próximas recomendações ficaram melhores.
```

---

# 132. Final Technical Experience

O administrador deverá conseguir responder:

```text id="final_admin"
what happened?
where?
when?
which workflow?
which agent?
which provider?
which model?
how much did it cost?
why was it approved?
why did it fail?
can it be retried safely?
```

---

# 133. Completion Condition of the Entire Project

O projeto só poderá ser considerado plenamente concluído quando existir:

```text id="project_complete"
multi-tenant SaaS
secure YouTube connection
Channel Intelligence
Channel DNA
Strategy
Idea Engine
Opportunity Engine
Calendar
Workflow Engine
Agent Runtime
Script/Storyboard
Media Gateway
Multi-provider routing
Cost control
Production
Quality Gate
SEO
Scheduling
Publishing
Analytics
Learning
Autopilot
Billing
Control Center
```

---

# 134. Final Rule for Implementation

O Claude Code deve sempre priorizar:

```text id="final_priorities"
correctness
security
maintainability
traceability
cost control
user simplicity
```

antes de:

```text id="final_avoid"
speed of adding features
```

---

# 135. Próxima Etapa

Após a entrega deste documento, a fase de especificação conceitual está encerrada.

O próximo trabalho deverá ser:

```text id="next_step"
Prompt Executivo — Fase 01
Project Foundation
```

Esse prompt deverá ser operacional, detalhado e imediatamente executável pelo Claude Code.

A partir daí, repetir:

```text id="phase_cycle"
Prompt da Fase
↓
Claude implementa
↓
Checklist de validação
↓
Correções
↓
Fase aprovada
↓
Próxima fase
```

---

# 136. Checklist Mestre Antes de Iniciar a Fase 01

Confirmar que o Claude Code recebeu:

- Documento 01;
- Documento 02;
- Documento 03;
- Documento 04;
- Documento 05;
- Documento 06;
- Documento 07;
- Documento 08;
- Documento 09;
- Documento 10.

Solicitar que esses documentos sejam tratados como:

```text id="master_docs"
PROJECT MASTER SPECIFICATIONS
```

e mantidos preferencialmente em:

```text id="docs_master"
/docs/master/
```

---

# 137. Estrutura Recomendada dos Documentos

```text id="docs_structure"
/docs/master/

01-product-brief.md
02-architecture-guidelines.md
03-data-model.md
04-workflows-orchestration.md
05-ai-agents.md
06-providers-media-router.md
07-channel-intelligence-growth.md
08-ux-ui.md
09-security-billing-governance.md
10-implementation-roadmap.md
```

---

# 138. Instrução Importante ao Claude Code

Antes da primeira linha de implementação, realizar uma leitura completa dos 10 documentos e produzir apenas um breve:

```text id="architecture_ack"
Architecture Acknowledgement
```

contendo:

```text id="architecture_ack_fields"
stack understood
20 phases understood
main domain boundaries
main security constraints
main rules that must never be violated
```

Esse acknowledgement não substitui a implementação.

Serve apenas para confirmar que a arquitetura foi compreendida corretamente.

---

# 139. Não Pedir Novo Redesign

Após o acknowledgement, seguir diretamente para:

```text id="start_f01"
F01
```

Não redesenhar a arquitetura já definida sem motivo técnico concreto.

---

# 140. Princípio Final

Este projeto deverá ser construído como uma plataforma de produção editorial autônoma, e não como um conjunto de scripts conectados.

A arquitetura deverá permitir que:

```text id="final_principle"
o usuário veja simplicidade
enquanto
o sistema mantém inteligência, controle, qualidade e rastreabilidade
```

Este documento encerra a especificação mestre e deverá permanecer como referência permanente durante todas as 20 fases.