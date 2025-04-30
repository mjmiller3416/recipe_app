from typing import Type, TypeVar, List, Optional
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
        # Derive table name from class name, e.g. Recipe -> recipes
        return cls.__name__.lower() + "s"

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
