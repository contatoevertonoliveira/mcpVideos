from __future__ import annotations

import re
import uuid

from sqlalchemy.orm import Session

from app.agents.idea_agent import run_idea_agent
from app.core.config import get_settings
from app.core.exceptions import DomainError, NotFoundError
from app.gateways.llm import LLMGateway, get_llm_gateway
from app.models.content_idea import ContentIdea
from app.models.enums import AuditActorType, IdeaOrigin, IdeaRelationshipType, IdeaStatus
from app.models.idea_relationship import IdeaRelationship
from app.repositories.audience_profile import AudienceProfileRepository
from app.repositories.channel import ChannelRepository
from app.repositories.channel_dna_version import ChannelDNAVersionRepository
from app.repositories.content_idea import ContentIdeaRepository
from app.repositories.content_strategy import ContentStrategyRepository
from app.repositories.idea_relationship import IdeaRelationshipRepository
from app.repositories.source_video import SourceVideoRepository
from app.services.audit import AuditService

# MVP heuristic (Documento 10 F09 "deduplication"): two titles are treated
# as near-duplicates if most of their significant words overlap. A real
# semantic/embedding-based dedup is future work - this is enough to catch
# the agent proposing an obvious rehash without adding new infrastructure.
_DEDUP_JACCARD_THRESHOLD = 0.6
_STOPWORDS = {
    "a",
    "o",
    "as",
    "os",
    "de",
    "da",
    "do",
    "das",
    "dos",
    "e",
    "em",
    "um",
    "uma",
    "que",
    "com",
    "para",
}


def _title_tokens(title: str) -> set[str]:
    words = re.findall(r"[a-zà-ÿ0-9]+", title.lower())
    return {word for word in words if word not in _STOPWORDS}


def _is_near_duplicate(title_a: str, title_b: str) -> bool:
    tokens_a, tokens_b = _title_tokens(title_a), _title_tokens(title_b)
    if not tokens_a or not tokens_b:
        return False
    overlap = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return (overlap / union) >= _DEDUP_JACCARD_THRESHOLD


class IdeaGenerationService:
    """Documento 05, secao 10 (Idea Agent); Documento 10 Fase 09."""

    def __init__(self, session: Session, llm_gateway: LLMGateway | None = None) -> None:
        self.session = session
        self.llm_gateway = llm_gateway or get_llm_gateway(get_settings())
        self.channels = ChannelRepository(session)
        self.dna_versions = ChannelDNAVersionRepository(session)
        self.strategies = ContentStrategyRepository(session)
        self.audience_profiles = AudienceProfileRepository(session)
        self.videos = SourceVideoRepository(session)
        self.ideas = ContentIdeaRepository(session)
        self.relationships = IdeaRelationshipRepository(session)
        self.audit = AuditService(session)

    async def generate_ideas(
        self, *, channel_id: uuid.UUID, organization_id: uuid.UUID
    ) -> list[ContentIdea]:
        channel = self.channels.get_by_id(channel_id, organization_id=organization_id)
        if channel is None:
            raise NotFoundError("Channel not found", code="CHANNEL_NOT_FOUND")

        active_dna = self.dna_versions.get_active(channel_id, organization_id=organization_id)
        if active_dna is None:
            raise DomainError(
                "Channel has no active Channel DNA yet - generate one first",
                code="CHANNEL_DNA_NOT_READY",
            )
        active_strategy = self.strategies.get_active(channel_id, organization_id=organization_id)
        if active_strategy is None:
            raise DomainError(
                "Channel has no active content strategy yet - approve one first",
                code="CHANNEL_STRATEGY_NOT_READY",
            )
        audience_profile = self.audience_profiles.get_current(
            channel_id, organization_id=organization_id
        )
        recent_videos = self.videos.list_by_channel(
            channel_id=channel_id, organization_id=organization_id, limit=10
        )
        existing_ideas = self.ideas.list_active_by_channel(
            channel_id=channel_id, organization_id=organization_id
        )

        output = await run_idea_agent(
            self.llm_gateway,
            dna=active_dna,
            audience_profile_json=audience_profile.profile_json if audience_profile else None,
            strategy=active_strategy,
            recent_videos=recent_videos,
            existing_idea_titles=[idea.title for idea in existing_ideas],
            session=self.session,
            organization_id=organization_id,
            channel_id=channel_id,
        )

        created: list[ContentIdea] = []
        duplicate_count = 0
        known_ideas = list(existing_ideas)
        for suggestion in output.ideas:
            duplicate = next(
                (idea for idea in known_ideas if _is_near_duplicate(idea.title, suggestion.title)),
                None,
            )

            idea = ContentIdea(
                organization_id=organization_id,
                channel_id=channel_id,
                title=suggestion.title,
                summary=suggestion.summary or None,
                idea_type=suggestion.content_pillar or None,
                origin=IdeaOrigin.TREND if suggestion.source_type == "trend" else IdeaOrigin.AI,
                # A near-duplicate is still recorded (never silently
                # dropped) but archived immediately and linked to the
                # original via IdeaRelationship, instead of entering the
                # active DRAFT pool a second time.
                status=IdeaStatus.ARCHIVED if duplicate else IdeaStatus.DRAFT,
                recommended_format=suggestion.recommended_format or None,
            )
            self.ideas.add(idea)
            known_ideas.append(idea)

            if duplicate is not None:
                duplicate_count += 1
                self.relationships.add(
                    IdeaRelationship(
                        organization_id=organization_id,
                        idea_id=idea.id,
                        related_idea_id=duplicate.id,
                        relationship_type=IdeaRelationshipType.RELATED,
                    )
                )
            else:
                created.append(idea)

        self.audit.record(
            organization_id=organization_id,
            actor_type=AuditActorType.SYSTEM,
            action="idea.generation.completed",
            resource_type="channel",
            resource_id=channel_id,
            metadata={
                "proposed": len(output.ideas),
                "created": len(created),
                "deduplicated": duplicate_count,
            },
        )
        return created
