# Documento 07 — Channel Intelligence, Growth Engine, Tendências, SEO e Recomendações

## 1. Objetivo

Este documento define como a plataforma deverá:

- entender automaticamente um canal conectado;
- identificar nicho, subnicho, público e proposta editorial;
- detectar padrões de desempenho;
- construir o Channel DNA;
- identificar oportunidades de crescimento;
- descobrir tendências relevantes;
- evitar conteúdo genérico ou fora de contexto;
- gerar ideias de vídeos e Shorts;
- priorizar pautas com maior potencial;
- criar clusters de conteúdo;
- sugerir frequência e calendário;
- otimizar SEO, títulos, descrição e thumbnails;
- medir resultados;
- alimentar o Learning Engine.

A regra principal é:

**a plataforma não deverá buscar viralização de forma isolada; deverá buscar crescimento dentro da identidade editorial do canal.**

---

# 2. Princípio Central

O sistema deverá otimizar simultaneamente:

```text id="g7p4k2"
CHANNEL FIT
+
AUDIENCE FIT
+
CONTENT QUALITY
+
DISCOVERABILITY
+
RETENTION POTENTIAL
+
CONSISTENCY
+
GROWTH POTENTIAL
```

Nunca otimizar apenas:

```text id="sf5dwx"
TREND
```

ou:

```text id="57o8hf"
KEYWORDS
```

---

# 3. Visão Geral do Growth Loop

```text id="6bsnk1"
CHANNEL DATA
     ↓
CHANNEL INTELLIGENCE
     ↓
CHANNEL DNA
     ↓
STRATEGY
     ↓
TREND SIGNALS
     ↓
IDEAS
     ↓
OPPORTUNITY SCORING
     ↓
CALENDAR
     ↓
PRODUCTION
     ↓
PUBLICATION
     ↓
ANALYTICS
     ↓
LEARNING
     ↓
STRATEGY / DNA UPDATE
       ↺
```

---

# 4. Channel Intelligence

Ao conectar um canal, a plataforma deverá iniciar uma análise automática.

Inputs principais:

```text id="4ru5be"
channel metadata
video history
Shorts history
playlists
titles
descriptions
durations
publication dates
available analytics
performance distribution
content frequency
```

---

# 5. Objetivos do Channel Analyst

Identificar:

```text id="x107z5"
primary niche
subniches
main topics
content pillars
formats
language
tone
audience profile
visual patterns
publishing patterns
high-performing patterns
low-performing patterns
series
recurring characters
recurring formats
```

---

# 6. Confirmado vs Inferido

Toda informação deverá indicar origem.

Exemplo:

```json id="s4z8ck"
{
  "value": "kids entertainment",
  "source": "inferred",
  "confidence": 0.92
}
```

Ou:

```json id="vxpqbj"
{
  "value": "pt-BR",
  "source": "channel_metadata",
  "confidence": 1.0
}
```

---

# 7. Channel DNA

O Channel DNA deverá ser a principal representação estratégica do canal.

Estrutura conceitual:

```json id="5exdc2"
{
  "classification": {},
  "audience": {},
  "content_pillars": [],
  "formats": {},
  "tone": {},
  "visual_identity": {},
  "title_patterns": [],
  "publishing_patterns": {},
  "performance_patterns": {},
  "brand_rules": {},
  "restrictions": {},
  "learned_rules": [],
  "confidence": 0.0
}
```

---

# 8. Channel DNA Não Deve Ser Estático

Ele deverá ser versionado.

Exemplo:

```text id="ijj1ag"
DNA v1
↓
30 novos conteúdos
↓
DNA candidate v2
↓
comparação
↓
activate or reject
```

---

# 9. Atualização do DNA

Não recalcular a cada evento pequeno.

Triggers possíveis:

```text id="ei67r8"
onboarding
significant content volume
monthly refresh
major performance shift
user request
strategy reclassification
```

---

# 10. Audience Intelligence

O sistema deverá identificar, quando dados permitirem:

```text id="mn0pea"
language
geographic distribution
age signals
viewing preferences
format preference
topic preference
content depth preference
engagement pattern
```

---

# 11. Audience Profiles

Pode haver mais de um segmento.

Exemplo:

```text id="28ac2t"
Primary audience
Secondary audience
Emerging audience
```

---

# 12. Confidence

Inferências de audiência deverão possuir confidence.

Nunca afirmar como fato dados não disponíveis.

---

# 13. Content Pillars

Cada canal deverá possuir pilares.

Exemplo:

```text id="ugp4pd"
Entertainment
Education
Stories
Music
Curiosities
Reviews
Tutorials
```

---

# 14. Pillar Weight

Cada pilar pode possuir:

```text id="qkwoe7"
target_ratio
historical_ratio
performance_score
strategic_priority
```

---

# 15. Content Mix

Exemplo:

