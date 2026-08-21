# Design System — mcp_videos

> Segue o Documento 08A (Direção Visual, Design System e Linguagem Futurista) e o Documento 08B (Visual Baseline V1, referências do Stitch em `docs/design/reference/`). Atualizar sempre que tokens ou componentes mudarem.

## Filosofia

Dark Mode Premium é o tema padrão (renderizado direto no servidor, sem flash). Light mode é uma escolha explícita do usuário, com paleta própria — não uma inversão do dark. Um único accent (blue-violet), cores semânticas consistentes, bordas e sombras sutis, glow controlado. Nunca cor hardcoded fora de `globals.css`.

## Colors

Definidos como CSS variables em `apps/web/src/app/globals.css` (`:root` = light, `.dark` = dark), expostos como utilities Tailwind via `@theme inline`.

| Token | Uso |
|---|---|
| `--background` | Fundo da página |
| `--surface` | Cards, sidebar, superfícies de primeiro nível |
| `--surface-elevated` | Popovers, dropdowns, modais |
| `--surface-hover` | Estado hover de superfícies |
| `--foreground` / `--muted-foreground` | Texto primário / secundário |
| `--border` / `--border-strong` | Bordas sutis / separadores mais visíveis |
| `--primary` / `--primary-foreground` | Accent principal (blue-violet) — CTAs, seleção, IA |
| `--secondary`, `--muted`, `--accent` | Superfícies neutras auxiliares (herdados do shadcn) |
| `--success` / `--warning` / `--danger` / `--info` | Cores semânticas de status (Documento 08A §42, §184-187) |
| `--destructive` | Alias histórico do shadcn — usar `--danger` em código novo |

Uso em Tailwind: `bg-surface`, `text-muted-foreground`, `border-border`, `text-success`, etc. — nunca `bg-[#...]`.

## Typography

Fonte: Geist Sans (`--font-sans`, já carregada via `next/font/google` em `layout.tsx`) — geométrica, moderna, alta legibilidade, já alinhada ao Documento 08A §15. Monoespaçada (`--font-mono`, Geist Mono) reservada para IDs/JSON/logs (§179) — ainda não usada nas telas de usuário.

Hierarquia recomendada (combinações de utilities Tailwind, não classes novas):

| Token | Uso | Classes sugeridas |
|---|---|---|
| display | Hero/landing | `text-4xl md:text-5xl font-semibold tracking-tight` |
| heading-xl | Título de página | `text-2xl font-semibold tracking-tight` |
| heading-lg | Título de seção | `text-xl font-semibold` |
| heading-md | Título de card | `text-base font-medium` (`CardTitle`) |
| heading-sm | Subtítulo | `text-sm font-medium` |
| body | Texto padrão | `text-sm` |
| body-small | Texto secundário | `text-xs` |
| caption | Legenda | `text-xs text-muted-foreground` |
| label | Rótulo de campo | `text-sm font-medium` (`Label`) |
| numeric | Métrica em destaque | `text-3xl font-semibold tabular-nums` |

## Radius

`--radius: 0.75rem` (base), com escala derivada em `@theme inline`: `radius-sm/md/lg/xl/2xl/3xl/4xl`. Componentes usam `rounded-lg`/`rounded-xl` por padrão — evitar cantos muito quadrados ou exagerados.

## Shadows

`--shadow-sm` / `--shadow-md` / `--shadow-lg` (soft, diffused, valores diferentes por tema — mais opacos no dark). `--shadow-glow-primary` para o glow sutil do botão primário e elementos de destaque de IA. Uso: `shadow-(--shadow-md)` etc.

## Motion

`--duration-fast` (120ms), `--duration-normal` (200ms), `--duration-slow` (320ms), `--ease-standard`. Faixa alvo para microinterações: 150–250ms (Documento 08A §81). `prefers-reduced-motion: reduce` é respeitado globalmente em `globals.css`.

## Z-Index

`--z-dropdown` (50), `--z-sticky` (40), `--z-overlay` (60), `--z-modal` (70), `--z-toast` (80) — usar via `z-(--z-modal)` etc. quando um componente precisar empilhar sobre outros (ainda não exercitado — nenhum modal/toast implementado até esta fase).

## Componentes

Base primitives em `apps/web/src/components/ui/` (shadcn + `@base-ui/react`): `Button`, `Input`, `Label`, `Card`, `Badge`. Todos consomem os tokens acima — nunca cor hardcoded dentro do componente.

