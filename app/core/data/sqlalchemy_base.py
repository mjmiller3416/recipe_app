"""app/core/data/sqlalchemy_base.py

Declarative base class for SQLAlchemy ORM models used across MealGenie.
"""

# ── Imports ────────────────────────────────────────────────────────────────
from __future__ import annotations

import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Provides a central metadata registry. Shared columns can be defined here to
    appear on every table that inherits from this class.
    """

    # created_at: Mapped[datetime.datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=func.now()
    # )
    pass
