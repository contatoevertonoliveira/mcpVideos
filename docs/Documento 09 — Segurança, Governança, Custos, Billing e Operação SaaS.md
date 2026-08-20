# Documento 09 — Segurança, Governança, Custos, Billing e Operação SaaS

## 1. Objetivo

Este documento define as regras obrigatórias para transformar a plataforma em um SaaS seguro, controlável e comercialmente sustentável.

Ele cobre:

- autenticação;
- autorização;
- multi-tenancy;
- OAuth;
- proteção de secrets;
- isolamento de dados;
- auditoria;
- rate limiting;
- quotas;
- budgets;
- billing;
- planos;
- consumo;
- limites operacionais;
- Autopilot seguro;
- incidentes;
- observabilidade;
- governança administrativa.

A regra central é:

**nenhuma automação pode existir sem limites técnicos, financeiros e de autorização claramente definidos.**

---

# 2. Princípio de Segurança

Segurança deverá ser aplicada em camadas:

```text
Authentication
      ↓
Authorization
      ↓
Tenant Isolation
      ↓
Policy Enforcement
      ↓
Resource Ownership
      ↓
Audit
      ↓
Operational Controls
```

---

# 3. Authentication

A plataforma deverá possuir autenticação própria.

Separar:

```text
Platform Authentication
```

de:

```text
YouTube / External Provider Authorization
```

---

# 4. Usuários

Estados:

```text
active
pending
suspended
disabled
```

Usuário suspenso não deverá continuar operando automações.

---

# 5. Senhas

Quando autenticação por senha existir:

- usar hashing forte;
- nunca armazenar senha em texto;
- nunca logar senha;
- nunca retornar hash pela API.

---

# 6. Sessões

Sessões deverão possuir:

```text
session_id
user_id
created_at
expires_at
last_seen_at
revoked_at
```

quando aplicável.

---

# 7. Session Revocation

Usuário deverá poder:

```text
logout
logout all devices
```

futuramente.

---

# 8. Multi-Factor Authentication

Preparar arquitetura para MFA futuro.

Não obrigatório no MVP.

---

# 9. Organizations

A organização será a principal unidade de tenant.

Toda entidade privada deverá pertencer direta ou indiretamente a:

```text
organization_id
```

---

# 10. Tenant Isolation

Regra obrigatória:

```text
User A / Org A
```

nunca poderá acessar:

```text
Org B
```

mesmo que descubra UUID de recurso.

---

# 11. Authorization Layer

Criar camada dedicada de autorização.

Exemplo:

```text
AuthorizationService
```

---

# 12. Roles

Inicialmente:

```text
owner
admin
editor
viewer
```

---

# 13. Owner

Pode:

```text
billing
organization settings
members
channels
automation
destructive actions
```

---

# 14. Admin

Pode operar quase toda a organização, exceto ações reservadas ao owner conforme policy.

---

# 15. Editor

Pode:

```text
ideas
calendar
projects
reviews
content metadata
```

---

# 16. Viewer

Somente leitura.

---

# 17. Permission Model

Preparar permissões granulares futuras.

Exemplos:

```text
channel.read
channel.manage
content.create
content.approve
publication.approve
autopilot.manage
billing.manage
member.manage
```

---

# 18. Backend Enforcement

Permissões deverão ser validadas no backend.

Nunca confiar apenas em UI escondendo botões.

---

# 19. Resource Ownership

Antes de acessar um recurso:

```text
resource.organization_id
==
current_organization.id
```

deve ser validado.

---

# 20. Google / YouTube OAuth

Conexão do canal deverá usar OAuth.

Tokens deverão ser armazenados de maneira segura.

---

# 21. Token Fields

```text
access_token_encrypted
refresh_token_encrypted
token_expires_at
scopes
```

---

# 22. Encryption

Tokens e secrets sensíveis deverão utilizar criptografia em repouso.

Não apenas base64.

---

# 23. Encryption Key

Chave de criptografia não deverá estar no banco.

Utilizar:

```text
environment secret
```

inicialmente.

Futuramente:

```text
KMS
Vault
Secrets Manager
```

---

# 24. OAuth Scopes

Solicitar apenas scopes necessários.

Princípio:

```text
least privilege
```

---

# 25. Reauthorization

Se token for revogado:

```text
channel_connection.status = reauthorization_required
```

---

# 26. Publication Stop

Canal sem credencial válida:

```text
não publica
```

---

# 27. Secret Redaction

Logs devem automaticamente remover:

```text
Authorization
access_token
refresh_token
api_key
password
secret
```

---

# 28. Provider Credentials

Credenciais externas deverão usar:

```text
ProviderCredentialResolver
```

e não ser entregues a agents.

---

# 29. BYOK

Quando Bring Your Own Key existir:

```text
organization scoped
encrypted
access controlled
```

---

# 30. BYOK Verification

Ao cadastrar:

```text
validate credential
```

sem retornar secret novamente.

---

# 31. Secret Rotation

Preparar suporte para:

```text
rotation
```

sem destruir integrações.

---

# 32. Environment Separation

Ambientes:

```text
development
staging
production
```

Nunca compartilhar credenciais de produção com development.

---

# 33. Database Security

Banco não deverá ser publicamente acessível.

---

# 34. Redis Security

Redis também deverá ficar em rede privada quando produção.

---

# 35. Object Storage

Assets deverão usar:

```text
private bucket
```

por padrão.

---

# 36. Signed URLs

Preview/download poderá usar URLs temporárias.

---

# 37. Public Assets

Somente quando necessário.

---

# 38. File Upload Security

Validar:

```text
MIME
size
dimensions
content type
```

e sanitizar nomes.

---

# 39. File Names

Não utilizar nome enviado pelo usuário como storage key final.

Gerar UUID/key própria.

---

# 40. Malware Scanning

Preparar integração futura para scan.

Especialmente para uploads empresariais.

---

# 41. API Security

Todas as APIs privadas deverão exigir autenticação.

---

# 42. Rate Limiting

Aplicar rate limit por:

```text
IP
user
organization
endpoint
```

conforme necessidade.

---

# 43. Heavy Endpoints

Endpoints que iniciam operações pagas deverão possuir limites mais rígidos.

---

# 44. AI Operation Limits

Exemplo:

```text
max generations/minute
max concurrent projects
```

---

# 45. Provider Quotas

Controlar:

```text
request quotas
credit quotas
provider-specific rate limits
```

---

# 46. YouTube Quota

Criar registro de consumo aproximado/real quando disponível.

---

# 47. Quota Guard

Antes de ação externa:

```text
check available quota
```

---

# 48. Abuse Protection

Evitar scripts de usuário disparando milhares de gerações via API.

---

# 49. Idempotency

Operações financeiras e externas críticas deverão exigir idempotência.

---

# 50. Audit Logs

Registrar ações críticas:

```text
login
channel connected
channel disconnected
autopilot changed
budget changed
content approved
publication approved
publication executed
provider credential changed
member changed
```

---

# 51. Audit Actor

```text
user
system
agent
worker
admin
```

---

# 52. Audit Log Immutability

Preferir append-only.

---

# 53. Audit Retention

Definir política futura por plano/regulação.

---

# 54. Sensitive Audit Data

Não guardar secret em metadata.

---

# 55. Admin Actions

Toda ação administrativa sobre cliente deve ser auditada.

---

# 56. Support Access

Se admin acessar organização para suporte:

```text
record who
when
why
```

---

# 57. Impersonation

Se implementado:

```text
explicit
temporary
audited
```

---

# 58. Automation Governance

Autopilot deverá operar sempre sob:

```text
AutomationPolicy
```

---

# 59. Automation Policy

Campos possíveis:

```text
max_publications_per_day
max_shorts_per_day
max_longform_per_week
max_daily_cost
max_monthly_cost
minimum_quality_score
allowed_formats
allowed_topics
blocked_topics
allowed_publish_hours
auto_publish_enabled
human_review_threshold
```

---

# 60. Safe Default

Novo canal:

```text
auto_publish = false
```

---

# 61. Autopilot Activation

