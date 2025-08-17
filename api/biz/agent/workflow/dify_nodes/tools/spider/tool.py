from typing import Any, Dict

from langchain_core.tools import tool

from ..base import ToolConfig
from .node import SpiderTool


@tool
def create_spider_tool(
    node_id: str,
    x_pos: int,
    y_pos: int,
    url: str,
    title: str = "网页爬虫",
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1000.0 Safari/537.36",
    generate_summary: bool = False,
    desc: str = "抓取指定网页的内容",
) -> Dict[str, Any]:
    """
    在工作流中创建一个网页爬虫工具节点。
    当用户需要获取特定网页的内容、抓取网站数据或解析网页信息时，使用此工具。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "spider_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        url (str): 要抓取的网页URL，可以引用其他节点的输出，例如 '{{#sys.query#}}' 或 '{{#previous_node.url#}}'。
        title (str, optional): 节点的显示标题。默认为 "网页爬虫"。
        user_agent (str, optional): 请求时使用的User-Agent字符串。默认为Chrome浏览器的UA。
        generate_summary (bool, optional): 是否生成网页内容摘要。默认为 False。
        desc (str, optional): 节点的可选描述信息。默认为 "抓取指定网页的内容"。

    Returns:
        Dict[str, Any]: 代表该网页爬虫节点的字典结构，可用于工作流编排。
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
                    "url": {"type": "mixed", "value": url},
                },
                "tool_configurations": {
                    "user_agent": {"type": "mixed", "value": user_agent},
                    "generate_summary": {"type": "constant", "value": generate_summary},
                },
            }
        },
    )

    # 创建工具实例并生成配置
    spider_tool = SpiderTool(config)
    return spider_tool.to_dict()
