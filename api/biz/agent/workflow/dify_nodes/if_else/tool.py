from typing import Any, Dict, List

from langchain_core.tools import tool

from ..base import Node, NodePosition, parse_variable
from .node import IfElseNodeData
from .type import IfElseCase, IfElseCondition


@tool
def create_if_else_node(
    node_id: str,
    x_pos: int,
    y_pos: int,
    cases: List[Dict[str, Any]],
    title: str = "条件分支",
    desc: str = "根据条件判断，将工作流引导至不同分支。",
) -> Dict[str, Any]:
    """
    在工作流中创建一个条件分支（If/Else）节点。
    当需要根据不同条件执行不同逻辑路径时使用此工具。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "if_else_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        cases (List[Dict[str, Any]]): 条件分支的配置列表。每个字典代表一个case（即一个if或else if分支）。
            - 每个case可以包含一个或多个`conditions`。
            - `logical_operator` ('and' 或 'or') 定义了case内多个`conditions`之间的关系。
            - 每个`condition`定义了一个具体的比较逻辑。
            - `variable` 现在应该是一个字符串，例如 '{{#sys.query#}}'。
            - `comparison_operator` 支持 'contains', 'not contains', 'start with', 'end with', 'is', 'is not', 'empty', 'not empty'。

            示例:
            [
                {
                    "id": "is_about_weather",
                    "logical_operator": "or",
                    "conditions": [
                        {"variable": "{{#sys.query#}}", "comparison_operator": "contains", "value": "天气"},
                        {"variable": "{{#sys.query#}}", "comparison_operator": "contains", "value": "几度"}
                    ]
                },
                {
                    "id": "is_empty_query",
                    "logical_operator": "and",
                    "conditions": [
                        {"variable": "{{#sys.query#}}", "comparison_operator": "empty", "value": ""}
                    ]
                }
            ]
        title (str, optional): 节点的显示标题。默认为 "条件分支"。
        desc (str, optional): 节点的可选描述信息。

    Returns:
        Dict[str, Any]: 代表该If/Else节点的字典结构。
    """
    if_else_cases = []
    for case_data in cases:
        conditions = []
        for i, cond in enumerate(case_data.get("conditions", [])):
            # 解析 variable 字符串
            selector_list = parse_variable(cond.get("variable", ""))

            conditions.append(
                IfElseCondition(
                    id=f"cond_{i}",
                    variable_selector=selector_list,
                    comparison_operator=cond.get("comparison_operator", "is"),
                    value=cond.get("value", ""),
                    varType=cond.get("varType", "string"),
                )
            )

        case_id = case_data.get("id", f"case_{len(if_else_cases)}")
        if_else_cases.append(
            IfElseCase(
                id=case_id,
                case_id=case_id,
                logical_operator=case_data.get("logical_operator", "and"),
                conditions=conditions,
            )
        )

    if_else_node_data = IfElseNodeData(
        title=title,
        desc=desc,
        cases=if_else_cases,
    )

    if_else_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=if_else_node_data,
        width=244,
        height=150,
    )

    return {
        "node": if_else_node.to_dict(),
        "observation": f"已经创建了一个名为'{title}'的条件分支节点。",
        "output": [],
    }