Requer aprovação explícita do usuário autorizado.

---

# 62. Autopilot Scope

Autopilot poderá ser ativado:

```text
organization
channel
```

Preferir por canal inicialmente.

---

# 63. Emergency Pause

Criar botão e backend:

```text
pause automation
```

---

# 64. Pause Effects

Ao pausar:

```text
não iniciar novos projetos automáticos
não agendar novas publicações automáticas
não publicar automaticamente
```

---

# 65. Existing Jobs

Política deverá definir se:

```text
continuam
```

ou:

```text
pausam no próximo checkpoint seguro
```

---

# 66. Automatic Pause Conditions

Exemplos:

```text
budget exceeded
OAuth revoked
publication failures repeated
quality failures repeated
provider outage
billing suspended
policy violation
```

---

# 67. Critical Pause

Casos como:

```text
billing suspended
OAuth revoked
security incident
```

não deverão auto-resumir.

---

# 68. Budget Model

Budgets poderão existir em:

```text
organization
channel
project
```

---

# 69. Budget Types

```text
soft warning
hard limit
```

---

# 70. Soft Warning

Exemplo:

```text
80%
```

gera alerta.

---

# 71. Hard Limit

Exemplo:

```text
100%
```

bloqueia nova operação paga.

---

# 72. Budget Reservation

Operações concorrentes deverão reservar custo estimado.

---

# 73. Reservation State

```text
reserved
consumed
released
expired
```

---

# 74. Budget Reconciliation

Após geração:

```text
estimated
vs
actual
```

ajustar reserva.

---

# 75. Overspend Guard

Nenhuma operação deve ultrapassar hard limit sem override autorizado.

---

# 76. Override

Override deve registrar:

```text
who
why
amount
timestamp
```

---

# 77. Cost Categories

```text
LLM
image
video
voice
music
render
storage
external APIs
```

---

# 78. Cost Attribution

Todo custo deve ser atribuível a:

```text
organization
channel
project
scene
attempt
provider
model
```

quando aplicável.

---

# 79. Cost Event

Cada cobrança externa:

```text
CostEvent
```

---

# 80. Cost Accuracy

Guardar:

```text
estimated_cost
actual_cost
```

---

# 81. Cost Currency

Guardar moeda original.

---

# 82. Billing Currency

Separar moeda cobrada ao cliente.

---

# 83. Plans

Criar entidade:

```text
plans
```

---

# 84. Plan Fields

```text
name
monthly_price
currency
features
limits
active
```

---

# 85. Plan Limits

Exemplos:

```text
channels
monthly shorts
monthly videos
storage
AI credits
team members
autopilot availability
analytics retention
```

---

# 86. Não Amarrar Plano a Provider

Cliente compra capacidade do produto.

Não:

```text
500 créditos Higgsfield
```

Preferir:

```text
60 Shorts/mês
```

ou sistema interno de créditos.

---

# 87. Internal Credits

Poderão existir posteriormente.

---

# 88. Credit Abstraction

Se utilizado:

```text
Customer Credit
```

não deve corresponder diretamente a crédito de provider específico.

---

# 89. Subscriptions

Estados:

```text
trialing
active
past_due
suspended
cancelled
expired
```

---

# 90. Subscription Enforcement

Se suspenso:

```text
new paid automation blocked
```

---

# 91. Existing Data

Nunca apagar conteúdo automaticamente por inadimplência.

---

# 92. Grace Period

Pode existir conforme política comercial.

---

# 93. Billing Provider

Manter abstração:

```text
BillingGateway
```

---

# 94. Billing Provider Independence

Não espalhar lógica de Stripe/Mercado Pago/etc. pelo domínio.

---

# 95. Billing Events

Exemplos:

```text
subscription.created
subscription.renewed
subscription.past_due
subscription.cancelled
payment.failed
```

---

# 96. Webhooks de Billing

Devem ser:

```text
validated
idempotent
audited
```

---

# 97. Usage Events

Registrar consumo:

```text
short generated
video generated
voice seconds
AI tokens
storage
```

---

# 98. Usage Aggregation

