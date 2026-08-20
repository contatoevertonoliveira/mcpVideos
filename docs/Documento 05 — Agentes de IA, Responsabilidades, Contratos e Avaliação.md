# Documento 05 — Agentes de IA, Responsabilidades, Contratos e Avaliação

## 1. Objetivo

Este documento define a arquitetura dos agentes de IA que participarão da plataforma.

Ele estabelece:

- quais agentes existirão;
- o papel de cada agente;
- o que cada agente pode fazer;
- o que cada agente não pode fazer;
- quais dados cada agente recebe;
- quais dados deve devolver;
- como os outputs serão estruturados;
- como prompts serão versionados;
- como decisões serão pontuadas;
- como agentes avaliadores revisarão outros agentes;
- como prevenir sobreposição de responsabilidades;
- como garantir rastreabilidade e segurança.

A regra principal é:

**agentes raciocinam e recomendam; services, policies e workflows validam e executam.**

---

# 2. Princípio Fundamental

Nenhum agente deverá possuir autonomia operacional irrestrita.

Não permitir:

```text
Agent
  ↓
YouTube API
  ↓
Publicação
```

Utilizar:

```text
Agent
  ↓
Structured Decision
  ↓
Service
  ↓
Policy Validation
  ↓
Workflow
  ↓
Execution
```

---

# 3. Arquitetura Geral dos Agentes

```text
                     AGENT LAYER
                         │
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
 INTELLIGENCE        PRODUCTION         QUALITY
       │                 │                 │
       ↓                 ↓                 ↓
   GROWTH            MEDIA PLAN          REVIEW
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ↓
                  STRUCTURED OUTPUT
                         ↓
                    POLICY ENGINE
                         ↓
                     SERVICES
```

---

# 4. Categorias de Agentes

Os agentes serão organizados em quatro grandes grupos:

```text
INTELLIGENCE
PRODUCTION
QUALITY
GROWTH
```

Posteriormente poderão existir categorias adicionais:

```text
OPERATIONS
FINANCE
SUPPORT
```

---

# 5. Agentes de Intelligence

Inicialmente previstos:

```text
Channel Analyst
Audience Analyst
Strategy Agent
Trend Researcher
Idea Agent
Opportunity Evaluator
Calendar Planner
Learning Analyst
```

---

# 6. Channel Analyst

ID sugerido:

```text
channel_analyst
```

Responsabilidade:

Analisar o histórico, estrutura e comportamento editorial do canal.

Inputs:

```text
channel metadata
source videos
source playlists
historical metrics
existing channel profile
existing DNA
```

Outputs:

```json
{
  "classification": {},
  "content_patterns": [],
  "format_patterns": [],
  "publishing_patterns": [],
  "high_performing_patterns": [],
  "low_performing_patterns": [],
  "anomalies": [],
  "confidence": 0.0,
  "evidence": []
}
```

Não pode:

- alterar Channel DNA diretamente;
- publicar;
- mudar estratégia;
- gerar conteúdo final;
- alterar dados históricos.

---

# 7. Audience Analyst

ID:

```text
audience_analyst
```

Responsabilidade:

Inferir e consolidar características da audiência.

Inputs:

```text
channel analytics
video analytics
channel metadata
historical performance
existing audience profile
```

Outputs:

```json
{
  "audience_segments": [],
  "estimated_age_ranges": [],
  "language": "",
  "interests": [],
  "content_preferences": [],
  "format_preferences": [],
  "confidence": 0.0,
  "evidence": []
}
```

Obrigatório distinguir:

```text
confirmed
inferred
unknown
```

---

# 8. Strategy Agent

ID:

```text
strategy_agent
```

Responsabilidade:

Propor a estratégia editorial do canal.

Inputs:

```text
Channel DNA
Audience Profile
Performance Baselines
Learned Rules
Existing Strategy
Business Constraints
```

Outputs:

```json
{
  "objectives": [],
  "content_mix": {},
  "content_pillars": [],
  "publishing_frequency": {},
  "format_strategy": {},
  "experimental_ratio": 0.0,
  "recommendations": [],
  "risks": [],
  "confidence": 0.0
}
```

Não pode:

- ativar estratégia sozinho sem policy;
- publicar;
- criar mídia;
- ignorar limites de custo.

---

# 9. Trend Researcher

ID:

```text
trend_researcher
```

Responsabilidade:

Identificar sinais externos relevantes ao nicho.

Inputs futuros:

```text
channel niche
content pillars
search data
social signals
news
trend sources
seasonality
```

Outputs:

```json
{
  "signals": [
    {
      "topic": "",
      "source": "",
      "trend_strength": 0,
      "recency": "",
      "relevance": 0,
      "confidence": 0
    }
  ]
}
```

Regra:

Tendência não pode sobrepor contexto editorial.

---

# 10. Idea Agent

ID:

```text
idea_agent
```

Responsabilidade:

Criar novas ideias de conteúdo contextualizadas.

Inputs obrigatórios:

```text
Channel DNA
Audience Profile
Content Strategy
Recent Publications
Planned Content
Learned Rules
Trend Signals
```