```text id="yfvf7i"
40% pillar A
30% pillar B
20% pillar C
10% experiments
```

---

# 16. Format Intelligence

Separar:

```text id="5bwjny"
Shorts
Long-form
Live
Community
```

mesmo que alguns formatos sejam futuros.

---

# 17. Formato Não Deve Ser Escolhido Arbitrariamente

Opportunity Evaluator deverá recomendar:

```text id="4txlay"
best format
```

com base em:

```text id="4yomvr"
topic
audience
historical results
story depth
retention potential
production feasibility
```

---

# 18. Shorts Intelligence

Analisar:

```text id="lsq9n3"
duration
hook style
pace
caption density
topic
completion patterns
publication timing
series
```

---

# 19. Long-form Intelligence

Analisar:

```text id="7kp9l1"
duration
intro length
chapters
topic depth
series
publishing frequency
relative performance
```

---

# 20. Historical Baselines

Criar baselines por:

```text id="6m4pmx"
channel
format
pillar
duration bucket
topic
publication window
```

---

# 21. Performance Baseline

Conceito:

```text id="g0ptp6"
100 = expected performance
```

Exemplo:

```text id="ah7r28"
132 = 32% acima
74 = 26% abaixo
```

---

# 22. Não Comparar Métricas Cruas Fora de Contexto

Exemplo incorreto:

```text id="tyvkfi"
Short de 24h
vs
vídeo de 2 anos
```

Usar janelas comparáveis.

---

# 23. Content Attributes

Cada conteúdo deverá possuir atributos analíticos.

Exemplo:

```text id="ny8of1"
topic
pillar
format
duration
hook_type
tone
series
characters
visual_style
publication_time
CTA_type
```

---

# 24. Feature Extraction

Alguns atributos virão:

```text id="7dl72u"
diretamente dos dados
```

Outros:

```text id="rmrjc3"
inferred by agents
```

Guardar provenance.

---

# 25. Growth Engine

O Growth Engine deverá utilizar:

```text id="mi4xy0"
historical performance
+
channel DNA
+
trends
+
content gaps
+
audience
+
calendar
+
learning rules
```

para gerar oportunidades.

---

# 26. Growth Engine Não Produz Conteúdo

Ele recomenda:

```text id="85fsz9"
what to produce
why
when
in what format
with what priority
```

---

# 27. Trend Intelligence

Criar camada própria:

```text id="1ox32t"
Trend Intelligence
```

Fontes futuras poderão incluir:

```text id="g6530e"
YouTube
Google Trends
Search engines
news
social platforms
competitor signals
seasonal calendars
```

---

# 28. Trend Signal

Contrato:

```json id="ovhkjp"
{
  "topic": "",
  "source": "",
  "signal_type": "",
  "strength": 0,
  "velocity": 0,
  "recency": "",
  "estimated_lifespan": "",
  "channel_relevance": 0,
  "confidence": 0
}
```

---

# 29. Signal Types

```text id="sk1dce"
rising
breakout
seasonal
evergreen
declining
news_driven
community_driven
```

---

# 30. Trend Strength

Não confundir:

```text id="w48lqx"
popular topic
```

com:

```text id="ymllpj"
relevant topic for this channel
```

---

# 31. Channel Relevance

Trend Signal deverá ser cruzado com Channel DNA.

Exemplo:

```text id="gjtf9g"
Trend Strength = 96
Channel Relevance = 18
```

Resultado:

```text id="0t97ng"
não recomendado
```

---

# 32. Trend Decay

Tendências possuem vida útil.

Guardar:

```text id="n7vprv"
detected_at
peak_estimate
expires_at
```

quando possível.

---

# 33. Trend Freshness

Opportunity Score deverá penalizar tendência velha.

---

# 34. Evergreen Content

Não depender apenas de trends.

A plataforma deverá equilibrar:

```text id="r4hc4v"
evergreen
+
trending
+
series
+
experimental
```

---

# 35. Estratégia de Mix

Exemplo configurável:

```text id="rp7joj"
50% evergreen
25% proven series
15% trend-responsive
10% experimental
```

---

# 36. Seasonality

O sistema deverá identificar oportunidades sazonais.

Exemplos:

```text id="5s1vwt"
Natal
Halloween
volta às aulas
férias
eventos esportivos
datas do nicho
```

---

# 37. Planning Horizon

Tendências rápidas exigem:

```text id="shw7ff"
short horizon
```

Conteúdo evergreen pode ser planejado com mais antecedência.

---

# 38. Competitor Intelligence

Preparar arquitetura futura para analisar concorrentes públicos.

Objetivos:

```text id="u3pt07"
topic gaps
format patterns
publishing frequency
emerging topics
```

Não copiar roteiros ou identidade.

---

# 39. Competitor Gap

Exemplo:

```text id="xk5yx8"
alta demanda
+
poucos conteúdos relevantes no canal
+
bom fit
```

