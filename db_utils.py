# db_utils.py
import os
import asyncpg
from typing import Optional, Dict, Any

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/dbname")

async def fetch_user_context_from_postgres(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Example fetch: assumes table user_contexts(user_id text primary key, ctx jsonb).
    Returns Python dict or None.
    """
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        row = await conn.fetchrow("SELECT ctx FROM user_contexts WHERE user_id = $1", user_id)
        if row:
            return row["ctx"]
        return None
    finally:
        await conn.close()
