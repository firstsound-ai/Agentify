from typing import Optional

from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from psycopg.rows import DictRow
from psycopg_pool import ConnectionPool

from settings import settings

_checkpointer: Optional[PostgresSaver] = None
_pool: Optional[ConnectionPool[Connection[DictRow]]] = None


def init_checkpointer():
    global _pool, _checkpointer
    _pool = ConnectionPool(
        conninfo=settings.DATABASE_URL,
        max_size=20,
        kwargs={"row_factory": DictRow, "autocommit": True},
        open=True,
    )
    _checkpointer = PostgresSaver(conn=_pool)
    _checkpointer.setup()


def close_checkpointer():
    if _pool:
        _pool.close()


def get_checkpointer() -> PostgresSaver:
    if _checkpointer is None:
        raise RuntimeError("checkpointer未初始化")
    return _checkpointer