Calcular uso mensal.

---

# 99. Usage Enforcement

Antes de operação:

```text
check plan limit
```

---

# 100. Burst Policy

Pode permitir tolerância pequena configurável.

---

# 101. Overage

Futuro:

```text
block
charge overage
upgrade prompt
```

dependendo do plano.

---

# 102. Billing Dashboard

Usuário vê:

```text
plan
usage
limits
next renewal
```

---

# 103. Internal Margin

Admin deverá poder calcular:

```text
customer revenue
-
provider cost
-
infra cost
=
gross margin
```

---

# 104. Margin per Organization

Métrica futura importante.

---

# 105. Margin per Content Type

Exemplo:

```text
Short margin
Long-form margin
```

---

# 106. Cost Anomaly

Detectar:

```text
usual project cost = $1
current = $6
```

---

# 107. Anomaly Action

```text
warn
pause
human review
```

conforme policy.

---

# 108. Fraud / Abuse Signals

Preparar futuro monitoramento:

```text
sudden generation spikes
multiple failed payment accounts
mass API calls
```

---

# 109. Trial Abuse

Se houver trial, limitar:

```text
channels
generation volume
autopilot
```

---

# 110. API Keys para Clientes

Futuro.

Se expor API pública:

```text
scoped keys
rate limits
rotation
revocation
```

---

# 111. Service-to-Service Auth

Em arquitetura distribuída futura:

```text
signed internal tokens
mTLS
```

quando necessário.

---

# 112. Internal Services

Não expor Celery/Redis/worker endpoints publicamente.

---

# 113. Network Segmentation

Produção:

```text
public frontend/API
private DB/Redis/workers
```

---

# 114. CORS

Configurar explicitamente.

---

# 115. CSRF

Se autenticação baseada em cookie:

```text
CSRF protection
```

---

# 116. XSS

Escapar conteúdo de usuário adequadamente.

---

# 117. SQL Injection

Utilizar ORM/parametrização.

Nunca construir SQL com string de usuário.

---

# 118. Shell Injection

FFmpeg e processos:

```text
argument arrays
validation
```

---

# 119. SSRF

Uploads/imports externos deverão validar URLs.

---

# 120. URL Allowlist

Quando recurso acessar URLs externas sensíveis.

---

# 121. Prompt Injection

Conteúdo externo deve ser tratado como dados.

---

# 122. Agent Tools

Somente allowlist.

---

# 123. Agents e Secrets

Agents nunca recebem:

```text
provider credentials
OAuth tokens
database passwords
```

---

# 124. Agents e Authorization

Agent não decide se usuário tem permissão.

Service decide antes.

---

# 125. Data Privacy

Guardar apenas dados necessários para operação.

---

# 126. Analytics Privacy

Não armazenar informação individual de audiência além do necessário/disponível.

---

# 127. Data Retention

Criar política por tipo:

```text
audit
analytics
raw provider payloads
media
logs
```

---

# 128. Raw Provider Payload

Pode conter dados excessivos.

Revisar e limitar retenção.

---

# 129. User Data Export

Preparar arquitetura para futuro:

```text
export organization data
```

---

# 130. Account Deletion

Futuro fluxo deverá respeitar:

```text
soft delete
retention obligations
billing records
audit
```

---

# 131. Backup

PostgreSQL:

```text
scheduled backups
```

---

# 132. Restore Testing

Backup sem teste de restore não é suficiente.

---

# 133. Object Storage Backup

Definir política.

---

# 134. Disaster Recovery

Documentar:

```text
RPO
RTO
```

quando produção amadurecer.

---

# 135. Monitoring

Monitorar:

```text
API health
DB
Redis
workers
providers
publication
billing
```

---

# 136. Alerts

Criticidade:

```text
INFO
WARNING
HIGH
CRITICAL
```

---

# 137. Critical Alerts

Exemplos:

```text
database unavailable
publication duplication risk
billing provider failure
OAuth mass failures
security incident
```

---

# 138. Operational Metrics

```text
active workflows
failed workflows
queue depth
provider latency
publication failures
cost rate
```

