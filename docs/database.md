# Database — Estado Atual do Schema

> Mantido conforme Documento 03, seção 133. Atualizar a cada fase que alterar o domínio.

Última atualização: Fase 03 — Authentication & Security.

## ERD

```mermaid
erDiagram
    ORGANIZATION ||--o{ ORGANIZATION_MEMBER : has
    USER ||--o{ ORGANIZATION_MEMBER : belongs
    ORGANIZATION ||--o{ CHANNEL : owns
    ORGANIZATION ||--o{ JOB : owns
    ORGANIZATION ||--o{ AUDIT_LOG : owns
    USER ||--o{ USER_SESSION : authenticates
    ORGANIZATION ||--o{ USER_SESSION : "active context (optional)"

    ORGANIZATION {
        uuid id PK
        string name
        string slug UK
        enum status
        string timezone
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }

    USER {
        uuid id PK
        string email UK
        string name
        string password_hash
        enum status
        timestamptz last_login_at
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }

    ORGANIZATION_MEMBER {
        uuid id PK
        uuid organization_id FK
        uuid user_id FK
        enum role
        enum status
        timestamptz created_at
        timestamptz updated_at
    }

    CHANNEL {
        uuid id PK
        uuid organization_id FK
        enum platform
        string external_channel_id
        string name
        string handle
        enum status
        enum automation_mode
        timestamptz connected_at
        timestamptz last_synced_at
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }

    JOB {
        uuid id PK
        uuid organization_id FK
        string job_type
        string resource_type
        uuid resource_id
        enum status
        int progress_percent
        uuid correlation_id
        timestamptz started_at
        timestamptz completed_at
        timestamptz created_at
        timestamptz updated_at
    }

    AUDIT_LOG {
        uuid id PK
        uuid organization_id FK
        enum actor_type
        uuid actor_id
        string action
        string resource_type
        uuid resource_id
        jsonb metadata_json
        inet ip_address
        timestamptz created_at
    }

    FEATURE_FLAG {
        uuid id PK
        string key
        enum scope_type
        uuid scope_id "polimorfico - sem FK fixa"
        boolean enabled
        jsonb config_json
        timestamptz created_at
        timestamptz updated_at
    }

    USER_SESSION {
        uuid id PK
        uuid user_id FK
        string token_hash UK
        uuid active_organization_id FK "nullable"
        string user_agent
        inet ip_address
        timestamptz created_at
        timestamptz expires_at
        timestamptz last_seen_at
        timestamptz revoked_at
    }
```

`FEATURE_FLAG` fica fora do diagrama de relacionamentos porque `scope_id` é polimórfico (aponta para `organizations.id` ou `channels.id` dependendo de `scope_type`, ou é nulo quando `scope_type=global`) — não tem FK fixa de propósito (Documento 03, seção 85).

`USER_SESSION` (tabela `sessions`) pertence a um `USER`, não a uma organização fixa — `active_organization_id` é o contexto de organização atual da sessão e pode mudar (endpoint `POST /auth/organization`), nunca uma FK obrigatória.

## Entidades por fase (o que já existe)

| Fase | Entidades | Status |
|---|---|---|
| 01 | — (nenhuma entidade de domínio) | ✅ |
| 02 | `organizations`, `users`, `organization_members`, `channels`, `jobs`, `feature_flags`, `audit_logs` | ✅ |
| 03 | `sessions` (modelo `UserSession`) | ✅ |
| 04+ | `channel_connections`, `channel_sync_runs`, ... | ⏳ |

Ver Documento 03, seções 110-129 para o mapeamento completo fase → entidades. `sessions` não está no Documento 03 (que deixa "sessions/tokens conforme implementação" em aberto — Documento 10 §112) — modelada aqui seguindo os campos exatos do Documento 09 §6 (`session_id`, `user_id`, `created_at`, `expires_at`, `last_seen_at`, `revoked_at`).

## Decisões de modelagem (Fase 02)

- **Enums:** `native_enum=False` em todos (armazenados como `VARCHAR` com `CHECK`, não `ENUM` nativo do Postgres) — evita o custo de `ALTER TYPE ADD VALUE` sempre que um novo valor de status for necessário em fases futuras.
- **Soft delete:** aplicado em `organizations`, `users`, `channels` (entidades "críticas" segundo Documento 02, seção 14). `organization_members`, `jobs`, `feature_flags` não têm — não são entidades de negócio de longa duração da mesma forma. `audit_logs` é append-only por definição (Documento 03, seção 102), sem `updated_at`/`deleted_at`.
- **`channels.status`** (`pending | active | disabled`) é uma decisão desta fase — o Documento 03 não especifica os valores exatos, só cita o campo. Representa o ciclo de vida do *registro* do canal na plataforma, distinto do status da *conexão OAuth* (`channel_connections.status`, que chega na Fase 04).
- **`channels` unique constraint** (`organization_id + platform + external_channel_id`) é um índice único parcial (`WHERE external_channel_id IS NOT NULL`), já que canais "placeholder" criados nesta fase ainda não têm `external_channel_id`.
- **Repositórios:** `TenantScopedRepository` nunca expõe `get_by_id`/`list` sem `organization_id` obrigatório — única forma de acessar entidades escopadas (Documento 02, seção 11). `BaseRepository` (sem escopo) é usado apenas para `Organization`, `User` e `UserSession`, que não são escopados por uma única organização fixa.

## Decisões de modelagem (Fase 03)

- **`users.status`** novo usuário nasce `active` (não `pending`) — não existe ainda fluxo de verificação de e-mail (Documento 09, seção 142, é opcional e não implementado nesta fase).
- **Sessões DB-backed, não JWT stateless.** Segue Documento 09 §6 e o princípio geral "estado vive no Postgres" (Documento 02 §21). Um token opaco de alta entropia (`secrets.token_urlsafe(32)`) é gerado no login/registro; só o hash SHA-256 é persistido (nunca o token puro — mesmo princípio de nunca guardar segredo em texto). Isso permite revogação real (`logout`, futura "logout de todos os dispositivos"), que um JWT auto-contido não permitiria sem uma blocklist.
- **Registro cria organização automaticamente.** Cada novo usuário vira `owner` de uma organização nova no `POST /auth/register` (Documento 08 §3: "Criar organização" é o primeiro passo após o cadastro). Não há fluxo de "entrar em organização existente" nesta fase (convite de membros fica para fase futura).
- **`AuthorizationService` + `Permission` (coarse-grained).** `app/domain/permissions.py` mapeia os 4 roles do Documento 09 §12 para um conjunto fixo de permissões (não o modelo granular por-recurso do Documento 09 §17, que é explicitamente "preparar para o futuro"). Owner tem tudo; Admin tem tudo exceto billing/org settings; Editor tem conteúdo; Viewer só leitura.
- **Rate limiting de login** via Redis (`app/security/rate_limit.py`) — 5 tentativas por e-mail em 15 min, depois `429`. Redis é usado só como contador (nunca fonte de verdade), conforme Documento 02 §21.
- **Nenhum endpoint de negócio novo além de auth.** `POST /organizations`, `POST /channels` etc. continuam não expostos — isso pertence às fases que de fato precisam deles, agora com autenticação e `require_permission` disponíveis para protegê-los.
