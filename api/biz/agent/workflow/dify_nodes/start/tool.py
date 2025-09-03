from typing import Annotated, Any, Dict, List

from langchain_core.tools import tool

from ..base import Node, NodePosition, NodeVariable
from .node import StartNodeData


@tool
def create_start_node(
    node_id: Annotated[str, "节点的唯一标识符 (例如: 'start-1')。"],
    x_pos: Annotated[int, "节点在画布上的X坐标。"],
    y_pos: Annotated[int, "节点在画布上的Y坐标。"],
    variables: Annotated[
        List[NodeVariable],
        "工作流的输入变量列表。请注意：工作流会默认包含 'sys.query' 作为用户问题输入。此处传入的 'variables' 是您需要额外添加的自定义变量。",
    ] = [],
    title: Annotated[str, "节点的显示标题。默认为 '开始'。"] = "开始",
    desc: Annotated[str, "节点的可选描述信息。"] = "",
) -> Dict[str, Any]:
    """为工作流创建一个开始节点。这是整个工作流的入口点。"""
    start_node_data = StartNodeData(title=title, desc=desc, variables=variables)
    start_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=start_node_data,
        width=244,
        height=140,
    )
    return {
        "node": start_node.to_dict(),
        "observation": f"已经创建了一个名为{title}的输出节点。",
        "output": start_node.get_output_variable_references(),
    }
