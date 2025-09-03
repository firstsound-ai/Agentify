from typing import Annotated, Any, Dict, List

from langchain_core.tools import tool

from ..base import Node, NodePosition, parse_variable
from .node import EndNodeData
from .type import EndOutput


@tool
def create_end_node(
    node_id: Annotated[str, "节点的唯一标识符 (例如: 'end_1')。"],
    x_pos: Annotated[int, "节点在画布上的X坐标。"],
    y_pos: Annotated[int, "节点在画布上的Y坐标。"],
    outputs: Annotated[
        List[Dict[str, Any]],
        "输出变量配置列表。每个字典代表一个输出变量。\n\
- variable (str): 输出变量名\n\
- value_selector (str): 变量选择器字符串，例如 '{{#1755411386775.text#}}'\n\
- value_type (str): 变量类型，默认为 'string'\n\
示例:\n\
[\n\
    {\n\
        'variable': 'result',\n\
        'value_selector': '{{#llm_node_1.text#}}',\n\
        'value_type': 'string'\n\
    },\n\
    {\n\
        'variable': 'score',\n\
        'value_selector': '{{#analysis_node.score#}}',\n\
        'value_type': 'number'\n\
    }\n\
]",
    ],
    title: Annotated[str, "节点的显示标题。默认为 '结束'。"] = "结束",
    desc: Annotated[str, "节点的可选描述信息。"] = "",
) -> Dict[str, Any]:
    """
    在工作流中创建一个结束节点。
    用于标识工作流的结束点，并可以定义输出变量。
    """

    # 解析输出变量配置
    end_outputs = []
    for output_data in outputs:
        # 解析 value_selector 字符串为选择器列表
        selector_str = output_data.get("value_selector", "")
        selector_list = parse_variable(selector_str)

        end_outputs.append(
            EndOutput(
                variable=output_data.get("variable", ""),
                value_selector=selector_list,
                value_type=output_data.get("value_type", "string"),
            )
        )

    end_node_data = EndNodeData(
        title=title,
        desc=desc,
        outputs=end_outputs,
    )

    end_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=end_node_data,
        width=244,
        height=90,
    )

    return {
        "node": end_node.to_dict(),
        "observation": f"已经创建了一个名为'{title}'的结束节点，包含 {len(end_outputs)} 个输出变量。",
        "output": [],
    }
