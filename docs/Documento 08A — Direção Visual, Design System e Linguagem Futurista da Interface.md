# Documento 08A — Direção Visual, Design System e Linguagem Futurista da Interface

## 1. Objetivo

Este documento complementa o Documento 08 e define a identidade visual obrigatória da plataforma.

O objetivo é garantir que o Claude Code construa uma interface:

- moderna;
- clean;
- premium;
- futurista;
- orientada a vídeo e IA;
- visualmente sofisticada;
- simples de usar;
- consistente em todas as telas;
- diferente de um painel administrativo tradicional.

A plataforma deverá transmitir a sensação de:

```text
AI Content Operating System
+
Video Creation Platform
+
Autonomous Editorial Control Center
```

sem parecer:

```text
ERP
CRM tradicional
painel Bootstrap
dashboard financeiro genérico
interface gamer
ferramenta técnica de desenvolvedor
```

---

# 2. Conceito Visual Principal

A linguagem visual deverá ser:

```text
FUTURISTIC
MINIMAL
PREMIUM
VIDEO-FIRST
AI-NATIVE
CINEMATIC
CALM
HIGH-END
```

A referência conceitual não é uma interface cheia de efeitos.

O futurismo deverá vir de:

```text
hierarquia
movimento
profundidade
tipografia
espaçamento
superfícies
microinterações
visualização inteligente de mídia
```

e não de excesso de neon.

---

# 3. Sensação Desejada

Ao entrar na plataforma, o usuário deverá sentir que está utilizando uma ferramenta avançada de produção audiovisual com IA.

A interface deve comunicar:

```text
controle
tecnologia
automação
inteligência
velocidade
confiança
sofisticação
```

Sem parecer complicada.

---

# 4. Filosofia Visual

Princípio:

**complexidade tecnológica nos bastidores; simplicidade visual na frente.**

A interface deve priorizar:

```text
conteúdo
preview de vídeo
status
próxima ação
insights
calendário
```

em vez de:

```text
configurações técnicas
gráficos desnecessários
logs
providers
modelos
filas
```

---

# 5. Video-First Design

Como o produto é focado em conteúdo audiovisual, vídeos, thumbnails e cenas deverão ter forte presença visual.

A plataforma deverá parecer mais próxima de uma:

```text
creative studio
```

do que de um:

```text
database dashboard
```

---

# 6. Tema Principal

O tema visual inicial recomendado será:

```text
Dark Mode Premium
```

com suporte arquitetural a Light Mode.

Não implementar o sistema de forma que dependa exclusivamente de dark mode.

---

# 7. Background Principal

Utilizar fundo escuro sofisticado.

Evitar:

```text
preto absoluto #000000 em toda a interface
```

Preferir tonalidades próximas de:

```text
charcoal
deep graphite
midnight
deep navy-black
```

O fundo poderá ter pequenas variações entre:

```text
page background
sidebar
surface
elevated surface
modal
```

---

# 8. Profundidade das Superfícies

Criar hierarquia visual clara:

```text
Background
↓
Surface
↓
Elevated Surface
↓
Interactive Surface
↓
Floating Layer
```

Evitar separar tudo com bordas fortes.

---

# 9. Borders

Utilizar bordas:

```text
finas
sutis
baixa opacidade
```

Principalmente para:

```text
cards
inputs
dialogs
tables
```

Evitar:

```text
bordas brancas fortes
bordas em todos os containers
```

---

# 10. Accent Color

Definir uma única família de cor principal da marca da aplicação.

Sugestão conceitual:

```text
electric blue
blue-violet
violet
cyan-blue
```

A escolha final deverá virar design token.

---

# 11. Gradients

Gradientes serão permitidos de maneira controlada.

Utilizar em:

```text
primary CTA
AI indicator
selected navigation
hero cards
special status
subtle background glow
```

Evitar preencher toda a interface com gradientes.

---

# 12. Neon

Pode existir um toque de luminosidade digital.

Mas:

```text
subtle glow
```

e não:

```text
cyberpunk neon overload
```

---

# 13. Glassmorphism

Permitido apenas pontualmente.

Exemplos:

```text
floating command palette
modal
overlay
AI assistant panel
preview controls
```

Não transformar todos os cards em vidro transparente.