---

# 139. Security Events

Criar:

```text
security.login_failed
security.permission_denied
security.suspicious_activity
```

---

# 140. Login Rate Limit

Proteção contra brute force.

---

# 141. Password Reset

Se implementado:

```text
single-use
expiring token
```

---

# 142. Email Verification

Pode ser exigida antes de conectar canal.

---

# 143. Organization Creation Limit

Evitar abuso em trial.

---

# 144. Channel Connection Limit

Conforme plano.

---

# 145. Concurrent Automation Limit

Conforme plano.

---

# 146. Publication Limits

Mesmo no Autopilot:

```text
max per day
max per week
```

---

# 147. Frequency Guard

Não permitir accidentalmente:

```text
100 uploads/day
```

por erro de scheduler.

---

# 148. Duplicate Publication Guard

Verificar:

```text
same project
same asset
same external ID
idempotency key
```

---

# 149. Scheduling Collision Guard

Evitar dois jobs publicando mesmo conteúdo.

---

# 150. Billing Before Expensive Operation

Dependendo do modelo comercial:

```text
subscription valid
usage available
budget available
```

antes de gerar.

---

# 151. Quality Before Publication

Regra:

```text
billing OK
```

não é suficiente.

Também:

```text
policy
quality
authorization
```

---

# 152. Publication Eligibility

```text
Account Active
+
Channel Connected
+
Subscription Valid
+
Automation Policy Allows
+
Quality Passed
+
Content Ready
+
Schedule Valid
```

---

# 153. Human Approval Eligibility

Usuário precisa possuir permission:

```text
publication.approve
```

---

# 154. Autopilot Approval

Registrar:

```text
approved_by = policy
```

ou equivalente.

---

# 155. Safety Review

Conteúdo crítico não pode ser bypassado por billing tier.

---

# 156. Plan Não Pode Reduzir Segurança

Planos mais caros podem dar:

```text
mais volume
mais automação
```

não:

```text
menos safety
```

---

# 157. Child-Directed Channel Policy

Canais classificados como infantis podem ter policy adicional.

---

# 158. Policy Versioning

Criar versões de:

```text
AutomationPolicy
QualityPolicy
PlatformPolicy
```

---

# 159. Policy Audit

Registrar qual versão aprovou publicação.

---

# 160. Terms Acceptance

Futuro:

```text
terms_version
accepted_at
```

---

# 161. Privacy Acceptance

Mesmo princípio.

---

# 162. Billing Compliance

Faturamento/fiscalização será tratado conforme mercado alvo.

Arquitetura deve evitar hardcoding local prematuro.

---

# 163. Localization

Planos podem ter:

```text
currency
country
tax configuration
```

futuramente.

---

# 164. SaaS Control Center

Admin deverá poder ver:

```text
organizations
subscriptions
usage
cost
margin
providers
incidents
security
```

---

# 165. Organization Risk View

Exemplo:

```text
budget high
publication failures
OAuth issue
billing overdue
```

---

# 166. Suspend Organization

Admin autorizado poderá suspender.

---

# 167. Suspension Effect

```text
login may remain read-only
new operations blocked
publishing blocked
```

conforme policy.

---

# 168. Read-Only Mode

Pode ser útil para billing.

---

# 169. Provider Cost Spike

Se preço mudar:

```text
router adapts
```

e admin recebe alerta.

---

# 170. Plan Cost Sustainability

Antes de definir plano comercial, calcular:

```text
expected provider cost
+
retry rate
+
infra
+
support
+
margin
```

---

# 171. Do Not Sell Unlimited Prematurely

Plano ilimitado é risco enquanto custo variável não for bem conhecido.

---

# 172. Cost Ceiling

Todo plano deverá ter mecanismos de limite interno.

---

# 173. Usage Forecast

Calcular:

```text
current usage
projected month-end usage
```

---

# 174. Spend Forecast

Mesmo princípio.

---

# 175. Margin Forecast

Admin only.

---

# 176. Billing Separation

```text
Usage Accounting
```

e:

```text
Payment Processing
```

