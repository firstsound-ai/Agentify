from typing import List, Optional, TypedDict

from pydantic import BaseModel, Field


class BlueprintDefinition(BaseModel):
    """定义一个完整的Agent/Workflow需求文档。"""

    blueprint_name: Optional[str] = Field(
        None, description=""
    )
    mission_statement: Optional[str] = Field(
        None, description="这个工作流存在的最终价值和核心目标 (The 'Why')。"
    )
    user_and_scenario: Optional[str] = Field(
        None, description="谁在用？在什么情况下用？ (The 'Who' & 'Where')。"
    )
    user_input: Optional[str] = Field(
        None, description="描述用户需要给出的指令或材料 (The 'Input')。"
    )
    ai_output: Optional[str] = Field(
        None, description="描述用户眼中最完美的输出结果 (The 'Output')。"
    )
    success_criteria: Optional[str] = Field(
        None, description="判断工作流好坏的客观标准。"
    )
    boundaries_and_limitations: Optional[str] = Field(
        None, description="明确定义哪些事是工作流不应该做的，以管理期望。"
    )

class GraphState(TypedDict):
    """定义工作流中流动的数据状态。"""

    final_document: str
    workflow: Optional[str]
    mermaid_code: Optional[str]
    error: Optional[str]