---

# 14. Blur

Blur deverá ser usado principalmente em elementos sobrepostos.

Evitar blur excessivo que prejudique leitura e performance.

---

# 15. Tipografia

A tipografia deverá parecer moderna e digital, mas extremamente legível.

Preferir sans-serif contemporânea.

Características:

```text
clean
geometric
high readability
modern
neutral
```

---

# 16. Hierarquia Tipográfica

Definir tokens:

```text
display
heading-xl
heading-lg
heading-md
heading-sm
body
body-small
caption
label
numeric
```

---

# 17. Títulos

Títulos devem ser:

```text
fortes
curtos
claros
```

Evitar headings gigantes em dashboards operacionais.

---

# 18. Métricas

Números relevantes poderão ter destaque maior.

Exemplo:

```text
112
Performance Index
```

---

# 19. Espaçamento

A interface deverá utilizar bastante espaço negativo.

Regra:

```text
menos informação por centímetro
+
melhor hierarquia
```

---

# 20. Grid

Utilizar grid consistente.

Desktop:

```text
12-column conceptual grid
```

Cards deverão alinhar-se visualmente.

---

# 21. Radius

Usar cantos arredondados modernos.

Não exagerar.

Definir tokens como:

```text
radius-sm
radius-md
radius-lg
radius-xl
```

---

# 22. Shadows

Sombras:

```text
soft
diffused
subtle
```

Não usar sombras fortes estilo interfaces antigas.

---

# 23. Glow

Glow pode ser usado em:

```text
Autopilot status
AI processing
selected state
hero visual
```

sempre de forma sutil.

---

# 24. Layout Base Desktop

Estrutura recomendada:

```text
┌─────────────────────────────────────────────────────────┐
│ SIDEBAR │ TOPBAR                                        │
│         ├───────────────────────────────────────────────│
│         │                                               │
│         │                CONTENT                        │
│         │                                               │
│         │                                               │
│         │                                               │
└─────────────────────────────────────────────────────────┘
```

---

# 25. Sidebar

Sidebar deverá ser:

```text
compacta
escura
minimalista
```

Pode possuir:

```text
logo
navigation
channel selector shortcut
bottom settings/user
```

---

# 26. Sidebar Expanded / Collapsed

Preparar suporte para:

```text
expanded
collapsed
```

No collapsed:

```text
icons
tooltips
```

---

# 27. Sidebar Navigation

Principal:

```text
Dashboard
Ideias
Calendário
Conteúdos
Analytics
```

Separação inferior:

```text
Canais
Configurações
```

---

# 28. Active Navigation

Estado ativo deverá ser elegante.

Pode usar:

```text
soft accent background
small glow
accent icon
```

Evitar grande bloco saturado.

---

# 29. Topbar

Topbar deve ser limpa.

Elementos:

```text
channel selector
global status
notifications
user menu
```

---

# 30. Channel Selector

Deverá mostrar:

```text
avatar/logo
channel name
platform
```

e permitir troca rápida.

---

# 31. Automation Status

Um pequeno indicador poderá mostrar:

```text
Assisted
Semi-Auto
Autopilot
Paused
```

---

# 32. Dashboard Hero

O dashboard poderá possuir no topo uma área principal discreta.

Exemplo:

```text
Bom dia

Seu canal está saudável.
3 conteúdos programados hoje.
```

Não precisa ser uma landing page gigante.

---

# 33. Dashboard Composition

Desktop recomendado:

```text
12 columns

Today / Pipeline       8 cols
Channel Health         4 cols

Opportunities          8 cols
AI Insight             4 cols

Recent Content        12 cols
```

Adaptável.

---

# 34. AI Insight Card

Esse deverá ser um componente visual marcante.

Exemplo:

```text
AI INSIGHT

Seus Shorts entre 20 e 30 segundos
tiveram +14% de retenção.

Recomendação:
priorizar 2 conteúdos nesse formato.

[Ver análise]
```

Pode possuir:

```text
subtle gradient
AI icon
soft glow
```

---

# 35. Opportunity Card

Componente importante.

Deve mostrar:

```text
score
title
format
pillar
short rationale
```

Exemplo:

```text
94

Por que os tubarões não piscam?

SHORT
Curiosidades

Alta aderência ao canal.

[Adicionar]
```

---

# 36. Score Visual

Score poderá aparecer como:

```text
ring
pill
large number
```

Mas evitar aparência de game.

---

# 37. Content Card

Conteúdos deverão usar thumbnail ou preview quando disponível.

Layout conceitual:

```text
┌─────────────────────┐
│                     │
│     VIDEO PREVIEW   │
│                     │
├─────────────────────┤
│ título              │
│ Short • Produzindo  │
│                     │
│ next action         │
└─────────────────────┘
```

---

# 38. Video Preview

Preview deverá ter prioridade.

Aspect ratios:

```text
16:9
9:16
1:1 future
```

Sem deformar mídia.

---

# 39. Shorts Preview

Shorts devem aparecer em miniatura vertical verdadeira.

Não forçar thumbnails 9:16 em cards 16:9.

---

# 40. Hover de Vídeo

Futuro:

```text
hover
→ muted preview
```

quando performance permitir.

Não obrigatório no MVP.

---

# 41. Content Status

Utilizar chips:

```text
Produzindo
Revisão
Pronto
Agendado
Publicado
```

---

# 42. Status Colors

Usar cores semanticamente consistentes.

Exemplo conceitual:

```text
neutral → planned
blue → producing
amber → review
green → ready/published
red → error
```

Definir via tokens, não hardcode.

---

# 43. Producing Animation

Status `Produzindo` poderá ter:

```text
small animated pulse
```

Muito discreto.

---

# 44. Autopilot Indicator

Quando ativo:

```text
● Autopilot
```

Pode utilizar glow sutil.

---

# 45. Pipeline Visual

Pipeline do conteúdo deverá ser representado visualmente.

Exemplo:

```text
Roteiro ✓ ─── Storyboard ✓ ─── Mídia ● ─── QA ○
```

---

# 46. Progress

Não utilizar porcentagem falsa.

Preferir etapas reais.

---

# 47. Calendar Visual

Calendário deverá parecer editorial e visual.

Não como calendário corporativo antigo.

---

# 48. Calendar Card

Mostrar:

```text
thumbnail
time
content type
title
status
```

---

# 49. Format Iconography

Diferenciar:

```text
Short
Video
Live
```

com ícones discretos.

---

# 50. Calendar Density

Usuário deverá conseguir enxergar uma semana sem excesso de informação.

---

# 51. Month View

Mais compacto.

Cards podem mostrar:

```text
format icon
title truncated
status
```

---

# 52. Drag State

Ao mover item:

```text
lifted card
soft shadow
target slot highlight
```

---

# 53. Review Queue

Tela deverá destacar:

```text
needs your attention
```

sem parecer erro crítico.

---

# 54. Review Cards

Visualmente usar hierarquia:

```text
reason
preview
suggested action
```

---

# 55. Problems

Exemplo:

```text
Atenção

A voz perdeu sincronização em 00:18.

Correção recomendada:
Substituir somente o áudio.
```

---

# 56. Critical Problem

Pode usar destaque vermelho controlado.

Evitar grandes áreas vermelhas.

---

# 57. Modals

Modals deverão ter:

```text
backdrop blur
elevated dark surface
clear title
few actions
```

---

# 58. Dialog Actions

CTA principal sempre claro.

Exemplo:

```text
Cancelar
Ativar Autopilot
```

---

# 59. Primary Button

Deverá possuir aparência premium.

Pode usar:

```text
accent fill
subtle gradient
soft glow on hover
```

---

# 60. Secondary Button

Surface ou outline discreto.

---

# 61. Ghost Button

Para ações de baixo peso.

---

# 62. Destructive Button

Vermelho apenas para ação destrutiva real.

---

# 63. Icon Buttons

Sempre com:

```text
tooltip
accessible label
```

---

# 64. Inputs

Inputs devem ser modernos.

Características:

```text
dark surface
subtle border
clear focus ring
comfortable height
```

---

# 65. Focus

Focus state deve ser claramente visível.

---

# 66. Search Field

Pode possuir:

```text
command icon
keyboard hint
```

futuramente.

---

# 67. Command Palette

Componente futuro importante.

Atalho:

```text
Ctrl/Cmd + K
```

