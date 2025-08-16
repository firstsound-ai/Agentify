from ..base import BaseTool


class TavilySearchTool(BaseTool):
    def get_tool_name(self) -> str:
        return "tavily"
