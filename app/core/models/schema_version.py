# ── Imports ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.core.data.base_model import ModelBase
from pydantic import Field


# ── Class Definition ────────────────────────────────────────────────────────────
class SchemaVersion(ModelBase):
    """
    Tracks which SQL migrations have been applied.
    """
    id: Optional[int] = None
    version: str = Field(
        ...,
        min_length=1,
        description="Identifier of the applied migration (e.g. '001_initial')"
    )
    applied_on: datetime = Field(
        default_factory=datetime.now,
        description="When this migration was applied"
    )