Poderá permitir:

```text
buscar conteúdo
abrir canal
criar ideia
abrir calendário
```

---

# 68. Tables

Tabelas devem ser minimalistas.

Evitar grade completa.

Preferir:

```text
row separators
hover state
sticky header
```

---

# 69. Analytics

Charts deverão parecer modernos.

Regras:

```text
few colors
clean axes
subtle grids
large whitespace
clear comparison
```

---

# 70. Graph Glow

Não aplicar glow forte às linhas.

---

# 71. Metric Cards

Formato:

```text
Views
824K
+18%
```

---

# 72. Secondary Metrics

Não mostrar 20 KPIs simultaneamente.

---

# 73. Performance Visualization

Performance Index poderá usar:

```text
large number
small trend line
relative label
```

---

# 74. Sparklines

Permitidas em cards quando úteis.

---

# 75. Donut Charts

Evitar excesso.

Usar apenas para proporções claras.

---

# 76. Content Mix

Poderá usar:

```text
stacked bar
```

em vez de pizza, quando mais legível.

---

# 77. Analytics Background

Manter mesmos surfaces do restante da aplicação.

Não criar um “segundo produto” visualmente.

---

# 78. AI Animation

Quando IA estiver processando:

```text
subtle animated gradient
soft shimmer
pulse
```

---

# 79. Shimmer

Skeletons podem possuir shimmer discreto.

---

# 80. Page Transitions

Transições rápidas.

Exemplo:

```text
fade
small translate
```

Evitar animações lentas.

---

# 81. Motion Duration

Preferir aproximadamente:

```text
150–250ms
```

para microinterações comuns.

---

# 82. Motion Philosophy

Motion deve explicar estado.

Não apenas decorar.

---

# 83. Hover

Cards interativos poderão:

```text
move 1–2px
soften border
increase surface brightness
```

---

# 84. No Excessive Scaling

Evitar:

```text
transform scale(1.1)
```

em dashboards.

---

# 85. Navigation Transition

Sidebar item pode deslizar indicator discretamente.

---

# 86. Loading Animations

Nunca usar spinners gigantes.

---

# 87. AI Processing State

Exemplo:

```text
Preparing your next ideas...
```

com elemento visual pequeno.

---

# 88. Futuristic Decorative Elements

Podem existir:

```text
subtle grid
ambient gradient
fine light line
small particles
```

em áreas especiais.

Não em todas as telas.

---

# 89. Background Grid

Se utilizado:

```text
extremely low opacity
```

Principalmente em:

```text
login
onboarding
empty state
```

---

# 90. Login Screen

Deverá passar impressão premium imediatamente.

Estrutura:

```text
LEFT / CENTER
brand
headline
login

BACKGROUND
cinematic abstract AI/video visual
```

---

# 91. Login Visual

Pode usar:

```text
abstract video frames
AI timeline
soft light trails
cinematic gradients
```

Evitar robô humanoide genérico.

---

# 92. Login Copy

Curta.

Exemplo conceitual:

```text
Your content.
Planned, created and optimized by AI.
```

Localizado na UI.

---

# 93. Onboarding Visual

Onboarding deve parecer:

```text
system discovering the channel
```

---

# 94. Channel Analysis Animation

Pode haver composição visual:

```text
channel avatar
↓
content nodes
↓
analysis
↓
DNA
```

Muito simplificada.

---

# 95. Analysis Result

Tela poderá ter:

```text
large channel avatar/logo

We understood your channel.
```

seguido de cards.

---

# 96. Channel DNA Visual

Não mostrar como formulário.

Mostrar:

```text
Content
Audience
Formats
Tone
Strengths
Opportunities
```

---

# 97. Strategy Visual

Content Mix pode ter barra visual.

Exemplo:

```text
Stories      ████████ 40%
Music        ██████   30%
Discovery    ████     20%
Experimental ██       10%
```

---

# 98. Idea Discovery Visual

Novas ideias poderão entrar em cards com animação suave.

---

# 99. AI Recommendation Badge

Usar algo discreto:

```text
AI Recommended
```

---

# 100. Generated Content Indicator

Pode existir:

```text
AI Generated
```

quando necessário para operação.

Não precisa dominar UI.

