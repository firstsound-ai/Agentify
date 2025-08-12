from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel

from biz.agent.requirement.state import Questionnaire, RequirementDefinition


class RequirementCreate(BaseModel):
    initial_requirement: str


class UserAnswers(BaseModel):
    """用户对问卷的回答"""

    answers: Dict[str, str]  # 格式: {"q1": "PYTHON_DS", "q2": "ALL_LEVELS", ...}


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_FOR_ANSWERS = "waiting_for_answers"  # 新增状态：等待用户回答


class RequirementTaskResponse(BaseModel):
    thread_id: str
    status: TaskStatus
    questionnaire: Optional[Questionnaire] = None
    final_document: Optional[RequirementDefinition] = None
    error: Optional[str] = None
    progress: str