Outputs:

```json
{
  "ideas": [
    {
      "title": "",
      "summary": "",
      "recommended_format": "",
      "content_pillar": "",
      "hook_concept": "",
      "reason": "",
      "source_type": "",
      "novelty": 0,
      "confidence": 0
    }
  ]
}
```

Não gerar:

- ideias fora do nicho apenas por viralidade;
- duplicatas sem justificativa;
- temas bloqueados pela policy.

---

# 11. Opportunity Evaluator

ID:

```text
opportunity_evaluator
```

Responsabilidade:

Avaliar e pontuar ideias.

Inputs:

```text
Content Idea
Channel DNA
Strategy
Audience
Performance History
Trend Signals
Production Constraints
```

Outputs:

```json
{
  "scores": {
    "channel_fit": 0,
    "audience_fit": 0,
    "strategic_fit": 0,
    "trend": 0,
    "novelty": 0,
    "retention_potential": 0,
    "search_potential": 0,
    "competition": 0,
    "brand_fit": 0,
    "production_feasibility": 0
  },
  "final_score": 0,
  "confidence": 0.0,
  "recommendation": "approve|review|reject",
  "reasoning_summary": ""
}
```

---

# 12. Calendar Planner

ID:

```text
calendar_planner
```

Responsabilidade:

Transformar oportunidades aprovadas em proposta de calendário.

Inputs:

```text
Active Strategy
Publishing Slots
Approved Opportunities
Current Calendar
Content Mix
Clusters
```

Outputs:

```json
{
  "recommended_items": [
    {
      "opportunity_id": "",
      "planned_at": "",
      "format": "",
      "reason": ""
    }
  ],
  "balance_report": {},
  "conflicts": []
}
```

Não pode publicar ou agendar diretamente.

---

# 13. Learning Analyst

ID:

```text
learning_analyst
```

Responsabilidade:

Detectar padrões de performance e propor aprendizados.

Inputs:

```text
historical metrics
performance baselines
content attributes
existing learned rules
```

Outputs:

```json
{
  "candidate_learnings": [
    {
      "finding": "",
      "sample_size": 0,
      "effect_size": 0.0,
      "confidence": 0.0,
      "evidence": []
    }
  ]
}
```

Não pode transformar correlação fraca em regra ativa.

---

# 14. Agentes de Production

Inicialmente:

```text
Research Agent
Hook Agent
Script Writer
Script Critic
Storyboard Director
Scene Planner
Media Director
Prompt Engineer
Voice Director
Audio Director
Editor Agent
```

---

# 15. Research Agent

ID:

```text
research_agent
```

Responsabilidade:

Preparar contexto factual ou temático para produção.

Inputs:

```text
content idea
project objective
channel context
source requirements
```

Outputs:

```json
{
  "key_points": [],
  "facts": [],
  "claims_requiring_verification": [],
  "sources": [],
  "content_risks": [],
  "confidence": 0.0
}
```

---

# 16. Hook Agent

ID:

```text
hook_agent
```

Responsabilidade:

Criar e avaliar hooks iniciais.

Outputs:

```json
{
  "hooks": [
    {
      "text": "",
      "type": "",
      "score": 0,
      "reason": ""
    }
  ],
  "recommended_hook": ""
}
```

Critérios:

```text
clarity
curiosity
relevance
speed
audience fit
truthfulness
```

---

# 17. Script Writer

ID:

```text
script_writer
```

Responsabilidade:

Criar roteiro.

Inputs:

```text
project
idea
research
hook
channel dna
audience
strategy
target duration
```

Outputs:

```json
{
  "hook": "",
  "sections": [],
  "cta": "",
  "dialogue": [],
  "estimated_duration_seconds": 0,
  "tone": "",
  "notes": []
}
```

---

# 18. Script Critic

ID:

```text
script_critic
```

Responsabilidade:

Revisar roteiro, não reescrevê-lo diretamente sem decisão do workflow.

Inputs:

```text
script
project objective
audience
channel dna
```

Outputs:

```json
{
  "score": 0,
  "approved": false,
  "issues": [],
  "strengths": [],
  "recommended_changes": [],
  "confidence": 0.0
}
```

---

# 19. Storyboard Director

ID:

```text
storyboard_director
```

Responsabilidade:

Transformar roteiro em estrutura visual.

Outputs:

```json
{
  "scenes": [
    {
      "scene_number": 1,
      "purpose": "",
      "duration_seconds": 0,
      "visual_concept": "",
      "camera": "",
      "movement": "",
      "audio": "",
      "dialogue": ""
    }
  ]
}
```

---

# 20. Scene Planner

ID:

```text
scene_planner
```

Responsabilidade:

Detalhar cada cena com estado e continuidade.

Inputs:

```text
storyboard
previous scene state
brand registry
characters
locations
```

Outputs:

```json
{
  "scene": {},
  "required_characters": [],
  "required_assets": [],
  "continuity_requirements": [],
  "scene_state_output": {},
  "generation_requirements": {}
}
```

