from __future__ import annotations

from app.models.content_cluster import ContentCluster
from app.repositories.base import TenantScopedRepository


class ContentClusterRepository(TenantScopedRepository[ContentCluster]):
    model = ContentCluster