pode gerar oportunidade.

---

# 40. Idea Sources

Toda ideia deverá ter origem.

```text id="3rrijo"
trend
evergreen
performance
series
repurpose
audience_gap
seasonality
user
experiment
```

---

# 41. Idea Generation

O Idea Agent deverá receber:

```text id="s44hqt"
current strategy
content gaps
recent publications
planned calendar
trends
learned rules
audience
```

---

# 42. Idea Cardinality

Gerar mais candidatos que vagas disponíveis.

Exemplo:

```text id="lfzscc"
20 ideias
↓
avaliar
↓
selecionar 5
```

---

# 43. Deduplicação

Antes de Opportunity Scoring:

```text id="amqklm"
exact duplicates
semantic duplicates
recently published topics
planned topics
```

---

# 44. Semantic Similarity

Preparar embeddings ou serviço equivalente futuramente.

---

# 45. Content Saturation

Criar penalização quando tema aparece demais recentemente.

Exemplo:

```text id="znk529"
topic saturation score
```

---

# 46. Character Saturation

Em canais com personagens:

```text id="vlqjde"
character frequency
```

também pode entrar no calendário.

---

# 47. Series Logic

Algumas séries merecem recorrência mesmo com temas semelhantes.

Distinguir:

```text id="ltd16r"
repetition
```

de:

```text id="uv94x9"
intentional series continuity
```

---

# 48. Opportunity Engine

Toda ideia válida deverá passar por scoring.

---

# 49. Opportunity Score Components

Base recomendada:

```text id="m0m687"
Channel Fit
Audience Fit
Strategic Fit
Trend
Novelty
Retention Potential
Search Potential
Competition
Brand Fit
Production Feasibility
Seasonality
Historical Similarity Performance
```

---

# 50. Suggested Weights

Exemplo inicial:

```text id="128ac3"
Channel Fit................20%
Audience Fit...............15%
Strategic Fit..............10%
Retention Potential........10%
Historical Performance.....10%
Trend......................10%
Search Potential...........7%
Novelty....................5%
Competition................5%
Brand Fit..................5%
Production Feasibility.....3%
```

Pesos configuráveis.

---

# 51. Viral Score

Não usar o termo como promessa.

Pode existir internamente:

```text id="ck1v6z"
Growth Potential Score
```

ou:

```text id="81z1hy"
Opportunity Score
```

Mais adequado.

---

# 52. Confidence

Toda oportunidade:

```text id="awvvt9"
score
+
confidence
```

---

# 53. Example

```text id="u3zwyr"
Opportunity Score = 92
Confidence = 0.90

→ strong candidate
```

```text id="ixhnmp"
Opportunity Score = 92
Confidence = 0.48

→ review
```

---

# 54. Evidence

Opportunity score deverá indicar evidências.

```json id="21coea"
{
  "channel_fit": {
    "score": 97,
    "evidence": ["..."]
  }
}
```

---

# 55. Production Feasibility

Avaliar:

```text id="7yhpis"
estimated scenes
assets
duration
special characters
media model requirements
cost
production time
```

---

# 56. Economic Opportunity

Futuramente:

```text id="1eah54"
growth potential
÷
estimated production cost
```

poderá gerar:

```text id="1p6jme"
efficiency score
```

---

# 57. Calendar Recommendation

Após ranking:

```text id="aw4u4n"
Opportunity
+
Content Mix
+
Publishing Slots
+
Topic Saturation
+
Clusters
```

---

# 58. Calendar Balance

Calendar Planner deverá verificar:

```text id="ji5xz3"
pillar balance
format balance
topic diversity
series cadence
character balance
trend urgency
production capacity
```

---

# 59. Production Capacity

Não sugerir calendário impossível.

Considerar:

```text id="2z7u51"
available budget
render capacity
provider capacity
current projects
```

---

# 60. Calendar Confidence

Pode indicar:

```text id="bv9c5j"
high confidence
medium confidence
experimental
```

---

# 61. Cluster Strategy

Conteúdo poderá fazer parte de:

```text id="ptbdlf"
Content Cluster
```

---

# 62. Cluster Example

```text id="84pl8y"
MAIN VIDEO
Como os tubarões enxergam?

Short 1
Tubarões enxergam no escuro?

Short 2
Por que tubarões não piscam?

Short 3
O olho mais estranho do oceano
```

---

# 63. Cluster Objectives

```text id="yq07ym"
topic authority
cross-traffic
content reuse
consistent storytelling
```

---

# 64. Repurpose Engine

Preparar futuro agente para transformar:

```text id="6ar6y1"
long-form → Shorts
Short → sequel
video → community post
```

---

# 65. Cannibalization Guard

Evitar publicar conteúdos praticamente idênticos muito próximos.

---

# 66. Search Intelligence

