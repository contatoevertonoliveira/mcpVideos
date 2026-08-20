# Database — Estado Atual do Schema

> Mantido conforme Documento 03, seção 133. Atualizar a cada fase que alterar o domínio.

Última atualização: Fase 05 — Channel Importer.

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
    CHANNEL ||--o| CHANNEL_CONNECTION : "has one"
    CHANNEL ||--o{ CHANNEL_SYNC_RUN : logs
    CHANNEL ||--o{ SOURCE_VIDEO : has
    CHANNEL ||--o{ SOURCE_PLAYLIST : has
    SOURCE_VIDEO ||--o{ SOURCE_VIDEO_METRIC : "historical snapshots"

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

    CHANNEL_CONNECTION {
        uuid id PK
        uuid organization_id FK
        uuid channel_id FK "UK with provider"
        enum provider "UK with channel_id"
        string external_account_id
        string access_token_encrypted "never returned by the API"
        string refresh_token_encrypted "never returned by the API"
        timestamptz token_expires_at
        string_array scopes
        enum status
        timestamptz created_at
        timestamptz updated_at
    }

    CHANNEL_SYNC_RUN {
        uuid id PK
        uuid organization_id FK
        uuid channel_id FK
        enum sync_type
        enum status
        timestamptz started_at
        timestamptz completed_at
        int items_discovered
        int items_created
        int items_updated
        string error_code
        string error_message
        uuid correlation_id
    }

    SOURCE_VIDEO {
        uuid id PK
        uuid organization_id FK
        uuid channel_id FK "UK with external_video_id"
        string external_video_id "UK with channel_id"
        string title
        string description
        enum video_type
        int duration_seconds
        timestamptz published_at
        string privacy_status
        string thumbnail_url
        jsonb raw_metadata_json
        timestamptz created_at
        timestamptz updated_at
    }

    SOURCE_PLAYLIST {
        uuid id PK
        uuid organization_id FK
        uuid channel_id FK "UK with external_playlist_id"
        string external_playlist_id "UK with channel_id"
        string title
        string description
        int item_count
        jsonb raw_metadata_json
        timestamptz created_at
        timestamptz updated_at
    }

    SOURCE_VIDEO_METRIC {
        uuid id PK
        uuid organization_id FK
        uuid channel_id FK
        uuid source_video_id FK "UK with captured_at"
        timestamptz captured_at "UK with source_video_id"
        bigint views
        bigint likes
        bigint comments
        float watch_time_minutes "NULL ate Fase 19"
        float average_view_duration "NULL ate Fase 19"
        float average_view_percentage "NULL ate Fase 19"
        int subscribers_gained "NULL ate Fase 19"
        int subscribers_lost "NULL ate Fase 19"
        bigint impressions "NULL ate Fase 19"
        float impressions_ctr "NULL ate Fase 19"
        jsonb raw_metrics_json
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
| 04 | `channel_connections`, `channel_sync_runs` | ✅ |
| 05 | `source_videos`, `source_playlists`, `source_video_metrics` | ✅ |
| 06+ | `channel_profiles`, `audience_profiles`, ... | ⏳ |

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

## Decisões de modelagem (Fase 04)

- **`channel_connections` unique constraint** em `(channel_id, provider)` — um canal só pode ter uma conexão ativa por provider (hoje só `google_youtube`), mas a estrutura já comporta múltiplos providers por canal no futuro.
- **Tokens sempre criptografados em repouso** (`app/security/encryption.py`, Fernet, chave via `TOKEN_ENCRYPTION_KEY` — nunca no banco). A API nunca devolve `access_token_encrypted`/`refresh_token_encrypted` em nenhuma resposta (testado explicitamente em `test_channels_endpoints.py`).
- **`YouTubeGateway` com duas implementações**: `GoogleYouTubeGateway` (real, via `httpx`, chama os endpoints OAuth2/YouTube Data API v3 do Google) e `FakeYouTubeGateway` (determinística, sem rede — Documento 02 §71). A escolha é via `Settings.youtube_fake_gateway` (`YOUTUBE_FAKE_GATEWAY=true` por padrão). O `FakeYouTubeGateway` aponta a "authorization_url" para o próprio callback do frontend (com um `code` falso já embutido), então o fluxo de conexão é clicável de ponta a ponta no navegador sem precisar de uma conta Google real.
- **State OAuth assinado, sem storage.** `app/security/signed_state.py` gera um token HMAC-SHA256 (stdlib puro, sem nova dependência) contendo `organization_id` + `user_id` + expiração — a validação no callback é 100% stateless e detecta adulteração/expiração. O usuário autenticado no callback precisa bater com o `user_id` do state (`STATE_USER_MISMATCH` se não bater).
- **`channel_sync_runs` na Fase 04** grava só o tipo `INITIAL` (a conexão em si) — importação de vídeos/playlists (`FULL`/`INCREMENTAL`) é Fase 05 (Channel Importer), conforme Documento 03 §113-114.
- **Upsert por `external_channel_id`**: reconectar um canal já existente (mesmo `organization_id` + `platform` + `external_channel_id`) atualiza o registro existente em vez de duplicar — cobre tanto reconexão quanto refresh de metadata.
- **Bug real encontrado via teste:** `TenantScopedRepository.add()`/`BaseRepository.add()` fazem `session.flush()` imediatamente. Construir uma entidade com campos `NOT NULL` ainda vazios e só preenchê-los *depois* de chamar `.add()` quebra com `IntegrityError`. Corrigido usando `session.add()` (sem flush) nesses dois pontos específicos do `ChannelConnectionService`, e documentado aqui para não se repetir em fases futuras: **sempre preencher os campos obrigatórios antes de persistir, ou usar `session.add()` cru quando precisar de duas etapas.**

## Decisões de modelagem (Fase 05)

- **`source_videos`/`source_playlists` unique constraint** em `(channel_id, external_*_id)`, igual ao padrão de `channels`/`channel_connections` — é o que garante a idempotência exigida pelo Documento 04 §19 ("re-sync não duplica"): o `ChannelSyncService` faz upsert por esse par.
- **`created_at`/`updated_at` em `source_playlists`** não estão nos "campos" listados no Documento 03 §13, mas foram adicionados por consistência com o resto do schema e porque o upsert idempotente precisa distinguir criação de atualização (mesma lógica de `source_videos`).
- **`source_video_metrics` é histórica e append-only** (Documento 03 §14: "nunca sobrescrever") — sem `TimestampMixin`, só `captured_at`. Unique constraint em `(source_video_id, captured_at)` para nunca duplicar a mesma captura se uma task Celery for reexecutada.
- **Métricas da YouTube Analytics API ficam `NULL` por enquanto.** `views`/`likes`/`comments` vêm do YouTube Data API v3 (`videos.list?part=statistics`), disponível com o mesmo escopo OAuth já usado. `watch_time_minutes`, `average_view_duration/percentage`, `subscribers_gained/lost`, `impressions`, `impressions_ctr` exigem a YouTube Analytics API (escopo e fluxo próprios) — isso é explicitamente Fase 19 (Analytics & Learning Engine) no Documento 10, não Fase 05. Implementar agora seria "funcionalidade de fase futura de forma improvisada" (regra não-negociável do `CLAUDE.md`).
- **`SourceVideoType` (short/long_form/live/unknown) é classificado pelo `ChannelSyncService`, não pelo gateway.** A YouTube Data API não tem um campo nativo "é Short" — a heurística usada (duração ≤ 60s) é aplicada centralmente no passo de "normalize" do fluxo (Documento 04 §18), para que `GoogleYouTubeGateway`/`FakeYouTubeGateway` só devolvam fatos brutos (duração, live ou não).
- **`YouTubeGateway` ganhou `list_playlists`/`list_videos`/`get_video_metrics`.** `GoogleYouTubeGateway` implementa a sequência real (`channels.list` para achar a playlist de uploads → `playlistItems.list` → `videos.list` em lotes de 50, com paginação limitada a 5 páginas como cap de segurança para o MVP). `FakeYouTubeGateway` devolve sempre os mesmos 5 vídeos/1 playlist determinísticos (2 shorts + 3 vídeos longos), para que o teste de "não duplica no re-sync" seja exercitável sem rede.
- **Primeira task Celery real do projeto** (`app/tasks/channel_sync.py`, nome lógico `channel.sync.v1` do Documento 04 §16). O motor completo de workflows versionados (`workflow_runs`, retry/resume/pause) só chega na Fase 11 — aqui é uma única task Celery com retry simples (`max_retries=3`, backoff exponencial com jitter), seguindo a regra fundamental de jobs do Documento 02 §21: o estado vive em `channel_sync_runs`/`jobs` no Postgres, o Celery só executa.
- **Bug real encontrado via teste manual no navegador (não pelos testes automatizados):** o disparo do sync (`dispatch_channel_sync`) cria a linha `Job` e chama `.delay()` dentro da mesma transação HTTP que ainda não commitou — o worker Celery, rodando em outro processo/conexão, às vezes lia o Postgres *antes* do commit da API terminar e falhava com "Job not found". Reproduzido de forma determinística disparando `POST /channels/{id}/sync` manualmente contra a stack Docker real. Corrigido com um retry curto e limitado (`_mark_running_with_retry`, até 5 tentativas / 1.5s) na primeira leitura do Job dentro da task, em vez de um padrão de outbox transacional completo (mais mecanismo do que esta fase precisa). Validado com 3 disparos concorrentes reais sem nenhuma falha.
