# Diretrizes Arquiteturais Obrigatórias

## 1. Objetivo deste Documento

Este documento define as regras técnicas obrigatórias para a implementação da plataforma.

O Claude Code deverá usar este documento como referência permanente durante todas as 20 fases do projeto.

Nenhuma fase deve ser implementada isoladamente sem considerar:

- escalabilidade;
- multiusuário;
- multicanal;
- modularidade;
- rastreabilidade;
- segurança;
- desacoplamento;
- observabilidade;
- testabilidade;
- custo;
- evolução futura.

A regra principal é:

**construir cada fase como parte de uma plataforma SaaS maior, e nunca como uma solução temporária isolada.**

---

# 2. Estrutura Geral do Repositório

Utilizar preferencialmente um monorepo.

Estrutura inicial recomendada:

```text
/
├── apps/
│   ├── web/
│   └── api/
│
├── services/
│   ├── worker/
│   ├── media/
│   └── scheduler/
│
├── packages/
│   ├── shared/
│   ├── schemas/
│   └── ui/
│
├── infra/
│   ├── docker/
│   ├── nginx/
│   └── scripts/
│
├── docs/
│
├── tests/
│
├── docker-compose.yml
├── .env.example
└── README.md
```

Evitar espalhar funcionalidades sem estrutura definida.

---

# 3. Frontend

Aplicação principal:

```text
apps/web
```

Tecnologias:

- Next.js;
- TypeScript;
- React;
- Tailwind CSS;
- shadcn/ui.

Estrutura interna recomendada:

```text
apps/web/src/

├── app/
├── components/
├── features/
├── hooks/
├── lib/
├── services/
├── stores/
├── types/
└── utils/
```

A organização principal deverá ser por feature.

Exemplo:

```text
features/

├── auth/
├── channels/
├── ideas/
├── calendar/
├── projects/
├── analytics/
└── settings/
```

Evitar um diretório gigantesco de componentes sem contexto.

---

# 4. Backend

Aplicação principal:

```text
apps/api
```

Tecnologia:

```text
Python + FastAPI
```

Estrutura recomendada:

```text
apps/api/app/

├── api/
├── core/
├── db/
├── models/
├── schemas/
├── repositories/
├── services/
├── domain/
├── events/
├── workflows/
├── agents/
├── gateways/
├── providers/
├── integrations/
├── security/
├── observability/
└── utils/
```

Cada camada terá responsabilidades distintas.

---

# 5. Regra de Responsabilidade por Camada

## API Layer

Responsável apenas por:

- receber requests;
- validar entrada;
- verificar autenticação;
- chamar services;
- retornar responses.

Não colocar regra de negócio diretamente em endpoints.

Errado:

```python
@router.post("/ideas")
def create_idea():
    # 200 linhas de lógica
```

Correto:

```python
@router.post("/ideas")
def create_idea():
    return idea_service.create(...)
```

---

# 6. Services

Services representam casos de uso da aplicação.

Exemplos:

```text
ChannelService
IdeaService
StrategyService
CalendarService
ProjectService
WorkflowService
MediaService
QualityService
PublicationService
AnalyticsService
```

Services podem coordenar repositories, events e gateways.

Não devem possuir detalhes de infraestrutura específica.

---

# 7. Repositories

Toda persistência deve ser acessada preferencialmente via repository.

Exemplo:

```text
ChannelRepository
IdeaRepository
ProjectRepository
WorkflowRepository
```

Evitar queries SQL espalhadas em:

- routes;
- agents;
- workers;
- providers.

---

# 8. Models

Models representam persistência no PostgreSQL.

Usar:

- SQLAlchemy;
- migrations via Alembic.

Models não devem conter lógica complexa de negócio.

---

# 9. Schemas

Utilizar Pydantic para:

- requests;
- responses;
- agent inputs;
- agent outputs;
- events;
- internal contracts.

Sempre que possível utilizar schemas explícitos.

Evitar:

```python
dict[str, Any]
```

quando houver estrutura previsível.

---

# 10. Domain Layer

Criar estruturas de domínio para regras importantes.

Exemplos:

```text
OpportunityScore
QualityScore
ChannelDNA
SceneState
PublicationState
BudgetPolicy
AutomationMode
```

Essas estruturas não deverão depender diretamente de FastAPI ou Celery.

---

# 11. Multi-Tenancy

Toda entidade relevante deverá possuir associação com:

```text
organization_id
```

e, quando necessário:

```text
user_id
channel_id
```

Nunca executar consultas sensíveis sem escopo organizacional.

Exemplo obrigatório:

```python
repository.get_by_id(
    id=project_id,
    organization_id=current_org.id
)
```

Evitar:

```python
repository.get_by_id(project_id)
```

---

# 12. IDs

Utilizar UUIDs para entidades de domínio.

Evitar IDs sequenciais expostos publicamente.

---

# 13. Timestamps

Toda entidade importante deverá possuir:

```text
created_at
updated_at
```

Quando aplicável:

```text
deleted_at
started_at
completed_at
published_at
scheduled_at
```

Utilizar timezone-aware UTC no banco.

Converter para timezone do usuário apenas na interface.

---

# 14. Soft Delete

Para entidades críticas utilizar soft delete quando adequado.

Exemplos:

- channels;
- projects;
- assets;
- users.

Evitar destruição permanente sem necessidade.

---

# 15. Status como Enum

Não utilizar strings arbitrárias espalhadas.

Criar enums.

Exemplo:

```python
class ProjectStatus(str, Enum):
    PLANNED = "planned"
    PRODUCING = "producing"
    REVIEW = "review"
    READY = "ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
```

---

# 16. Máquina de Estados

Processos importantes deverão possuir transições válidas.

Exemplo:

```text
PLANNED
   ↓
PRODUCING
   ↓
REVIEW
   ↓
READY
   ↓
SCHEDULED
   ↓
PUBLISHED
```

Evitar permitir:

```text
PLANNED → PUBLISHED
```

sem workflow legítimo.

---

# 17. Event-Driven Architecture

Mudanças importantes deverão gerar eventos internos.

Padrão:

```text
domain.resource.action
```

Exemplos:

```text
channel.connected
channel.analysis.completed

idea.created
idea.approved

project.created
project.production.started

script.generated

media.generation.completed

quality.review.failed
quality.review.passed

publication.scheduled
publication.completed
publication.failed
```

---

# 18. Event Payload

Todo evento deverá conter informações mínimas:

```json
{
  "event_id": "...",
  "event_type": "...",
  "timestamp": "...",
  "organization_id": "...",
  "resource_id": "...",
  "correlation_id": "...",
  "payload": {}
}
```

---

# 19. Correlation ID

Todo workflow deverá possuir:

```text
correlation_id
```

Esse identificador deverá acompanhar:

- logs;
- tasks;
- generations;
- agents;
- workflows;
- publications.

Isso permitirá rastrear uma execução completa.

---

# 20. Celery

Utilizar Celery somente para processamento assíncrono.

Exemplos:

- importação de canal;
- análise;
- geração;
- render;
- publicação;
- coleta de analytics.

Celery nunca deverá ser a fonte de verdade do estado.

---

# 21. Regra Fundamental de Jobs

Estado deve estar no PostgreSQL.

Celery apenas executa.

Errado:

```text
"se existe task no Celery, está processando"
```

Correto:

```text
database status = PROCESSING
task executes
database status = COMPLETED
```

---

# 22. Idempotência

Tasks importantes deverão ser idempotentes.

Se uma task executar duas vezes, não deverá necessariamente:

- publicar duas vezes;
- cobrar duas vezes;
- criar dois projetos;
- duplicar assets.

Criar idempotency keys quando necessário.

---

# 23. Retry

Implementar retries controlados.

Cada operação deverá declarar:

```text
max_attempts
retry_delay
backoff
```

Evitar retries infinitos.

---

# 24. Dead Letter / Failed Jobs

Jobs que excederem limite de tentativas deverão ser registrados como falhos.

Guardar:

- erro;
- stack trace;
- input;
- provider;
- attempts;
- timestamp.

---

# 25. Workflow Engine

Não implementar workflows como funções monolíticas.

