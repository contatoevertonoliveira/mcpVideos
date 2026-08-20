# Documento 06 — MCPs, Providers, Media Gateway, Model Router, Custos e Fallbacks

## 1. Objetivo

Este documento define a camada de integração com provedores externos de IA, MCPs, geração multimídia, roteamento de modelos, controle de custos, fallbacks, resiliência e seleção automática de infraestrutura.

A regra central é:

**a aplicação nunca deverá depender diretamente de um provedor específico.**

O sistema deverá sempre conversar com uma camada de abstração própria.

---

# 2. Visão Geral

Arquitetura:

```text id="zj9wm4"
APPLICATION CORE
      ↓
WORKFLOW ENGINE
      ↓
MEDIA SERVICE
      ↓
MEDIA GATEWAY
      ↓
MODEL ROUTER
      ↓
PROVIDER ADAPTER
      ↓
MCP / API EXTERNA
```

Exemplo:

```text id="ww1zrg"
Scene Planner
      ↓
Media Director
      ↓
Media Request
      ↓
Media Gateway
      ↓
Model Router
      ↓
Higgsfield / Kie / fal / WaveSpeed / Replicate
```

---

# 3. MCP não é Regra de Negócio

MCP deve ser tratado como protocolo de acesso ou integração.

Não criar lógica como:

```text id="woq2aq"
if content_type == "kids":
    call_higgsfield_mcp()
```

Correto:

```text id="k3zxrr"
request capability
      ↓
Model Router
      ↓
best eligible provider/model
```

---

# 4. Abstrações Principais

Criar:

```text id="an1iww"
LLMGateway
MediaGateway
VoiceGateway
MusicGateway
SearchGateway
PlatformGateway
```

Este documento foca principalmente em:

```text id="g3ax6e"
MediaGateway
VoiceGateway
MusicGateway
ModelRouter
ProviderRegistry
CostController
```

---

# 5. MediaGateway

Interface conceitual:

```python id="q1tw65"
class MediaGateway:
    async def generate_image(...)
    async def edit_image(...)
    async def generate_video(...)
    async def image_to_video(...)
    async def text_to_video(...)
    async def upscale(...)
    async def remove_background(...)
    async def get_job_status(...)
    async def cancel_job(...)
```

---

# 6. VoiceGateway

Interface:

```python id="suk1yf"
class VoiceGateway:
    async def text_to_speech(...)
    async def list_voices(...)
    async def get_voice(...)
```

Futuro:

```text id="mvdmck"
voice cloning
voice conversion
```

somente quando permitido e necessário.

---

# 7. MusicGateway

Interface:

```python id="md3mfa"
class MusicGateway:
    async def generate_music(...)
    async def generate_loop(...)
    async def get_job_status(...)
```

---

# 8. Provider Registry

Criar:

```text id="v02k5t"
providers
```

Cada provider deverá possuir:

```text id="sdw5g6"
id
name
slug
provider_type
status
base_url
supports_mcp
supports_api
supports_webhooks
documentation_url
priority
settings_json
```

---

# 9. Tipos de Provider

```text id="igmh7w"
llm
media
voice
music
multi
search
platform
```

---

# 10. Status de Provider

```text id="qk28m4"
healthy
degraded
unavailable
disabled
maintenance
```

---

# 11. Providers Previstos

Arquitetura deverá permitir adapters futuros para:

```text id="6i98q1"
Higgsfield
Kie
fal.ai
WaveSpeed
Replicate
ModelRunner
RunPod
outros
```

Não implementar todos inicialmente.

---

# 12. Provider Adapter

Cada provider deverá implementar contrato comum.

Estrutura recomendada:

```text id="4bpkvr"
providers/

├── base/
├── higgsfield/
├── kie/
├── fal/
├── wavespeed/
└── replicate/
```

---

# 13. Adapter Responsibilities

Adapter é responsável por:

```text id="kth1ga"
authentication
request translation
provider-specific payload
submission
status polling
webhook normalization
error normalization
result parsing
usage extraction
```

---

# 14. Adapter Não Pode

Provider Adapter não deve:

```text id="g96qf3"
decidir conteúdo
decidir orçamento
decidir prioridade editorial
alterar workflow
publicar no YouTube
```

---

# 15. Capability-Based Design

A aplicação deverá solicitar capacidades.

Exemplo:

```text id="j0q9f9"
IMAGE_GENERATION
IMAGE_EDIT
IMAGE_TO_VIDEO
TEXT_TO_VIDEO
UPSCALE
TTS
MUSIC_GENERATION
```

Não solicitar provider diretamente.

---

# 16. Media Request Contract

Exemplo conceitual:

```json id="71fc4n"
{
  "request_id": "uuid",
  "organization_id": "uuid",
  "channel_id": "uuid",
  "project_id": "uuid",
  "scene_id": "uuid",

  "capability": "image_to_video",

  "quality_tier": "standard",

  "duration_seconds": 6,

  "resolution": {
    "width": 1080,
    "height": 1920
  },

  "aspect_ratio": "9:16",

  "references": [],

  "requirements": {
    "character_consistency": "high",
    "camera_control": true,
    "audio_required": false
  },

  "budget": {
    "max_cost": 0.60,
    "currency": "USD"
  },

  "priority": "normal"
}
```

---

# 17. Requirements

Media Request poderá declarar:

```text id="kb9z5l"
character_consistency
reference_support
first_frame_control
last_frame_control
camera_motion
lip_sync
audio_generation
resolution
duration
transparent_background
style_reference
```

---

# 18. Hard Requirements vs Preferences

Separar:

```text id="ra348l"
hard_requirements
```

de:

```text id="ji7qtx"
preferences
```

Exemplo:

```text id="qgd0fx"
Hard:
9:16 obrigatório

Preference:
preferir 1080p
```

---

# 19. Model Registry

Criar:

```text id="ihac57"
ai_models
```

Cada modelo:

```text id="wg725s"
provider_id
external_model_id
name
category
status
quality_score
reliability_score
speed_score
metadata_json
```

---

# 20. Capabilities

Tabela:

```text id="c2w845"
model_capabilities
```

Exemplos:

```text id="baw8al"
image_generation
image_edit
image_to_video
text_to_video
upscale
tts
music
lip_sync
```

---

# 21. Capability Metadata

Exemplo:

```json id="tch39u"
{
  "max_duration": 10,
  "supported_aspect_ratios": ["16:9", "9:16"],
  "reference_images": true,
  "max_reference_images": 4,
  "supports_audio": false
}
```

---

# 22. Model Availability

Modelo deverá possuir:

```text id="8y8zud"
enabled
```

separado de:

```text id="en9q9t"
provider status
```

Assim admin pode desabilitar um modelo específico.

---

# 23. Provider Pricing

Criar tabela versionada:

```text id="up3ktv"
provider_model_prices
```

Campos:

```text id="4b0fjv"
provider_id
model_id
operation
unit
price
currency
valid_from
valid_until
```

---

# 24. Unidades de Cobrança

Suportar:

```text id="d9aw6d"
request
image
second
minute
megapixel
token
character
credit
GPU second
GPU minute
```

---

# 25. Pricing Normalization

Criar serviço:

```text id="ctb7x8"
PricingNormalizer
```

Responsável por converter preços de diferentes providers para estimativa comparável.

---

# 26. Créditos Proprietários

Se provider cobrar em créditos:

```text id="k1gfr1"
provider credit
↓
estimated fiat value
```

Guardar ambos quando possível.

---

# 27. Cost Estimate

Antes de gerar:

```text id="tc8pqk"
estimate_cost(request, model)
```

Resultado:

```json id="9x1r9z"
{
  "estimated_cost": 0.42,
  "currency": "USD",
  "confidence": 0.91
}
```

---

# 28. Actual Cost

Após execução:

```text id="48u2db"
actual_cost
```

deverá ser atualizado quando provider informar consumo real.

---

# 29. Estimated vs Actual

Nunca substituir histórico.

Guardar ambos:

```text id="f5isqs"
estimated_cost
actual_cost
```

---

# 30. Model Router

Criar serviço:

```text id="3v1jcf"
ModelRouter
```

Responsabilidade:

Selecionar melhor combinação:

```text id="9dgwf9"
provider + model
```

para uma solicitação.

---

# 31. Router Inputs

```text id="qh3zrm"
capability
requirements
quality tier
budget
provider health
model health
pricing
historical QA
historical latency
historical failure rate
channel policy
organization policy
```

---

# 32. Router Output

```json id="xj10uj"
{
  "provider_id": "",
  "model_id": "",
  "estimated_cost": 0.0,
  "routing_score": 0,
  "reasoning_summary": "",
  "fallback_candidates": []
}
```

---

# 33. Routing Score

Exemplo:

```text id="er3uge"
routing_score =
quality_weight × quality
+
cost_weight × cost_efficiency
+
reliability_weight × reliability
+
speed_weight × speed
+
approval_weight × historical_approval
```

---

# 34. Pesos Configuráveis

Exemplo:

```json id="im41p5"
{
  "quality": 0.35,
  "cost": 0.25,
  "reliability": 0.20,
  "speed": 0.10,
  "historical_approval": 0.10
}
```

Não hardcode.

---

# 35. Quality Tiers

Definir:

```text id="tci5gx"
economy
standard
premium
```

---

# 36. Economy

Prioriza:

```text id="5xkrty"
cost
acceptable quality
speed
```

---

# 37. Standard

Equilíbrio:

```text id="6vc53f"
quality
cost
reliability
```

---

# 38. Premium

Prioriza:

```text id="2wtmfr"
quality
consistency
reliability
```

com maior tolerância de custo.

---

# 39. Hero Scene

Se:

```text id="exwx24"
hero_scene = true
```

Router poderá aumentar peso de qualidade.

---

# 40. Scene Importance

Adicionar:

```text id="5h4izk"
scene_importance
```

Exemplo:

```text id="d6vr91"
low
normal
high
hero
```

---

# 41. Historical QA Score

Modelo deverá aprender com dados reais.

Exemplo:

```text id="5he9c3"
Model X
historical QA approval = 94%
```

Esse score deve entrar no Router.

---

# 42. Contextual QA

Futuramente separar approval rate por contexto.

Exemplo:

```text id="hipv6h"
Model X

kids animation
96%

realistic humans
74%
```

---

# 43. Model Performance Profile

Preparar entidade derivada:

```text id="txig3k"
ModelPerformanceProfile
```

Por:

```text id="3w06bl"
capability
content type
style
channel type
```

---

# 44. Cost per Approved Asset

Métrica crítica:

```text id="1k24ut"
total cost of attempts
──────────────────────
approved output
```

---

# 45. Exemplo

