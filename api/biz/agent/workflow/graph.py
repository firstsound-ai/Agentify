from langgraph.graph import END, StateGraph

from biz.agent.workflow.node import (
    agent_node,
    planner_node,
    should_continue,
    tool_executor_node,
)
from biz.agent.workflow.state import AgentState
from dal.checkpointer import get_checkpointer

workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("agent", agent_node)
workflow.add_node("tool_executor", tool_executor_node)
workflow.set_entry_point("planner")
workflow.add_edge("planner", "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "call_tool": "tool_executor",
        "end": END,
        "continue": "agent",
    },
)
workflow.add_edge("tool_executor", "agent")


_app = None


def get_workflow_agent():
    global _app
    if _app is None:
        # checkpointer = get_checkpointer()
        # _app = workflow.compile(checkpointer=checkpointer)
        _app = workflow.compile()
    return _app
