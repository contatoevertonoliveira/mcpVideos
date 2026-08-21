# Documento 08B — Visual Baseline V1 e Regras de Reprodução pelo Claude Code

## 1. Objetivo

Este documento complementa:

```text
Documento 08  — UX/UI e Control Center
Documento 08A — Direção Visual, Design System e Linguagem Futurista
```

O Documento 08B estabelece as telas produzidas e aprovadas no Google Stitch como:

```text
VISUAL BASELINE V1
```

Essas referências passam a representar a direção visual oficial da aplicação durante sua implementação.

O Claude Code deverá utilizar simultaneamente:

```text
Documento 08
+
Documento 08A
+
Documento 08B
+
Referências visuais do Stitch
```

O objetivo não é simplesmente copiar screenshots pixel por pixel.

O objetivo é transformar o conceito aprovado em um **Design System consistente, reutilizável, responsivo e preparado para evolução**.

---

## 2. Referências Visuais Oficiais

Organizar as imagens fornecidas em:

```text
/docs/design/reference/

01-dashboard.png
02-ideas.png
03-calendar.png
04-content-production.png
05-brand-concept.png
```

Esses arquivos representam:

```text
Visual Baseline V1
```

e deverão ser consultados antes da implementação das respectivas telas.

---

## 3. Regra Fundamental

As referências do Stitch são:

```text
VISUAL DIRECTION
```

e não:

```text
STATIC SCREENSHOTS TO BE HARD-CODED
```

Claude Code deverá extrair delas:

- linguagem visual;
- hierarquia;
- proporções;
- densidade;
- navegação;
- composição;
- padrões de cards;
- comportamento das superfícies;
- tipografia;
- estados;
- identidade de IA;
- linguagem audiovisual.

Depois deverá consolidar tudo isso em componentes reutilizáveis.

---

## 4. Direção Aprovada

A direção visual apresentada pelo Stitch está aprovada como base.

Preservar:

```text
Dark Premium
Clean
Minimal
AI Native
Video First
High-End SaaS
Futuristic
Operational
Cinematic
```

O produto deve parecer um:

> **AI Content Operating System**

e não apenas um painel de gerenciamento de YouTube.

---

## 5. O Que Está Aprovado

Manter como referência:

- fundo graphite/navy-black;
- sidebar escura;
- superfícies discretamente elevadas;
- accent azul/violeta;
- tipografia branca/off-white;
- textos secundários azulados/cinzas;
- cards com bordas discretas;
- thumbnails integradas à interface;
- status pequenos;
- hierarquia tipográfica forte;
- bastante espaço negativo;
- ícones lineares;
- poucos elementos saturados;
- IA representada de maneira abstrata;
- pipeline visual;
- previews audiovisuais grandes.

---

## 6. O Que NÃO Deve Ser Copiado Literalmente

Existem pequenas inconsistências entre as telas geradas pelo Stitch.

Claude Code deverá normalizar:

```text
sidebar width
topbar behavior
AI Magic position
page margins
card radius
card padding
icon size
button height
status badge style
navigation spacing
header alignment
```

Nenhuma inconsistência entre screenshots deverá gerar componentes diferentes sem necessidade funcional.

---

## 7. Shell Oficial da Aplicação

Criar um único:

```text
AppShell
```

Estrutura:

```text
┌──────────────┬──────────────────────────────────────────┐
│              │ TOPBAR                                  │
│   SIDEBAR    ├──────────────────────────────────────────┤
│              │                                          │
│              │ PAGE CONTENT                             │
│              │                                          │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

Esse shell será compartilhado pelas páginas principais.

---

## 8. Sidebar Oficial

As quatro telas apresentam pequenas variações.

Unificar.

Desktop recomendado:

```text
width expanded: ~176–196px
width collapsed: ~64–72px
```

Não tratar esses números como pixel-perfect obrigatório; preservar principalmente a proporção visual.

---

## 9. Sidebar — Estrutura

Parte superior:

```text
Logo
Product Name
Product Descriptor
```

Navegação principal:

```text
Dashboard
Ideas
Calendar
Content
Analytics
```

Área especial:

```text
AI Magic
```

Área inferior:

```text
Channels
Settings
Profile
```

---

## 10. AI Magic

O botão `AI Magic` apresentado pelo Stitch representa uma função global de IA.

Ele deverá possuir visual especial, mas não competir com a navegação.

Manter:

```text
blue → violet subtle gradient
AI abstract icon
soft glow on hover
```

### Regra

Sua posição deve ser **idêntica em todas as telas**.

Não alternar entre topo e centro da sidebar conforme a página.

---

## 11. Evolução Futura do AI Magic

Esse componente poderá futuramente abrir:

```text
AI Command Center
```

permitindo comandos como:

```text
"Crie três ideias para amanhã"