```text id="f7fnqf"
Model A
$0.30 per generation
approval 50%

Expected approved cost ≈ $0.60

Model B
$0.45 per generation
approval 90%

Expected approved cost ≈ $0.50
```

Router poderá preferir B.

---

# 46. First Pass Approval Rate

Manter:

```text id="wop7n9"
first_pass_approval_rate
```

---

# 47. Generation Success Rate

Separar:

```text id="xfshbi"
technical_generation_success
```

de:

```text id="upakio"
quality_approval
```

---

# 48. Provider Reliability

Métricas:

```text id="d2n17o"
success rate
timeout rate
error rate
average latency
queue time
webhook reliability
```

---

# 49. Provider Health Monitor

Criar workflow:

```text id="i72is0"
provider.health.check.v1
```

---

# 50. Health Check

Poderá verificar:

```text id="kgmzf5"
API reachable
authentication valid
status endpoint
recent success rate
recent latency
```

---

# 51. Circuit Breaker

Implementar conceito:

```text id="f4a7zs"
CLOSED
OPEN
HALF_OPEN
```

---

# 52. Open Circuit

Se provider falhar repetidamente:

```text id="00o98e"
Router deixa de selecioná-lo temporariamente.
```

---

# 53. Half Open

Após cooldown:

```text id="d3tiwi"
permitir pequena quantidade de requests teste
```

---

# 54. Provider Emergency Disable

Admin poderá desabilitar:

```text id="ctwyxi"
provider
```

ou:

```text id="ixmb2z"
model
```

sem deploy.

---

# 55. Provider Priority

Permitir prioridade administrativa.

Exemplo:

```text id="g79uuz"
preferred
normal
fallback_only
```

---

# 56. Fallback Strategy

Cada geração deverá possuir lista de fallback elegível.

Exemplo:

```text id="l53lbf"
Primary:
Provider A / Model X

Fallback 1:
Provider B / Model X

Fallback 2:
Provider B / Model Y
```

---

# 57. Fallback Types

```text id="zng57c"
same_model_different_provider
different_model_same_capability
lower_quality_tier
different_production_method
human_review
```

---

# 58. Production Method Fallback

Exemplo:

```text id="agxded"
text_to_video premium
      ↓ fail / budget
image_to_video
      ↓ fail
static image + motion
```

Somente se workflow permitir.

---

# 59. Semantic Fallback

Fallback deve preservar objetivo da cena.

Não simplesmente trocar método e perder narrativa.

---

# 60. Hard Requirement Guard

Nunca usar fallback que viole requisito obrigatório.

Exemplo:

```text id="n2v9g6"
transparent background obrigatório
```

Modelo sem alpha support é inelegível.

---

# 61. Retry vs Fallback

Distinguir:

```text id="vghumk"
retry
= repetir operação similar
```

de:

```text id="wvr2j3"
fallback
= trocar provider/model/método
```

---

# 62. Retry Policy

Exemplo configurável:

```text id="9gfz7f"
Attempt 1
same provider/model

Attempt 2
same model, alternate provider

Attempt 3
alternate model
```

---

# 63. Error Categories

Normalizar erros:

```text id="9vv87z"
AUTH_ERROR
RATE_LIMIT
QUOTA_EXCEEDED
PROVIDER_TIMEOUT
PROVIDER_UNAVAILABLE
MODEL_UNAVAILABLE
INVALID_REQUEST
CONTENT_REJECTED
BUDGET_EXCEEDED
OUTPUT_INVALID
DOWNLOAD_FAILED
UNKNOWN_PROVIDER_ERROR
```

---

# 64. Retryable Errors

Exemplo:

```text id="4xa7wx"
RATE_LIMIT
TIMEOUT
TEMPORARY_UNAVAILABLE
```

---

# 65. Non-Retryable

Exemplo:

```text id="t89e1w"
INVALID_REQUEST
AUTH_ERROR
POLICY_REJECTION
```

---

# 66. Provider-Specific Errors

Adapter traduz para erro comum.

Nunca deixar services dependerem de códigos específicos do provider.

---

# 67. Async Provider Jobs

Suportar providers que retornam:

```text id="idovqe"
job_id
```

---

# 68. Lifecycle

```text id="2uqkgt"
SUBMITTED
QUEUED
PROCESSING
COMPLETED
FAILED
CANCELLED
```

---

# 69. Polling

Se não houver webhook:

```text id="u9x7ax"
poll
```

com backoff.

---

# 70. Polling Backoff

Exemplo:

```text id="s5u865"
5s
10s
20s
30s
60s
```

Configurável.

---

# 71. Polling Timeout

Nunca aguardar indefinidamente.

---

# 72. Webhooks

Quando provider suportar:

```text id="pd3il1"
prefer webhook
```

com reconciliation posterior.

---

# 73. Webhook Validation

Validar:

```text id="fvda3o"
signature
provider
payload schema
idempotency
```

---

# 74. Reconciliation

Mesmo com webhook:

```text id="sz0u3e"
reconciliation jobs
```

deverão detectar jobs perdidos.

---

# 75. Generation State

```text id="vrvfip"
PENDING
ROUTING
SUBMITTED
PROCESSING
COMPLETED
FAILED
CANCELLED
REVIEW
```

---

# 76. Generation Attempts

Toda troca ou retry gera novo:

```text id="0hjffg"
generation_attempt
```

---

# 77. Nunca Sobrescrever Attempt

Preservar:

```text id="ixt12p"
inputs
provider
model
cost
latency
output
error
QA score
```

---

# 78. Selected Attempt

Generation aponta para:

```text id="hkvmoi"
selected_attempt_id
```

somente após aprovação.

---

# 79. Output Validation

Antes de registrar asset:

```text id="o2x95p"
download file
validate MIME
validate checksum
validate size
validate dimensions
validate duration
```

---

# 80. Broken Asset

Se provider disser sucesso mas arquivo inválido:

```text id="qtmx8c"
OUTPUT_INVALID
```

---

# 81. Storage

Após validação:

```text id="k6b4qk"
external result
↓
our object storage
↓
MediaAsset
```

Não depender indefinidamente de URL temporária do provider.

---

# 82. Source URL

Guardar URL externa apenas como metadata quando útil.

---

# 83. Asset Lineage

Registrar:

```text id="g0grip"
generation_attempt
→ media_asset
```

---

# 84. Reference Assets

Media Request deverá aceitar:

```text id="vapb2n"
reference_asset_ids
```

Router verifica se modelo suporta quantidade e tipo.

---

# 85. Character Consistency

Quando prioridade alta:

```text id="0bz864"
character_consistency = high
```

Router deverá dar preferência a modelos com bom histórico nessa categoria.

---

# 86. First/Last Frame

Suportar capability:

```text id="rix12k"
first_frame
last_frame
```

quando modelo permitir.

---

# 87. Prompt Adaptation

`PromptEngineer` produz prompt semântico.

Adapter poderá transformar campos específicos para cada modelo.

---

# 88. Model-Specific Prompt Adapter

Criar conceito:

```text id="mbm3c8"
PromptAdapter
```

Exemplo:

```text id="bo707y"
generic prompt
↓
Veo adapter
Kling adapter
Seedance adapter
```

Sem alterar objetivo narrativo.

---

# 89. Negative Prompts

Suportar quando provider/modelo aceitar.

Se modelo não aceitar:

```text id="37yedk"
adapter ignora de forma explícita
```

---

# 90. Unsupported Settings

Nunca enviar parâmetros inválidos silenciosamente.

Adapter deve:

```text id="mzznqx"
validate
normalize
```

---

# 91. Model Capability Discovery

Podem existir duas fontes:

```text id="nu5fqb"
manual registry
provider discovery API
```

---

# 92. Manual Override

Admin poderá corrigir capability incorreta.

---

# 93. Pricing Refresh

Criar workflow:

```text id="d37c5u"
provider.pricing.refresh.v1
```

quando provider permitir consulta.

---

# 94. Manual Pricing

Quando não houver API:

```text id="t6mupi"
admin configuration
```

---

# 95. Price Freshness

Registrar:

```text id="a9915m"
last_verified_at
```

---

# 96. Stale Pricing

Se preço estiver desatualizado:

```text id="el5mla"
cost estimate confidence reduz
```

---

# 97. Currency

Armazenar moeda original e moeda base.

Exemplo:

```text id="9pihfg"
provider_currency = USD
billing_currency = BRL
```

---

# 98. FX

Conversão futura deverá usar serviço separado.

Não misturar taxa de câmbio com provider adapter.

---

# 99. Budget Controller

Criar:

```text id="rk2fui"
BudgetController
```

---

# 100. Budget Scopes

```text id="giv512"
organization
channel
project
scene
workflow
```

---

# 101. Budget Periods

```text id="w5dp9n"
per_request
per_project
daily
weekly
monthly
```

---

# 102. Warning Threshold

Exemplo:

```text id="k5wewr"
80%
```

---

# 103. Hard Limit

Exemplo:

```text id="un1b3f"
100%
```

Ao atingir:

```text id="o7m2yy"
block paid operation
```

salvo override autorizado.

---

# 104. Budget Reservation

Para concorrência, considerar reservar custo estimado antes de submeter job.

Fluxo:

```text id="byh2pm"
estimate
↓
reserve
↓
execute
↓
actual cost
↓
release difference
```

---

# 105. Evitar Overspend por Concorrência

Sem reservation:

```text id="15puhw"
10 workers
cada um vê $10 disponíveis
cada um gasta $3
```

pode exceder orçamento.

---

# 106. Cost Event

Toda operação paga gera:

```text id="sh1uy5"
CostEvent
```

---

# 107. Cost Event Fields

```text id="3o2h6t"
organization
channel
project
scene
provider
model
operation
estimated
actual
currency
attempt
timestamp
```

---

# 108. Cost Categories

```text id="80nnem"
llm
image
video
voice
music
storage
render
external_api
```

---

# 109. Internal Cost

Futuramente separar:

```text id="ip71u2"
provider cost
```

de:

```text id="nlf719"
internal infrastructure cost
```

---

# 110. True Production Cost

Conceito:

```text id="8dt566"
AI generation
+
retry
+
voice
+
music
+
render
+
storage
+
other external cost
```

---

# 111. Cost per Project

Dashboard interno deverá conseguir calcular:

```text id="v1bi6v"
total_cost(project_id)
```

---

# 112. Cost per Published Asset

```text id="1ln1dv"
production cost
────────────────
published content
```

---

# 113. Cost per Minute

Para long-form:

```text id="pi96mz"
cost_per_rendered_minute
```

---

# 114. Cost per View

Depois da publicação:

```text id="jxq6fd"
production cost
───────────────
views
```

---

# 115. ROI Layer

