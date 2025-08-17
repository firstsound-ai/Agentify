from langgraph.graph import END, StateGraph

from biz.agent.blueprint.state import GraphState
from dal.checkpointer import get_checkpointer
from common.utils.get_llm_model import get_llm_model
from typing import Dict, Any
from typing import Literal, Optional
from typing import List, Optional, TypedDict
from biz.agent.blueprint.prompt import CHAT_PROMPT, DECISION_PROMPT, WORKFLOW_REFINE_PROMPT, MERMAID_PROMPT
from pydantic import BaseModel, Field
import json
from settings import settings

# llm = get_llm_model(model_name="gemini-2.5-flash", temperature=0.5)
llm = get_llm_model(model_name="Qwen/Qwen3-30B-A3B-Instruct-2507", temperature=0.5)

chat_chain = CHAT_PROMPT | llm
decision_chain = DECISION_PROMPT | llm
workflow_refine_chain = WORKFLOW_REFINE_PROMPT | llm
mermaid_chain = MERMAID_PROMPT | llm


class MessageState(TypedDict):
    """定义工作流中流动的数据状态。"""
    initial_messages: Optional[str]
    messages: Optional[str]
    workflow: Optional[dict]
    refined_workflow: Optional[dict]
    decision: Optional[Literal["update", "end"]]
    mermaid_code: Optional[str]


def chat_node(state: MessageState):
    messages = chat_chain.invoke({"workflow": state["workflow"], "messages": state["initial_messages"]})
    return {"messages": messages}

def update_workflow_node(state: MessageState):
    response = workflow_refine_chain.invoke({"workflow": state["workflow"], "refine_requirement": state["initial_messages"]})
    assert isinstance(response.content, str)
    workflow = response.content.strip("```json").strip("```")
    workflow = json.loads(workflow)
    print("refined_workflow", workflow)
    return {"refined_workflow": workflow}

def should_continue(state: MessageState):
    return state['decision']

def continue_node(state: MessageState):
    decision = decision_chain.invoke({"messages": state["initial_messages"]})
    """条件函数，决定下一步流向"""
    assert decision.content in ["update", "end"]
    print("decision", decision.content)
    return {"decision": decision.content}

def generate_mermaid_node(state: MessageState):
    print("--- 节点：生成mermaid流程图代码 ---")
    response = mermaid_chain.invoke({"workflow": state["workflow"]})
    print("生成的mermaid", response.content)
    return {"mermaid_code": response.content}


workflow = StateGraph(MessageState)
# 添加节点
workflow.add_node("chat", chat_node)
workflow.add_node("continue", continue_node)
workflow.add_node("update_workflow", update_workflow_node)
workflow.add_node("mermaid", generate_mermaid_node)

workflow.add_edge("chat", "continue")

workflow.add_conditional_edges(
    "continue",
    should_continue,
    {
        "update": "update_workflow",  # 如果继续，更新workflow和mermaid
        "end": END,          # 如果结束，流程终止
    }
)

workflow.add_edge("update_workflow", "mermaid")
# 设置边
workflow.add_edge("mermaid", END)
# 设置入口点
workflow.set_entry_point("chat")

_app = None


def get_chat_workflow():
    global _app
    if _app is None:
        checkpointer = get_checkpointer()
        _app = workflow.compile(
            checkpointer=checkpointer)
    return _app