---

# 101. Media Studio Feel

Na tela Project Detail, especialmente cenas, a interface poderá ficar mais próxima de uma pequena ferramenta audiovisual.

---

# 102. Scene Grid

Storyboard:

```text
Scene 01
preview

Scene 02
preview

Scene 03
preview
```

---

# 103. Scene Card

Mostrar:

```text
preview
duration
status
scene number
```

---

# 104. Scene Detail Drawer

Ao clicar:

```text
preview
dialogue
visual direction
assets
status
```

---

# 105. Timeline

Na fase de edição, utilizar timeline simplificada.

Não tentar replicar Premiere Pro.

---

# 106. Timeline Purpose

Mostrar:

```text
scene order
duration
voice
music
```

apenas o necessário.

---

# 107. Preview Player

Player moderno.

Controls:

```text
play
timeline
volume
fullscreen
```

---

# 108. Review Overlay

Futuro:

comentários podem apontar timestamp.

---

# 109. Thumbnail Studio

Visual:

```text
candidate thumbnails side-by-side
```

---

# 110. Selected Candidate

Deve ter:

```text
accent border
check
```

---

# 111. Title Studio

Títulos podem ser apresentados como cards.

---

# 112. Title + Thumbnail Pair

Idealmente exibir juntos para seleção.

---

# 113. Pair Preview

Simular aparência simplificada de recomendação YouTube.

---

# 114. Mobile Preview

Opcional:

mostrar thumbnail/título em formato aproximado mobile.

---

# 115. Branding

A interface da plataforma não deverá competir visualmente com as marcas dos canais.

Usar identidade própria neutra.

---

# 116. Channel Colors

Não aplicar automaticamente cores do canal à interface global.

Podem aparecer em:

```text
avatar
small accent
preview
```

---

# 117. Multi-Channel Distinction

Channel selector deve deixar claro o contexto atual.

---

# 118. Empty Dashboard

Novo usuário sem canal:

```text
large central CTA

Connect your YouTube channel
```

com visual futurista discreto.

---

# 119. Empty Ideas

Pode mostrar:

```text
AI scanning animation
```

se análise em andamento.

---

# 120. Empty Calendar

Mostrar:

```text
We haven't planned content yet.
```

com CTA de geração.

---

# 121. Error State Visual

Erros não devem quebrar estética.

Usar cards claros com:

```text
icon
message
action
```

---

# 122. Success State

Confirmações podem usar check animado pequeno.

---

# 123. Toasts

Pequenos.

Não cobrir conteúdo.

---

# 124. Notifications Drawer

Painel lateral elegante.

---

# 125. Notification Item

Mostrar:

```text
icon
title
description
time
action
```

---

# 126. Responsive Sidebar

Desktop:

```text
left sidebar
```

Mobile:

```text
drawer/bottom navigation
```

---

# 127. Mobile Bottom Navigation

Prioridade:

```text
Home
Ideas
Calendar
Content
More
```

---

# 128. Mobile Content Cards

Preview deve continuar visível.

---

# 129. Mobile Approval

Aprovação deverá ser fácil com uma mão.

---

# 130. Mobile Analytics

Mostrar poucos KPIs por vez.

---

# 131. Breakpoints

Definir tokens/breakpoints consistentes.

---

# 132. Accessibility

Mesmo com visual sofisticado:

```text
contrast
keyboard
screen reader labels
focus
reduced motion
```

são obrigatórios.

---

# 133. Reduced Motion

Respeitar:

```text
prefers-reduced-motion
```

---

# 134. Color Alone

Nunca depender apenas de cor para status.

Usar:

```text
icon
label
color
```

---

# 135. Contrast

Textos secundários não podem ficar ilegíveis em dark mode.

---

# 136. Iconography

Utilizar uma única biblioteca de ícones.

Estilo:

```text
simple
outlined
modern
consistent
```

---

# 137. Custom Icons

Só criar quando realmente necessário.

---

# 138. AI Icon

Evitar clichê:

```text
robot head
```

Pode usar identidade abstrata:

```text
spark
nodes
waveform
gradient mark
```

---

# 139. Logo da Plataforma

Deve funcionar em:

```text
horizontal
compact icon
dark
light
```

---

# 140. Branding Architecture