"Analise meu calendário"

"Produza um Short"

"Por que este vídeo teve baixa retenção?"
```

A F01 deverá apenas preparar o componente visual.

Não implementar funcionalidade futura prematuramente.

---

## 12. Topbar Oficial

Criar um componente:

```text
TopBar
```

Contendo, conforme contexto:

```text
Global Search
Notifications
Channel Selector
Autopilot Status
User Actions
```

Nem todas as informações precisam estar sempre visíveis.

---

## 13. Page Container

Todas as páginas devem compartilhar:

```text
PageContainer
```

com:

- largura consistente;
- padding consistente;
- alinhamento comum;
- breakpoints;
- spacing vertical padronizado.

---

## 14. Page Header

Criar:

```text
PageHeader
```

Estrutura:

```text
Title
Subtitle
Optional Metadata

                         Primary Action
```

Exemplos:

```text
Ideas
New opportunities found for your channel.

                         Generate new ideas
```

ou:

```text
Calendar
This week · 8 items planned

                         Week | Month | List
```

---

## 15. Tipografia

A tipografia apresentada está conceitualmente aprovada.

Criar hierarquia consistente.

Sugestão:

```text
Display       36–40
Page Title    32–36
Section       20–24
Card Title    16–20
Body          14–16
Small         12–13
Caption       11–12
```

Os valores deverão responder adequadamente ao viewport.

---

## 16. Texto Principal

Usar off-white em vez de branco absoluto em todas as situações.

---

## 17. Texto Secundário

Usar foreground muted.

Nunca reduzir contraste a ponto de prejudicar leitura.

---

## 18. Background

A referência visual utiliza corretamente um fundo quase preto.

Transformar em token:

```text
--background
```

Não utilizar `#000`.

---

## 19. Surface Hierarchy

Criar pelo menos:

```text
--surface
--surface-subtle
--surface-elevated
--surface-hover
--surface-selected
```

---

## 20. Borders

Criar:

```text
--border-subtle
--border-default
--border-focus
```

A maioria dos cards deverá utilizar `border-subtle`.

---

## 21. Accent

A identidade apresentada pelo Stitch utiliza corretamente azul/violeta.

Definir:

```text
--accent-primary
--accent-secondary
--accent-soft
--accent-glow
```

---

## 22. Semantic Colors

Separar identidade da aplicação de estados.

Criar:

```text
--success
--warning
--danger
--info
--processing
```

---

## 23. Dashboard — Baseline Oficial

A tela Dashboard deverá preservar a arquitetura apresentada.

Estrutura aproximada:

```text
PAGE HEADER
Good morning
Channel summary                 Autopilot

TODAY                           CHANNEL HEALTH
                                NEEDS ATTENTION

METRICS
```

Com evolução futura para oportunidades e insights.

---

## 24. Dashboard — Today

O bloco `Today` deverá continuar sendo o elemento principal.

Motivo:

ele responde imediatamente:

> O que está acontecendo com meu canal hoje?

---

## 25. Today Item

Criar componente:

```text
TodayContentItem
```

Campos:

```text
thumbnail
time
format
title
status
pipeline
```

---

## 26. Today — Estados

Exemplos:

```text
Published
Producing
Scheduled
Review
Failed
```

---

## 27. Pipeline Compacto

A representação:

```text
Script ✓
Storyboard ✓
Media ●
QA ○
```

está aprovada.

Criar:

```text
CompactPipeline
```

---

## 28. Channel Health

A composição circular está aprovada.

Criar:

```text
ChannelHealthCard
```

Exemplo:

```text
     92
    /100

Connection ✓
Calendar   ✓
Production ✓
Budget     ✓
```

---

## 29. Channel Health Não é Gamificação

Não transformar em sistema de medalhas, XP ou ranking.

Representa condição operacional.

---

## 30. Needs Your Attention

O card âmbar está aprovado.

Criar:

```text
AttentionCard
```

Usar apenas quando ação humana for necessária.

---

## 31. Métricas do Dashboard

