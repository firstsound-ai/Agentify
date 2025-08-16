from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from ..base import Node, NodePosition, parse_variable
from .node import LoopNodeData
from .type import LoopCondition, LoopStartNodeData, LoopVariable


@tool
def create_loop_node(
    node_id: str,
    x_pos: int,
    y_pos: int,
    loop_variables: List[Dict[str, Any]],
    break_conditions: Optional[List[Dict[str, Any]]] = None,
    loop_count: int = 10,
    logical_operator: str = "or",
    error_handle_mode: str = "terminated",
    title: str = "循环",
    desc: str = "执行循环操作，可以设置循环变量和跳出条件。",
) -> Dict[str, Any]:
    """
    在工作流中创建一个循环节点。
    用于需要重复执行一组操作的场景，支持设置循环变量和跳出条件。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "loop_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        loop_variables (List[Dict[str, Any]]): 循环变量配置列表。每个字典代表一个循环变量。
            - `id` (str): 变量的唯一标识符
            - `label` (str): 变量名称
            - `var_type` (str): 变量类型，如 "string", "number", "boolean"
            - `value_type` (str): 值类型，"constant" 表示常量，"variable" 表示引用其他变量
            - `value` (str | List[str]): 如果是常量，直接是值；如果是变量，是变量选择器字符串如 "{{#sys.query#}}"

            示例:
            [
                {
                    "id": "var1",
                    "label": "counter",
                    "var_type": "number",
                    "value_type": "constant",
                    "value": 0
                },
                {
                    "id": "var2",
                    "label": "user_input",
                    "var_type": "string",
                    "value_type": "variable",
                    "value": "{{#sys.query#}}"
                }
            ]
        break_conditions (List[Dict[str, Any]], optional): 循环跳出条件列表。
            - `id` (str): 条件的唯一标识符
            - `varType` (str): 变量类型，如 "string", "number"
            - `variable` (str): 变量选择器字符串，如 "{{#loop_1.counter#}}"
            - `comparison_operator` (str): 比较操作符，支持 'contains', 'not contains', 'start with', 'end with', 'is', 'is not', 'empty', 'not empty'
            - `value` (Any): 比较的值

            示例:
            [
                {
                    "id": "cond1",
                    "varType": "number",
                    "variable": "{{#loop_1.counter#}}",
                    "comparison_operator": "is",
                    "value": 100
                }
            ]
        loop_count (int, optional): 最大循环次数，默认为 10。
        logical_operator (str, optional): 多个跳出条件之间的逻辑关系，"and" 或 "or"，默认为 "or"。
        error_handle_mode (str, optional): 错误处理模式，"terminated" 或 "continue"，默认为 "terminated"。
        title (str, optional): 节点的显示标题，默认为 "循环"。
        desc (str, optional): 节点的可选描述信息。

    Returns:
        Dict[str, Any]: 代表该循环节点的字典结构。
    """
    # 处理循环变量
    processed_loop_variables = []
    for var_data in loop_variables:
        var_value = var_data.get("value", "")

        # 如果是变量类型，需要解析变量选择器
        if var_data.get("value_type") == "variable" and isinstance(var_value, str):
            var_value = parse_variable(var_value)

        processed_loop_variables.append(
            LoopVariable(
                id=var_data.get("id", ""),
                label=var_data.get("label", ""),
                var_type=var_data.get("var_type", "string"),
                value_type=var_data.get("value_type", "constant"),
                value=var_value,
            )
        )

    # 处理跳出条件
    processed_break_conditions = []
    if break_conditions:
        for i, cond_data in enumerate(break_conditions):
            # 解析变量选择器
            variable_selector = parse_variable(cond_data.get("variable", ""))

            processed_break_conditions.append(
                LoopCondition(
                    id=cond_data.get("id", f"cond_{i}"),
                    varType=cond_data.get("varType", "string"),
                    variable_selector=variable_selector,
                    comparison_operator=cond_data.get("comparison_operator", "is"),
                    value=cond_data.get("value", ""),
                )
            )

    # 生成start_node_id
    start_node_id = f"{node_id}start"

    loop_node_data = LoopNodeData(
        title=title,
        desc=desc,
        start_node_id=start_node_id,
        break_conditions=processed_break_conditions,
        loop_count=loop_count,
        logical_operator=logical_operator,
        error_handle_mode=error_handle_mode,
        loop_variables=processed_loop_variables,
    )

    loop_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=loop_node_data,
        width=388,
        height=178,
    )

    # 创建循环开始节点
    loop_start_data = LoopStartNodeData(
        title="",
        desc="",
        isInLoop=True,
        selected=False,
    )

    loop_start_node = Node(
        id=start_node_id,
        type="custom-loop-start",
        position=NodePosition(x=24, y=68),  # 相对于父节点的位置
        data=loop_start_data,
        width=44,
        height=48,
        selected=False,
    )

    # 设置循环开始节点的父节点和其他属性
    loop_start_dict = loop_start_node.to_dict()
    loop_start_dict["parentId"] = node_id
    loop_start_dict["selectable"] = False
    loop_start_dict["draggable"] = False
    loop_start_dict["zIndex"] = 1002
    # 计算绝对位置
    loop_start_dict["positionAbsolute"] = {"x": x_pos + 24, "y": y_pos + 68}

    return {
        "node": [loop_node.to_dict(), loop_start_dict],
        "observation": f"已经创建了一个名为'{title}'的循环节点和循环开始节点，包含 {len(processed_loop_variables)} 个循环变量和 {len(processed_break_conditions)} 个跳出条件。",
        "output": None,
    }