Criar:

```text
Logo
Symbol
Wordmark
App Icon
```

quando branding final for definido.

---

# 141. CSS Architecture

Utilizar design tokens via:

```text
CSS variables
```

e Tailwind theme.

---

# 142. Não Hardcode Cores

Evitar:

```text
bg-[#123456]
```

espalhado.

Preferir:

```text
bg-surface
text-muted
border-subtle
accent-primary
```

---

# 143. Design Tokens Obrigatórios

Criar no mínimo:

```text
--background
--surface
--surface-elevated
--surface-hover

--foreground
--muted-foreground

--border
--border-strong

--primary
--primary-foreground

--success
--warning
--danger
--info

--radius-sm
--radius-md
--radius-lg
--radius-xl
```

---

# 144. Gradient Tokens

Definir centralmente.

---

# 145. Shadow Tokens

Mesmo princípio.

---

# 146. Motion Tokens

Definir:

```text
fast
normal
slow
```

---

# 147. Z-Index Scale

Definir:

```text
dropdown
sticky
overlay
modal
toast
```

---

# 148. Component Library

Criar componentes reutilizáveis.

Base:

```text
Button
Input
Select
Dialog
Sheet
Dropdown
Tooltip
Tabs
Badge
Avatar
Card
Table
Skeleton
Toast
Progress
```

---

# 149. Product-Specific Components

Criar progressivamente:

```text
ChannelCard
ContentCard
OpportunityCard
InsightCard
CalendarContentCard
ProductionPipeline
QualityScore
AutomationStatus
VideoPreviewCard
MetricCard
ReviewCard
```

---

# 150. No Copy-Pasted Cards

Componentes semelhantes devem compartilhar base.

---

# 151. Storybook

Opcional.

Se adotado futuramente, usar para design system.

Não obrigatório no MVP.

---

# 152. Visual Regression

Preparar possibilidade futura de screenshots E2E.

---

# 153. Theme Architecture

Suportar:

```text
dark
light
system
```

Mesmo que dark seja padrão visual inicial.

---

# 154. Light Theme

Light mode não deverá parecer versão quebrada do dark.

Tokens devem cuidar disso.

---

# 155. Dark Theme

Dark deve ser a referência premium principal.

---

# 156. Performance

Efeitos visuais não devem comprometer:

```text
scroll
render
video playback
mobile
```

---

# 157. Avoid Heavy WebGL by Default

Não usar 3D/WebGL no dashboard só para parecer futurista.

---

# 158. Decorative Animation Budget

Poucos elementos animados simultaneamente.

---

# 159. Video Thumbnails

Usar lazy loading.

---

# 160. Skeleton Loading

Layouts não devem pular quando conteúdo carregar.

---

# 161. Content Density

Criar modos futuros:

```text
comfortable
compact
```

não necessário inicialmente.

---

# 162. Design Inspiration Direction

Conceitualmente buscar combinação de:

```text
modern creative software
premium AI tools
cinematic streaming interfaces
minimal productivity tools
```

Sem copiar diretamente nenhum produto específico.

---

# 163. O que NÃO queremos — Regra Obrigatória

Não criar aparência de:

```text
ERP
sistema bancário antigo
admin template genérico
Bootstrap dashboard
WordPress plugin
painel de hospedagem
```

---

# 164. Não Exagerar em Cards

Nem toda informação precisa estar dentro de card.

Usar também:

```text
sections
lists
tables
open space
```

---

# 165. Não Exagerar em Glass

Glassmorphism deve ser acento.

---

# 166. Não Exagerar em Glow

Glow deve sinalizar inteligência/atividade, não decoração constante.

---

# 167. Não Exagerar em Gradientes

Gradientes saturados em todas as superfícies são proibidos.

---

# 168. Não Usar Muitas Cores de Accent

Um accent principal + cores semânticas.

---

# 169. Não Usar 8 Fontes

Uma família principal.

Talvez uma segunda apenas para branding, se necessário.

---

# 170. Não Exibir Texto Demais

Preferir:

```text
headline
summary
details on demand
```

---

# 171. Não Exibir Dados Técnicos ao Usuário

Reforço:

```text
MCP
model
provider
Celery
Redis
prompt
tokens
worker
```

