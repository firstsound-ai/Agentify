"""
依赖注入容器

这个模块实现了一个简单的依赖注入容器，用于管理应用中的全局组件。
主要管理LangGraph应用实例、Checkpointer等核心组件。
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from settings import settings


class Container:
    """依赖注入容器"""

    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._checkpointer: Optional[AsyncPostgresSaver] = None
        self._langgraph_app = None

    async def get_checkpointer(self) -> AsyncPostgresSaver:
        """获取或创建PostgreSQL checkpointer实例"""
        if self._checkpointer is None:
            self._checkpointer = AsyncPostgresSaver(
                conn=AsyncConnectionPool(
                    conninfo=settings.DATABASE_URL,
                )
            )
            await self._checkpointer.setup()
        return self._checkpointer

    async def get_langgraph_app(self):
        """获取或创建LangGraph应用实例"""
        if self._langgraph_app is None:
            # 延迟导入避免循环依赖
            from biz.agent.requirement.graph import create_requirement_graph

            checkpointer = await self.get_checkpointer()
            self._langgraph_app = create_requirement_graph(checkpointer)
        return self._langgraph_app

    def register(self, name: str, instance: Any):
        """注册实例到容器"""
        self._instances[name] = instance

    def get(self, name: str) -> Any:
        """从容器获取实例"""
        return self._instances.get(name)

    async def cleanup(self):
        """清理资源"""
        if self._checkpointer:
            # 关闭连接池
            if hasattr(self._checkpointer, "conn"):
                await self._checkpointer.conn.close()
            self._checkpointer = None
        self._langgraph_app = None


# 全局容器实例
_container: Optional[Container] = None


def get_container() -> Container:
    """获取全局容器实例"""
    global _container
    if _container is None:
        _container = Container()
    return _container


@asynccontextmanager
async def container_lifespan():
    """容器生命周期管理"""
    container = get_container()
    try:
        yield container
    finally:
        await container.cleanup()
