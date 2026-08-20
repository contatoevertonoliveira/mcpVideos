# apps/web

Frontend da plataforma (Next.js + TypeScript + Tailwind + shadcn/ui). Ver [README raiz](../../README.md) para instruções completas de ambiente.

```bash
npm install
npm run dev          # http://localhost:3000
npm run lint
npm run typecheck
npm run test
npm run build
```

Estrutura (`src/`):

```text
app/                rotas do App Router
components/ui/      componentes shadcn/ui
lib/                utilitários (ex.: leitura de env server-side)
services/api/       cliente de acesso à API (centralizado, ver Documento 08 §180-181)
types/               tipos compartilhados do domínio no frontend
```

Diretórios `features/`, `hooks/` e `stores/` chegam junto da primeira feature real (Fase 03 — Authentication), seguindo a regra de não criar telas/estruturas vazias para fases futuras (Documento 10 §176).