não pertencem ao User App.

---

# 172. Control Center Visual

O Control Center poderá ser mais denso.

Mas deverá compartilhar a mesma identidade.

---

# 173. Admin Density

Pode mostrar mais:

```text
tables
filters
technical metadata
```

sem perder legibilidade.

---

# 174. Admin Accent

Não criar identidade completamente diferente.

---

# 175. Workflow Inspector

Pode usar timeline vertical.

---

# 176. Provider Health

Cards compactos:

```text
Healthy
Degraded
Down
```

---

# 177. Errors

Admin pode usar status técnico mais forte.

---

# 178. Logs

Logs deverão usar fonte monoespaçada apenas onde necessário.

---

# 179. Code/JSON

Monospace somente em:

```text
IDs
JSON
logs
technical data
```

---

# 180. Futuristic Elements by Context

## Dashboard

```text
subtle
premium
calm
```

## Production

```text
more visual
more motion
```

## Analytics

```text
data-focused
clean
```

## Control Center

```text
technical
dense
precise
```

---

# 181. Home Dashboard Priority

Ordem visual recomendada:

```text
1. Today / Action Required
2. Upcoming
3. Opportunities
4. Insight
5. Performance
```

---

# 182. User Attention

Itens que precisam de ação humana recebem prioridade visual.

---

# 183. Autonomous Background Work

Itens funcionando normalmente devem ser discretos.

---

# 184. Attention Color

Amber deverá ser reservado a:

```text
review
warning
action required
```

---

# 185. Red

Somente:

```text
failure
critical
destructive
```

---

# 186. Green

```text
success
ready
healthy
published
```

---

# 187. Blue/Accent

```text
active
processing
AI
selected
```

---

# 188. Preview Background

Mídias deverão ter background neutro e não competir com a imagem.

---

# 189. 9:16 Media

Não cortar automaticamente conteúdo importante.

Usar contain/crop de forma contextual.

---

# 190. Media Aspect Ratio Tokens

Criar componentes:

```text
VideoAspectRatio
```

ou equivalente.

---

# 191. Thumbnail Generation Progress

Mostrar:

```text
Generating 2 of 3
```

se real.

---

# 192. Multiple Variants

Visual de candidatos em grid.

---

# 193. AI Suggestion Reason

Sempre poder abrir:

```text
Why this?
```

---

# 194. Explainability Panel

Painel lateral pode mostrar:

```text
Channel Fit
Historical Evidence
Trend
Recommendation
```

---

# 195. Simple Default

Esse painel fica fechado por padrão.

---

# 196. Search / Command Future

A arquitetura de layout deverá deixar espaço para busca global.

---

# 197. Notification Future

Mesmo para canal com muitas automações, evitar badges gigantes.

---

# 198. Multi-Tenant Header

Se usuário gerencia agência:

```text
organization selector
channel selector
```

devem ser claros.

---

# 199. Breadcrumb

Em tela profunda:

```text
Contents / Video X / Scenes
```

---

# 200. URL Structure

Design deverá respeitar rotas claras.

---

# 201. Visual Consistency Check

Antes de concluir cada feature, verificar:

```text
spacing
radius
typography
color tokens
states
icons
motion
```

---

# 202. No One-Off Styling

Evitar estilos especiais locais sem necessidade.

---

# 203. User Feedback Animation

Ao aprovar:

```text
small check transition
```

---

# 204. Optimistic Visuals

Somente quando operação puder ser revertida.

---

# 205. Publication

Nunca animar como publicado até backend confirmar.

---

# 206. AI Status Language

Pode usar:

```text
AI is preparing your content
```

mas sem antropomorfizar excessivamente.

---

# 207. Naming

Interface poderá usar conceito de:

```text
AI Insights
```

ou:

```text
Recommendations
```

Não precisa dizer “Agent” ao usuário.

---

# 208. Overall Mood

A aplicação deve parecer:

```text
expensive
modern
calm
intelligent
fast
```

e não:

```text
noisy
childish
overdecorated
experimental
```

---

# 209. First Impression Test

Ao abrir screenshot do dashboard, uma pessoa deve entender que se trata de:

```text
uma plataforma moderna de criação e gestão de conteúdo audiovisual
```

