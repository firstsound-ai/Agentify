from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from common.dto.requirement import RequirementCreate, TaskStatus
from common.dto.user import UserInfo
from dal.po.requirement import Requirement


class RequirementDAO:
    @staticmethod
    def create_requirement(
        db: Session, requirement: RequirementCreate, user_info: UserInfo
    ) -> str:
        thread_id = str(uuid4())
        new_requirement = Requirement(
            id=thread_id,
            initial_requirement=requirement.initial_requirement,
            user_id=user_info.id,
            status=TaskStatus.PENDING.value,
            progress="等待处理中...",
        )
        db.add(new_requirement)
        return thread_id

    @staticmethod
    def get_requirement_by_id(db: Session, thread_id: str) -> Optional[Requirement]:
        return db.query(Requirement).filter(Requirement.id == thread_id).first()

    @staticmethod
    def update_requirement_status(
        db: Session,
        thread_id: str,
        status: TaskStatus,
        progress: Optional[str] = None,
        questionnaire: Optional[dict] = None,
        final_document: Optional[dict] = None,
        error_message: Optional[str] = None,
        user_answers: Optional[dict] = None,
    ):
        requirement = db.query(Requirement).filter(Requirement.id == thread_id).first()
        if requirement:
            setattr(requirement, "status", status.value)
            if progress:
                setattr(requirement, "progress", progress)
            if questionnaire:
                setattr(requirement, "questionnaire", questionnaire)
            if final_document:
                setattr(requirement, "final_document", final_document)
            if error_message:
                setattr(requirement, "error_message", error_message)
            if user_answers:
                setattr(requirement, "user_answers", user_answers)
            db.commit()
            return requirement
        return None