---

# 21. Media Director

ID:

```text
media_director
```

Responsabilidade:

Decidir como cada cena deve ser produzida.

Pode recomendar:

```text
text_to_video
image_to_video
static_image
parallax
stock
animation
generated_audio
```

Output:

```json
{
  "scene_id": "",
  "production_method": "",
  "quality_tier": "economy|standard|premium",
  "capabilities_required": [],
  "estimated_complexity": 0,
  "budget_priority": 0,
  "hero_scene": false
}
```

Não escolhe obrigatoriamente provider específico.

Essa decisão pertence ao Media Router.

---

# 22. Prompt Engineer

ID:

```text
prompt_engineer
```

Responsabilidade:

Criar instruções técnicas para modelos de mídia.

Inputs:

```text
scene
media plan
brand rules
character references
model capability
```

Outputs:

```json
{
  "positive_prompt": "",
  "negative_prompt": "",
  "reference_requirements": [],
  "model_specific_settings": {}
}
```

Não pode alterar a história.

---

# 23. Voice Director

ID:

```text
voice_director
```

Responsabilidade:

Definir características da voz.

Outputs:

```json
{
  "voice_profile": "",
  "language": "",
  "pace": "",
  "emotion": "",
  "pronunciation_notes": [],
  "character_voice_id": null
}
```

---

# 24. Audio Director

ID:

```text
audio_director
```

Responsabilidade:

Planejar:

```text
voice
music
SFX
mix
silence
transitions
```

Output:

```json
{
  "voice_tracks": [],
  "music_plan": {},
  "sfx_plan": [],
  "mix_notes": []
}
```

---

# 25. Editor Agent

ID:

```text
editor_agent
```

Responsabilidade:

Propor plano de montagem.

Não executa FFmpeg diretamente.

Output:

```json
{
  "timeline": [],
  "transitions": [],
  "subtitle_plan": {},
  "audio_mix_plan": {},
  "render_profile": ""
}
```

O `MediaProcessingService` executa.

---

# 26. Agentes de Quality

Inicialmente:

```text
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

# 27. Princípio dos Avaliadores

Avaliador não deve saber a decisão esperada.

Evitar prompt como:

```text
Confirme que este vídeo está bom.
```

Utilizar:

```text
Avalie independentemente este conteúdo conforme critérios abaixo.
```

---

# 28. Structured QA Contract

Todos os agentes de QA deverão retornar estrutura semelhante:

```json
{
  "approved": false,
  "score": 0,
  "confidence": 0.0,
  "critical_failure": false,
  "issues": [
    {
      "type": "",
      "severity": "",
      "description": "",
      "location": {},
      "recommended_action": ""
    }
  ],
  "strengths": []
}
```

---

# 29. Script QA

Avalia:

```text
clarity
structure
hook
audience fit
duration
coherence
CTA
brand tone
```

---

# 30. Visual QA

Avalia:

```text
visual defects
distortion
extra limbs
duplicate characters
wrong characters
incorrect objects
composition
resolution
frame consistency
```

---

# 31. Audio QA

Avalia:

```text
voice clarity
language
pronunciation
sync
music level
SFX
clipping
silence
missing audio
```

---

# 32. Continuity QA

Avalia:

```text
character position
objects
clothing
environment
time of day
story continuity
scene-to-scene state
```

Exemplo:

Se personagem segurava um mapa na cena anterior e ele desaparece sem motivo:

```text
issue = continuity_object_missing
```

---

# 33. Brand Guardian

ID:

```text
brand_guardian
```

Avalia aderência ao Brand Registry.

Critérios:

```text
logo
colors
visual identity
characters
tone
style
forbidden elements
canonical rules
```

---

# 34. Audience QA

Avalia adequação ao público.

Critérios variam por Channel DNA.

Exemplo:

```text
complexity
vocabulary
pace
tone
age suitability
```

---

# 35. Safety QA

Responsabilidade:

Verificar políticas de segurança e adequação antes de publicação.

Safety QA pode gerar:

```text
critical_failure = true
```

A decisão de bloqueio será aplicada por policy/service.

---

# 36. Technical QA

Avalia mídia tecnicamente.

Exemplos:

```text
codec
resolution
aspect ratio
duration
audio stream
file corruption
frame issues
```

Pode ser parcialmente determinístico, sem LLM.

---

# 37. Retention QA

Avalia potencial de retenção.

Critérios:

```text
opening speed
dead time
scene rhythm
information density
pattern changes
duration
CTA timing
```

---

# 38. Final QA

Não deverá repetir todas as análises do zero.

Deve consolidar:

```text
Script QA
Visual QA
Audio QA
Continuity QA
Brand QA
Audience QA
Safety QA
Technical QA
Retention QA
```

Output:

```json
{
  "final_score": 0,
  "decision": "pass|repair|regenerate|human_review",
  "critical_failures": [],
  "repair_actions": [],
  "confidence": 0.0
}
```

---

# 39. Agentes de Growth

Inicialmente:

```text
SEO Agent
Title Agent
Thumbnail Strategist
Thumbnail Evaluator
Performance Analyst
Growth Strategist
```

---

# 40. SEO Agent

Responsabilidade:

Produzir pacote SEO contextual.

Inputs:

```text
script
content
channel dna
audience
historical performance
search intent
```

Outputs:

```json
{
  "description": "",
  "keywords": [],
  "hashtags": [],
  "chapters": [],
  "search_intent": "",
  "related_topics": []
}
```

---

# 41. Title Agent

Responsabilidade:

Criar múltiplos títulos.

Output:

```json
{
  "candidates": [
    {
      "title": "",
      "clarity_score": 0,
      "curiosity_score": 0,
      "search_score": 0,
      "brand_fit_score": 0,
      "accuracy_score": 0,
      "final_score": 0
    }
  ]
}
```

---

# 42. Thumbnail Strategist

Responsabilidade:

Criar conceitos de thumbnail.

Não necessariamente gera a imagem.

Output:

```json
{
  "concepts": [
    {
      "concept": "",
      "focal_subject": "",
      "composition": "",
      "headline": "",
      "emotion": "",
      "brand_requirements": []
    }
  ]
}
```

---

# 43. Thumbnail Evaluator

Avalia:

```text
clarity
subject visibility
visual hierarchy
brand fit
text readability
relevance
click potential
mobile readability
```

---

# 44. Performance Analyst

Responsabilidade:

Interpretar resultados publicados.

Inputs:

```text
analytics snapshots
baseline
content attributes
```

Outputs:

```json
{
  "performance_index": 0,
  "strengths": [],
  "weaknesses": [],
  "possible_causes": [],
  "recommendations": [],
  "confidence": 0.0
}
```

---

# 45. Growth Strategist

Responsabilidade:

Consolidar aprendizados em recomendações de crescimento.

Não altera estratégia diretamente.

Output:

```json
{
  "recommended_adjustments": [],
  "experiments": [],
  "risks": [],
  "priority_actions": []
}
```

---

# 46. Agent Registry

Todos os agentes deverão existir em:

```text
agents
agent_versions
agent_prompts
agent_runs
```

Nunca instanciar agente informal sem registro.

---

# 47. Agent Definition

Cada Agent deverá possuir:

```text
slug
name
category
description
active
```

---

# 48. Agent Version

Cada versão:

```text
agent_id
version
provider
model
configuration
prompt_version
input_schema
output_schema
status
```

---

# 49. Estados da Versão

```text
draft
testing
active
deprecated
disabled
```

---

# 50. Uma Versão Ativa

Por função/configuração deverá existir uma versão ativa claramente identificada.

---

# 51. Prompt Registry

Prompts deverão ser armazenados de forma versionada.

Estrutura recomendada:

```text
agents/prompts/
    channel_analyst/
        v1.md
    idea_agent/
        v1.md
    script_writer/
        v1.md