O padrão:

```text
VIEWS (30D)

824K
↗ +12%
```

está aprovado.

Criar:

```text
MetricCard
```

---

## 32. Dashboard — Evolução

Conforme Documento 08A, futuramente adicionar:

```text
Opportunities
AI Insight
Recent Content
```

sem destruir a composição inicial.

---

## 33. Ideas — Baseline Oficial

A página Ideas está aprovada como estrutura.

Preservar:

```text
Page Header
Filters
Opportunity Grid
```

---

## 34. Ideas Filters

Criar:

```text
FilterChips
```

Exemplos:

```text
All
Shorts
Videos
Curiosities
Music
Stories
```

---

## 35. Opportunity Card

A estrutura visual está aprovada.

Criar:

```text
OpportunityCard
```

Com:

```text
score
format
title
summary
pillar
source
reason
actions
```

---

## 36. Opportunity Score

Manter score pequeno porém claramente identificável.

Exemplo:

```text
↗ 94
```

---

## 37. Score Semantics

Não determinar cor diretamente no componente.

Usar função:

```text
getOpportunityScoreVariant(score)
```

ou equivalente.

---

## 38. Opportunity Reason

O bloco:

```text
Why:
High search volume...
```

é importante.

Ele cria explicabilidade.

Preservar.

---

## 39. Source

Pode representar:

```text
Trend Analysis
Audience
Channel History
Competitor Gap
Search Demand
Learning Engine
```

---

## 40. Card Actions

A hierarquia deverá ser:

```text
Primary:
Add to calendar

Secondary:
Details

Tertiary:
Discard
```

O ícone de lixeira não deve parecer tão importante quanto o CTA principal.

---

## 41. Generate New Ideas

O botão principal no topo está aprovado.

Usar accent azul claro/primary.

---

## 42. Calendar — Baseline Oficial

A estrutura semanal apresentada está aprovada.

Preservar:

```text
Week Header
Day Columns
Content Cards
AI Suggestions
```

---

## 43. Calendar Header

Criar:

```text
CalendarToolbar
```

com:

```text
Week
Month
List
Filters
```

---

## 44. Calendar Grid

Criar componente próprio:

```text
EditorialCalendar
```

Não depender exclusivamente de uma biblioteca com aparência visual incompatível.

Bibliotecas podem cuidar de comportamento, mas styling deverá seguir o Design System.

---

## 45. Calendar Content Card

Criar:

```text
CalendarContentCard
```

Mostrar:

```text
time
thumbnail
format
title
status
```

---

## 46. Calendar Status Rail

O uso de uma pequena linha colorida lateral está aprovado.

Ela pode representar estado sem pintar o card inteiro.

---

## 47. AI Idea Card

O card tracejado apresentado na quinta-feira está conceitualmente aprovado.

Representa:

```text
suggestion
not yet scheduled
```

Criar:

```text
CalendarSuggestionCard
```

---

## 48. AI Idea Visual

Deverá ser menos sólido que um conteúdo aprovado.

Usar:

```text
dashed/subtle border
muted surface
AI badge
```

---

## 49. Calendar Drag & Drop

Ao implementar:

```text
drag
→ card elevation

drop target
→ subtle accent

saving
→ small processing indicator
```

---

## 50. Content Production — Baseline Oficial

Esta tela deverá ser considerada uma das principais referências de identidade do produto.

Ela representa a transformação do sistema de:

```text
dashboard SaaS
```

para:

```text
AI audiovisual production environment
```

---

## 51. Content Header

Preservar:

```text
status
project ID
title
actions
```

Mas IDs técnicos poderão ser omitidos do User App caso não tenham utilidade.

---

## 52. Content Navigation

Tabs:

```text
Overview
Script
Scenes
Preview
SEO
History
```

estão aprovadas.

---

## 53. Preview Principal

O vídeo deverá ser o maior elemento da tela.

Criar:

```text
VideoPreview
```

---

## 54. Video Preview Controls

Usar player próprio ou customizado conforme necessidade.

Manter aparência integrada.

---

## 55. Rendering State

Durante geração:

```text
Rendering Scene 02...
```

pode aparecer junto à timeline/progress.

---

## 56. Production Pipeline

A coluna direita está aprovada.

Criar:

```text
ProductionPipeline
```

---

## 57. Pipeline Steps

Exemplos:

```text
Idea Generation
Script
Storyboard
Media Generation
Quality Assurance
SEO & Metadata
Publication
```

