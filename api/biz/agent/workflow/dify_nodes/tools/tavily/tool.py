from typing import Any, Dict, Optional

from langchain_core.tools import tool

from ..base import ToolConfig
from .node import TavilySearchTool


@tool
def create_tavily_search_tool(
    node_id: str,
    x_pos: int,
    y_pos: int,
    query: str,
    title: str = "Tavily搜索",
    search_depth: str = "basic",
    topic: str = "general",
    days: Optional[int] = None,
    time_range: str = "not_specified",
    max_results: int = 5,
    include_images: bool = False,
    include_answer: bool = False,
    include_raw_content: bool = False,
    include_domains: Optional[str] = None,
    exclude_domains: Optional[str] = None,
    desc: str = "使用Tavily进行网络搜索",
) -> Dict[str, Any]:
    """
    在工作流中创建一个Tavily搜索工具节点。
    当用户需要获取实时网络信息、最新新闻、研究资料或任何需要网络搜索的内容时，使用此工具。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "tavily_search_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        query (str): 搜索查询内容，可以引用其他节点的输出，例如 '{{#sys.query#}}' 或 '{{#previous_node.output#}}'。
        title (str, optional): 节点的显示标题。默认为 "Tavily搜索"。
        search_depth (str, optional): 搜索深度，"basic"或"advanced"。默认为 "basic"。
        topic (str, optional): 搜索主题类别，"general"、"news"或"finance"。默认为 "general"。
        days (int, optional): 搜索多少天内的内容。默认为None。
        time_range (str, optional): 时间范围，"not_specified"、"day"、"week"、"month"或"year"。默认为 "not_specified"。
        max_results (int, optional): 最大搜索结果数量。默认为 5。
        include_images (bool, optional): 是否包含图片。默认为 False。
        include_answer (bool, optional): 是否包含AI生成的答案。默认为 False。
        include_raw_content (bool, optional): 是否包含原始内容。默认为 False。
        include_domains (str, optional): 包含的特定域名，逗号分隔。默认为 None。
        exclude_domains (str, optional): 排除的特定域名，逗号分隔。默认为 None。
        desc (str, optional): 节点的可选描述信息。默认为 "使用Tavily进行网络搜索"。

    Returns:
        Dict[str, Any]: 代表该Tavily搜索节点的字典结构，可用于工作流编排。
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
                    "search_depth": {"type": "constant", "value": search_depth},
                    "topic": {"type": "constant", "value": topic},
                    "days": {
                        "type": "constant",
                        "value": days if days is not None else 3,
                    },
                    "time_range": {"type": "constant", "value": time_range},
                },
            }
        },
    )
    tavily_tool = TavilySearchTool(config)
    tool_config = tavily_tool.generate_config()

    return {
        "node": tool_config,
        "observation": f"已经创建了一个名为'{title}'的Tavily搜索节点。搜索查询：{query}",
        "output": tavily_tool.get_tool_output_references(node_id),
    }
