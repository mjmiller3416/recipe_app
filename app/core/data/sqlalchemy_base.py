"""app/core/data/sqlalchemy_base.py

Declarative base class for all SQLAlchemy ORM models.

This allows models across the application to share the same metadata.
A timestamp mixin may be added here in the future.
"""

# ── Imports ──────────────────────────────────────────────────────────────
from __future__ import annotations

# from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    # 🔹 Shared timestamp columns (uncomment if needed)
    # created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
    # updated_at: Mapped[datetime] = mapped_column(
    #     default_factory=datetime.utcnow,
    #     onupdate=datetime.utcnow,
    # )