Utilizar estrutura semelhante a:

```text
WorkflowDefinition
WorkflowRun
WorkflowStep
WorkflowEvent
```

---

# 26. Workflow Definition

Exemplo:

```text
short.production.v1
```

Com steps:

```text
research
script
script_qa
storyboard
media_generation
assembly
quality
seo
ready
```

---

# 27. Workflow Versioning

Nunca alterar silenciosamente um workflow existente em produção.

Criar:

```text
short.production.v1
short.production.v2
```

Projetos existentes permanecem vinculados à versão original.

---

# 28. Agent Registry

Agentes deverão ser registrados.

Estrutura mínima:

```text
Agent
AgentVersion
AgentRun
```

Cada versão deverá registrar:

- name;
- role;
- prompt version;
- model;
- provider;
- configuration;
- input schema;
- output schema.

---

# 29. Prompts

Prompts devem ser versionados.

Evitar prompts hardcoded em:

- routes;
- workers;
- services.

Criar estrutura centralizada.

Exemplo:

```text
agents/prompts/

channel_analyst/
strategy_agent/
idea_agent/
script_writer/
quality_visual/
```

---

# 30. Structured Output

Agentes deverão retornar JSON estruturado sempre que possível.

Exemplo:

```json
{
  "score": 92,
  "approved": true,
  "issues": [],
  "recommendations": []
}
```

Evitar depender de parsing de textos livres.

---

# 31. LLM Gateway

Toda comunicação com LLM deverá ocorrer através de:

```text
LLMGateway
```

Interface conceitual:

```python
generate()
generate_structured()
stream()
```

Nunca chamar diretamente APIs de LLM em services de negócio.

---

# 32. Media Gateway

Toda geração multimídia deverá ocorrer através de:

```text
MediaGateway
```

Interface futura:

```python
generate_image()
generate_video()
image_to_video()
text_to_video()
upscale()
edit_image()
get_job_status()
cancel_job()
```

---

# 33. Voice Gateway

Criar abstração específica:

```text
VoiceGateway
```

Métodos futuros:

```python
text_to_speech()
list_voices()
clone_voice()
```

quando permitido pelo provider.

---

# 34. Music Gateway

Criar abstração independente para música.

```text
MusicGateway
```

Não acoplar música ao MediaGateway caso o provider possua ciclo operacional diferente.

---

# 35. Provider Adapters

Cada provider deverá existir como adapter.

Estrutura:

```text
providers/

├── higgsfield/
├── kie/
├── fal/
├── wavespeed/
└── replicate/
```

Cada adapter implementa contratos comuns.

---

# 36. Proibição de Vendor Lock-In

Nenhuma regra de negócio deverá depender de um provider específico.

Errado:

```python
if project.type == "short":
    use_higgsfield()
```

Correto:

```python
media_router.select_provider(request)
```

---

# 37. Model Registry

Modelos disponíveis deverão ser configuráveis.

Evitar hardcoding de modelos no código.

Cada modelo poderá conter:

```text
provider
model_id
capabilities
quality_score
reliability_score
cost
max_duration
resolution
reference_support
audio_support
enabled
```

---

# 38. Media Router

Criar serviço responsável por selecionar:

```text
provider + model
```

baseado em critérios.

Arquitetura futura deverá aceitar:

```text
cost_weight
quality_weight
speed_weight
reliability_weight
```

---

# 39. Provider Health

Cada provider deverá possuir status operacional.

Exemplo:

```text
HEALTHY
DEGRADED
UNAVAILABLE
```

O Media Router deverá evitar providers indisponíveis.

---

# 40. Cost Tracking

Toda operação externa paga deverá registrar custo.

Tabela conceitual:

```text
cost_events
```

Campos:

```text
organization_id
channel_id
project_id
scene_id
provider
model
operation
quantity
currency
estimated_cost
actual_cost
timestamp
```

---

# 41. Budget Enforcement

Antes de gerar mídia, verificar orçamento quando aplicável.

Exemplo:

```text
Project Budget
$3.00

Spent
$2.68

Next Generation
$0.70

Result:
BLOCK
```

---

# 42. Storage

