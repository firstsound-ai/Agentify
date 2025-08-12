from typing import Optional

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from settings import settings

# 全局checkpointer实例，用于缓存
_checkpointer: Optional[AsyncPostgresSaver] = None


async def get_checkpointer() -> AsyncPostgresSaver:
    """
    FastAPI依赖注入函数：获取PostgreSQL checkpointer实例
    这个函数会被FastAPI的Depends()使用
    """
    global _checkpointer

    if _checkpointer is None:
        _checkpointer = AsyncPostgresSaver(
            conn=AsyncConnectionPool(
                conninfo=settings.DATABASE_URL,
            )
        )
        await _checkpointer.setup()

    return _checkpointer


async def cleanup_checkpointer():
    """清理checkpointer资源"""
    global _checkpointer
    if _checkpointer and hasattr(_checkpointer, "conn"):
        await _checkpointer.conn.close()
    _checkpointer = None