```

Ou persistência equivalente com checksum.

---

# 52. Prompt Layers

Quando aplicável:

```text
system instructions
developer/business rules
runtime context
task input
```

Não concatenar tudo arbitrariamente.

---

# 53. Runtime Context

Enviar apenas o necessário.

Não fornecer todo Channel DNA para todos os agentes.

Exemplo:

`Title Agent` precisa:

```text
title patterns
audience
topic
script summary
SEO context
```

Não precisa:

```text
provider health
scene generation logs
OAuth data
```

---

# 54. Context Builder

Criar camada:

```text
AgentContextBuilder
```

Responsável por montar contexto específico.

---

# 55. Context Isolation

Nunca incluir:

```text
API keys
OAuth tokens
passwords
secrets
private provider credentials
```

em prompts.

---

# 56. Context Size Control

AgentContextBuilder deve possuir:

```text
token budget
priority
summarization
truncation policy
```

Evitar prompts gigantes.

---

# 57. Structured Inputs

Inputs importantes deverão utilizar Pydantic schemas.

Exemplo:

```python
class OpportunityEvaluationInput(BaseModel):
    idea: ContentIdeaContext
    channel: ChannelContext
    strategy: StrategyContext
    performance: PerformanceContext
```

---

# 58. Structured Outputs

Preferir sempre output validável.

Se output não validar:

```text
retry structured generation
```

antes de aceitar texto livre.

---

# 59. Schema Validation

Fluxo:

```text
LLM RESPONSE
    ↓
PARSE
    ↓
SCHEMA VALIDATION
    ↓
VALID?
    ├─ YES → SAVE
    └─ NO → REPAIR/RETRY
