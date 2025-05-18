""" database/base_model.py

Base model for CRUD operations with SQLite and Pydantic. 
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import re
from typing import List, Optional, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel

from .db import get_connection

# ── Constants ───────────────────────────────────────────────────────────────────
T = TypeVar("T", bound="ModelBase")

# ── Classes ─────────────────────────────────────────────────────────────────────
class ModelBase(PydanticBaseModel):
    """ Base class providing generic CRUD operations for Pydantic models. """
    id: Optional[int] = None

# ── Public Methods ──────────────────────────────────────────────────────────────
    @classmethod
    def table_name(cls) -> str:
        # CamelCase → snake_case
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        # if it ends in 'y', drop it and add 'ies'
        if snake.endswith("y"):
            return snake[:-1] + "ies"
        # otherwise just add a simple 's'
        return snake + "s"

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        """ Fetch all records from the table. """
        with get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM {cls.table_name()}").fetchall() 
        
        return [cls.model_validate(dict(row)) for row in rows] 

    @classmethod
    def get(cls: Type[T], id: int) -> Optional[T]:
        """ Fetch a record by its ID. """
        with get_connection() as conn:
            row = conn.execute(
                f"SELECT * FROM {cls.table_name()} WHERE id = ?", (id,)
            ).fetchone()

        return cls.model_validate(dict(row)) if row else None

    @classmethod
    def update(cls: Type[T], id: int, **fields) -> Optional[T]:
        """ Shortcut to patch specific columns on a record. """
        instance = cls.get(id)
        if not instance:
            return None
        for k, v in fields.items():
            setattr(instance, k, v)

        return instance.save()

    @classmethod
    def exists(cls, **fields) -> bool:
        """ 
        Quickly checks if a record matching the given field values exists.
        Usage: Recipe.exists(recipe_name="Pancakes", servings=4)
        """
        cols = " AND ".join(f"{k}=?" for k in fields)
        vals = tuple(fields.values())

        with get_connection() as conn:
            row = conn.execute( 
                f"SELECT 1 FROM {cls.table_name()} WHERE {cols} LIMIT 1",
                vals
            ).fetchone() 

        return bool(row) 

    def save(self) -> "ModelBase":
        """ Save the current instance to the database. """
        data = self.model_dump(exclude_none=True)
        cols, vals = zip(*data.items())
        placeholders = ", ".join("?" for _ in cols)

        with get_connection() as conn:
            result = conn.execute(
                f"INSERT OR REPLACE INTO {self.table_name()} ({', '.join(cols)}) "
                f"VALUES ({placeholders})",
                tuple(vals),
            )
            # context manager will commit on success
            if self.id is None:
                self.id = result.lastrowid

        return self

    def delete(self):
        """ Delete the current instance from the database. """
        if self.id is None:
            raise ValueError("Cannot delete unsaved record")
        
        with get_connection() as conn:
            conn.execute(
                f"DELETE FROM {self.table_name()} WHERE id = ?", (self.id,)
            )

    @classmethod
    def first(cls, **filters):
        """Return the first matching row (or None)."""
        results = cls.filter(**filters)
        return results[0] if results else None
    
    @classmethod
    def filter(cls, **filters):
        """
        Return a list of rows matching the given filters.

        Args:
            **filters: Field-value pairs to match exactly.

        Returns:
            list[cls]: Matching model instances.
        """
        results = []
        for row in cls.all():
            if all(getattr(row, k, None) == v for k, v in filters.items()):
                results.append(row)
        return results