---

## 58. Pipeline Step States

```text
completed
active
pending
attention
failed
```

---

## 59. Active Pipeline Step

Pode expandir detalhes.

Exemplo:

```text
Media Generation

Visuals 2/12       18%
Audio/Voiceover   100%
```

---

## 60. Scene Pipeline

A seção inferior está aprovada.

Criar:

```text
ScenePipeline
```

---

## 61. Scene Card

Criar:

```text
SceneCard
```

Com:

```text
scene number
time range
preview
title
generation status
progress
```

---

## 62. Review Required

O card âmbar integrado entre as cenas está aprovado conceitualmente.

Porém deverá ser tratado como:

```text
QualityIssueCard
```

e não necessariamente ocupar permanentemente uma posição no grid.

---

## 63. Quality Issue

Estrutura:

```text
REVIEW REQUIRED

Scene 01 — Audio Sync

Voice sync issue detected at 00:18.

[Approve as is]
[Apply Fix]
```

---

## 64. Apply Fix

CTA de correção deverá ter maior peso visual que `Approve as is` quando a recomendação automática for reparar.

---

## 65. Quick Actions

A coluna:

```text
Edit Source Script
Adjust Style Prompts
Halt Production
```

é útil.

Criar:

```text
QuickActionsCard
```

---

## 66. Halt Production

É ação crítica.

Usar vermelho discreto.

Não posicionar como CTA primário.

---

## 67. Layout da Production Page

Desktop:

```text
MAIN CONTENT              RIGHT PANEL

Video Preview             Production Pipeline

Scene Pipeline            Quick Actions
```

---

## 68. Responsive Production

Tablet:

```text
Preview
Pipeline
Scenes
Actions
```

Mobile:

```text
Preview
Current Status
Attention
Scenes
Actions
```

---

## 69. Video-First Rule

Nas telas de conteúdo:

> vídeo e imagem têm precedência visual sobre texto administrativo.

---

## 70. Brand Concept — Baseline

A marca apresentada:

```text
YOUTUBE AI AUTOMATION
```

não deverá necessariamente ser adotada como nome definitivo.

O conceito gráfico, porém, poderá servir de referência.

---

## 71. Elementos de Marca Aproveitáveis

O símbolo apresenta:

```text
play
connected nodes
automation
movement
```

Essa direção está alinhada ao produto.

---

## 72. Evitar Dependência da Marca YouTube

O nome final não deverá obrigatoriamente conter:

```text
YouTube
```

porque a arquitetura prevê expansão futura.

---

## 73. Branding Placeholder

Enquanto não houver marca definitiva, utilizar:

```text
Creator OS
```

como nome interno/placeholder visual, se necessário.

Não tratar automaticamente como marca comercial definitiva.

---

## 74. Descriptor

Pode utilizar temporariamente:

```text
AI Content Automation
```

em vez de:

```text
AI Automation
```

por ser mais descritivo.

---

## 75. Futurismo — Refinamento

O Stitch já criou uma boa base, mas o Claude deverá aumentar levemente a identidade de IA através de:

```text
subtle ambient lighting
processing animations
AI-specific accents
media previews
pipeline transitions
microinteractions
```

---

## 76. Não Alterar Estrutura Para Parecer Mais Futurista

Não adicionar:

```text
3D globes
random particles everywhere
holograms
large neon rings
animated backgrounds everywhere
```

---

## 77. Ambient Glow

Permitido em:

```text
AI Magic
Autopilot
active generation
special AI Insight
```

---

## 78. Autopilot

Criar componente:

```text
AutopilotStatus
```

Exemplo:

```text
● Autopilot Active
```

---

## 79. Autopilot States

```text
manual
assisted
semi-auto
autopilot
paused
```

---

## 80. Autopilot Visual Importance

Deve ser visível, mas não dominar a página.

---

## 81. Component Architecture

Estrutura conceitual:

```text
UI PRIMITIVES
    ↓
PRODUCT COMPONENTS
    ↓
FEATURE COMPONENTS
    ↓
PAGE COMPOSITIONS
```

---

## 82. UI Primitives

Exemplos:

```text
Button
Badge
Card
Input
Select
Tabs
Tooltip
Dropdown
Dialog
Sheet
Progress
Avatar
Skeleton
```

---

## 83. Product Components

