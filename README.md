# mcp_videos

Plataforma SaaS multiusuário e multicanal de planejamento, geração, avaliação, agendamento, publicação e otimização automática de conteúdo para YouTube (Content Intelligence + Content Production + Content Growth Automation).

A especificação completa do produto e da arquitetura vive em [`/docs`](docs) — ver [`docs/PROGRESS.md`](docs/PROGRESS.md) para o estado atual do projeto e [`docs/ARCHITECTURE-ACKNOWLEDGEMENT.md`](docs/ARCHITECTURE-ACKNOWLEDGEMENT.md) para um resumo da arquitetura.

**Status:** Fase 01 — Project Foundation.

---

## Requisitos

- Docker + Docker Compose
- Node.js 22+ (apenas se for rodar o frontend fora do Docker)
- Python 3.12 (apenas se for rodar o backend fora do Docker)

## Estrutura do monorepo

```text
apps/
  web/        Next.js (frontend)
  api/        FastAPI (backend)
services/
  worker/     Celery worker (reutiliza a imagem de apps/api na Fase 01)
  media/      Media processing — chega na Fase 15
  scheduler/  Scheduler — chega na Fase 18
packages/
  shared/     Código compartilhado entre apps TS — ainda vazio
  schemas/    Contratos compartilhados — ainda vazio
  ui/         Design system compartilhado — ainda vazio (componentes ficam em apps/web por ora)
infra/
  docker/     Assets Docker compartilhados (ainda vazio)
  nginx/      Reverse proxy para staging/produção (ainda vazio)
  scripts/    Scripts operacionais (ex.: smoke-test.sh)
docs/         Documentação mestre do projeto e documentação técnica viva
tests/        Testes E2E cross-stack (chegam a partir da Fase 03)
```

## Ambiente local

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
docker compose up
```

Isso sobe: `web` (Next.js, porta 3000), `api` (FastAPI, porta **8002** no host — porta 8000 evitada de propósito para não colidir com outros projetos locais), `worker` (Celery), `postgres` (5432), `redis` (6379) e `minio` (9000/9001, console em `/minio/`).

Validar que tudo subiu corretamente:

```bash
bash infra/scripts/smoke-test.sh
```

Isso confere `/health`, `/health/db`, `/health/redis` na API e que o frontend está servindo.

## Backend (apps/api)

Sem Docker, para desenvolvimento local:

```bash
cd apps/api
python -m venv .venv
./.venv/Scripts/activate       # Windows
# source .venv/bin/activate    # Linux/Mac
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8002
```

Comandos úteis:

```bash
ruff check .            # lint
mypy app                # typecheck
pytest                  # testes de unidade (não exigem infra)
```

### Migrations (Alembic)

```bash
cd apps/api
alembic revision --autogenerate -m "descricao da mudanca"
alembic upgrade head
```

Rodando fora do Docker, aponte `DATABASE_URL` para `localhost` em vez do hostname interno `postgres` (que só existe dentro da rede do `docker compose`), por exemplo:

```bash
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/mcp_videos alembic upgrade head
```

### Testes de integração (repositories/services)

A partir da Fase 02, os testes de repository/service rodam contra um PostgreSQL real (Documento 10, seção 49 — testar DB/repositories de verdade, não mockado). Cada teste roda dentro de uma transação que é sempre revertida no final, então não é preciso limpar dados manualmente.

Crie o banco de teste uma vez (com o `docker compose` já rodando):

```bash
docker exec mcp_videos-postgres-1 psql -U postgres -c "CREATE DATABASE mcp_videos_test;"
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/mcp_videos_test alembic upgrade head
```

Depois disso, `pytest` já aponta para `mcp_videos_test` em `localhost:5432` por padrão (ajustável via `TEST_DATABASE_URL`).

## Frontend (apps/web)

```bash
cd apps/web
npm install
npm run dev
```

Comandos úteis:

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

## Documentação

- [`docs/PROGRESS.md`](docs/PROGRESS.md) — estado atual do projeto, o que já foi feito, o que falta.
- [`docs/ARCHITECTURE-ACKNOWLEDGEMENT.md`](docs/ARCHITECTURE-ACKNOWLEDGEMENT.md) — resumo da arquitetura acordada.
- `docs/Documento 01–10 - *.md` — especificação mestre completa (produto, arquitetura, dados, workflows, agentes, providers, growth, UX, segurança/billing, plano de implementação).