Preparar futura integração:

```text id="9fgz90"
cost
vs
revenue
```

Não implementar inicialmente.

---

# 116. Provider Account Models

Suportar:

```text id="x17qh0"
platform-managed
BYOK
hybrid
```

---

# 117. Platform Managed

Nós fornecemos credenciais.

Cliente usa saldo/plano da nossa plataforma.

---

# 118. BYOK

Cliente fornece API key do provider.

Credencial:

```text id="mdrzd8"
encrypted
organization scoped
```

---

# 119. Hybrid

Router poderá usar:

```text id="s15r1t"
client provider
```

ou:

```text id="evd3rs"
platform provider
```

conforme policy.

---

# 120. Credential Resolution

Criar:

```text id="ngup5x"
ProviderCredentialResolver
```

---

# 121. Precedência

Exemplo:

```text id="ph0j5p"
channel credential
↓
organization credential
↓
platform credential
```

somente quando policy permitir.

---

# 122. Secrets

Nunca salvar API key em texto.

Utilizar:

```text id="dnc834"
encrypted storage
```

---

# 123. Logs

Nunca logar:

```text id="72itzg"
Authorization header
API key
secret
raw OAuth token
```

---

# 124. MCP Adapter

Para providers MCP:

```text id="p3e5gc"
MCPProviderAdapter
```

poderá encapsular:

```text id="ieiumv"
tool discovery
tool invocation
schema mapping
result normalization
```

---

# 125. MCP Tool Discovery

Não assumir que ferramentas são eternamente iguais.

Cachear discovery com versão/TTL quando necessário.

---

# 126. MCP Capability Mapping

Exemplo:

```text id="19ieya"
MCP tool:
generate_video_x
```

mapeado para:

```text id="cma5dd"
capability = image_to_video
```

---

# 127. MCP Tool Changes

Se tool desaparecer:

```text id="2x5jnq"
mark model/capability degraded
```

não quebrar todo sistema.

---

# 128. MCP Timeouts

Mesmo princípio de API.

---

# 129. MCP Error Normalization

MCP error deverá virar erro interno comum.

---

# 130. MCP vs Direct API

Um mesmo provider poderá possuir:

```text id="h7vp8c"
MCP
API
```

Router/adapter poderá escolher transporte.

---

# 131. Transport Layer

Separar:

```text id="k94w7x"
provider
```

de:

```text id="4v7yvb"
transport
```

Exemplo:

```text id="lb1f48"
Provider: Higgsfield
Transport: MCP
```

---

# 132. Transport Types

```text id="xm1yrd"
REST
MCP
SDK
webhook
local
```

---

# 133. Provider Adapter Hierarchy

Exemplo:

```text id="1bhsjy"
BaseProviderAdapter
    ↓
MediaProviderAdapter
    ↓
HiggsfieldAdapter
```

---

# 134. Local Models

Arquitetura deverá permitir:

```text id="e7035d"
local provider
```

futuramente.

Exemplo:

```text id="a61sk1"
RunPod
local GPU
Ollama-like inference
```

---

# 135. Self-Hosted

Provider registry deverá suportar:

```text id="iy7no0"
self_hosted = true
```

---

# 136. Internal Endpoint

Nunca expor endpoint interno de provider diretamente ao frontend.

---

# 137. Rate Limiter

Criar rate limiting por provider.

---

# 138. Provider Concurrency

Campos:

```text id="fkm5oo"
max_concurrent_requests
max_requests_per_minute
```

---

# 139. Model Concurrency

Alguns modelos poderão possuir limite diferente.

---

# 140. Queue Per Provider

Preparar:

```text id="0c9e03"
provider queue
```

para controlar concorrência.

---

# 141. Priority Scheduling

Publicação iminente pode receber maior prioridade que asset experimental.

---

# 142. Fairness

Nenhuma organização deverá monopolizar provider.

---

# 143. Provider Quotas

Registrar:

```text id="y25obo"
remaining quota
```

quando disponível.

---

# 144. Quota Guard

Se provider estiver perto do limite:

```text id="kbqc8h"
Router reduz seleção
```

---

# 145. Provider Credit Balance

Quando provider trabalhar com créditos:

```text id="w20dcl"
balance
last_checked_at
```

---

# 146. Low Balance Alert

Evento:

```text id="n71wua"
provider.balance.low
```

---

# 147. Provider Auto Disable

Se saldo chegar a zero:

```text id="swgu71"
status = degraded/unavailable
```

---

# 148. Central Provider Dashboard

Control Center deverá futuramente mostrar:

```text id="k489nh"
Provider
Status
Balance
Models
Requests
Failures
Latency
Spend
QA Approval
```

---

# 149. Model Dashboard

Mostrar:

```text id="d601ev"
Model
Capability
Price
Quality
Approval
Latency
Cost per Approved Asset
```

---

# 150. Automatic Model Discovery

Quando provider disponibilizar catálogo:

```text id="3gq6rs"
sync models
```

mas novos modelos devem inicialmente entrar:

```text id="7i03sz"
disabled/testing
```

não automaticamente em produção.

---

# 151. Model Activation Flow

```text id="0ylzvj"
DISCOVERED
↓
TESTING
↓
EVALUATED
↓
ACTIVE
```

---

# 152. Model Evaluation

Antes de ativar:

```text id="o7myk1"
quality tests
cost tests
latency
consistency
failure rate
```

---

