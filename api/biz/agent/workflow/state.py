from typing import Annotated, Dict, List, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    requirement_doc: Dict
    sop: Dict
    todo_list: List[
        Dict
    ]  # 格式: [{"nodeId": "node-001", "nodeTitle": "...", "status": "pending"}]

    # 执行阶段的追踪
    nodes_created: List[Dict]
    available_variables: List[str]
    messages: Annotated[list, add_messages]
