""" database/base_model.py

Base model for CRUD operations with SQLite and Pydantic.
"""

# ── Imports ─────────────────────────────────────────────────────────────────────
import re
import sqlite3
from typing import Any, List, Optional, Type, TypeVar, Tuple

from pydantic import BaseModel as PydanticBaseModel

from .db import get_connection

# ── Type Variables ─────────────────────────────────────────────────────────────
T = TypeVar("T", bound="ModelBase")

# ── Model Base Class ───────────────────────────────────────────────────────────
class ModelBase(PydanticBaseModel):
    """Base class providing generic CRUD operations for Pydantic models."""

    id: Optional[int] = None

    @classmethod
    def table_name(cls) -> str:
        # CamelCase → snake_case
        snake = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        if snake.endswith("y"):
            return snake[:-1] + "ies"
        return snake + "s"

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        """Fetch all records from the table."""
        return cls.raw_query(f"SELECT * FROM {cls.table_name()}")

    @classmethod
    def get(cls: Type[T], id: int) -> Optional[T]:
        """ Fetch a record by its ID. """
        results = cls.raw_query(
            f"SELECT * FROM {cls.table_name()} WHERE id = ?", (id,)
        )
        return results[0] if results else None

    @classmethod
    def raw_query(
        cls: Type[T],
        sql: str,
        params: Tuple[Any, ...] = (),
        connection: Optional[sqlite3.Connection] = None
    ) -> List[T]:
        """
        Execute raw SQL and return model instances.
        
        Args:
            sql (str): The SQL query to execute.
            params (Tuple[Any, ...]): Parameters for the SQL query.
            connection (Optional[sqlite3.Connection]): Optional database connection.
        Returns:
            List[T]: List of model instances matching the query.
        """
        def _run(conn: sqlite3.Connection) -> List[T]:
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            return [cls.model_validate(dict(row)) for row in rows]

        if connection:
            return _run(connection)
        with get_connection() as conn:
            return _run(conn)

    @classmethod
    def update(
        cls: Type[T],
        id: int,
        *,
        connection: Optional[sqlite3.Connection] = None,
        **fields: Any
    ) -> Optional[T]:
        """
        Shortcut to patch specific columns on a record.
        
        Args:
            id (int): The ID of the record to update.
            connection (Optional[sqlite3.Connection]): Optional database connection.
            **fields: Column-value pairs to update.
        Returns:
            Optional[T]: The updated model instance, or None if not found.
        """
        instance = cls.get(id)
        if not instance:
            return None
        for k, v in fields.items():
            setattr(instance, k, v)
        return instance.save(connection=connection)

    @classmethod
    def exists(cls, **fields: Any) -> bool:
        """
        Check if a record exists with the given field-value pairs.

        Args:
            **fields: Column-value pairs to check for existence.
        Returns:
            bool: True if a matching record exists, False otherwise.
        """
        cols = " AND ".join(f"{k}=?" for k in fields)
        vals = tuple(fields.values())
        sql = f"SELECT 1 FROM {cls.table_name()} WHERE {cols} LIMIT 1"
        with get_connection() as conn:
            row = conn.execute(sql, vals).fetchone()
        return bool(row)

    def save(self, connection: Optional[sqlite3.Connection] = None) -> T:
        """Insert or replace this model into the database."""
        data = self.model_dump(exclude_none=True)
        cols, vals = zip(*data.items())
        placeholders = ", ".join("?" for _ in cols)
        sql = (
            f"INSERT OR REPLACE INTO {self.table_name()} "
            f"({', '.join(cols)}) VALUES ({placeholders})"
        )

        def _run(conn: sqlite3.Connection) -> T:
            cursor = conn.execute(sql, tuple(vals))
            if self.id is None:
                self.id = cursor.lastrowid
            return self

        if connection:
            return _run(connection)
        with get_connection() as conn:
            return _run(conn)

    def delete(self, connection: Optional[sqlite3.Connection] = None) -> None:
        """Delete this model's record from the database."""
        if self.id is None:
            raise ValueError("Cannot delete unsaved record")
        sql = f"DELETE FROM {self.table_name()} WHERE id = ?"

        def _run(conn: sqlite3.Connection) -> None:
            conn.execute(sql, (self.id,))

        if connection:
            _run(connection)
        else:
            with get_connection() as conn:
                _run(conn)

    @classmethod
    def first(cls: Type[T], **filters: Any) -> Optional[T]:
        """Return the first matching row (or None)."""
        results = cls.filter(**filters)
        return results[0] if results else None

    @classmethod
    def filter(cls: Type[T], **filters: Any) -> List[T]:
        """
        SQL‐powered filter: only returns rows where each column == value.

        Args:
            **filters: Column-value pairs to filter by.
        Returns:
            List[T]: List of model instances matching the filters.
        """
        if not filters:
            return cls.all()

        # build WHERE clause: "col1 = ? AND col2 = ?"
        cols = " AND ".join(f"{k}=?" for k in filters)
        sql = f"SELECT * FROM {cls.table_name()} WHERE {cols}"
        params = tuple(filters.values())
        return cls.raw_query(sql, params)

    @classmethod
    def get_by_field(cls: Type[T], **fields: Any) -> Optional[T]:
        """Return a single row matching the given field-value pairs."""
        return cls.first(**fields)
    
    @classmethod
    def join_query(
        cls: Type[T],
        join_clause: str,
        where_clause: str = "",
        params: Tuple[Any, ...] = ()
    ) -> List[T]:
        """
        Execute a JOIN query and return model instances.
        
        Args:
            join_clause (str): The JOIN clause to use in the SQL query.
            where_clause (str): Optional WHERE clause to filter results.
            params (Tuple[Any, ...]): Parameters for the SQL query.
        Returns:
            List[T]: List of model instances matching the query.
        """
        base_sql = f"SELECT {cls.table_name()}.* FROM {cls.table_name()} {join_clause}"
        if where_clause:
            base_sql += f" WHERE {where_clause}"
        return cls.raw_query(base_sql, params)