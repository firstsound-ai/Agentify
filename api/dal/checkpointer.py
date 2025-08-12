from typing import Optional

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

from settings import settings

_checkpointer: Optional[AsyncPostgresSaver] = None
_pool: Optional[AsyncConnectionPool[AsyncConnection[DictRow]]] = None


async def init_checkpointer():
    """Initializes the connection pool and checkpointer."""
    global _pool, _checkpointer
    _pool = AsyncConnectionPool(
        conninfo=settings.DATABASE_URL,
        open=False,
    )
    await _pool.open()
    _checkpointer = AsyncPostgresSaver(conn=_pool)


async def close_checkpointer():
    """Closes the connection pool."""
    if _pool:
        await _pool.close()


async def get_checkpointer() -> AsyncPostgresSaver:
    if _checkpointer is None:
        raise RuntimeError("Checkpointer has not been initialized.")
    return _checkpointer
