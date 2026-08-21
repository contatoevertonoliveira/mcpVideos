# UI — Estado Atual do Frontend

> Mantido conforme Documento 08/08A/08B. Atualizar a cada fase que adicionar ou reestilizar telas.

Última atualização: skin refactor do Dashboard e do AppShell para o Documento 08B (Visual Baseline V1), logo após o retrofit de Ideias e Calendário.

## Estrutura de rotas

```
src/app/
├── page.tsx                    "/" - splash/status da API, não autenticado
├── (auth)/
│   ├── login/page.tsx           "/login"
│   └── register/page.tsx        "/register"
├── (app)/                       route group autenticado - layout.tsx valida sessão
│   │                             e renderiza AppShell uma única vez
│   ├── layout.tsx
│   ├── dashboard/page.tsx       "/dashboard"
│   ├── ideas/page.tsx           "/ideas"     (Documento 08B baseline)
│   ├── calendar/page.tsx        "/calendar"  (Documento 08B baseline)
│   └── channels/page.tsx        "/channels"
└── oauth/youtube/{start,callback}/route.ts   Route Handlers (BFF OAuth, Fase 04)
```

`(auth)` e `(app)` são route groups do Next.js — não aparecem na URL. `proxy.ts` continua protegendo por caminho, sem relação com a estrutura de pastas.

## Telas implementadas

| Tela | Rota | Fase | Notas visuais |
|---|---|---|---|
| Splash/Status | `/` | F01 | Card de status da API + CTAs de login/registro |
| Login | `/login` | F03 | Card centralizado, glow radial de fundo sutil |
| Registro | `/register` | F03 | Idem, cria organização automaticamente |
| Dashboard | `/dashboard` | F03 (skin refactor 08B) | `PageHeader` (saudação + badge de automação) + card "Hoje" (`TodayContentItem`) + "Status operacional" + "Precisa da sua atenção" + 3 `MetricCard`, tudo com dados reais |
| Ideias | `/ideas` | F09 (retrofit 08B) | `PageHeader` + `FilterChips` (status) + grid de `OpportunityCard`, seguindo `docs/design/reference/ideas.png` |
| Calendário | `/calendar` | F10 (retrofit 08B) | `PageHeader` + `CalendarToolbar` (Semana/Lista) + `EditorialCalendar` (grid semanal) ou lista de `CalendarItemCard` |
| Canais | `/channels` | F04-F08 | Lista de canais conectados; cada card acumula: sincronizar, diagnóstico (Fase 06), DNA (Fase 07), estratégia com aprovação (Fase 08). Ideias/Calendário foram removidos daqui na retrofit do Documento 08B — viraram telas dedicadas |

## Retrofit Documento 08B (Ideias e Calendário)

O Documento 08B (Visual Baseline V1) chegou em `/docs` durante a implementação da Fase 10, com referências aprovadas do Google Stitch em `docs/design/reference/`. Por instrução explícita do usuário, Ideias e Calendário foram retrofitadas para o baseline antes de seguir (mesmo padrão do retrofit do Documento 08A na Fase 09).

**Novos componentes** (`apps/web/src/components/`): `page-header.tsx` (título/subtítulo/ação primária), `filter-chips.tsx` (tabs via link+searchParam, sem JS client), `opportunity-card.tsx` (score com `getOpportunityScoreVariant`, badge de formato, pilar/fonte, callout "Por quê", ação "Adicionar ao calendário"), `calendar-item-card.tsx` (tratamento tracejado+badge "IA" para sugestões vs. rail de status colorido para itens já decididos — Documento 08B §46-48), `calendar-toolbar.tsx` (toggle Semana/Lista + navegação de semana), `editorial-calendar.tsx` (grid semanal de 7 colunas).

**`AppShell` reestruturado**: nav principal agora é Dashboard/Ideias/Calendário (Documento 08B §9); Canais virou item da nav utilitária inferior (mesmo grupo do usuário/Sair), já que — diferente do Stitch, que assume single-channel-context — este produto ainda lista múltiplos canais numa única tela de gestão, mais parecida com "Settings" do que com um item de uso diário.

**Decisão de escopo — canal "primário"**: nenhum seletor de canal (Documento 08B §12 "Channel Selector") foi construído ainda. `/ideas` e `/calendar` operam sobre o primeiro canal `connected` retornado por `listChannels()` (fallback: o primeiro da lista). Com múltiplos canais de teste conectados, isso pode escolher um canal sem DNA/Estratégia ainda — comportamento correto, não um bug: um usuário real só teria um canal conectado nesse ponto da jornada.

