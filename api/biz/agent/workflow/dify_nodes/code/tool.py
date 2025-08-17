from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from ..base import Node, NodePosition, parse_variable
from .node import CodeNodeData
from .type import CodeOutput, CodeVariable


@tool
def create_code_node(
    node_id: str,
    x_pos: int,
    y_pos: int,
    code: str,
    code_language: str = "python3",
    variables: Optional[List[Dict[str, Any]]] = None,
    outputs: Optional[Dict[str, Dict[str, Any]]] = None,
    title: str = "代码执行",
    desc: str = "执行自定义代码逻辑",
) -> Dict[str, Any]:
    """
    在工作流中创建一个代码执行节点。
    当需要执行自定义的代码逻辑时使用此工具，支持Python和JavaScript。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "code_step_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        code (str): 要执行的代码。对于Python，应该是一个main函数；对于JavaScript，应该是一个main函数。
            Python示例: "def main(arg1: str, arg2: str) -> dict:\\n    return {'result': arg1 + arg2}"
            JavaScript示例: "function main(arg1, arg2) {\\n    return {'result': arg1 + arg2};\\n}"
        code_language (str, optional): 代码语言，支持 "python3" 或 "javascript"。默认为 "python3"。
        variables (List[Dict[str, Any]], optional): 输入变量列表。每个变量包含:
            - variable: 变量名
            - value: 变量引用字符串，例如 "{{#sys.query#}}" 或 "{{#previous_node.result#}}"
            - value_type: 值类型，支持 "string", "number", "object", "array[string]", "array[number]", "array[object]"
            示例: [{"variable": "arg1", "value": "{{#sys.query#}}", "value_type": "string"}]
        outputs (Dict[str, Dict[str, Any]], optional): 输出变量定义。键为变量名，值包含:
            - type: 输出类型，支持 "string", "number", "object", "array[string]", "array[number]", "array[object]"
            - children: 子对象（可选）
            示例: {"result": {"type": "string", "children": None}}
        title (str, optional): 节点的显示标题。默认为 "代码执行"。
        desc (str, optional): 节点的可选描述信息。默认为 "执行自定义代码逻辑"。

    Returns:
        Dict[str, Any]: 代表该代码节点的字典结构，可用于工作流编排。
    """
    if variables is None:
        variables = []
    if outputs is None:
        outputs = {"result": {"type": "string", "children": None}}

    # 转换变量
    code_variables = []
    for var in variables:
        value = var.get("value", "")
        # 统一使用parse_variable解析字符串格式的变量引用
        value_selector = parse_variable(value)

        code_variables.append(
            CodeVariable(
                variable=var.get("variable", ""),
                value_selector=value_selector,
                value_type=var.get("value_type", "string"),
            )
        )

    # 转换输出
    code_outputs = {}
    for key, output_info in outputs.items():
        code_outputs[key] = CodeOutput(
            type=output_info.get("type", "string"),
            children=output_info.get("children", None),
        )

    code_node_data = CodeNodeData(
        title=title,
        desc=desc,
        code_variables=code_variables,
        code_language=code_language,
        code=code,
        outputs=code_outputs,
    )

    # 根据outputs更新output_variables
    code_node_data.update_output_variables_from_outputs()

    code_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=code_node_data,
        width=244,
        height=54,
    )

    print(code_node)

    return {
        "node": code_node.to_dict(),
        "observation": f"已经创建了一个名为{title}的代码执行节点。节点的描述为：{desc}，代码语言为：{code_language}",
        "output": code_node.get_output_variable_references(),
    }
