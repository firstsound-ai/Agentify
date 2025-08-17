from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from ..base import Node, NodePosition, parse_variable
from .node import VariableAggregatorNodeData
from .type import VariableReference


@tool
def create_variable_aggregator_node(
    node_id: str,
    x_pos: int,
    y_pos: int,
    variables: Optional[List[Dict[str, Any]]] = None,
    output_type: str = "string",
    title: str = "变量聚合器",
    desc: str = "将多路分支的变量聚合为一个变量",
) -> Dict[str, Any]:
    """
    在工作流中创建一个变量聚合器节点。
    当需要将多个分支的输出结果聚合为一个统一的变量时使用此工具，
    确保下游节点可以通过统一的变量引用来访问不同分支的结果。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "aggregator_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        variables (List[Dict[str, Any]], optional): 要聚合的变量列表。每个变量包含:
            - variable: 变量名称，用于标识聚合后的变量
            - value: 变量引用字符串，例如 "{{#llm_node_1.text#}}" 或 "{{#previous_node.result#}}"
            - value_type: 值类型，支持 "string", "number", "object", "array[string]", "array[number]", "array[object]"
            示例: [{"variable": "llm1_output", "value": "{{#llm_node_1.text#}}", "value_type": "string"}]
        output_type (str, optional): 聚合后的输出类型。支持 "string", "number", "object", "array", etc。默认为 "string"。
        title (str, optional): 节点的显示标题。默认为 "变量聚合器"。
        desc (str, optional): 节点的可选描述信息。默认为 "将多路分支的变量聚合为一个变量"。

    Returns:
        Dict[str, Any]: 代表该变量聚合器节点的字典结构，可用于工作流编排。
    """
    if variables is None:
        variables = []

    # 转换变量引用
    variable_references = []
    for var in variables:
        value = var.get("value", "")
        # 统一使用parse_variable解析字符串格式的变量引用
        value_selector = parse_variable(value)

        variable_references.append(
            VariableReference(
                variable=var.get("variable", ""),
                value_selector=value_selector,
                value_type=var.get("value_type", "string"),
            )
        )

    aggregator_node_data = VariableAggregatorNodeData(
        title=title,
        desc=desc,
        variable_references=variable_references,
        output_type=output_type,
    )

    aggregator_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=aggregator_node_data,
        width=244,
        height=131,
    )

    return {
        "node": aggregator_node.to_dict(),
        "observation": f"已经创建了一个名为{title}的变量聚合器节点。该节点将聚合{len(variable_references)}个变量，输出类型为{output_type}。",
        "output": aggregator_node.get_output_variable_references(),
    }
