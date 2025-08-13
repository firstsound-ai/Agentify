from typing import List, Optional

from pydantic import BaseModel

from biz.agent.requirement.state import Questionnaire, RequirementDefinition, UserAnswer
from common.enums.task import TaskStatus


class RequirementCreate(BaseModel):
    initial_requirement: str


class UserAnswers(BaseModel):
    answers: List[UserAnswer]  # 改为新的用户答案结构
    additional_requirements: Optional[str] = None  # 用户额外补充的要求


class RequirementTaskResponse(BaseModel):
    thread_id: str
    status: TaskStatus
    questionnaire: Optional[Questionnaire] = None
    final_document: Optional[RequirementDefinition] = None
    error: Optional[str] = None
    progress: str


class RequirementFields(BaseModel):
    """需求可编辑字段模型 - 可用于请求和响应"""

    requirement_name: Optional[str] = None
    mission_statement: Optional[str] = None
    user_and_scenario: Optional[str] = None
    user_input: Optional[str] = None
    ai_output: Optional[str] = None
    success_criteria: Optional[str] = None
    boundaries_and_limitations: Optional[str] = None

    class Config:
        from_attributes = True  # Pydantic v2 的配置，支持从 ORM 对象创建