devem ser módulos separados.

---

# 177. Invoice Data

Futuro:

```text
invoices
```

não necessário até billing real.

---

# 178. Plan Entitlements

Criar serviço:

```text
EntitlementService
```

---

# 179. Entitlement Examples

```text
can_use_autopilot
max_channels
max_team_members
can_use_premium_models
analytics_retention_days
```

---

# 180. Feature Flags vs Entitlements

Diferenciar:

```text
Feature Flag
= lançamento/operação
```

```text
Entitlement
= direito do plano
```

---

# 181. Authorization vs Entitlement

Diferenciar:

```text
Authorization
= usuário pode fazer?
```

```text
Entitlement
= organização comprou esse recurso?
```

---

# 182. Example

Usuário admin pode ter permissão de Autopilot.

Mas se plano não possuir:

```text
EntitlementService = false
```

---

# 183. Plan Change

Upgrade:

```text
new entitlements active
```

---

# 184. Downgrade

Não apagar dados.

Recursos excedentes podem ficar:

```text
read-only
paused
```

---

# 185. Graceful Downgrade

Exemplo:

3 canais conectados, plano novo permite 1.

Não deletar canais.

Pedir seleção ou pausar extras.

---

# 186. Billing Webhook Failure

Criar reconciliation periódico.

---

# 187. Payment State Source of Truth

Billing provider + nosso banco reconciliado.

---

# 188. Never Trust Frontend for Payment

Frontend nunca ativa plano sozinho.

---

# 189. Incident Management

Criar conceito:

```text
Incident
```

futuramente.

---

# 190. Incident Types

```text
provider outage
publication failure
billing outage
security event
data issue
```

---

# 191. Incident Timeline

Registrar eventos e ações.

---

# 192. Kill Switch

Admin deverá poder:

```text
disable auto publish globally
disable provider
disable feature
```

sem deploy.

---

# 193. Global Auto-Publish Kill Switch

Muito importante.

---

# 194. Kill Switch Priority

Deve prevalecer sobre channel policy.

---

# 195. Maintenance Mode

Futuro.

---

# 196. Readiness Checks

Antes de deploy, validar:

```text
DB
Redis
storage
critical secrets
```

---

# 197. Migration Safety

Backup e teste para migrations destrutivas.

---

# 198. Zero-Downtime Aspirational

Não obrigatório no MVP, mas evitar migrations que bloqueiem desnecessariamente.

---

# 199. Secrets in CI/CD

Nunca colocar secrets no repositório.

---

# 200. Dependency Security

Executar scans de dependências no CI futuramente.

---

# 201. Security Headers

Frontend/API deverão utilizar headers apropriados.

---

# 202. HTTPS

Produção somente HTTPS.

---

# 203. Cookie Security

Quando usado:

```text
Secure
HttpOnly
SameSite
```

adequadamente.

---

# 204. Data Access Logs

Acesso administrativo sensível poderá ser auditado.

---

# 205. PII Minimization

Guardar apenas dados pessoais necessários.

---

# 206. Security Documentation

Manter:

```text
/docs/security.md
```

---

# 207. Billing Documentation

Manter:

```text
/docs/billing.md
```

---

# 208. Operations Documentation

Manter:

```text
/docs/operations.md
```

---

# 209. Runbooks

Criar futuramente:

```text
provider outage
YouTube publication failure
OAuth outage
billing outage
budget incident
```

---

# 210. Security Checklist por Fase

Toda fase deve verificar:

```text
auth
authorization
tenant isolation
secret exposure
audit
rate limits
```

quando aplicável.

---

# 211. Definition of Done — External Integration

Só considerada pronta quando:

```text
credentials encrypted
timeouts
error handling
rate limit
audit
tests
```

---

# 212. Definition of Done — Paid Operation

Só pronta quando:

```text
entitlement checked
budget checked
usage tracked
cost tracked
idempotency
```

---

# 213. Definition of Done — Autopilot Feature

Só pronta quando:

```text
policy
limits
pause
audit
quality gate
budget
human escalation
```

existirem.

---

# 214. Definition of Done — Billing