SEO Agent deverá trabalhar com intenção, não apenas keywords.

---

# 67. Search Intent Types

```text id="9gl3bo"
informational
how-to
comparison
entertainment
discovery
news
transactional
```

---

# 68. Keyword Strategy

Keywords deverão ser:

```text id="mcibq8"
relevant
natural
contextual
```

Não stuffing.

---

# 69. Metadata Package

Para cada projeto:

```text id="035rag"
title
description
keywords
hashtags
chapters
search intent
related topics
```

---

# 70. Title Intelligence

Title Agent deverá gerar candidatos distintos.

---

# 71. Title Attributes

```text id="h0k79m"
clarity
accuracy
curiosity
specificity
channel fit
search relevance
mobile readability
```

---

# 72. Title Length

Não fixar regra absoluta.

Usar:

```text id="9ei9my"
readability
visibility
intent
```

como critérios.

---

# 73. Clickbait Guard

Título não pode prometer algo ausente.

---

# 74. Title Candidate Example

```json id="8rj32p"
{
  "title": "...",
  "scores": {
    "clarity": 93,
    "curiosity": 88,
    "accuracy": 100,
    "search": 84
  },
  "final_score": 91
}
```

---

# 75. Thumbnail Intelligence

Thumbnail deverá complementar título.

Evitar:

```text id="wx7u2y"
title and thumbnail saying exactly the same thing
```

quando estratégia visual puder adicionar informação.

---

# 76. Thumbnail Attributes

```text id="s8df2v"
focal clarity
emotion
contrast
subject size
mobile readability
brand fit
story relevance
visual curiosity
```

---

# 77. Thumbnail Text

Se usado:

```text id="8wbcgm"
short
readable
non-redundant
```

---

# 78. Character-Based Channels

Se houver Character Registry:

```text id="uqlptu"
canonical appearance
```

é requisito obrigatório.

---

# 79. Thumbnail Candidate Scoring

```text id="gxtziz"
brand fit
clarity
click potential
relevance
mobile legibility
```

---

# 80. SEO Does Not Override Brand

SEO Agent não pode mudar identidade do canal apenas para perseguir keywords.

---

# 81. Search vs Recommendation

Reconhecer que YouTube possui diferentes fontes de descoberta.

Estratégia deverá poder considerar:

```text id="kc0xqd"
search
suggested
browse
Shorts feed
external
```

quando dados permitirem.

---

# 82. Traffic Source Intelligence

Performance Analyst deverá identificar padrões por fonte de tráfego quando disponível.

---

# 83. Content Goal

Cada projeto deverá possuir objetivo.

Exemplos:

```text id="w0461c"
search acquisition
retention
subscriber growth
series continuation
trend capture
evergreen authority
```

---

# 84. Não Usar Mesma Otimização Para Todo Conteúdo

Exemplo:

```text id="7ngczr"
search-driven video
```

não deve ser otimizado igual a:

```text id="qnj08g"
Short de feed
```

---

# 85. Short Growth Strategy

Priorizar:

```text id="g1vv2b"
fast hook
retention
loop potential
clarity
visual motion
```

---

# 86. Long-form Growth Strategy

Priorizar:

```text id="9zyi7w"
title-thumbnail fit
intro retention
watch time
topic depth
session continuation
```

---

# 87. Intro Analysis

Para long-form, monitorar:

```text id="vsj3jm"
early retention
```

quando dados permitirem.

---

# 88. Hook Classification

Criar tipos:

```text id="auopv1"
question
surprise
promise
story
visual
challenge
curiosity_gap
statement
```

---

# 89. Hook Performance

Aprender por canal:

```text id="qygdtj"
question hooks +11%
```

---

# 90. Duration Buckets

Criar buckets configuráveis.

Exemplo Shorts:

```text id="tcljf1"
0–15
16–25
26–35
36–45
46–60
```

---

# 91. Duration Learning

Learning Engine poderá identificar melhor faixa.

---

# 92. Publication Time Intelligence

Analisar:

```text id="52sz6o"
day
hour
format
audience activity
historical performance
```

---

# 93. Não Confundir Correlação e Causalidade

Horário pode estar associado a tema/formato.

Learning Agent deve reportar confidence.

---

# 94. Best Time Recommendation

Retornar:

```text id="z4kgb8"
recommended window
+
confidence
```

não uma falsa precisão absoluta.

---

# 95. Seasonality vs Best Time

Calendário deverá conciliar ambos.

---

# 96. Content Gap Analysis

Growth Engine deverá perguntar:

```text id="4y8r5v"
What topics fit this channel but are underrepresented?
```

---

# 97. Gap Types

```text id="2jpxep"
topic gap
format gap
series gap
audience gap
search gap
seasonal gap
```

---

# 98. Growth Opportunity

Exemplo:

```text id="u35c67"
Channel has strong performance in animal curiosities
but only 4% of recent content uses this pillar
```

