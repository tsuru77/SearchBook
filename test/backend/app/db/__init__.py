"""
Module pour la gestion de la connexion PostgreSQL avec pool.
"""
import psycopg2
from psycopg2 import pool
import os
from contextlib import contextmanager

# Configuration
DB_DSN = os.environ.get(
    "DB_DSN",
    "postgresql://searchbook:searchbookpass@localhost:5432/searchbook"
)

# Pool de connexions
_connection_pool = None

def initialize_pool(minconn=2, maxconn=20):
    """Initialise le pool de connexions PostgreSQL."""
    global _connection_pool
    _connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn, maxconn, DB_DSN
    )

def close_pool():
    """Ferme le pool de connexions."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()

@contextmanager
def get_db_connection():
    """Context manager pour obtenir une connexion du pool."""
    if _connection_pool is None:
        initialize_pool()
    
    conn = _connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _connection_pool.putconn(conn)

@contextmanager
def get_db_cursor():
    """Context manager pour obtenir un curseur avec connection du pool."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