# 153. Evaluation Dataset

Usar conjuntos de teste internos.

Exemplo:

```text id="f4c47w"
kids animation
photorealistic
character consistency
camera motion
product image
thumbnail
```

---

# 154. Model Benchmarks

Guardar:

```text id="60bg8c"
benchmark_id
model
score
cost
latency
date
```

---

# 155. Benchmark Aging

Resultados antigos podem perder relevância.

Registrar data.

---

# 156. Model Version Change

Se provider atualizar modelo silenciosamente, performance pode mudar.

Detectar via regressão operacional quando possível.

---

# 157. Canary

Novo modelo pode receber pequeno percentual.

Exemplo:

```text id="d4rjfx"
5%
```

---

# 158. Shadow Generation

Para testes premium, sistema poderá gerar em paralelo sem usar resultado em produção.

Somente admin/testes.

---

# 159. Cost Guard para Experimentos

Shadow/testing deve possuir budget separado.

---

# 160. Router Explainability

Toda decisão de routing deverá possuir:

```text id="o100pc"
reasoning_summary
```

Exemplo:

```text id="27rqvo"
Selected Model B because:
- supports image references
- QA approval 93%
- estimated cost within budget
- provider healthy
```

---

# 161. Router Decision Log

Registrar:

```text id="cvnsq6"
eligible models
rejected models
selected model
score
reason
```

---

# 162. Rejected Candidate Reasons

Exemplos:

```text id="g6uoi6"
over_budget
missing_capability
provider_unhealthy
policy_blocked
poor_reliability
```

---

# 163. Deterministic Eligibility

Antes do scoring:

```text id="puwiv2"
filter ineligible
```

Depois:

```text id="jta9et"
rank eligible
```

---

# 164. Eligibility Flow

```text id="saepcd"
ALL MODELS
   ↓
CAPABILITY FILTER
   ↓
POLICY FILTER
   ↓
HEALTH FILTER
   ↓
BUDGET FILTER
   ↓
REQUIREMENT FILTER
   ↓
SCORING
   ↓
SELECT
```

---

# 165. No Eligible Model

Se nenhum modelo elegível:

```text id="pspbkx"
try production fallback
```

ou:

```text id="myc2dn"
human review
```

---

# 166. Never Silent Failure

Usuário/admin deverá receber estado claro.

---

# 167. Content Restrictions

Se provider não suporta certo conteúdo permitido pela plataforma:

```text id="qu7frm"
Router deve respeitar provider restrictions
```

---

# 168. Policy Layer

Provider adapter não decide policy de negócio.

Policy Service define elegibilidade.

---

# 169. Data Residency Future

Preparar metadata:

```text id="0uj8at"
region
data_residency
```

para clientes corporativos futuros.

---

# 170. Retention Policy

Guardar resultados externos no nosso storage conforme política.

---

# 171. Temporary Files

Arquivos temporários de geração deverão ser removidos.

---

# 172. Checksum Deduplication

Antes de duplicar storage:

```text id="gl84ja"
checksum
```

---

# 173. Cache

Resultados determinísticos ou metadata podem usar cache.

Não cachear geração criativa como se fosse idempotente sem intenção.

---

# 174. Request Hash

Pode ser usado para detectar retry técnico idêntico.

---

# 175. Idempotency

Providers que suportam idempotency key deverão recebê-la.

---

# 176. Generation Idempotency

Evitar que timeout local cause duas gerações pagas sem necessidade.

---

# 177. Submission Reconciliation

Após timeout:

```text id="zdz016"
check provider job
```

antes de resubmeter.

---

# 178. Cancellation

Se provider suporta cancelamento:

```text id="xju105"
cancel_job
```

---

# 179. Cancellation Cost

Registrar eventual custo mesmo de job cancelado.

---

# 180. Provider SLA

Preparar atributos:

```text id="qwxmle"
expected_latency
max_latency
historical_p95
```

---

# 181. Production Deadline

Media Request poderá incluir:

```text id="nqdojp"
deadline_at
```

---

# 182. Deadline-Aware Routing

Se publicação próxima:

```text id="pj2s6e"
speed weight increases
```

---

# 183. Cost-Aware Deadline

Router deve equilibrar custo e prazo.

---

# 184. Channel Preferences

Canal poderá futuramente preferir:

```text id="l7w8rn"
quality first
balanced
cost first
```

---

# 185. Organization Preferences

Agência poderá configurar defaults.

---

# 186. Provider Allowlist

Admin/organização poderá restringir quais providers podem ser usados.

---

# 187. Model Allowlist

Mesmo princípio.

---

# 188. Provider Denylist

Permitir bloquear provider para cliente específico.

---

# 189. BYOK Cost Accounting

Mesmo quando cliente paga direto ao provider:

```text id="tk3oa2"
estimate usage
```

para analytics internos.

Marcar:

```text id="d5s4eu"
billed_by = customer_provider
```

---

# 190. Platform Cost

Se conta da plataforma:

```text id="35d5ng"
billed_by = platform
```

---

# 191. Margin Layer Future

Preparar separação:

```text id="zk0l4k"
provider_cost
customer_charge
```

---

# 192. Customer Credits

Fase SaaS poderá transformar custos em créditos internos.

Não fazer providers vazarem diretamente na UX.

---

# 193. User UX

Usuário comum deverá enxergar algo como:

```text id="5ka8ou"
Produzindo vídeo...
```

e não:

```text id="9q43cl"
Seedance via Kie $0.42
```

---

# 194. Advanced Mode

Futuramente pode existir transparência opcional.

---

# 195. Admin UX

Control Center deverá ter detalhe técnico completo.

---

# 196. Observability

Eventos:

```text id="km5mrw"
media.routing.started
media.routing.completed
generation.submitted
generation.completed
generation.failed
generation.fallback
budget.warning
budget.exceeded
provider.degraded
```

---

# 197. Metrics

Preparar:

```text id="fqkw4x"
provider_requests_total
provider_failures_total
provider_latency
generation_cost
generation_attempts
fallback_rate
model_approval_rate
```

---

# 198. Alertas

Admin alerts:

```text id="1bfizg"
provider outage
error spike
latency spike
cost spike
low credits
QA degradation
```

---

# 199. Cost Anomaly Detection

Futuro:

```text id="76q6zm"
project usually costs $0.80
current projected cost $4.20
```

alertar/bloquear conforme policy.

---

# 200. Quality Anomaly Detection

Exemplo:

```text id="5mi2ps"
Model X approval fell from 91% to 62%
```

Router reduz uso automaticamente.

---

# 201. Provider Drift

Detectar mudanças de comportamento.

---

# 202. Automatic Downgrade

Se provider degrada:

```text id="quczmn"
preferred → fallback
```

---

# 203. Automatic Recovery

Após saúde estabilizar:

```text id="fj56tk"
gradual recovery
```

não mandar 100% imediatamente.

---

# 204. Routing Policies Versioned

Criar:

```text id="dvt8on"
RoutingPolicy
RoutingPolicyVersion
```

quando implementação amadurecer.

---

# 205. Default Routing Policy

Exemplo:

```text id="ubuu3t"
balanced.v1
```

---

# 206. Policies Futuras

```text id="th2d2v"
cost_first.v1
quality_first.v1
fast_delivery.v1
```

---

# 207. Scene-Specific Routing

Hero scene:

```text id="p5qh9k"
quality_first
```

Background scene:

```text id="nzq6qq"
cost_first
```

---

# 208. Media Plan Integration

Media Director recomenda:

```text id="nuwrvo"
production method
quality tier
```

Router decide:

```text id="nmlwv5"
provider/model
```

---

# 209. Separation of Concerns

```text id="bj2dof"
Media Director
WHAT kind of production

Model Router
WITH WHAT infrastructure

Provider Adapter
HOW to call it
```

---

# 210. Example Full Flow

```text id="mgy4kg"
Scene 07
   ↓
Media Director
image_to_video / premium
   ↓
Prompt Engineer
prompt + references
   ↓
Media Request
   ↓
Budget Controller
approved
   ↓
Model Router
   ↓
Provider B / Model Y
   ↓
Generation Attempt
   ↓
Provider Adapter
   ↓
Output
   ↓
Storage
   ↓
Visual QA
   ↓
FAIL
   ↓
Router receives failure context
   ↓
Fallback Candidate
   ↓
Provider C / Model Z
   ↓
Output
   ↓
QA PASS
   ↓
Selected Attempt
```

---

# 211. Failure Feedback

QA failure deverá poder alimentar routing.

Exemplo:

```text id="jcprvb"
issue_type:
character_inconsistency
```

Router poderá evitar modelo com histórico ruim nesse atributo.

---

# 212. Quality Feedback Dimensions

Preparar:

```text id="3c4g6d"
anatomy
character_consistency
motion
camera
text_rendering
lip_sync
audio
visual_fidelity
```

---

# 213. Contextual Router

Futuro Router poderá aprender:

```text id="p9md8h"
For this channel + this content type + this capability
Model X performs best.
```

---

# 214. Cold Start

Sem histórico:

```text id="cxjtas"
use platform benchmark
```

---

# 215. Warm Start

Após dados suficientes:

```text id="40vo49"
channel-specific performance
```

pode receber maior peso.

---

# 216. Minimum Sample Size

Não mudar routing drasticamente com 2 gerações.

---

# 217. Exploration

Router poderá reservar pequeno percentual para testar alternativas.

Exemplo:

```text id="wcfqjv"
95% proven models
5% exploration
```

somente se policy permitir.

---

# 218. No Exploration Near Deadline

Se conteúdo crítico:

```text id="cbm5id"
use proven route
```

---

# 219. No Exploration in Autopilot Critical Content

Configuração possível.

---

# 220. Model Retirement

Status:

```text id="5bhy8w"
deprecated
retired
```

---

# 221. Existing Projects

Projeto já iniciado poderá continuar usando modelo original se ainda disponível.

---

# 222. Forced Migration

Se modelo removido:

```text id="guhfbi"
fallback route
```

com registro.

---

# 223. Documentation

Manter:

```text id="x0cfmf"
/docs/providers.md
```

Contendo:

```text id="egwpuq"
providers
models
capabilities
routing
pricing
fallbacks
health
cost accounting
```

---

# 224. Provider Adapter Documentation

Cada adapter deve documentar:

```text id="5jw6jx"
authentication
supported capabilities
sync/async
webhooks
errors
rate limits
pricing source
known limitations
```

---

# 225. Tests

Cada provider adapter deverá possuir:

```text id="uosced"
unit tests
contract tests
mock tests
error mapping tests
```

---

# 226. Fake Provider

Criar:

```text id="h6h789"
FakeMediaProvider
```

para desenvolvimento.

