from __future__ import annotations

import re
import uuid

_SLUG_INVALID_CHARS = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    slug = _SLUG_INVALID_CHARS.sub("-", value.strip().lower()).strip("-")
    return slug or "org"


def unique_suffix() -> str:
    return uuid.uuid4().hex[:6]
