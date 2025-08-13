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
