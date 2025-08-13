from typing import Dict, Optional

from pydantic import BaseModel

from biz.agent.requirement.state import Questionnaire, RequirementDefinition
from common.enums.task import TaskStatus


class RequirementCreate(BaseModel):
    initial_requirement: str


class UserAnswers(BaseModel):
    answers: Dict[str, str]  # 格式: {"q1": "PYTHON_DS", "q2": "ALL_LEVELS", ...}


class RequirementTaskResponse(BaseModel):
    thread_id: str
    status: TaskStatus
    questionnaire: Optional[Questionnaire] = None
    final_document: Optional[RequirementDefinition] = None
    error: Optional[str] = None
    progress: str
