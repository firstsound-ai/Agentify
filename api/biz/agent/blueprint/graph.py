from langgraph.graph import END, StateGraph

from biz.agent.blueprint.node import (
    generate_workflow_node,
    generate_mermaid_node
)

from biz.agent.blueprint.state import GraphState
from dal.checkpointer import get_checkpointer

workflow = StateGraph(GraphState)

workflow.add_node("workflow_generator", generate_workflow_node)
workflow.add_node("mermaid_generator", generate_mermaid_node)

workflow.set_entry_point("workflow_generator")

workflow.add_edge("workflow_generator", "mermaid_generator")
workflow.add_edge("mermaid_generator", END)

_app = None


def get_blueprint_workflow():
    global _app
    if _app is None:
        checkpointer = get_checkpointer()
        _app = workflow.compile(checkpointer=checkpointer)
    return _app