```text
MetricCard
VideoPreview
StatusBadge
ChannelHealth
AutopilotStatus
CompactPipeline
```

---

## 84. Feature Components

```text
TodayContentItem
OpportunityCard
CalendarContentCard
CalendarSuggestionCard
ProductionPipeline
SceneCard
QualityIssueCard
```

---

## 85. Proibido

Não criar:

```text
DashboardCard1
DashboardCard2
DarkCard
PurpleCard
```

se a diferença puder ser representada por variantes de um componente existente.

---

## 86. Component Variants

Exemplo:

```text
<Card variant="default" />
<Card variant="elevated" />
<Card variant="attention" />
```

---

## 87. Status Component

Centralizar estados:

```text
<StatusBadge status="producing" />
```

Não repetir regras de cor em cada página.

---

## 88. Iconography

Utilizar uma biblioteca única.

Não misturar vários estilos.

---

## 89. Spacing System

Usar escala consistente.

Exemplo conceitual:

```text
4
8
12
16
20
24
32
40
48
64
```

via tokens/framework.

---

## 90. Radius

Cards das referências usam cantos discretos.

Manter aproximadamente:

```text
8–12px
```

para superfícies comuns.

Modals podem usar radius maior.

---

## 91. Border Width

Normalmente:

```text
1px
```

com baixa opacidade.

---

## 92. Shadows

No dark mode:

evitar depender de sombras pretas.

Utilizar principalmente:

```text
surface contrast
border
subtle ambient shadow
```

---

## 93. Buttons

Padronizar alturas.

Exemplo:

```text
sm
md
lg
```

---

## 94. Primary CTA

Usar azul claro/accent semelhante às referências.

---

## 95. AI CTA

Pode usar gradiente azul-violeta.

Não aplicar esse gradiente em todo botão primário.

---

## 96. Attention CTA

Pode utilizar amber/orange.

---

## 97. Destructive CTA

Somente vermelho.

---

## 98. Hover

Cards:

```text
surface slightly brighter
border slightly stronger
translateY(-1px)
```

---

## 99. Selected

Elementos selecionados podem utilizar:

```text
accent border
accent soft background
```

---

## 100. Focus

Focus ring deve ser visível e consistente.

---

## 101. Motion

Usar:

```text
150–250ms
```

como referência para microinterações.

---

## 102. Production Motion

Pode ser um pouco mais expressivo:

```text
progress
pulse
shimmer
processing indicator
```

---

## 103. Reduced Motion

Respeitar configuração do sistema operacional.

---

## 104. Skeletons

Criar skeletons compatíveis com layout real.

---

## 105. Loading

Evitar:

```text
full-page spinner
```

quando skeleton ou progress contextual for melhor.

---

## 106. Empty States

Devem seguir a mesma linguagem premium.

---

## 107. Error States

Não substituir a tela inteira por mensagem técnica.

---

## 108. Responsive Baseline

As referências são desktop.

Claude deverá derivar comportamento responsivo.

---

## 109. Desktop

```text
>= 1280px
```

Sidebar expandida.

Layouts multicoluna.

---

## 110. Laptop

```text
1024–1279px
```

Reduzir gaps e, se necessário, sidebar.

---

## 111. Tablet

```text
768–1023px
```

Sidebar colapsável.

Cards reorganizados.

---

## 112. Mobile

```text
< 768px
```

Não simplesmente reduzir o desktop.

Reorganizar prioridades.

---

## 113. Mobile Navigation

Usar:

```text
bottom navigation
```

para ações principais.

---

## 114. Mobile Dashboard Priority

Ordem:

```text
Attention
Today
Autopilot
Health
Metrics
```

se houver atenção pendente.

---

## 115. Mobile Production Priority

```text
Preview
Current Step
Quality Attention
Scenes
Actions
```

---

## 116. Mobile Calendar

Preferir:

```text
day/list hybrid
```

em vez de sete colunas comprimidas.

---

## 117. Accessibility

WCAG deverá orientar contraste e interação.

---

## 118. Touch Targets

Em mobile, manter alvos adequados.

---

## 119. Tooltip

Ícones sem label visual deverão possuir tooltip no desktop.

---

## 120. Screen Readers

Botões apenas com ícone precisam de `aria-label`.

---

## 121. Visual Regression

Ao implementar telas principais, gerar screenshots de desenvolvimento para comparação visual quando o ambiente permitir.

---

## 122. Não Buscar Pixel Perfection Cega