Recomendação:

```text id="dlbr9s"
increase temporarily
```

---

# 99. Performance Decay

Learned rules deverão expirar ou perder peso.

Exemplo:

```text id="nm77sk"
pattern from 18 months ago
```

pode não refletir situação atual.

---

# 100. Recency Weighting

Aprendizado deverá considerar recência.

---

# 101. Sample Size

Regra mínima.

Não concluir:

```text id="r33y67"
blue thumbnails are better
```

com apenas dois vídeos.

---

# 102. Effect Size

Guardar magnitude.

Exemplo:

```text id="a0at7u"
+1.2%
```

pode ser estatisticamente pouco útil.

---

# 103. Confidence

Guardar:

```text id="7vn1dj"
0.0–1.0
```

---

# 104. Learning Candidate

Estrutura:

```json id="clz23u"
{
  "finding": "",
  "sample_size": 0,
  "effect_size": 0.0,
  "confidence": 0.0,
  "recency_score": 0.0,
  "evidence": []
}
```

---

# 105. Validated Rule

Somente após thresholds.

---

# 106. Learned Rule Weight

Não usar todas as regras igualmente.

Pode possuir:

```text id="6a2d0h"
confidence
priority
validity
scope
```

---

# 107. Rule Scope

```text id="s1x100"
channel
format
pillar
series
character
```

---

# 108. Example

```text id="0zhc0w"
Scope:
Shorts / Music

Rule:
Hooks with action in first 1.5s outperform static openings.

Confidence:
0.89
```

---

# 109. Recommendation Engine

Deverá traduzir insights em recomendações simples para usuário.

Exemplo:

```text id="ggfhi6"
Seus Shorts de 20–30 segundos tiveram retenção 14% maior nas últimas 8 semanas.
Recomendamos priorizar essa faixa nas próximas publicações.
```

---

# 110. Não Mostrar Excessiva Estatística

Dashboard principal deve resumir.

Detalhes ficam em Analytics.

---

# 111. Insight Prioritization

Cada insight poderá possuir:

```text id="29hrpp"
impact
confidence
urgency
```

---

# 112. Insight Score

Exemplo:

```text id="ylq2r5"
impact × confidence × urgency
```

---

# 113. Actionable Insights

Evitar mensagens genéricas como:

```text id="7wymtx"
Faça vídeos melhores.
```

Preferir:

```text id="5k2gh5"
Seus vídeos musicais com menos de 2 minutos estão performando 19% acima do baseline. Considere 2 novos conteúdos nesse formato esta semana.
```

---

# 114. Growth Alerts

Eventos futuros:

```text id="hw6l51"
trend.high_relevance_detected
performance.breakout
performance.decline
topic.saturation
content_gap.detected
```

---

# 115. Breakout Detection

Detectar conteúdos significativamente acima do baseline.

---

# 116. Breakout Follow-Up

Quando acontecer:

```text id="hk9n3m"
analyze
↓
identify replicable patterns
↓
suggest related content
```

---

# 117. Não Copiar Automaticamente

Breakout não significa:

```text id="y7lbbv"
criar 10 vídeos iguais
```

Considerar saturação.

---

# 118. Sequel Opportunity

Pode sugerir:

```text id="o70yws"
part 2
related question
deeper version
Short derivative
```

---

# 119. Underperformance Analysis

Detectar vídeos abaixo do baseline.

---

# 120. Underperformance Does Not Automatically Mean Bad Topic

Analisar:

```text id="ax58fs"
title
thumbnail
timing
retention
production quality
topic
```

---

# 121. Diagnosis Categories

```text id="ccgknd"
discovery issue
click issue
retention issue
content mismatch
topic issue
timing issue
insufficient data
```

---

# 122. Optimization Suggestion

Growth Engine poderá recomendar:

```text id="j2sktn"
new title
new thumbnail
related sequel
avoid repeating topic
```

---

# 123. Metadata Revision

Preparar workflow futuro para atualizar título/thumbnail de vídeos publicados quando policy permitir.

---

# 124. Não Alterar Conteúdo Publicado Automaticamente no MVP

Somente sugerir inicialmente.

---

# 125. Content Health

Cada canal poderá possuir:

```text id="3ljb39"
Content Health Score
```

Baseado em:

```text id="fmlkve"
consistency
diversity
performance trend
publishing cadence
content backlog
quality
```

---

# 126. Growth Health

Separar:

```text id="yo5byx"
channel growth
```

de:

```text id="hf8c4d"
content operation health
```

---

# 127. Strategy Health

Avaliar aderência do calendário à estratégia.

---

# 128. Opportunity Inventory

Sistema deverá manter estoque de ideias.

Exemplo:

```text id="533q0h"
20 approved opportunities
7 scheduled
13 available
```

---

# 129. Minimum Idea Inventory