Nunca salvar arquivos multimídia grandes diretamente no PostgreSQL.

Utilizar object storage.

Banco guarda:

```text
storage_key
mime_type
size
checksum
metadata
```

---

# 43. Asset Registry

Toda mídia deverá ser registrada.

Criar:

```text
MediaAsset
```

Tipos:

```text
image
video
audio
voice
music
thumbnail
subtitle
render
```

---

# 44. Asset Lineage

Registrar origem do asset.

Exemplo:

```text
generated_from
provider
model
prompt_version
source_asset
generation_attempt
```

Isso será importante para auditoria.

---

# 45. FFmpeg

Centralizar operações multimídia em serviço.

Exemplo:

```text
MediaProcessingService
```

Não executar comandos FFmpeg diretamente espalhados pelo código.

---

# 46. Segurança de Comandos

Nunca interpolar entrada de usuário diretamente em shell.

Utilizar listas de argumentos e validação.

---

# 47. OAuth YouTube

Implementar integração como gateway.

Exemplo:

```text
YouTubeGateway
```

Responsável por:

- OAuth;
- channels;
- videos;
- playlists;
- uploads;
- thumbnails;
- analytics quando aplicável.

---

# 48. Tokens OAuth

Tokens deverão:

- ser criptografados;
- possuir refresh;
- possuir expiration;
- ser associados ao usuário/conexão;
- nunca aparecer em logs.

---

# 49. Rate Limits e Quotas

Criar mecanismo para controlar:

- quota YouTube;
- APIs externas;
- LLMs;
- providers.

Registrar uso.

---

# 50. Error Handling

Criar hierarquia de erros.

Exemplo:

```text
ApplicationError
DomainError
ProviderError
AuthenticationError
QuotaError
BudgetExceededError
WorkflowError
```

Não retornar stack traces ao usuário.

---

# 51. Logs

Utilizar structured logging.

Exemplo:

```json
{
  "level": "INFO",
  "event": "media_generation_started",
  "project_id": "...",
  "correlation_id": "...",
  "provider": "..."
}
```

---

# 52. Não Logar

Nunca registrar:

- passwords;
- OAuth tokens;
- API keys;
- secrets;
- dados sensíveis desnecessários.

---

# 53. Audit Log

Separar log técnico de auditoria.

Audit logs devem registrar ações relevantes de usuários e automações.

---

# 54. Observability

Preparar arquitetura para:

- metrics;
- logs;
- traces;
- health checks.

Não é obrigatório integrar observabilidade externa na primeira fase, mas a arquitetura deve permitir.

---

# 55. Health Endpoints

Backend deverá possuir:

```text
/health
/health/db
/health/redis
```

Control Center poderá usar esses endpoints futuramente.

---

# 56. Configuração

Utilizar configuração por ambiente.

Exemplo:

```text
APP_ENV
DATABASE_URL
REDIS_URL
STORAGE_ENDPOINT
STORAGE_BUCKET
SECRET_KEY
```

Nunca commitar `.env` real.

---

# 57. Feature Flags

Criar estrutura de feature flags.

Possíveis flags:

```text
AUTOPILOT
AUTO_PUBLISH
TREND_ENGINE
LEARNING_ENGINE
MEDIA_ROUTER
COST_ROUTER
```

---

# 58. API Versioning

Rotas públicas deverão utilizar versão.

Exemplo:

```text
/api/v1/
```

Preparar para:

```text
/api/v2/
```

sem quebrar clientes antigos.

---

# 59. Response Pattern

Utilizar respostas previsíveis.

Sucesso:

```json
{
  "data": {},
  "meta": {}
}
```

Erro:

```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project not found"
  }
}
```

---

# 60. Paginação

Endpoints de listas deverão utilizar paginação.

Evitar endpoints que retornem milhares de registros.

---

# 61. Frontend API Client

Centralizar acesso ao backend.

Exemplo:

```text
services/api/
```

Não espalhar `fetch()` indiscriminadamente pelos componentes.

---

# 62. Server State

Utilizar ferramenta apropriada para server state, como TanStack Query.

Evitar duplicar estado remoto desnecessariamente em stores globais.

