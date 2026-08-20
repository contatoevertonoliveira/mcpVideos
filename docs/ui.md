# UI — Estado Atual do Frontend

> Mantido conforme Documento 08/08A. Atualizar a cada fase que adicionar ou reestilizar telas.

Última atualização: retrofit da fundação visual (Documento 08A), antes da Fase 09.

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
│   └── channels/page.tsx        "/channels"
└── oauth/youtube/{start,callback}/route.ts   Route Handlers (BFF OAuth, Fase 04)
```

`(auth)` e `(app)` são route groups do Next.js — não aparecem na URL. `proxy.ts` continua protegendo por caminho (`/dashboard`, `/channels`), sem relação com a estrutura de pastas.

## Telas implementadas

| Tela | Rota | Fase | Notas visuais |
|---|---|---|---|
| Splash/Status | `/` | F01 | Card de status da API + CTAs de login/registro |
| Login | `/login` | F03 | Card centralizado, glow radial de fundo sutil |
| Registro | `/register` | F03 | Idem, cria organização automaticamente |
| Dashboard | `/dashboard` | F03 | Saudação + conta + link para Canais + lista de organizações |
| Canais | `/channels` | F04-F08 | Lista de canais conectados; cada card acumula, conforme a fase: sincronizar, diagnóstico (Fase 06), DNA (Fase 07), estratégia com aprovação (Fase 08) |

## O que ainda não existe

Todas as telas do Documento 08A ainda não construídas porque as fases que as exigem não chegaram: Ideias (F09), Calendário (F10), Conteúdos/Pipeline (F12+), Analytics (F19), Control Center (F20), Command Palette, notificações, onboarding com animação de análise do canal. A navegação lateral do `AppShell` hoje só lista Dashboard/Canais — os demais itens do Documento 08A §27 (Ideias, Calendário, Conteúdos, Analytics) serão adicionados quando as rotas correspondentes existirem, não antes (evita links mortos).

## Decisões de escopo desta passada de retrofit

- **Sidebar/topbar shell construído, mas sem drawer mobile real.** Mobile usa uma barra de nav horizontal compacta abaixo do topbar em vez de um `Sheet`/drawer lateral — o primitive `Sheet` (Documento 08A §148) ainda não existe no projeto e não valia a pena construí-lo só para isso agora. Revisar quando houver mais itens de navegação ou um caso de uso real para o drawer.
- **Sem `Select`/`Dialog`/`Tooltip`/`Toast`/etc.** ainda — nenhuma tela atual precisa deles de verdade. Serão criados quando a primeira tela realmente os exigir (ex.: confirmação destrutiva real vai precisar de `Dialog`).
- **Hero do dashboard é minimalista, sem números fabricados.** O Documento 08A §32 sugere algo como "3 conteúdos programados hoje" — como não existe Calendário ainda (Fase 10), não inventamos essa métrica; o hero mostra saudação + organização atual, real.
- **Página `/channels` ainda é uma lista de cards simples**, não o dashboard rico do Documento 08A (Opportunity Card, AI Insight Card etc.) — esses componentes pertencem a fases futuras (Ideas & Opportunity Engine, F09) que ainda não têm dados reais para alimentá-los.
