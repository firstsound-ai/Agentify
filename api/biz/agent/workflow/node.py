import json

from langchain_core.messages import HumanMessage, ToolMessage

from biz.agent.workflow.dify_nodes import tool_map, tools_list
from biz.agent.workflow.prompt import EXECUTOR_SYSTEM_PROMPT, PLANNER_PROMPT
from biz.agent.workflow.state import AgentState
from common.utils.get_llm_model import get_llm_model

llm = get_llm_model(model_name="gemini-2.5-pro", temperature=0)

def tool_executor_node(state: AgentState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return {}

    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    if tool_name not in tool_map:
        raise ValueError(f"Tool '{tool_name}' not found in the provided tool map.")

    tool_to_call = tool_map[tool_name]
    tool_output = tool_to_call.invoke(tool_args)
    observation = tool_output["observation"]
    tool_message = ToolMessage(content=str(observation), tool_call_id=tool_call["id"])

    new_nodes_created = state["nodes_created"] + [tool_output["node"]]
    new_available_variables = state["available_variables"] + tool_output["output"]

    current_node_title = tool_output["node"]["data"]["title"]
    updated_todo_list = state["todo_list"]
    for task in updated_todo_list:
        if task["nodeTitle"] == current_node_title and task["status"] == "pending":
            task["status"] = "completed"
            break

    return {
        "messages": [tool_message],
        "nodes_created": new_nodes_created,
        "available_variables": new_available_variables,
        "todo_list": updated_todo_list,
    }


def planner_node(state: AgentState):
    tools_summary = "\n".join(
        [f"- {tool.name}: {tool.description}" for tool in tools_list]
    )

    prompt = PLANNER_PROMPT.format(
        tools_summary=tools_summary,
        sop=state["sop"],
        requirement_doc=state["requirement_doc"],
    )
    response = llm.invoke(prompt)
    assert isinstance(response.content, str)
    response = response.content.strip("```json").strip("```")

    todo_list = json.loads(response)

    # 初始化执行代理的第一条消息
    initial_message = HumanMessage(
        content=f"""
任务规划已完成。这是你的待办事项列表，请开始执行。

**Original SOP:**
{state["sop"]}

**To-Do List:**
{todo_list}
"""
    )

    return {"todo_list": todo_list, "messages": [initial_message]}


agent_llm = llm.bind_tools(tools_list)


def agent_node(state: AgentState):
    system_prompt = EXECUTOR_SYSTEM_PROMPT.format(
        available_variables=state["available_variables"]
    )
    messages_with_system_prompt = [HumanMessage(content=system_prompt)] + state[
        "messages"
    ]

    response = agent_llm.invoke(messages_with_system_prompt)
    print(response)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "call_tool"
    if all(task["status"] == "completed" for task in state["todo_list"]):
        return "end"
    else:
        return "continue"