---

# 63. UI Clean

A interface do usuário deverá esconder complexidade técnica.

Usuário não deverá ver:

- provider;
- modelo;
- MCP;
- retries;
- tokens;
- prompt;
- queue.

Exceto em modo avançado futuro.

---

# 64. Control Center

Informações técnicas serão reservadas para painel administrativo.

---

# 65. Design Consistency

Criar design system básico.

Definir:

- spacing;
- typography;
- buttons;
- cards;
- states;
- alerts;
- badges;
- loading;
- empty states.

Evitar estilos ad hoc.

---

# 66. Estados de Loading

Todo processo assíncrono deverá possuir feedback visual.

Exemplo:

```text
Analisando canal...
Gerando estratégia...
Preparando conteúdo...
```

Nunca deixar usuário sem saber se algo está acontecendo.

---

# 67. Erros para Usuário

Mensagens devem ser humanas.

Errado:

```text
HTTP 503 PROVIDER_TIMEOUT
```

Correto:

```text
Não foi possível concluir esta geração. O sistema tentará uma alternativa.
```

Detalhe técnico fica no Control Center.

---

# 68. Testing

Cada módulo deverá possuir testes.

Estrutura mínima:

```text
unit
integration
e2e
```

---

# 69. Unit Tests

Testar principalmente:

- scoring;
- state machines;
- policies;
- budget;
- routing;
- services.

---

# 70. Integration Tests

Testar:

- database;
- repositories;
- API;
- workers;
- workflows.

---

# 71. Provider Mocks

Todos os gateways externos deverão possuir mocks.

Exemplo:

```text
FakeLLMGateway
FakeMediaGateway
FakeYouTubeGateway
```

Isso permitirá testes sem custo.

---

# 72. Seed Data

Criar comandos para popular ambiente local com:

- usuário;
- organização;
- canal fictício;
- ideias;
- projetos.

Facilitar desenvolvimento da interface.

---

# 73. Database Migrations

Toda mudança de schema deverá usar migration.

Nunca alterar banco manualmente em produção.

---

# 74. Backward Compatibility

Mudanças futuras deverão preservar dados existentes sempre que possível.

Nunca apagar coluna simplesmente porque não está mais sendo usada sem plano de migração.

---

# 75. Documentation as Code

Toda nova fase deverá atualizar `/docs`.

Não deixar documentação para o final.

---

# 76. ADRs

Para decisões arquiteturais importantes, criar:

```text
docs/adr/
```

ADR significa:

```text
Architecture Decision Record
```

Exemplo:

```text
ADR-001-monorepo.md
ADR-002-postgresql.md
ADR-003-celery.md
```

---

# 77. README

README deverá sempre conter:

- requisitos;
- instalação;
- ambiente;
- comandos;
- testes;
- migrations;
- execução local.

---

# 78. Definition of Done

Uma fase só poderá ser considerada concluída quando:

- código estiver implementado;
- migrations estiverem criadas;
- testes passarem;
- lint passar;
- types passarem;
- Docker subir;
- documentação estiver atualizada;
- não houver secrets no código;
- funcionalidades existentes continuarem funcionando.

---

# 79. Regra para Alterações Futuras

Claude Code deverá evitar refactors desnecessários em módulos concluídos.

Só alterar estrutura anterior quando:

- necessário para fase atual;
- houver justificativa;
- migrations forem seguras;
- testes existentes continuarem passando.

---

# 80. Proibição de Placeholders Enganosos

Não criar funções que aparentem estar prontas mas não funcionem.

Exemplo proibido:

```python
def publish_video():
    return True
```

Se algo ainda não estiver implementado:

```text
NotImplemented
```

ou feature flag.

---

# 81. TODOs

TODOs devem ser claros e rastreáveis.

Exemplo:

```text
TODO(F13):
Implement Higgsfield adapter during Media Gateway phase.
```

Evitar:

```text
TODO: fix later
```

---

# 82. Compatibilidade com Desenvolvimento Incremental

Toda fase deverá produzir um sistema executável.

Exemplo:

Após Fase 04, já deve ser possível:

```text
login
+
conectar canal
+
ver informações básicas
```

Mesmo que produção ainda não exista.

---

# 83. Não Antecipar Implementação Complexa

Se uma feature pertence à Fase 17, a Fase 06 não deverá implementá-la escondida.

Criar apenas interfaces ou contratos necessários.

---

# 84. Preparação sem Overengineering

Evitar dois extremos:

```text
código improvisado
```

e

```text
arquitetura absurda para algo ainda inexistente
```

Criar interfaces claras e implementação mínima necessária.

---

# 85. Concurrency

Operações longas nunca deverão bloquear request HTTP.

Exemplo:

```text
POST /channel/analyze
```

deve:

```text
criar job
retornar job_id
processar em worker
```

---

# 86. Job Status

Criar endpoint genérico para consultar operações assíncronas.

Exemplo:

```text
GET /jobs/{job_id}
```

---

# 87. WebSocket / SSE

Preparar possibilidade futura para atualização em tempo real.

Não obrigatório inicialmente.

---

# 88. Files e Uploads

Uploads deverão:

- validar MIME;
- validar tamanho;
- sanitizar nome;
- gerar identificador;
- usar storage.

Nunca confiar apenas na extensão.

---

# 89. Checksums

Para assets importantes armazenar checksum.

Isso poderá detectar duplicações.

---

# 90. Deduplicação

Evitar regenerar/importar informação idêntica quando possível.

Exemplo:

vídeo do YouTube já importado não deve ser recriado a cada sincronização.

---

# 91. Sync Strategy

Integrações deverão diferenciar:

```text
full_sync
incremental_sync
```

Após onboarding, preferir incremental.

---

# 92. External IDs

Guardar IDs externos separadamente.

Exemplo:

```text
youtube_channel_id
youtube_video_id
provider_job_id
```

Não utilizar ID externo como primary key local.

---

# 93. Scheduler

Agendamentos deverão estar registrados no banco.

Worker apenas executa o que o banco determina.

---

# 94. Timezones

Usuário poderá configurar timezone.

Agendamento deverá ser armazenado em UTC e exibido localmente.

---

# 95. Publication Lock

Antes de publicar, criar mecanismo que impeça upload duplicado por dois workers.

---

# 96. Concurrency Lock

Usar locks para operações críticas como:

```text
publish
billing
generation billing
channel sync
```

quando necessário.

---

# 97. Analytics Snapshots

Não sobrescrever métricas históricas.

Registrar snapshots temporais.

---

# 98. Learning Data

Conclusões do Learning Engine deverão ser separadas dos dados brutos.

Nunca substituir dados históricos por inferência.

---

# 99. Provenance

Sempre que possível registrar de onde veio uma informação.

Exemplo:

```text
source = youtube
source = user
source = inferred
source = agent
```

---

# 100. Confidence

Inferências importantes de IA deverão possuir:

```text
confidence
```

quando aplicável.

---

# 101. Human Override

Decisões automáticas importantes deverão permitir intervenção humana.

Exemplo:

```text
AI classification:
Kids Entertainment

User override:
Education
```

Guardar ambos.

---

# 102. Autopilot Safety

Autopilot deverá possuir limites.

Exemplos:

```text
max_daily_publications
max_daily_cost
allowed_formats
allowed_channels
minimum_quality_score
```

---

# 103. Auto Publish

Auto Publish deverá ser opt-in.

Nunca habilitar automaticamente para um novo canal.

---

# 104. Emergency Stop

Criar possibilidade futura de:

```text
PAUSE AUTOMATION
```

por:

- organização;
- canal;
- projeto.

---

# 105. Provider Emergency Disable

Admin deverá poder desabilitar um provider sem deploy.

---

# 106. Secrets Management

Arquitetura deverá permitir futuramente integração com:

- AWS Secrets Manager;
- Vault;
- similares.

Inicialmente `.env` apenas em ambiente local.

---

# 107. Database Indexes

Criar índices para consultas importantes.

Exemplo:

```text
organization_id
channel_id
status
created_at
scheduled_at
external_id
```

---

# 108. Unique Constraints

Criar constraints onde necessário.

Exemplo:

```text
organization_id + youtube_channel_id
```

não deve duplicar conexão.

---

# 109. Transaction Boundaries

Operações críticas deverão usar transações.

Exemplo:

```text
create project
+
create workflow
+
emit event
```

não deve deixar estado parcial.

---

# 110. Outbox Pattern

Preparar arquitetura para implementar Outbox Pattern para eventos críticos se necessário.

Não obrigatório na Fase 01.

---

# 111. API Documentation

FastAPI deverá disponibilizar documentação OpenAPI.

Endpoints importantes deverão possuir descrições adequadas.

---

# 112. Naming Conventions

Python:

```text
snake_case
PascalCase para classes
```

TypeScript:

```text
camelCase
PascalCase para componentes/types
```

Banco:

```text
snake_case
```

---

# 113. Service Naming

Preferir nomes claros.

Exemplo:

```text
ChannelAnalysisService
```

em vez de:

```text
ChannelManagerHelper
```

---

# 114. Métodos

Métodos devem representar intenção.

Preferir:

```text
approve_idea()
schedule_publication()
```

em vez de:

```text
update()
process()
handle()
```

quando possível.

---

# 115. Código Simples

Preferir legibilidade em vez de abstração excessiva.

Nenhum padrão deve ser utilizado apenas por parecer sofisticado.

---

# 116. Dependências

Não adicionar biblioteca sem necessidade real.

Antes de instalar dependência, verificar se:

- existe manutenção;
- possui licença adequada;
- é realmente necessária.

---

# 117. Lockfiles

Manter lockfiles versionados.

---

# 118. Security Updates

Evitar dependências obsoletas.

---

# 119. CI

Preparar pipeline futuro com:

```text
lint
tests
typecheck
build
```

---

# 120. Git Strategy

Commits preferencialmente pequenos e relacionados à fase atual.

Mensagens claras.

Exemplo:

```text
feat(channels): add youtube connection model
```

---

# 121. Branching

Usar branches por feature/fase quando apropriado.

---

# 122. Não Quebrar Main

Código entregue ao branch principal deverá:

- compilar;
- subir;
- passar testes.

---

# 123. Feature Completion Report

Ao finalizar cada fase, Claude Code deverá fornecer um relatório contendo:

```text
Fase concluída
Arquivos criados
Arquivos alterados
Migrations
Endpoints
Testes
Decisões arquiteturais
Pendências futuras
Como executar
Como validar
```

---

# 124. Implementation Plan Before Coding

Antes de cada fase, Claude Code deverá:

1. revisar este documento;
2. revisar o briefing mestre;
3. analisar código existente;
4. listar arquivos que pretende criar/alterar;
5. indicar dependências;
6. identificar migrations;
7. implementar;
8. executar testes;
9. corrigir problemas;
10. documentar resultado.

---

# 125. Regra de Não Recomeçar

Claude Code nunca deverá recriar o projeto ou substituir toda a arquitetura durante fases futuras sem autorização explícita.

O sistema deverá evoluir incrementalmente.

---

# 126. Compatibilidade com as 20 Fases

Toda implementação deverá respeitar esta sequência:

```text
01 Foundation
02 Core Domain
03 Authentication
04 YouTube Integration
05 Channel Importer
06 Channel Intelligence
07 Channel DNA
08 Strategy Engine
09 Ideas & Opportunities
10 Content Calendar
11 Workflow & Agents
12 Scripts & Storyboards
13 MCP / Media Gateway
14 Router & Costs
15 Production
16 Quality Gate
17 SEO & Thumbnail
18 Publishing
19 Analytics & Learning
20 Autopilot & SaaS
```

---

# 127. Princípio Final

O sistema deve ser:

```text
SIMPLES PARA O USUÁRIO
ROBUSTO NOS BASTIDORES
MODULAR NO CÓDIGO
RASTREÁVEL NAS AUTOMAÇÕES
SEGURO NAS INTEGRAÇÕES
CONTROLÁVEL NOS CUSTOS
EVOLUTIVO NA ARQUITETURA
```

Claude Code deve sempre privilegiar essas características ao tomar decisões de implementação.