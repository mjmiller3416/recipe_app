import re
from typing import List, Optional, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel

from .db import get_connection

T = TypeVar("T", bound="ModelBase")

class ModelBase(PydanticBaseModel):
    """
    Base class providing generic CRUD operations for Pydantic models.
    """
    id: Optional[int] = None

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
        conn = get_connection()
        rows = conn.execute(f"SELECT * FROM {cls.table_name()}").fetchall()
        # Use Pydantic v2 model_validate method for parsing
        return [cls.model_validate(dict(row)) for row in rows]

    @classmethod
    def get(cls: Type[T], id: int) -> Optional[T]:
        conn = get_connection()
        row = conn.execute(
            f"SELECT * FROM {cls.table_name()} WHERE id = ?", (id,)
        ).fetchone()
        return cls.model_validate(dict(row)) if row else None

    @classmethod
    def update(cls: Type[T], id: int, **fields) -> Optional[T]:
        """
        Shortcut to patch specific columns on a record.
        Example: Recipe.update(1, servings=8, total_time=30)
        """
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
        conn = get_connection()
        cols = " AND ".join(f"{k}=?" for k in fields)
        vals = tuple(fields.values())
        row = conn.execute(
            f"SELECT 1 FROM {cls.table_name()} WHERE {cols} LIMIT 1",
            vals
        ).fetchone()
        return bool(row)

    def save(self) -> "ModelBase":
        # Use model_dump for Pydantic v2 serialization
        data = self.model_dump(exclude_none=True)
        cols, vals = zip(*data.items())
        placeholders = ", ".join("?" for _ in cols)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT OR REPLACE INTO {self.table_name()} ({', '.join(cols)}) "
            f"VALUES ({placeholders})",
            tuple(vals),
        )
        conn.commit()
        if self.id is None:
            self.id = cursor.lastrowid
        return self

    def delete(self):
        if self.id is None:
            raise ValueError("Cannot delete unsaved record")
        conn = get_connection()
        conn.execute(
            f"DELETE FROM {self.table_name()} WHERE id = ?", (self.id,)
        )
        conn.commit()
