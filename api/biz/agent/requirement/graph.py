from langgraph.graph import END, StateGraph

from biz.agent.requirement.node import (
    finalize_document_node,
    generate_draft_node,
    generate_questions_node,
    user_answers_node,
)
from biz.agent.requirement.state import GraphState
from dal.checkpointer import get_checkpointer

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


def get_workflow_app():
    checkpointer = get_checkpointer()
    return workflow.compile(checkpointer=checkpointer)