Diferenças são permitidas quando melhorarem:

```text
consistency
accessibility
responsiveness
maintainability
```

---

## 123. Critério de Fidelidade

Pergunta principal:

> A implementação parece claramente pertencer ao mesmo produto apresentado nas referências?

Se não, deverá ser revisada.

---

## 124. Design System Documentation

Manter:

```text
/docs/design-system.md
```

---

## 125. Documentar

```text
colors
surfaces
typography
spacing
radius
shadows
motion
buttons
cards
statuses
navigation
media
```

---

## 126. F01 — O Que Implementar

Na Fase 01, usar este baseline para criar somente:

```text
ThemeProvider
Design Tokens
AppShell
Sidebar
TopBar
PageContainer

Button
Badge
Card
Input
Tabs
Tooltip
Skeleton

basic responsive behavior
```

---

## 127. F01 — Showcase

Criar uma rota apenas de desenvolvimento, se apropriado:

```text
/dev/ui
```

para validar o Design System.

Não disponibilizar em produção.

---

## 128. Showcase Deve Demonstrar

```text
typography
buttons
badges
cards
inputs
surfaces
statuses
sidebar
topbar
loading
```

---

## 129. F01 — Não Implementar

Ainda não criar funcionalidade real de:

```text
Dashboard
Ideas
Calendar
Production
Analytics
Autopilot
```

Somente foundations compartilhadas.

---

## 130. Implementação Progressiva das Referências

As telas deverão entrar conforme as fases funcionais correspondentes.

```text
Dashboard Shell
→ progressivamente

Ideas
→ F09

Calendar
→ F10

Content Production
→ F12–F17
```

---

## 131. Mock Data

Durante implementação visual de uma feature, dados mock podem ser utilizados temporariamente.

Mas devem ficar claramente separados dos serviços reais.

---

## 132. Proibido Hardcode de Mock em Produção

Não deixar:

```text
824K
+6.2K
92
```

hardcoded em componentes finais.

---

## 133. Data-Driven Components

Componentes devem receber props.

Exemplo conceitual:

```tsx
<MetricCard
  label="Views"
  value={metrics.views}
  trend={metrics.viewsTrend}
/>
```

---

## 134. Internationalization

Os screenshots utilizam inglês.

A arquitetura deve permitir:

```text
pt-BR
en
```

e outros idiomas futuramente.

---

## 135. Não Codificar Texto Dentro de Componente Genérico

Preferir i18n ou conteúdo recebido por props conforme arquitetura.

---

## 136. Datas e Horários

Renderizar de acordo com locale e timezone do usuário/canal.

---

## 137. Media Aspect Ratio

Componentes deverão suportar explicitamente:

```text
9:16
16:9
1:1
```

---

## 138. Não Deformar Mídia

Obrigatório.

---

## 139. Shorts

Sempre preservar natureza vertical quando a UI permitir.

---

## 140. Long Form

Utilizar preview horizontal.

---

## 141. Performance Visual

Lazy-load thumbnails e mídia.

---

## 142. Video Playback

Não iniciar dezenas de vídeos automaticamente.

---

## 143. Hover Preview

Somente quando:

```text
supported
performant
useful
```

---

## 144. Sidebar Consistency Test

Ao navegar entre:

```text
Dashboard
Ideas
Calendar
Content
Analytics
```

a sidebar não pode mudar de:

```text
width
logo position
navigation spacing
AI Magic position
```

---

## 145. Header Consistency Test

Page titles devem compartilhar alinhamento e escala.

---

## 146. Card Consistency Test

Cards semelhantes devem compartilhar:

```text
radius
border
surface
padding logic
```

---

## 147. Button Consistency Test

Mesmo CTA não deve parecer diferente em páginas distintas.

---

## 148. Status Consistency Test

`Producing` deve possuir o mesmo tratamento visual em toda a aplicação.

O mesmo para:

```text
Published
Scheduled
Review
Failed
```

---

## 149. Final Design Test — Dashboard

Deve transmitir:

```text
"Minha operação está sob controle."
```

---

## 150. Final Design Test — Ideas

Deve transmitir:

```text
"A IA encontrou oportunidades relevantes para mim."
```

---

## 151. Final Design Test — Calendar

Deve transmitir:

```text
"Consigo visualizar o que será produzido e publicado."
```

---

## 152. Final Design Test — Production

Deve transmitir:

```text
"Meu vídeo está sendo produzido e eu consigo acompanhar cada etapa."
```

---

## 153. Final Design Test — AI

A IA deve parecer:

```text
embedded throughout the product
```

e não uma feature isolada.

---

## 154. Final Design Test — Control

Mesmo em Autopilot, a UI deverá sempre oferecer:

```text
visibility
explainability
pause
review
override
```

---

## 155. Futuro Control Center

O Control Center administrativo deverá derivar do mesmo Design System.

Pode aumentar densidade, mas não mudar identidade.

---

## 156. Não Criar Segundo Design System

User App e Control Center compartilham:

```text
tokens
primitives
icons
typography
statuses
```

---

## 157. Nome Interno do Design System

Pode ser identificado no projeto simplesmente como:

```text
Creator UI
```

até definição de branding.

---

## 158. Source of Truth Visual

A ordem de autoridade será:

```text
1. Documento 08
   UX / journeys / information architecture

2. Documento 08A
   visual language / design principles

3. Documento 08B
   implementation baseline

4. Stitch references
   concrete visual examples
```

Se houver conflito visual pequeno entre screenshots:

```text
08B + Design System consistency
```

prevalecem sobre reprodução literal.

---

## 159. Instrução Direta ao Claude Code

Antes de implementar frontend relacionado a uma tela coberta pelas referências:

```text
1. Read Document 08
2. Read Document 08A
3. Read Document 08B
4. Inspect relevant Stitch reference
5. Identify reusable components
6. Check existing design tokens
7. Implement
8. Test responsive behavior
9. Test accessibility
10. Compare visually with baseline
```

---

## 160. Não Redesenhar Sem Necessidade

Claude Code não deverá decidir sozinho que:

```text
sidebar should move
cards should become white
theme should become light
navigation should change
dashboard composition should change
```

sem requisito funcional ou justificativa técnica concreta.

---

## 161. Melhorias São Permitidas

Claude poderá corrigir:

```text
alignment
responsive behavior
accessibility
spacing inconsistencies
component consistency
contrast
```

sem descaracterizar o baseline.

---

## 162. Mudanças Maiores

Qualquer mudança significativa de:

```text
navigation
visual identity
page composition
accent family
layout architecture
```

deverá ser tratada como alteração do design aprovado.

---

## 163. Resultado Esperado

Ao comparar a aplicação implementada com as telas Stitch, devemos perceber imediatamente:

```text
mesma família visual
mesma personalidade
mesmo produto
```

mas a versão implementada deverá apresentar maior:

```text
consistência
responsividade
acessibilidade
reutilização
robustez
```

---

## 164. Visual Baseline Status

A partir deste documento:

```text
VISUAL BASELINE V1
STATUS: APPROVED
```

As quatro telas principais representam oficialmente:

```text
Dashboard
Ideas
Calendar
Content Production
```

e o quinto material representa:

```text
Brand Direction Concept
```

---

## 165. Relação com o Roadmap

O Documento 08B **não cria uma nova fase**.

Continuamos com:

```text
20 fases
```

definidas no Documento 10.

O 08B apenas determina como o frontend dessas fases deverá ser construído.

---

## 166. Estrutura Final da Documentação Visual

Recomendado:

```text
/docs/master/

08-ux-ui.md
08A-visual-design-system.md
08B-visual-baseline-v1.md
```

e:

```text
/docs/design/reference/

01-dashboard.png
02-ideas.png
03-calendar.png
04-content-production.png
05-brand-concept.png
```

mais:

```text
/docs/design-system.md
```

que será atualizado conforme o código evoluir.

---

## 167. Princípio Final

A interface deverá preservar a simplicidade percebida nas referências do Stitch enquanto a plataforma cresce em complexidade.

O usuário deverá enxergar:

```text
IDEIA
→
CALENDÁRIO
→
PRODUÇÃO
→
REVISÃO
→
PUBLICAÇÃO
→
RESULTADO
```

e não:

```text
agents
prompts
providers
queues
workers
MCPs
model routing
internal orchestration
```

A infraestrutura pode ser extremamente complexa.

**A experiência do usuário não deve ser.**

---

## Status do Documento

```text
DOCUMENT: 08B
NAME: Visual Baseline V1
STATUS: APPROVED
TYPE: Mandatory Visual Implementation Specification
DEPENDS ON: Documents 08 and 08A
APPLIES TO: All frontend implementation phases
```
