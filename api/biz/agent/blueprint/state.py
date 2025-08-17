from typing import Optional, TypedDict


class GraphState(TypedDict):
    """定义工作流中流动的数据状态。"""

    final_document: str
    workflow: Optional[str]
    mermaid_code: Optional[str]
    error: Optional[str]
