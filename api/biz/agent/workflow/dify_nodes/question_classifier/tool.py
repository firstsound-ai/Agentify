from typing import Annotated, Any, Dict, List

from langchain_core.tools import tool

from ..base import Node, NodePosition, parse_variable
from ..llm.type import LLMModel
from .node import QuestionClassifierNodeData
from .type import QuestionClassifierClass


@tool
def create_question_classifier_node(
    node_id: Annotated[str, "节点的唯一标识符 (例如: 'classifier-1')。"],
    x_pos: Annotated[int, "节点在画布上的X坐标。"],
    y_pos: Annotated[int, "节点在画布上的Y坐标。"],
    query: Annotated[str, "要进行分类的用户问题变量引用 (例如: '{{#sys.query#}}')。"],
    classes: Annotated[List[str], "用于分类的类别名称列表。"] = [],
    title: Annotated[str, "节点的显示标题。默认为 '问题分类器'。"] = "问题分类器",
    model_provider: str = "langgenius/siliconflow/siliconflow",
    model_name: str = "deepseek-ai/DeepSeek-V3",
    desc: str = "根据用户问题进行分类",
) -> Dict[str, Any]:
    """
    在工作流中创建一个问题分类器节点。
    当需要根据用户输入的问题将其引导到不同的处理分支时，使用此工具。
    """
    query_variable_selector = parse_variable(query)

    classifier_classes = [
        QuestionClassifierClass(id=str(i + 1), name=name)
        for i, name in enumerate(classes)
    ]

    classifier_data = QuestionClassifierNodeData(
        title=title,
        desc=desc,
        query_variable_selector=query_variable_selector,
        model=LLMModel(provider=model_provider, name=model_name),
        classes=classifier_classes,
    )

    classifier_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=classifier_data,
        width=320,
        height=240,
    )

    return {
        "node": classifier_node.to_dict(),
        "observation": f"已经创建了一个名为{title}的问题分类器节点。",
        "output": classifier_node.get_output_variable_references(),
    }
