from typing import Any, Dict

from langchain_core.tools import tool

from ..base import Node, NodePosition, parse_variable
from .node import DocumentExtractorNodeData


@tool
def create_document_extractor_node(
    node_id: str,
    x_pos: int,
    y_pos: int,
    variable_selector: str,
    title: str = "文档提取器",
    desc: str = "提取并解析文档文件中的文本内容",
) -> Dict[str, Any]:
    """
    在工作流中创建一个文档提取器节点。
    当需要从用户上传的文档文件中提取文本内容时使用此工具。
    支持TXT、Markdown、PDF、HTML、DOCX等格式的文档文件。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "doc_extractor_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        variable_selector (str): 输入的文件变量选择器。
            对于单个文件: "{{#start.file#}}" 或 "{{#previous_node.file#}}"
            对于文件数组: "{{#start.files#}}" 或 "{{#previous_node.files#}}"
            系统内置 "{{#sys.files}}"
        title (str, optional): 节点的显示标题。默认为 "文档提取器"。
        desc (str, optional): 节点的描述信息。默认为 "提取并解析文档文件中的文本内容"。

    Returns:
        Dict[str, Any]: 代表该文档提取器节点的字典结构，可用于工作流编排。

    注意:
        - 输入变量类型为 File 时，输出变量为 string 类型的 text
        - 输入变量类型为 Array[File] 时，输出变量为 array[string] 类型的 text
        - 仅支持文档类型文件（TXT、PDF、DOCX等），不支持图片、音频、视频文件
    """
    # 解析变量选择器
    parsed_variable = parse_variable(variable_selector)

    # 判断是否为数组文件类型
    is_array_file = False
    if variable_selector and "files" in variable_selector.lower():
        is_array_file = True

    # 创建文档提取器节点数据
    doc_extractor_node_data = DocumentExtractorNodeData(
        title=title,
        desc=desc,
        variable_selector=parsed_variable,
        is_array_file=is_array_file,
    )

    # 创建节点
    doc_extractor_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=doc_extractor_node_data,
        width=244,
        height=54,
    )

    # 确定输出描述
    output_desc = "提取的文本内容"
    if is_array_file:
        output_desc = "提取的文本内容列表（每个文件对应一个文本）"

    return {
        "node": doc_extractor_node.to_dict(),
        "observation": f"已经创建了一个名为{title}的文档提取器节点。节点的描述为：{desc}。{output_desc}",
        "output": doc_extractor_node.get_output_variable_references(),
    }