```

---

# 60. Invalid Output

Nunca salvar output inválido como se fosse decisão válida.

---

# 61. Agent Run

Cada execução deverá registrar:

```text
agent_version
input
output
provider
model
tokens
latency
cost
status
correlation_id
workflow
resource
```

---

# 62. Agent Run Status

```text
pending
running
completed
failed
invalid_output
cancelled
```

---

# 63. Agent Timeout

Todo agente deverá possuir timeout.

---

# 64. Agent Retry

Retry máximo configurável.

Não infinito.

---

# 65. LLM Fallback

LLMGateway poderá permitir:

```text
primary model
secondary model
```

quando policy autorizar.

---

# 66. Agent Cost

Toda execução paga deverá gerar CostEvent.

---

# 67. Agent Quality

Preparar métrica:

```text
agent approval rate
```

Exemplo:

```text
Script Writer v3
First-pass QA approval: 87%
```

---

# 68. Agent Performance

Guardar futuramente:

```text
success rate
average latency
average cost
schema failure rate
QA approval rate
```

---

# 69. Model Comparison

O mesmo agente poderá ter experimentos:

```text
script_writer.v4
Model A

script_writer.v5
Model B
```

Comparar resultados.

---

# 70. Não Misturar Agent e Model

Agent:

```text
função de negócio
```

Model:

```text
motor de IA
```

Um agente pode trocar de modelo sem mudar sua identidade funcional.

---

# 71. Agent Capability Matrix

Manter documentação semelhante:

| Agent | Reads | Writes Recommendation | Executes External Action |
|---|---|---|---|
| Channel Analyst | channel data | profile analysis | No |
| Idea Agent | DNA/strategy | ideas | No |
| Script Writer | project context | script | No |
| Visual QA | media asset | review | No |
| SEO Agent | content | SEO package | No |

Nenhum agente deve executar ação externa sensível diretamente.

---

# 72. Separation of Duties

Evitar que o mesmo agente:

```text
crie
+
avalie
```

o próprio resultado quando a decisão for importante.

Exemplo:

```text
Script Writer
↓
Script Critic
```

e não:

```text
Script Writer
↓
"avalie seu próprio roteiro"
```

---

# 73. Evaluator Independence

Agentes avaliadores devem utilizar prompts distintos e, quando custo justificar, poderão utilizar modelo diferente.

---

# 74. Multi-Judge

Para decisões críticas futuras, permitir:

```text
Judge A
Judge B
Judge C
```

e consenso.

Não obrigatório no MVP.

---

# 75. Consensus Engine

Arquitetura futura:

```text
AgentReviewConsensusService
```

Inputs:

```text
multiple reviews
weights
confidence
```

Output:

```text
consensus decision
```

---

# 76. Score Normalization

Scores devem seguir preferencialmente:

```text
0–100
```

Confidence:

```text
0.0–1.0
```

---

# 77. Score Meaning

Definir claramente.

Exemplo:

```text
90–100 excellent
80–89 strong
70–79 moderate
60–69 weak
<60 poor
```

Mas policies podem utilizar thresholds diferentes.

---

# 78. Confidence Não é Score

Exemplo:

```text
Score = 94
Confidence = 0.52
```

significa:

agente gostou do conteúdo, mas possui pouca evidência.

---

# 79. Evidence

Avaliações importantes deverão incluir evidências.

Exemplo:

```json
{
  "score": 92,
  "evidence": [
    {
      "type": "historical",
      "description": "..."
    }
  ]
}
```

---

# 80. Reasoning Summary

Guardar apenas resumo da justificativa operacional.

Não depender de chain-of-thought interno.

Campo:

```text
reasoning_summary
```

deverá conter explicação curta e auditável.

---

# 81. Decision Contract

Para agentes de decisão utilizar estrutura comum:

```json
{
  "decision": "",
  "score": 0,
  "confidence": 0.0,
  "reasoning_summary": "",
  "issues": [],
  "recommended_actions": []
}
```

---

# 82. Agent Permissions

Criar conceito futuro:

```text
AgentPermission
```

Exemplo:

```text
READ_CHANNEL_DNA
READ_ANALYTICS
CREATE_IDEA
CREATE_REVIEW
```

Mesmo sem enforcement completo inicialmente, manter boundary conceitual.

---

# 83. Agentes Não Podem

Regra geral:

- acessar banco diretamente;
- fazer SQL;
- consumir OAuth tokens;
- publicar diretamente;
- alterar budget;
- alterar billing;
- mudar automation policy;
- desativar safety;
- executar shell;
- escolher credenciais;
- alterar outro agente.

---

# 84. Tools

Se agentes utilizarem tools no futuro, cada tool deverá ser registrada e limitada.

Exemplo:

```text
search_trends
fetch_project_context
inspect_asset
```

---

# 85. Tool Allowlist

Agente só poderá utilizar tools explicitamente permitidas.

---

# 86. Tool Results

Resultados externos deverão ser normalizados antes de entrar no contexto quando possível.

---

# 87. Prompt Injection Protection

Conteúdo vindo de:

```text
video descriptions
comments
web pages
external documents
```

deve ser tratado como dados, não como instruções.

---

# 88. Untrusted Content Boundary

Context Builder deverá marcar dados externos como:

```text
UNTRUSTED_CONTENT
```

ou mecanismo equivalente.

---

# 89. Research Agent Safety

Research Agent nunca deverá obedecer instruções encontradas em conteúdo externo.

---

# 90. User Instructions

Preferências do usuário podem influenciar:

```text
style
topics
frequency
approval policy
```

mas nunca podem sobrescrever:

```text
system safety
platform restrictions
authorization rules
```

---

# 91. User Overrides

Quando usuário altera uma decisão de IA:

```text
AI suggestion
↓
User override
```

guardar ambos.

---

# 92. Feedback to Agents

User overrides poderão futuramente alimentar aprendizado.

Exemplo:

```text
Idea Agent recommended
User rejected