Quando abaixo de threshold:

```text id="ny3w7h"
trigger idea discovery
```

---

# 130. Calendar Inventory

Mesmo princípio.

---

# 131. Trend Urgency

Trend de curta duração pode furar fila editorial somente se policy permitir.

---

# 132. Urgent Opportunity

```text id="duzix8"
high relevance
+
high trend velocity
+
short lifespan
```

---

# 133. Calendar Rescheduling

Pode sugerir:

```text id="x9zeq1"
move evergreen content
```

para abrir espaço.

No modo Assisted, requer aprovação.

---

# 134. Growth Autopilot

No futuro, Autopilot poderá:

```text id="96dv0h"
discover trends
score
adjust calendar
```

dentro de limits.

---

# 135. Growth Policy

Exemplo:

```json id="5ovxj6"
{
  "allow_trend_insertion": true,
  "max_calendar_changes_per_week": 2,
  "minimum_trend_score": 85
}
```

---

# 136. Strategic Guardrails

Nunca quebrar:

```text id="5lsn2k"
blocked topics
brand rules
audience safety
publishing limits
budget
```

---

# 137. Search Data Provider Abstraction

Criar:

```text id="a23cg9"
SearchIntelligenceGateway
```

para futuras fontes.

---

# 138. Trend Provider Abstraction

Criar:

```text id="9mwnmk"
TrendGateway
```

---

# 139. Competitor Provider Abstraction

Criar:

```text id="m30daa"
CompetitorIntelligenceGateway
```

quando implementado.

---

# 140. Growth Data Provenance

Guardar fonte de cada signal.

---

# 141. Signal Deduplication

Mesma tendência encontrada em múltiplas fontes deverá ser consolidada.

---

# 142. Multi-Source Confidence

Se múltiplas fontes independentes confirmam:

```text id="bc40mn"
confidence increases
```

---

# 143. False Trend Guard

Não reagir automaticamente a sinal único de baixa confiança.

---

# 144. Trend Spam Guard

Fontes externas podem trazer conteúdo irrelevante.

Sempre aplicar Channel Fit.

---

# 145. News-Sensitive Channels

Arquitetura deverá permitir canais em que recência tem maior peso.

---

# 146. Evergreen Channels

Em canais infantis ou educativos, trend weight pode ser menor.

---

# 147. Strategy Profiles

Futuramente permitir perfis:

```text id="55tiwp"
growth aggressive
balanced
brand conservative
evergreen first
trend responsive
```

---

# 148. Default

Começar com:

```text id="w803ay"
balanced
```

---

# 149. Goal-Based Strategy

Usuário poderá futuramente escolher:

```text id="tlvzi6"
grow subscribers
maximize views
increase consistency
build authority
reduce production cost
```

---

# 150. Multi-Objective Optimization

Growth Engine deverá suportar mais de um objetivo.

---

# 151. Goal Weights

Exemplo:

```text id="wq1vuf"
views 50%
subscribers 30%
cost efficiency 20%
```

---

# 152. Não Prometer Resultado

Scores são heurísticas e previsões internas.

Não apresentar como garantia de viralização.

---

# 153. Experiment Engine

Preparar futuro suporte para:

```text id="tlxu2c"
content experiments
```

---

# 154. Experiment Types

```text id="aylx3c"
hook
duration
title
thumbnail
posting time
format
CTA
```

---

# 155. Experimental Ratio

Estratégia deverá reservar percentual controlado.

---

# 156. Experiment Baseline

Comparar com conteúdo semelhante.

---

# 157. Experiment Result

```text id="44pss9"
win
loss
inconclusive
```

---

# 158. Inconclusive Matters

Não forçar conclusão.

---

# 159. SEO Quality Gate

SEO Package deve passar por:

```text id="q1nswa"
accuracy
brand fit
readability
policy
metadata consistency
```

---

# 160. Metadata Consistency

Título, thumbnail e conteúdo precisam contar a mesma história.

---

# 161. Title-Thumbnail Pair Score

Criar conceito:

```text id="7l2wk5"
Pair Score
```

---

# 162. Pair Evaluation

Avaliar:

```text id="xlxqsf"
complementarity
accuracy
curiosity
clarity
```

---

# 163. Multiple Candidates

Sistema poderá manter:

```text id="m2z86i"
Title A
Title B
Title C

Thumbnail A
Thumbnail B
Thumbnail C
```

---

# 164. Selection

No Assisted:

```text id="my9you"
user chooses
```

No Autopilot:

```text id="n31k3r"
policy + score chooses
```

---

# 165. Channel-Specific SEO

Aprender padrões de títulos que funcionam naquele canal.

---

# 166. Avoid Global SEO Rules

O que funciona em canal financeiro pode não funcionar em infantil.

---

# 167. Analytics Feedback

Após publicação, relacionar performance com:

```text id="0zt8zi"
topic
title style
thumbnail style
hook
duration
time
format
```

---

# 168. Attribution Caution

Performance depende de múltiplas variáveis.

Learning Engine deverá evitar atribuição excessivamente simples.

---

# 169. Growth Knowledge Base

Learned Rules + Performance Insights formam a memória de crescimento.

---

# 170. Knowledge Aging

Regras antigas deverão perder influência ou expirar.

---

# 171. User Corrections

Se usuário rejeitar insight:

```text id="w2uk8w"
store feedback
```

---

# 172. User Preferences

Usuário pode indicar:

```text id="ek4nh0"
don't cover topic X
prioritize series Y
maximum 1 Short/day
```

Growth Engine deve respeitar.

---

# 173. Explicit Preferences Beat Inference

Dentro dos limites de segurança.

---

# 174. Growth Dashboard

Interface simples:

```text id="y8q5pg"
O que está funcionando
O que caiu
Novas oportunidades
Próximos conteúdos
Recomendações
```

---

# 175. Example Insight Cards

```text id="outq0v"
↑ Shorts musicais
+18% vs baseline

→ Recomendação
Produzir 2 esta semana
```

---

# 176. Trend Card

```text id="dwhjca"
Tendência relevante detectada

Tema: X
Fit com canal: 94
Urgência: Alta

[Adicionar ao calendário]
```

---

# 177. Opportunity Card

```text id="se5w5g"
92
Opportunity Score

Tema
Formato recomendado
Motivo
Janela sugerida
```

---

# 178. User Should Not See 12 Scores by Default

Mostrar score final.

Detalhes ficam expansíveis.

---

# 179. Explainability

Ao abrir detalhes:

```text id="ipsfol"
Channel Fit 96
Audience Fit 91
Trend 84
Retention 90
```

---

# 180. Internal Admin Analytics

Control Center deverá permitir investigar:

```text id="ek0vuo"
which recommendation engine version
which agent version
which weights
```

---

# 181. Growth Policy Versioning

Pesos e thresholds deverão ser versionáveis.

---

# 182. Strategy Versioning

Toda mudança significativa:

```text id="9ia9j6"
new strategy version
```

---

# 183. User Approval

No Assisted, strategy candidate precisa aprovação.

---

# 184. Strategy Diff

Mostrar:

```text id="7jqu6n"
Old
New
Reason
Expected impact
```

---

# 185. Strategy Change Limits

Autopilot não deverá alterar drasticamente mix editorial de uma só vez.

---

# 186. Maximum Change

Exemplo configurável:

```text id="lqh29b"
content pillar weight change ≤ 15%
```

por ciclo.

---

# 187. Strategy Stability

Growth Engine deve valorizar consistência.

---

# 188. Cold Start Channels

Para canal novo com pouco histórico:

```text id="i71i60"
greater use of niche priors
+
user context
+
benchmark data
```

---

# 189. Low Data Confidence

Mostrar:

```text id="sbvsbk"
confidence lower
```

---

# 190. Cold Start Exploration

Maior experimental ratio pode ser apropriado.

---

# 191. Mature Channel

Com histórico robusto:

```text id="cn3y3r"
more channel-specific optimization
```

---

# 192. Cross-Channel Learning

Futuramente plataforma poderá aprender benchmarks agregados.

Mas:

```text id="o6td6c"
never leak private channel data
```

---

# 193. Aggregated Benchmark

Somente dados anonimizados/agregados quando aplicável.

---

# 194. Benchmark Use

Exemplo:

```text id="st8jqp"
new kids music channel
```

pode usar baseline global desse segmento até possuir histórico próprio.

---

# 195. Channel-Specific Data Takes Priority

Quando amostra suficiente.

---

# 196. Recommendation Confidence Levels

```text id="v3ssq7"
High
Medium
Low
```

mapear para confidence interno.

---

# 197. Low Confidence Recommendations

Não auto-aplicar em Autopilot.

---

# 198. High Impact + Low Confidence

Enviar para Human Review.

---

# 199. Growth Event Types

```text id="z3l4om"
growth.opportunity.created
growth.insight.created
growth.breakout.detected
growth.decline.detected
trend.detected
content.saturation.detected
strategy.change.recommended
```

---

# 200. Growth Workflows

Principais:

```text id="mya64a"
channel.intelligence.refresh.v1
strategy.refresh.v1
ideas.discovery.v1
opportunity.evaluate.v1
calendar.plan.v1
performance.evaluate.v1
learning.evaluate.v1
seo.optimize.v1
thumbnail.evaluate.v1
```

---

# 201. Fases Relacionadas