---

# 227. Fake Async Provider

Simular:

```text id="9afmia"
queued
processing
completed
failed
```

---

# 228. Router Tests

Testar:

```text id="o8s4rf"
capability filtering
budget filtering
provider outage
cost selection
quality selection
fallback
hard requirements
```

---

# 229. Budget Tests

Testar concorrência e reservation.

---

# 230. Cost Accuracy Tests

Validar estimativas conhecidas.

---

# 231. Integration Tests

Provider real somente em suite opcional com credenciais.

Nunca necessário para testes básicos.

---

# 232. Contract Tests

Garantir que todos adapters retornem o mesmo contrato normalizado.

---

# 233. Feature Flags

Exemplos:

```text id="vvu2oj"
MEDIA_ROUTER_ENABLED
MULTI_PROVIDER_ENABLED
PROVIDER_HIGGSFIELD_ENABLED
PROVIDER_KIE_ENABLED
COST_ROUTING_ENABLED
QUALITY_ROUTING_ENABLED
```

---

# 234. MVP Provider Strategy

Para primeira versão funcional:

```text id="yz9gs4"
1 provider principal
1 provider fallback
Fake provider para testes
```

Não integrar cinco providers de imediato.

---

# 235. Ordem Recomendada

Primeiro:

```text id="bgeuu3"
FakeMediaProvider
```

Depois:

```text id="3eb42u"
Provider A
```

Depois:

```text id="ts7cc0"
Provider B
```

Então:

```text id="h0nm0f"
multi-provider routing
```

---

# 236. Provider Selection no MVP

Inicialmente poderá ser:

```text id="f3wo8t"
priority + capability + budget
```

Depois evoluir para score completo.

---

# 237. Não Overengineer Inicialmente

O destino arquitetural é sofisticado.

A primeira implementação deve ser mínima, porém compatível.

---

# 238. Relação com as Fases

Principalmente:

```text id="gxau5e"
F13
Provider Registry
Media Gateway
Adapters
Model Registry

F14
Model Router
Pricing
Cost Controller
Budget
Fallback

F15
Production integration
Storage
Assets
Media Processing

F16
QA feedback into routing

F20
Billing/margin/customer credits
```

---

# 239. Critérios de Aceite da Fase 13

Quando implementada, deverá ser possível:

```text id="gq3cyv"
create media request
↓
resolve provider/model
↓
submit generation
↓
track status
↓
store output
↓
register generation attempt
```

ao menos com Fake Provider e um provider real.

---

# 240. Critérios de Aceite da Fase 14

Deverá ser possível:

```text id="ou90bb"
compare eligible models
estimate cost
enforce budget
select route
retry
fallback
record costs
```

---

# 241. Critérios de Aceite de Resiliência

Simular:

```text id="mf5pkx"
primary provider unavailable
```

e confirmar:

```text id="nmh46j"
fallback used
workflow continues
cost tracked
event logged
```

---

# 242. Critério de Vendor Independence

Trocar provider principal não deverá exigir alterar:

```text id="afhbgw"
ProjectService
SceneService
Workflow business logic
```

Apenas configuração/adapter/router.

---

# 243. Critério de Cost Tracking

Toda geração deverá permitir responder:

```text id="1e3lkj"
Quanto custou?
Qual provider?
Qual modelo?
Quantas tentativas?
Qual tentativa foi aprovada?
```

---

# 244. Critério de Explainability

Toda seleção automática deverá permitir responder:

```text id="5vw89g"
Por que este provider/modelo foi escolhido?
```

---

# 245. Critério de Safety

Nenhum agent poderá fornecer credencial diretamente ao provider.

Credenciais são resolvidas apenas pela infraestrutura segura.

---

# 246. Critério de Recovery

Se aplicação reiniciar enquanto provider processa:

```text id="zt4pno"
provider_job_id
```

deve permitir retomar/reconciliar.

---

# 247. Critério de Idempotência

Timeout de request não poderá automaticamente causar duplicação de job pago.

---

# 248. Critério de Storage

Output aprovado deve ser copiado para storage controlado pela plataforma.

---

# 249. Critério de Histórico

Tentativas falhas permanecem registradas.

---

# 250. Fluxo Final Esperado

```text id="zgq10p"
MEDIA REQUIREMENT
      ↓
CAPABILITY
      ↓
ELIGIBILITY FILTER
      ↓
BUDGET CHECK
      ↓
ROUTING SCORE
      ↓
PROVIDER / MODEL
      ↓
GENERATION
      ↓
VALIDATION
      ↓
QUALITY
      ↓
PASS?
 ┌────┴────┐
 YES       NO
 ↓          ↓
ASSET     RETRY/FALLBACK
 ↓
PROJECT
```

---

# 251. Princípio Final

A infraestrutura multimídia deverá ser tratada como um mercado dinâmico de capacidade computacional e modelos.

O sistema deve ser capaz de:

```text id="ug3wb0"
escolher
comparar
substituir
recuperar
medir
aprender
otimizar
```

sem expor essa complexidade ao usuário final.

O produto não deve ser:

```text id="y9g53z"
uma interface para um provider
```

mas sim:

```text id="wzbf9w"
uma plataforma de orquestração que utiliza os melhores providers disponíveis para cumprir uma intenção de produção.
```

Este documento deverá permanecer como referência obrigatória durante todas as fases relacionadas a IA, mídia, MCPs, geração, custos e infraestrutura externa.