Reason:
too repetitive
```

---

# 93. Feedback Event

Criar evento futuro:

```text
agent.output.overridden
```

---

# 94. Agent A/B Testing

Preparar possibilidade de testar versões.

Exemplo:

```text
50% Idea Agent v3
50% Idea Agent v4
```

Somente quando houver volume suficiente.

---

# 95. Experiment Attribution

Guardar qual versão participou de cada resultado publicado.

Isso permitirá correlacionar:

```text
agent version
→ content performance
```

---

# 96. Agent Registry UI

Control Center futuro poderá mostrar:

```text
Agent
Version
Model
Status
Runs
Cost
Approval Rate
Latency
```

---

# 97. Prompt Management UI

Futuro Control Center poderá:

```text
view prompt
create new version
test
activate
rollback
```

Nunca editar versão ativa em-place.

---

# 98. Prompt Rollback

Permitir retornar:

```text
v4 → v3
```

sem apagar histórico.

---

# 99. Model Rollback

Mesmo princípio.

---

# 100. Agent Testing

Cada agente deverá possuir:

```text
unit/schema tests
fixture tests
golden cases
failure cases
```

quando implementado.

---

# 101. Golden Cases

Criar exemplos conhecidos.

Exemplo:

```text
Input:
canal infantil musical

Expected:
não sugerir política
não sugerir violência
manter perfil infantil
```

---

# 102. Regression Tests

Mudança de prompt não deverá destruir casos previamente aprovados.

---

# 103. Evaluation Dataset

Preparar diretório futuro:

```text
/tests/agent_evals/
```

Com casos de teste versionados.

---

# 104. Offline Evaluation

Antes de ativar nova versão de agente:

```text
run eval suite
compare with active version
```

---

# 105. Activation Policy

Nova versão poderá seguir:

```text
DRAFT
↓
TESTING
↓
EVALUATED
↓
ACTIVE
```

---

# 106. Shadow Mode

Preparar possibilidade futura:

```text
Agent v4 runs
but does not influence workflow
```

Comparar com v3.

---

# 107. Agent Failure Handling

Se agente falhar:

```text
retry
↓
fallback model
↓
workflow review
```

conforme policy.

---

# 108. Invalid Schema Handling

Diferenciar:

```text
provider failure
```

de:

```text
output schema failure
```

---

# 109. Agent Hallucination Guard

Agentes que lidam com dados factuais deverão informar:

```text
unknown
```

quando informação não estiver disponível.

Não inventar métricas.

---

# 110. Analytics Grounding

Performance Analyst deve receber dados calculados pela plataforma.

Não deve estimar views ou CTR ausentes como fatos.

---

# 111. Provenance Requirement

Campos relevantes podem usar:

```json
{
  "value": "...",
  "source": "youtube|user|agent|derived",
  "confidence": 0.0
}
```

quando necessário.

---

# 112. Agentes de Conteúdo Infantil

Quando Channel DNA identificar conteúdo infantil, Context Builder deverá incluir policy específica.

Agentes como:

```text
Script Writer
Visual Director
Audience QA
Safety QA
SEO Agent
```

devem adaptar comportamento.

---

# 113. Character Context

Quando houver personagens:

```text
Character Registry
```

deverá ser fonte canônica.

Prompt Engineer não deve inventar visual novo se referência canônica existir.

---

# 114. Character Lock

Cada geração deverá poder receber:

```text
character_ids
reference_assets
canonical_prompt
negative_prompt
continuity_state
```

---

# 115. Scene Context

Scene Planner deve fornecer apenas estado relevante à próxima cena.

Evitar repassar todo vídeo repetidamente.

---

# 116. Memory Types

Separar:

```text
Channel Memory
Project Memory
Scene Memory
Learning Memory
```

---

# 117. Channel Memory

Inclui:

```text
DNA
audience
strategy
learned rules
brand
```

---

# 118. Project Memory

Inclui:

```text
objective
script
storyboard
approvals
current state
```

---

# 119. Scene Memory

Inclui:

```text
characters
objects
environment
continuity
```

---

# 120. Learning Memory

Inclui apenas regras validadas ou candidatos claramente marcados.

---

# 121. Não Criar Uma Memória Gigante

Cada agente deve consumir apenas memória relevante.

---

# 122. Agent Context Snapshot

Para runs importantes, guardar snapshot ou referências de qual contexto foi utilizado.

Assim será possível reproduzir decisão.

---

# 123. Reproducibility

Mesmo com modelos não determinísticos, devemos saber:

```text
agent version
prompt version
model
settings
input
context refs
```

---

# 124. Temperature

Configuração pertence ao Agent Version.

Não espalhar valores em chamadas.

---

# 125. Deterministic Agents

Agentes de avaliação e classificação devem usar configurações mais estáveis quando apropriado.

---

# 126. Creative Agents

Agentes como Idea Agent podem possuir maior diversidade.

---

# 127. Agent-Level Budgets

Preparar:

```text
max_tokens
max_cost
max_retries
```

por agente.

---

# 128. Workflow-Level Agent Budget

Workflow também poderá limitar custo total de LLM.

---

# 129. Cost-Aware Model Selection

LLMGateway poderá escolher modelo conforme:

```text
task complexity
quality requirements
cost policy
```

Mas decisões críticas devem ser auditáveis.

---

# 130. Agent Tiers

Possível configuração:

```text
economy
standard
premium
```

Exemplo:

```text
Idea generation → economy/standard
Final QA → premium
```

---

# 131. Criticality

Cada Agent Version deverá poder possuir:

```text
criticality = low|medium|high
```

Isso influencia fallback e QA.

---

# 132. Human Review Triggers

Agent output poderá exigir revisão quando:

```text
confidence too low
critical issue
policy conflict
invalid assumptions
high-cost decision
```

---

# 133. Agent Decisions Are Advisory

Mesmo:

```text
approved = true
```

não significa automaticamente execução.

QualityPolicyService decide.

---

# 134. Example Quality Flow

```text
Visual QA
score 93
approved true