```text id="o2y5ia"
F05 Channel Importer
→ raw data

F06 Channel Intelligence
→ classification/audience

F07 Channel DNA
→ structured identity

F08 Strategy
→ content strategy

F09 Ideas & Opportunities
→ discovery/scoring

F10 Calendar
→ planning

F17 SEO & Thumbnail
→ discoverability

F19 Analytics & Learning
→ feedback loop

F20 Autopilot
→ autonomous optimization
```

---

# 202. Testes Obrigatórios

Criar testes para:

```text id="fwbeq2"
duplicate ideas
topic saturation
strategy balance
opportunity scoring
trend relevance
low confidence
calendar conflicts
baseline calculations
learning thresholds
```

---

# 203. Golden Cases

Exemplos:

```text id="93f2pq"
kids music channel
financial education channel
faceless curiosity channel
new channel with little data
mature channel with strong history
```

---

# 204. Expected Behavior Example

Canal:

```text id="yran3t"
kids entertainment
music + stories
```

Trend:

```text id="22ryt6"
major cryptocurrency event
```

Resultado esperado:

```text id="762fz9"
high trend
low channel fit
REJECT
```

---

# 205. Another Example

Trend:

```text id="dkuurs"
new dinosaur discovery
```

Canal:

```text id="n5qzjt"
kids science/curiosity
```

Resultado:

```text id="xd1mtp"
high relevance
candidate opportunity
```

---

# 206. Another Example

Canal publicou:

```text id="itmp1v"
5 dinosaur Shorts in last 7 days
```

Nova ideia de dinossauro:

```text id="xac513"
high fit
high trend
```

Mas:

```text id="v246tx"
saturation penalty
```

Calendar Planner pode adiar.

---

# 207. Definition of Done — Channel Intelligence

Considerado pronto quando:

```text id="724t6x"
channel can be analyzed
profile created
audience inferred
patterns identified
confidence stored
evidence stored
```

---

# 208. Definition of Done — Opportunity Engine

Pronto quando:

```text id="sre8u7"
ideas generated
duplicates filtered
scores calculated
weights configurable
confidence included
ranking produced
```

---

# 209. Definition of Done — Calendar Intelligence

Pronto quando:

```text id="vp472z"
recommended slots generated
pillar balance checked
format mix checked
conflicts detected
calendar persisted
```

---

# 210. Definition of Done — SEO

Pronto quando:

```text id="h7eg5w"
multiple title candidates
SEO package
thumbnail concepts
scores
selection workflow
```

---

# 211. Definition of Done — Learning

Pronto quando:

```text id="w3kt9n"
snapshots compared
baseline available
insights created
candidate learning created
confidence/sample/effect required
validated rules stored
```

---

# 212. Documentation

Manter:

```text id="kwms26"
/docs/growth.md
```

com:

```text id="p94fru"
Channel DNA
audience
strategy
trend engine
opportunity scoring
calendar intelligence
SEO
learning
```

---

# 213. Score Documentation

Todos os scores deverão documentar:

```text id="shc43t"
meaning
range
inputs
weights
thresholds
version
```

---

# 214. No Magic Scores

Nenhum score poderá existir apenas porque “a IA disse 92”.

Deverá possuir componentes e regras documentadas.

---

# 215. LLM Contribution

LLM pode avaliar critérios qualitativos.

Mas cálculo final deverá preferencialmente ocorrer em código.

Exemplo:

```text id="u7tz3c"
Agent outputs component scores
↓
OpportunityScoreService
calculates weighted total
```

---

# 216. Deterministic Calculations

Sempre que cálculo puder ser determinístico:

```text id="ntm0ag"
use code
```

não LLM.

---

# 217. Growth Engine Authority

Growth Engine pode:

```text id="nw6lfg"
recommend
rank
prioritize
```

Não pode:

```text id="jj6mc8"
ignore policy
publish directly
alter billing
```

---

# 218. Autopilot Integration

No Autopilot:

```text id="xqra9a"
Growth Engine recommends
↓
Policy Engine validates
↓
Calendar Workflow executes
```

---

# 219. User Trust

Toda recomendação importante deverá poder ser explicada em linguagem simples.

Exemplo:

```text id="2n9sk9"
Recomendamos este Short porque conteúdos semelhantes tiveram retenção acima da média, o tema está crescendo e ele não foi explorado recentemente no canal.
```

---

# 220. Princípio Final

O Growth Engine deverá funcionar como um **editor-chefe orientado por dados**, não como um caçador cego de tendências.

Ele deve ser capaz de responder:

```text id="ad8rc1"
O que publicar?
Por quê?
Para quem?
Em qual formato?
Quando?
Com qual prioridade?
Qual o risco?
Qual a confiança?
Como isso se relaciona com o que já publicamos?
O que aprendemos depois?
```

O objetivo é criar crescimento sustentável mantendo a identidade editorial do canal.

Este documento deverá permanecer como referência obrigatória durante todas as fases relacionadas a inteligência de canal, estratégia, ideação, tendências, SEO, analytics e aprendizado.