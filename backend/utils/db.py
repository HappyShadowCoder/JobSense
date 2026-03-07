"""
utils/db.py — PostgreSQL connection pool using psycopg2
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

# Connection pool — reuses connections instead of opening a new one per request
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=os.getenv("DATABASE_URL")
        )
    return _pool


def get_db():
    """
    Get a connection from the pool.
    Usage:
        conn = get_db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
            conn.commit()
        finally:
            release_db(conn)
    """
    return get_pool().getconn()


def release_db(conn):
    """Return connection to pool."""
    get_pool().putconn(conn)


def query_one(sql: str, params: tuple = ()):
    """Execute a SELECT and return a single row as dict, or None."""
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchone()
    finally:
        release_db(conn)


def query_all(sql: str, params: tuple = ()):
    """Execute a SELECT and return all rows as list of dicts."""
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        release_db(conn)


def execute(sql: str, params: tuple = (), returning: bool = False):
    """
    Execute INSERT / UPDATE / DELETE.
    If returning=True, returns the first row (useful for RETURNING id).
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            result = cur.fetchone() if returning else None
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        release_db(conn)
