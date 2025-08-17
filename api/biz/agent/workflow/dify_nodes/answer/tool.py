from typing import Any, Dict

from langchain_core.tools import tool

from ..base import Node, NodePosition
from .node import AnswerNodeData


@tool
def create_answer_node(
    node_id: str,
    x_pos: int,
    y_pos: int,
    answer_content: str,
    title: str = "直接回复",
    desc: str = "",
) -> Dict[str, Any]:
    """
    创建一个回答节点，用于直接回复用户。
    当工作流有最终输出需要呈现给用户时使用此功能。

    Args:
        node_id (str): 此节点的唯一标识符（例如，“final_answer”）。
        x_pos (int): 节点位置的 X 坐标。
        y_pos (int): 节点位置的 Y 坐标。
        answer_content (str): 回答的内容。可以使用类似 '{{#llm_node_id.text#}}' 的变量来引用其他节点的结果。此外，如果有必要的话，你也可以结合多个变量和自定义文本来构建复杂内容，例如："来自第一个节点的结果是：{{#node1.text#}}。第二个节点的结果是：{{#node2.text#}}。"
        title (str): Answer 节点的显示标题。默认为“直接回复”。
        desc (str): 节点的可选描述。

    Returns:
        Dict[str, Any]: 代表该开始节点的字典结构，可用于工作流编排。
    """
    answer_node_data = AnswerNodeData(title=title, desc=desc, answer=answer_content)
    answer_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=answer_node_data,
        width=244,
        height=105,
    )
    return {
        "node": answer_node.to_dict(),
        "observation": f"已经创建了一个名为{title}的输出节点。当前节点会输出{answer_content}",
        "output": answer_node.get_output_variable_references(),
    }
