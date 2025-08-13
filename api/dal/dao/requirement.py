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
        user_answers: Optional[list] = None,  # 改为list类型
        additional_requirements: Optional[str] = None,  # 新增参数
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
            if additional_requirements:
                setattr(requirement, "additional_requirements", additional_requirements)
            return requirement
        return None

    @staticmethod
    def update_requirement_with_final_document(
        db: Session,
        thread_id: str,
        final_document: dict,
        requirement_name: Optional[str] = None,
        mission_statement: Optional[str] = None,
        user_and_scenario: Optional[str] = None,
        user_input: Optional[str] = None,
        ai_output: Optional[str] = None,
        success_criteria: Optional[str] = None,
        boundaries_and_limitations: Optional[str] = None,
    ):
        """更新需求完成状态并保存最终文档内容到对应数据库字段"""
        requirement = db.query(Requirement).filter(Requirement.id == thread_id).first()
        if requirement:
            setattr(requirement, "status", TaskStatus.COMPLETED.value)
            setattr(requirement, "progress", "最终需求文档已生成完成")
            setattr(requirement, "final_document", final_document)

            # 将文档内容保存到对应的数据库字段
            if requirement_name:
                setattr(requirement, "requirement_name", requirement_name)
            if mission_statement:
                setattr(requirement, "mission_statement", mission_statement)
            if user_and_scenario:
                setattr(requirement, "user_and_scenario", user_and_scenario)
            if user_input:
                setattr(requirement, "user_input", user_input)
            if ai_output:
                setattr(requirement, "ai_output", ai_output)
            if success_criteria:
                setattr(requirement, "success_criteria", success_criteria)
            if boundaries_and_limitations:
                setattr(
                    requirement,
                    "boundaries_and_limitations",
                    boundaries_and_limitations,
                )

            return requirement
        return None

    @staticmethod
    def get_requirement_fields(db: Session, thread_id: str) -> Optional[Requirement]:
        return db.query(Requirement).filter(Requirement.id == thread_id).first()

    @staticmethod
    def update_requirement_fields(
        db: Session, thread_id: str, **fields
    ) -> Optional[Requirement]:
        requirement = db.query(Requirement).filter(Requirement.id == thread_id).first()
        if not requirement:
            return None

        allowed_fields = [
            "requirement_name",
            "mission_statement",
            "user_and_scenario",
            "user_input",
            "ai_output",
            "success_criteria",
            "boundaries_and_limitations",
        ]

        for field_name in allowed_fields:
            if field_name in fields and fields[field_name] is not None:
                setattr(requirement, field_name, fields[field_name])

        return requirement
