"""Enumeration for predefined dashboard widget sizes."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True)
class Size:
    rows: int
    cols: int


class WidgetSize(Enum):
    """Valid widget sizes in grid cells."""

    SIZE_1x1 = Size(1, 1)
    SIZE_1x2 = Size(1, 2)
    SIZE_2x1 = Size(2, 1)
    SIZE_2x2 = Size(2, 2)
    SIZE_3x1 = Size(3, 1)
    SIZE_4x3 = Size(4, 3)

    @property
    def rows(self) -> int:
        return self.value.rows

    @property
    def cols(self) -> int:
        return self.value.cols