mesmo sem ler todo o texto.

---

# 210. Second Impression Test

Após poucos segundos, deve ficar claro que:

```text
IA está automatizando a operação
```

---

# 211. Third Impression Test

Ao usar a plataforma, deve ficar claro que:

```text
o usuário continua no controle
```

---

# 212. Claude Code — Regra de Implementação Visual

Antes de criar qualquer tela:

1. consultar Documento 08;
2. consultar Documento 08A;
3. utilizar design tokens existentes;
4. reutilizar componentes;
5. verificar responsividade;
6. implementar dark mode corretamente;
7. evitar cores hardcoded;
8. incluir loading/empty/error states;
9. testar hover/focus;
10. respeitar acessibilidade;
11. não inventar nova linguagem visual por página.

---

# 213. Design System First

Durante Fase 01, criar apenas o foundation necessário:

```text
theme
tokens
typography
basic surfaces
buttons
inputs
cards
layout shell
```

---

# 214. Não Criar Todas as Telas na Fase 01

O Documento 08A define a linguagem final.

As telas serão construídas conforme suas fases.

---

# 215. UI Foundation Deliverables — F01

Criar:

```text
global theme
dark mode
light-ready architecture
CSS variables
Tailwind semantic tokens
basic typography
radius system
shadow system
sidebar shell
topbar shell
responsive app layout
basic primitives
```

---

# 216. F01 Visual Demo

Claude Code deverá criar uma página temporária/development showcase ou dashboard skeleton suficiente para verificar:

```text
background
sidebar
topbar
cards
buttons
inputs
badges
typography
```

Sem implementar features futuras falsas.

---

# 217. F01 Acceptance Visual

Deverá ser possível confirmar que o projeto já possui:

```text
identidade visual coerente
dark theme premium
responsive foundation
semantic design tokens
```

antes das próximas telas.

---

# 218. Phase 04 Visual

Conexão de canal deverá ser o primeiro fluxo user-facing realmente refinado.

---

# 219. Phase 06–10 Visual

Diagnóstico, Strategy, Ideas e Calendar deverão consolidar a identidade do produto.

---

# 220. Phase 12–17 Visual

A interface audiovisual deverá ganhar mais protagonismo:

```text
storyboard
preview
scenes
quality
thumbnail
```

---

# 221. Phase 20 Visual

Control Center deverá utilizar design system existente, mas permitir maior densidade.

---

# 222. Documentation

Criar/manter:

```text
/docs/ui.md
```

e:

```text
/docs/design-system.md
```

---

# 223. design-system.md

Deverá documentar:

```text
colors
tokens
typography
spacing
radius
shadows
motion
components
status colors
layout
```

---

# 224. Component Documentation

Para componentes próprios importantes:

```text
purpose
variants
states
responsive behavior
```

---

# 225. Screenshot Review

Ao concluir telas importantes, revisar visualmente em:

```text
desktop large
laptop
tablet
mobile
```

---

# 226. Dark Mode Review

Verificar:

```text
contrast
surface hierarchy
hover
borders
inputs
disabled
```

---

# 227. Light Mode Review

Quando ativado:

```text
não simplesmente inverter cores
```

Utilizar tokens semanticamente adequados.

---

# 228. Final Visual Architecture

```text
DESIGN TOKENS
      ↓
UI PRIMITIVES
      ↓
PRODUCT COMPONENTS
      ↓
FEATURE LAYOUTS
      ↓
PAGES
```

Nunca:

```text
PAGE
↓
custom CSS
↓
another custom page
```

---

# 229. Final UX/Visual Objective

A plataforma deverá unir:

```text
YouTube content management
+
AI creation
+
editorial planning
+
automation
+
analytics
```

em uma única experiência visual coerente.

---

# 230. Princípio Final

A interface deve fazer a automação parecer poderosa, mas nunca intimidante.

O produto deve transmitir visualmente:

```text
"The system is doing a lot for me,
but I always know what is happening."
```

Esse é o equilíbrio visual e operacional que deverá guiar toda a implementação.

Este Documento 08A deverá ser considerado complemento obrigatório do Documento 08 e lido pelo Claude Code antes da criação da fundação visual na Fase 01 e antes da implementação de qualquer nova tela.