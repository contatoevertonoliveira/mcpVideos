# Database — Estado Atual do Schema

> Mantido conforme Documento 03, seção 133. Atualizar a cada fase que alterar o domínio.

Última atualização: Fase 02 — Core Domain & Database.

## ERD

```mermaid
erDiagram
    ORGANIZATION ||--o{ ORGANIZATION_MEMBER : has
    USER ||--o{ ORGANIZATION_MEMBER : belongs
    ORGANIZATION ||--o{ CHANNEL : owns
    ORGANIZATION ||--o{ JOB : owns
    ORGANIZATION ||--o{ AUDIT_LOG : owns

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
```

`FEATURE_FLAG` fica fora do diagrama de relacionamentos porque `scope_id` é polimórfico (aponta para `organizations.id` ou `channels.id` dependendo de `scope_type`, ou é nulo quando `scope_type=global`) — não tem FK fixa de propósito (Documento 03, seção 85).

## Entidades por fase (o que já existe)

| Fase | Entidades | Status |
|---|---|---|
| 01 | — (nenhuma entidade de domínio) | ✅ |
| 02 | `organizations`, `users`, `organization_members`, `channels`, `jobs`, `feature_flags`, `audit_logs` | ✅ |
| 03+ | `channel_connections`, `channel_sync_runs`, ... | ⏳ |

Ver Documento 03, seções 110-129 para o mapeamento completo fase → entidades.

## Decisões de modelagem (Fase 02)

- **Enums:** `native_enum=False` em todos (armazenados como `VARCHAR` com `CHECK`, não `ENUM` nativo do Postgres) — evita o custo de `ALTER TYPE ADD VALUE` sempre que um novo valor de status for necessário em fases futuras.
- **Soft delete:** aplicado em `organizations`, `users`, `channels` (entidades "críticas" segundo Documento 02, seção 14). `organization_members`, `jobs`, `feature_flags` não têm — não são entidades de negócio de longa duração da mesma forma. `audit_logs` é append-only por definição (Documento 03, seção 102), sem `updated_at`/`deleted_at`.
- **`channels.status`** (`pending | active | disabled`) é uma decisão desta fase — o Documento 03 não especifica os valores exatos, só cita o campo. Representa o ciclo de vida do *registro* do canal na plataforma, distinto do status da *conexão OAuth* (`channel_connections.status`, que chega na Fase 04).
- **`channels` unique constraint** (`organization_id + platform + external_channel_id`) é um índice único parcial (`WHERE external_channel_id IS NOT NULL`), já que canais "placeholder" criados nesta fase ainda não têm `external_channel_id`.
- **`users.status`** novo usuário nasce `active` (não `pending`) nesta fase, por não existir ainda fluxo de verificação de e-mail (Documento 09, seção 142, é opcional e chega com a Fase 03 — Authentication).
- **Repositórios:** `TenantScopedRepository` nunca expõe `get_by_id`/`list` sem `organization_id` obrigatório — única forma de acessar entidades escopadas (Documento 02, seção 11). `BaseRepository` (sem escopo) é usado apenas para `Organization` e `User`, que são as raízes do tenant.
- **Senha:** hashing via `bcrypt` (`app/security/password.py`). Login/sessão ainda não existem — chegam na Fase 03.
