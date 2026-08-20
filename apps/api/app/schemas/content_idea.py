from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import IdeaOrigin, IdeaStatus


class ContentIdeaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel_id: uuid.UUID
    title: str
    summary: str | None
    recommended_format: str | None
    idea_type: str | None
    origin: IdeaOrigin
    status: IdeaStatus
    created_at: datetime
    # From the idea's latest ContentOpportunity, if it has been evaluated
    # yet (Documento 10 F09 UI: score/title/summary/format/reason cards).
    opportunity_score: float | None = None
    reasoning_summary: str | None = None
