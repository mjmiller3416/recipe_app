# database/models/schema_version.py

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from database.base_model import ModelBase


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