Safety QA
critical_failure true

Final result:
BLOCK
```

Safety prevalece.

---

# 135. Evaluation Weighting

Final QA poderá aplicar pesos configuráveis.

Exemplo conceitual:

```text
Visual 20%
Audio 10%
Brand 15%
Continuity 15%
Audience 10%
Retention 15%
SEO 5%
Technical 10%
```

Safety poderá ser gate absoluto.

---

# 136. Weight Versioning

Quality policy deve possuir versão.

---

# 137. No Circular Evaluation

Evitar:

```text
Agent A evaluates B
Agent B evaluates A
```

em loops indefinidos.

Workflow define número máximo de ciclos.

---

# 138. Repair Loop

Exemplo:

```text
Script Writer
↓
Script Critic
↓ fail
Script Writer repair
↓
Script Critic
↓ fail
Human Review
```

---

# 139. Repair Context

Ao reparar, fornecer apenas:

```text
original output
issues
required changes
```

Não pedir geração totalmente nova quando desnecessário.

---

# 140. Repair Tracking

Registrar:

```text
repair_of_version
issues_addressed
```

---

# 141. Agent Naming Convention

Utilizar slugs consistentes:

```text
channel_analyst
audience_analyst
strategy_agent
idea_agent
script_writer
visual_qa
seo_agent
```

---

# 142. Agent Code Structure

Sugestão:

```text
app/agents/

├── registry/
├── contracts/
├── contexts/
├── prompts/
├── evaluators/
└── runtime/
```

---

# 143. Agent Runtime

Criar componente:

```text
AgentRuntime
```

Responsável por:

```text
resolve active version
build context
call LLMGateway
validate output
record run
record cost
emit event
```

---

# 144. AgentRuntime Não Deve

Implementar regra de negócio de:

```text
calendar
publication
billing
workflow routing
```

---

# 145. Agent Invocation Flow

```text
Workflow Step
   ↓
AgentRuntime.execute(agent_slug, input)
   ↓
Resolve Agent Version
   ↓
Build Context
   ↓
LLMGateway
   ↓
Validate Output
   ↓
Persist AgentRun
   ↓
Return Structured Result
```

---

# 146. Events

AgentRuntime deverá emitir:

```text
agent.run.started
agent.run.completed
agent.run.failed
agent.output.invalid
```

---

# 147. Metrics

Preparar métricas:

```text
agent_runs_total
agent_failures_total
agent_latency
agent_cost
agent_invalid_outputs
```

---

# 148. Logging

Logs devem conter:

```text
agent_slug
agent_version
workflow_run_id
correlation_id
```

Nunca logar contexto sensível completo sem necessidade.

---

# 149. Agent Output Storage

Outputs grandes podem ser armazenados de maneira estruturada, mas evitar duplicação excessiva.

---

# 150. Content Hash

Prompts e outputs importantes poderão possuir checksum para auditoria.

---

# 151. Agent Version Migration

Mudança de schema de output exige nova versão de agente.

---

# 152. Backward Compatibility

Workflow antigo deverá continuar entendendo schema antigo da versão vinculada.

---

# 153. Model Provider Independence

Agent Version referencia:

```text
provider
model
```

mas código do agente não chama provider diretamente.

---

# 154. Central LLM Gateway

Interface conceitual:

```python
class LLMGateway:
    generate(...)
    generate_structured(...)