`Badge` tem variantes `default`, `secondary`, `destructive`, `success`, `warning`, `info`, `outline`, `ghost`, `link` — usar `success`/`warning`/`danger`(`destructive`)/`info` para status semânticos (Documento 08A §42).

`Button` variante `default` (primary) tem glow sutil no hover (`--shadow-glow-primary`) — não abusar em botões secundários/ghost.

### Layout shell

- `AppShell` (`apps/web/src/components/app-shell.tsx`): sidebar fixa (desktop) + topbar + nav horizontal compacta (mobile) + área de conteúdo. Usado pelo layout do route group `(app)` — todas as páginas autenticadas ficam dentro dele automaticamente. Nav principal: Dashboard/Ideias/Calendário (Documento 08B §9); nav utilitária inferior: Canais.
- `ThemeToggle` (`apps/web/src/components/theme-toggle.tsx`): alterna `dark`/`light`, persiste em `localStorage`. Renderizado client-only (`next/dynamic` com `ssr:false`) para não conflitar com o script anti-FOUC.
- `PageHeader` (`apps/web/src/components/page-header.tsx`): título + subtítulo opcional + slot de ação primária à direita (Documento 08B §14).
- Slot **"AI Magic"** dentro do `AppShell`: `<div>` não-interativo com glow (`--shadow-glow-primary`) — visual apenas, por instrução do Documento 08B §10-11 de não implementar funcionalidade prematuramente.
- `MetricCard` (`metric-card.tsx`): label + valor numérico grande + hint opcional — usado no Dashboard, sempre com dados reais (nunca fabricar o valor).
- `TodayContentItem` (`today-content-item.tsx`): hora + badge de formato + título + badge de status, para o card "Hoje" do Dashboard.

### Componentes de produto (Documento 08B)

- `OpportunityCard` (`opportunity-card.tsx`): card de ideia — score (`getOpportunityScoreVariant`, nunca cor fixa no componente, Documento 08B §37), badge de formato, título/resumo, pilar/fonte, callout "Por quê" com borda colorida, ação "Adicionar ao calendário" (só quando `status === "recommended"`) ou badge de status persistente.
- `FilterChips` (`filter-chips.tsx`): tabs de filtro via `<Link>`+searchParam (sem client JS) — usado em `/ideas` para status (adaptação do Documento 08B §34, que usa categorias de tópico que não existem no domínio real do produto).
- `CalendarItemCard` (`calendar-item-card.tsx`): tratamento tracejado + badge "IA" para sugestões não decididas (Documento 08B §47-48) vs. borda sólida + rail de status colorido para itens já aprovados/rejeitados (§46). Ações Aprovar/Rejeitar sempre; Mover (reagendar) apenas fora do modo compacto (grid semanal).
- `CalendarToolbar` (`calendar-toolbar.tsx`) + `EditorialCalendar` (`editorial-calendar.tsx`): toggle Semana/Lista com navegação de semana via link, grid de 7 colunas para a visualização semanal (Documento 08B §42-44). "Mês" não implementado (ver `docs/ui.md`, decisão de escopo).

### Ainda não implementados (Documento 08A §148, lista completa de primitives)

`Select`, `Dialog`, `Sheet`, `Dropdown`, `Tooltip`, `Tabs`, `Avatar`, `Table`, `Skeleton`, `Toast`, `Progress` — serão criados conforme as telas que precisarem deles (ex.: `Sheet` para o drawer mobile da sidebar, `Toast` quando houver a primeira ação com feedback assíncrono real). Não construídos preventivamente sem um consumidor real, para não acumular componentes não exercitados.

## Dark/Light

`<html>` renderiza com a classe `dark` no servidor por padrão (Documento 08A §153-155: dark é o tema principal). Um script inline em `layout.tsx` roda antes do hydration e remove a classe se `localStorage` tiver `"mcp-videos-theme": "light"` salvo — sem flash de tema errado. Light mode tem paleta própria e calibrada (não é um dark invertido).

## Checklist antes de criar uma tela nova (Documento 08A §212)

1. Consultar Documento 08 e Documento 08A.
2. Usar os tokens existentes (nunca cor hardcoded).
3. Reutilizar componentes de `components/ui/` e `AppShell`.
4. Verificar responsividade (mobile: nav horizontal no topo; desktop: sidebar).
5. Confirmar que funciona em dark e light.
6. Sem cor hardcoded fora de `globals.css`.
7. Incluir estados de loading/empty/error quando aplicável.
8. Testar hover/focus.
9. Respeitar acessibilidade (contraste, labels, foco visível, `prefers-reduced-motion`).
10. Não inventar uma linguagem visual nova só para aquela página.
