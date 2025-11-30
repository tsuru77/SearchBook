"""Database connection and utilities for PostgreSQL."""

import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from typing import Generator, Any

from app.core.config import settings


def get_db_connection():
    """Get a PostgreSQL database connection."""
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


@contextmanager
def get_db_cursor(commit: bool = False) -> Generator:
    """Context manager for database cursor."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        yield cursor
        if commit:
            conn.commit()
    finally:
        cursor.close()
        conn.close()


def execute_query(query: str, params: tuple = (), commit: bool = False) -> Any:
    """Execute a single query."""
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params)
        if commit:
            return cursor.rowcount
        return cursor.fetchall()


def execute_query_one(query: str, params: tuple = ()) -> Any:
    """Execute a query and return a single row."""
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()


def execute_query_all(query: str, params: tuple = ()) -> list:
    """Execute a query and return all rows."""
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()