Só pronta quando:

```text
plan
subscription
webhook validation
reconciliation
entitlements
usage
graceful failure
```

estiverem funcionando.

---

# 215. Fases Relacionadas

Principalmente:

```text
F02
multi-tenancy

F03
authentication/security

F04
OAuth

F13–15
provider credentials/cost

F18
publication safety

F20
plans/subscriptions/billing/admin
```

---

# 216. MVP Security Priority

Antes de qualquer Autopilot real:

```text
tenant isolation
auth
OAuth encryption
publication idempotency
budget limits
audit logs
```

devem estar maduros.

---

# 217. MVP Billing

Pode começar simples:

```text
plan
limits
manual subscription status
usage
```

antes de integração com pagamento.

---

# 218. Não Bloquear Desenvolvimento por Billing

Billing completo pertence à Fase 20.

Mas arquitetura deve estar preparada desde o início.

---

# 219. User Trust Principle

Usuário deve saber:

```text
o que está conectado
o que está automatizado
quanto pode gastar
o que pode ser publicado
como pausar
```

---

# 220. Admin Trust Principle

Admin deve conseguir responder:

```text
quem executou?
quem autorizou?
quanto custou?
qual policy permitiu?
qual integração foi usada?
como interromper?
```

---

# 221. SaaS Sustainability Principle

Nenhum plano comercial deverá ser lançado sem conhecer:

```text
average cost per short
average cost per video
retry rate
QA approval rate
storage cost
provider variance
```

---

# 222. Cost Benchmark

Antes de pricing final:

```text
simulate real workloads
```

---

# 223. Unit Economics

Monitorar:

```text
ARPU
COGS
gross margin
cost per organization
cost per published content
```

---

# 224. Autopilot Unit Economics

Especial atenção porque gera consumo sem ação manual do usuário.

---

# 225. Autopilot Spend Guard

Sempre existir:

```text
daily cap
monthly cap
project cap
```

---

# 226. No Infinite Retry

Regra financeira e operacional.

---

# 227. No Infinite Generation

Mesmo princípio.

---

# 228. No Infinite Planning

Idea/strategy agents também precisam limites.

---

# 229. Security Before Convenience

Nunca simplificar UX removendo controle crítico.

---

# 230. Simplicidade Externa, Rigor Interno

Usuário vê:

```text
Budget mensal: R$ 300
```

Internamente:

```text
reservations
cost events
provider pricing
actuals
forecast
```

---

# 231. Final SaaS Architecture

```text
USER
  ↓
AUTH
  ↓
ORGANIZATION
  ↓
ENTITLEMENTS
  ↓
POLICIES
  ↓
WORKFLOWS
  ↓
BUDGET
  ↓
PROVIDERS
  ↓
QUALITY
  ↓
PUBLICATION
  ↓
USAGE
  ↓
BILLING
  ↓
AUDIT
```

---

# 232. Final Governance Rule

Nenhuma ação de alto impacto deverá depender apenas de um output de IA.

Ações como:

```text
publicar
gastar
alterar policy
mudar billing
conectar credencial
```

devem passar obrigatoriamente por código determinístico, permissões e policies.

---

# 233. Instrução ao Claude Code

Ao implementar qualquer recurso SaaS ou integração sensível:

1. identificar tenant;
2. verificar autenticação;
3. verificar autorização;
4. verificar entitlement;
5. verificar policy;
6. verificar budget se houver custo;
7. executar operação;
8. registrar usage;
9. registrar cost;
10. registrar audit;
11. emitir evento;
12. tratar retry/idempotência;
13. não expor secret;
14. criar testes de isolamento;
15. criar testes de permissão;
16. criar testes de falha.

---

# 234. Princípio Final

A plataforma deverá ser capaz de operar automaticamente em escala sem perder:

```text
controle
segurança
previsibilidade
rastreabilidade
sustentabilidade financeira
```

Autonomia sem governança será considerada falha arquitetural.

Este documento deverá permanecer como referência obrigatória durante todas as fases de autenticação, integrações, custos, Autopilot, billing e operação SaaS.