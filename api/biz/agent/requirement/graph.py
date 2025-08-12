from typing import Optional

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, StateGraph

from biz.agent.requirement.node import (
    finalize_document_node,
    generate_draft_node,
    generate_questions_node,
    user_answers_node,
)
from biz.agent.requirement.state import GraphState

# 全局应用实例缓存
_app = None


def create_requirement_graph(checkpointer: Optional[AsyncPostgresSaver] = None):
    """
    创建需求处理的LangGraph应用

    Args:
        checkpointer: PostgreSQL checkpointer实例

    Returns:
        编译后的LangGraph应用
    """
    workflow = StateGraph(GraphState)

    # 添加所有节点
    workflow.add_node("draft_generator", generate_draft_node)
    workflow.add_node("question_generator", generate_questions_node)
    workflow.add_node("user_answers_handler", user_answers_node)
    workflow.add_node("document_finalizer", finalize_document_node)

    # 设置入口点
    workflow.set_entry_point("draft_generator")

    # 添加边：定义工作流程
    workflow.add_edge("draft_generator", "question_generator")
    workflow.add_edge("question_generator", "user_answers_handler")
    workflow.add_edge("user_answers_handler", "document_finalizer")
    workflow.add_edge("document_finalizer", END)

    # 编译图，使用传入的checkpointer
    return workflow.compile(checkpointer=checkpointer)


async def get_requirement_app(checkpointer: AsyncPostgresSaver):
    """
    FastAPI依赖注入函数：获取LangGraph应用实例

    Args:
        checkpointer: 由FastAPI注入的checkpointer实例

    Returns:
        编译后的LangGraph应用
    """
    global _app

    # 缓存应用实例，避免重复创建
    if _app is None:
        _app = create_requirement_graph(checkpointer)

    return _app