**Decisão de escopo — visualização "Mês"**: só "Semana" e "Lista" foram implementadas (Documento 08B §43 lista Week/Month/List). "Mês" foi adiada pela mesma régua de outras fases (Sheet mobile, Publishing Slots UI): grid mensal é bastante trabalho de layout para um segundo modo de visualização sem um requisito de aceite exigindo especificamente isso.

**Ação "descartar ideia" não implementada**: o `OpportunityCard` do Stitch mostra um ícone de lixeira (descartar) além de "Add to calendar" — o backend da Fase 09 só tem `ContentIdeaService.approve()`, sem endpoint de rejeição/descarte de ideia. Adicionar essa ação exigiria uma mudança de backend fora do escopo "retrofit visual"; por isso o card não mostra esse botão (regra de não construir UI sem capacidade real por trás).

**Achado sobre os assets do Documento 08B**: `docs/design/reference/calendar.png` contém, na prática, o mesmo conteúdo visual de `ideas.png` (dimensões e hash diferentes, mas pixels idênticos — provavelmente um export duplicado/errado do lado do usuário). A tela de Calendário foi implementada a partir da especificação textual do Documento 08B §42-49 (Week Header, Day Columns, `CalendarContentCard`, `CalendarSuggestionCard` tracejado) em vez da imagem, que aliás é a fonte de maior prioridade pela própria hierarquia do documento (§158: Documento 08B > referências do Stitch em caso de conflito). Vale re-exportar o arquivo correto quando possível.

## Skin refactor Documento 08B (Dashboard e AppShell)

Pedido explícito do usuário logo após o retrofit de Ideias/Calendário: "a skin do sistema precisa ser refatorada e seguir as referencias... estrutura totalmente moderna igual as imagens deixadas". `/dashboard` foi reconstruído seguindo o Documento 08B §23-31, mas **só com dados reais já expostos pela API** — nunca fabricando números (§131-132).

**Mapeamento Stitch → real:**
- `Good morning` + subtítulo → saudação por horário do servidor + contagem real de itens do calendário para hoje.
- `Autopilot Active` pill → badge com o `automation_mode` real do canal (manual/assistido/semi-automático/autopilot).
- `Today` → `TodayContentItem` por `calendar_item` cujo `planned_at` é hoje; sem os pontos de pipeline (Script/Storyboard/Media/QA — não existem até F12+).
- `ChannelHealthCard` (círculo 92/100) → substituído por "Status operacional": 4 checagens booleanas reais (canal conectado, DNA ativo, estratégia ativa, calendário com itens). A pontuação composta do Stitch não tem fórmula definida em documento nenhum — inventá-la violaria a regra de não fabricar dados.
- `Needs Your Attention` → real: estratégia pendente de aprovação e/ou sugestões de calendário aguardando revisão.
- `MetricCard` (`Views 30d`/`Subs 30d`/`OS Index`) → 3 métricas reais já expostas (vídeos importados, ideias aprovadas, itens no calendário) — não há endpoint de métricas agregadas ainda (Fase 19) e "OS Index" não é definido em nenhum documento.

**`AppShell`**: bloco de logo agora empilha nome + descritor ("mcp_videos" / "AI Automation"); adicionado o slot **"AI Magic"** (Documento 08B §10-11) como um `<div>` deliberadamente não-interativo (o documento manda só "preparar o componente visual" nesta fase, sem funcionalidade real).

**Removida** a antiga seção "Suas organizações" do dashboard — era só uma lista estática (nome + badge de role), sem nenhum botão de troca de organização de fato conectado a uma ação; confirmado que nenhuma funcionalidade real foi perdida. E-mail do usuário continua visível no rodapé da sidebar.

## Decisões de escopo herdadas (Documento 08A)

- **Sidebar/topbar shell construído, mas sem drawer mobile real.** Mobile usa uma barra de nav horizontal compacta abaixo do topbar em vez de um `Sheet`/drawer lateral — o primitive `Sheet` ainda não existe no projeto.
- **Sem `Select`/`Dialog`/`Tooltip`/`Toast`/etc.** ainda — nenhuma tela atual precisa deles de verdade.
- **Login/Registro/splash e Canais** ainda não passaram por uma segunda rodada de polimento específica do Documento 08B — continuam no nível do retrofit do Documento 08A. Content Production/Analytics (telas do 08B) ficam fora da navegação até as fases correspondentes (F12+/F19) existirem.
