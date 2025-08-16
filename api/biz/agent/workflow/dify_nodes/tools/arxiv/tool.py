from typing import Any, Dict

from langchain_core.tools import tool

from ..base import ToolConfig
from .node import ArxivTool


@tool
def create_arxiv_search_tool(
    node_id: str,
    x_pos: int,
    y_pos: int,
    query: str,
    title: str = "Arxiv搜索",
    max_results: int = 5,
    desc: str = "使用Arxiv搜索学术论文",
) -> Dict[str, Any]:
    """
    在工作流中创建一个Arxiv搜索工具节点。
    当用户需要搜索学术论文、科研文献、研究报告等学术资源时，使用此工具。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "arxiv_search_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        query (str): 搜索查询内容，可以引用其他节点的输出，例如 '{{#sys.query#}}' 或 '{{#previous_node.output#}}'。
        title (str, optional): 节点的显示标题。默认为 "Arxiv搜索"。
        max_results (int, optional): 最大搜索结果数量。默认为 5。
        desc (str, optional): 节点的可选描述信息。默认为 "使用Arxiv搜索学术论文"。

    Returns:
        Dict[str, Any]: 代表该Arxiv搜索节点的字典结构，可用于工作流编排。
    """

    # 创建工具配置
    config = ToolConfig(
        id=node_id,
        title=title,
        x_pos=x_pos,
        y_pos=y_pos,
        desc=desc,
        extra_params={
            "data": {
                "tool_parameters": {
                    "query": {"type": "mixed", "value": query},
                },
            }
        },
    )

    # 创建工具实例
    arxiv_tool = ArxivTool(config)

    # 生成节点配置
    tool_config = arxiv_tool.generate_config()

    return {
        "node": tool_config,
        "observation": f"已经创建了一个名为'{title}'的Arxiv搜索节点。搜索查询：{query}",
        "output": arxiv_tool.get_tool_output_references(node_id),
    }