```

---

# 155. Provider Adapters

Possíveis:

```text
OpenAI
Anthropic
Google
local models
other providers
```

sem acoplamento ao AgentRuntime.

---

# 156. Vendor Outage

Se provider indisponível:

```text
LLM Router
↓
allowed fallback
```

conforme Agent Policy.

---

# 157. Critical Agents

Alguns agentes poderão proibir fallback automático entre famílias de modelo sem validação.

Configurável.

---

# 158. Agent Policy

Criar conceito:

```text
AgentExecutionPolicy
```

Exemplo:

```json
{
  "max_retries": 2,
  "allow_model_fallback": true,
  "max_cost": 0.10,
  "minimum_confidence": 0.75
}
```

---

# 159. Agent Configuration Hierarchy

```text
system defaults
↓
agent version
↓
organization policy
↓
channel policy
↓
workflow override
```

---

# 160. Agentes Globais vs Específicos

Inicialmente agentes serão globais à plataforma.

Contexto os torna específicos ao canal.

Futuramente poderá existir customização por organização.

---

# 161. Custom Agents

Não implementar no MVP.

Preparar apenas arquitetura para futura personalização.

---

# 162. User-Editable Prompts

Também não implementar inicialmente.

Prompts são administrados pela plataforma.

---

# 163. Reasoning Audit

Não armazenar nem exigir cadeia interna de raciocínio.

Guardar apenas:

```text
decision
score
confidence
evidence
reasoning_summary
```

---

# 164. Final Agent Map

```text
CHANNEL
  ↓
Channel Analyst
Audience Analyst
  ↓
Strategy Agent
Trend Researcher
  ↓
Idea Agent
Opportunity Evaluator
Calendar Planner
  ↓
Research Agent
Hook Agent
Script Writer
Script Critic
  ↓
Storyboard Director
Scene Planner
Media Director
Prompt Engineer
Voice Director
Audio Director
Editor Agent
  ↓
Visual QA
Audio QA
Continuity QA
Brand Guardian
Audience QA
Safety QA
Technical QA
Retention QA
Final QA
  ↓
SEO Agent
Title Agent
Thumbnail Strategist
Thumbnail Evaluator
  ↓
PUBLICATION
  ↓
Performance Analyst
Learning Analyst
Growth Strategist
  ↓
STRATEGY / IDEAS
      ↺
```

---

# 165. Agentes do MVP Inicial

Não implementar todos imediatamente.

Prioridade sugerida:

```text
1. Channel Analyst
2. Audience Analyst
3. Strategy Agent
4. Idea Agent
5. Opportunity Evaluator
6. Calendar Planner
7. Script Writer
8. Script Critic
9. Storyboard Director
10. Media Director
11. Prompt Engineer
12. Visual QA
13. Continuity QA
14. Brand Guardian
15. Safety QA
16. SEO Agent
17. Title Agent
18. Performance Analyst
19. Learning Analyst
```

Outros entram conforme as fases.

---

# 166. Relação com as 20 Fases

Principalmente:

```text
F06 Channel Intelligence
→ Channel Analyst
→ Audience Analyst

F08 Strategy
→ Strategy Agent

F09 Ideas
→ Idea Agent
→ Opportunity Evaluator

F10 Calendar
→ Calendar Planner

F11 Agent Engine
→ AgentRuntime
→ Registry
→ contracts

F12 Production Intelligence
→ Script Writer
→ Script Critic
→ Storyboard
→ Scene Planner

F13–15 Media
→ Media Director
→ Prompt Engineer
→ Voice/Audio/Editor

F16 Quality
→ QA Agents

F17 Growth
→ SEO
→ Title
→ Thumbnail

F19 Learning
→ Performance Analyst
→ Learning Analyst
→ Growth Strategist
```

---

# 167. Definition of Done de um Agente

Um agente só é considerado implementado quando possuir:

```text
registry entry
version
prompt version
input schema
output schema
AgentRuntime integration
tests
failure handling
cost tracking
logging
events
documentation
```

---

# 168. Documentação

Manter:

```text
/docs/agents.md
```

Para cada agente:

```text
purpose
inputs
outputs
model
prompt version
permissions
dependencies
workflow usage
```

---

# 169. Claude Code — Regra de Implementação

Ao implementar um agente:

1. verificar fase atual;
2. confirmar responsabilidade exclusiva;
3. criar contrato de input;
4. criar contrato de output;
5. criar prompt versionado;
6. registrar Agent;
7. criar Agent Version;
8. integrar ao AgentRuntime;
9. integrar LLMGateway;
10. validar structured output;
11. adicionar retries controlados;
12. registrar AgentRun;
13. registrar custo;
14. emitir eventos;
15. criar testes;
16. adicionar documentação;
17. não permitir chamada direta a provider externo;
18. não permitir execução direta de ação sensível.

---

# 170. Princípio Final

A camada de agentes deve ser:

```text
especializada
modular
substituível
versionada
avaliável
auditável
controlada
```

O sistema não deverá depender de um “superagente” responsável por tudo.

Cada agente deverá possuir responsabilidade clara e limitada, e todas as decisões importantes deverão passar por workflows, policies e services antes de qualquer ação externa.

Este documento deverá permanecer como referência obrigatória durante todo o desenvolvimento.