from ..base import BaseTool


class ArxivTool(BaseTool):
    def get_tool_name(self) -> str:
        return "arxiv"
