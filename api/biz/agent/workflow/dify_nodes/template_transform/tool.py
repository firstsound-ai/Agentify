from typing import Annotated, Any, Dict, List, Optional

from langchain_core.tools import tool

from ..base import Node, NodePosition, parse_variable
from .node import TemplateTransformNodeData
from .type import TemplateVariable


@tool
def create_template_transform_node(
    node_id: Annotated[str, "节点的唯一标识符 (例如: 'template_step_1')。"],
    x_pos: Annotated[int, "节点在画布上的X坐标。"],
    y_pos: Annotated[int, "节点在画布上的Y坐标。"],
    template: Annotated[
        str,
        "Jinja2模板内容。支持所有Jinja2语法，包括变量替换、循环、条件等。\n\
示例: '用户输入: {{ user_query }}\n处理结果: {{ result }}'\n\
示例: '{% for item in items %}{{ item }}\n{% endfor %}'",
    ],
    variables: Annotated[
        Optional[List[Dict[str, Any]]],
        "输入变量列表。每个变量包含:\n\
- variable: 变量名，在模板中使用\n\
- value: 变量引用字符串，例如 '{{#sys.query#}}' 或 '{{#previous_node.result#}}'\n\
- value_type: 值类型，支持 'string', 'number', 'object', 'array[string]', 'array[number]', 'array[object]'\n\
示例: [{'variable': 'user_query', 'value': '{{#sys.query#}}', 'value_type': 'string'}]\n\
",
    ] = None,
    title: Annotated[str, "节点的显示标题。默认为 '模板转换'。"] = "模板转换",
    desc: Annotated[
        str, "节点的可选描述信息。默认为 '使用Jinja2模板进行数据转换和文本处理'。"
    ] = "使用Jinja2模板进行数据转换和文本处理",
) -> Dict[str, Any]:
    """
    在工作流中创建一个模板转换节点。
    当需要使用Jinja2模板语法对数据进行格式化、转换或文本处理时使用此工具。
    """
    if variables is None:
        variables = []

    # 转换变量
    template_variables = []
    for var in variables:
        value = var.get("value", "")
        # 统一使用parse_variable解析字符串格式的变量引用
        value_selector = parse_variable(value)

        template_variables.append(
            TemplateVariable(
                variable=var.get("variable", ""),
                value_selector=value_selector,
                value_type=var.get("value_type", "string"),
            )
        )

    template_node_data = TemplateTransformNodeData(
        title=title,
        desc=desc,
        template_variables=template_variables,
        template=template,
    )

    template_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=template_node_data,
        width=244,
        height=54,
    )

    print(template_node)

    return {
        "node": template_node.to_dict(),
        "observation": f"已经创建了一个名为{title}的模板转换节点。节点的描述为：{desc}",
        "output": template_node.get_output_variable_references(),
    }
