from typing import Any, Dict, List

from langchain_core.tools import tool

from ..base import Node, NodePosition, NodeVariable
from .node import StartNodeData


@tool
def create_start_node(
    node_id: str,
    x_pos: int,
    y_pos: int,
    variables: List[NodeVariable],
    title: str = "开始",
    desc: str = "",
) -> Dict[str, Any]:
    """为工作流创建一个开始节点。这是整个工作流的入口点。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "start-1")。
        x_pos (int): 节点在画布上的 X 坐标。
        y_pos (int): 节点在画布上的 Y 坐标。
        variables (List[NodeVariable]): 工作流的输入变量列表。
                                       请注意：工作流会默认包含 'sys.query' 作为用户问题输入。
                                       此处传入的 'variables' 是您需要额外添加的自定义变量。
        title (str, optional): 节点的显示标题。默认为 "开始"。
        desc (str, optional): 节点的可选描述。默认为空字符串。

    Returns:
        Dict[str, Any]: 代表该开始节点的字典结构，可用于工作流编排。
    """
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
