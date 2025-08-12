from typing import Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


class RequirementDefinition(BaseModel):
    """定义一个完整的Agent/Workflow需求文档。"""

    requirement_name: Optional[str] = Field(
        None, description="为这个工作流起一个简洁明了的名字。"
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


# 这是用于生成问卷的Pydantic模型
class Option(BaseModel):
    value: str = Field(..., description="选项的唯一标识值，通常为大写英文")
    label: str = Field(..., description="选项的显示文本，给用户看")


class Question(BaseModel):
    id: str = Field(..., description="问题的唯一ID，例如 'q1', 'q2'")
    question: str = Field(..., description="问题的具体文本")
    options: List[Option] = Field(..., description="该问题的选项列表")


class Questionnaire(BaseModel):
    """用于生成澄清问题的结构化问卷"""

    questions: List[Question] = Field(..., description="一个包含所有问题的列表")


class GraphState(TypedDict):
    """定义工作流中流动的数据状态。"""

    user_request: str
    product_draft: Optional[str]
    questionnaire: Optional[Questionnaire]  # 直接使用Pydantic模型
    user_answers: Optional[Dict[str, str]]
    final_document: Optional[RequirementDefinition]  # 最终产出也是Pydantic模型
    error: Optional[str]
