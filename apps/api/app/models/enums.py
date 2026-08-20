"""Domain enums shared across models.

Documento 02, secao 15: nunca usar strings arbitrarias para status.
"""

from enum import StrEnum


class OrganizationStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


class UserStatus(StrEnum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


class OrganizationRole(StrEnum):
    """Documento 09, secao 12."""

    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class MembershipStatus(StrEnum):
    ACTIVE = "active"
    INVITED = "invited"
    REMOVED = "removed"


class ChannelPlatform(StrEnum):
    """Documento 03, secao 8: platform="youtube" inicialmente, sem acoplar
    o nome da tabela a um provider especifico."""

    YOUTUBE = "youtube"


class ChannelStatus(StrEnum):
    """Ciclo de vida do registro do canal na plataforma (distinto do status
    da conexao OAuth, que chega na Fase 04 em channel_connections)."""

    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"


class AutomationMode(StrEnum):
    """Documento 03, secao 9. Novo canal sempre comeca em ASSISTED - nunca
    auto-publicacao irrestrita."""

    MANUAL = "manual"
    ASSISTED = "assisted"
    SEMI_AUTO = "semi_auto"
    AUTOPILOT = "autopilot"


class JobStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FeatureFlagScope(StrEnum):
    GLOBAL = "global"
    ORGANIZATION = "organization"
    CHANNEL = "channel"


class AuditActorType(StrEnum):
    USER = "user"
    SYSTEM = "system"
    AGENT = "agent"
    WORKER = "worker"


class ChannelConnectionProvider(StrEnum):
    """Documento 03, secao 10. Unico provider inicial."""

    GOOGLE_YOUTUBE = "google_youtube"


class ChannelConnectionStatus(StrEnum):
    """Documento 08, secao 137 (Channel Connection State)."""

    CONNECTED = "connected"
    NEEDS_REAUTHORIZATION = "needs_reauthorization"
    SYNCING = "syncing"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class SyncType(StrEnum):
    """Documento 03, secao 11."""

    INITIAL = "initial"
    FULL = "full"
    INCREMENTAL = "incremental"
    MANUAL = "manual"


class SyncRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SourceVideoType(StrEnum):
    """Documento 03, secao 12. Classificado pelo ChannelSyncService a
    partir da duracao (heuristica: <=60s = short), nao pelo gateway."""

    SHORT = "short"
    LONG_FORM = "long_form"
    LIVE = "live"
    UNKNOWN = "unknown"


class AudienceProfileSource(StrEnum):
    """Documento 03, secao 17."""

    YOUTUBE = "youtube"
    USER = "user"
    INFERRED = "inferred"
    MIXED = "mixed"


class ChannelDNAStatus(StrEnum):
    """Documento 03, secao 16. Apenas uma versao ACTIVE por canal."""

    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"


class ContentStrategyStatus(StrEnum):
    """Documento 03, secao 19. Apenas uma versao ACTIVE por canal - a
    transicao draft->active exige aprovacao explicita (Documento 05 sec.
    8: Strategy Agent "nao pode ativar estrategia sozinho sem policy")."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class IdeaOrigin(StrEnum):
    """Documento 03, secao 22."""

    AI = "ai"
    TREND = "trend"
    USER = "user"
    ANALYTICS = "analytics"
    SERIES = "series"
    REPURPOSE = "repurpose"


class IdeaStatus(StrEnum):
    """Documento 03, secao 22. RECOMMENDED/REJECTED sao definidos pelo
    OpportunityEvaluationService a partir do score calculado em codigo
    (Documento 10 F09: "calculo final deve ocorrer em codigo") - nunca
    pela opiniao livre do agente. APPROVED e sempre uma acao humana."""

    DRAFT = "draft"
    EVALUATING = "evaluating"
    RECOMMENDED = "recommended"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class OpportunityStatus(StrEnum):
    """Documento 03, secao 23. Espelha o resultado do calculo de score."""

    RECOMMENDED = "recommended"
    REJECTED = "rejected"


class ScoreType(StrEnum):
    """Documento 03, secao 24 ("tipos iniciais") - os 9 componentes que
    compoem o opportunity_score. Nunca guardar so o score final; cada
    componente vira sua propria linha em opportunity_scores."""

    CHANNEL_FIT = "channel_fit"
    AUDIENCE_FIT = "audience_fit"
    TREND = "trend"
    NOVELTY = "novelty"
    RETENTION_POTENTIAL = "retention_potential"
    SEARCH_POTENTIAL = "search_potential"
    COMPETITION = "competition"
    BRAND_FIT = "brand_fit"
    STRATEGIC_FIT = "strategic_fit"


class ContentClusterStatus(StrEnum):
    """Documento 03, secao 25."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class IdeaRelationshipType(StrEnum):
    """Documento 03, secao 26."""

    PARENT = "parent"
    CHILD = "child"
    RELATED = "related"
    REPURPOSE = "repurpose"
    SEQUEL = "sequel"
    SERIES = "series"
