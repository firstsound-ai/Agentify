from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from common.dto.blueprint import TaskStatus
from common.dto.blueprint import BlueprintResponse
from common.dto.user import UserInfo
from dal.po.blueprint import Blueprint

class BlueprintDAO:
    @staticmethod
    def create_blueprint(
        db: Session, thread_id: str, user_info: UserInfo
    ) -> str:
        blueprint_id = str(uuid4())
        new_blueprint = Blueprint(
            id=blueprint_id,
            thread_id=thread_id,
            blueprint_name="我的流程",
            user_id=user_info.id,
            status=TaskStatus.PENDING.value,
            progress="等待处理中...",
        )
        db.add(new_blueprint)
        return blueprint_id
    
    @staticmethod
    def update_blueprint_status(
        db: Session,
        blueprint_id: str,
        status: TaskStatus,
        progress: Optional[str] = None,
        workflow: Optional[dict] = None,
        mermaid_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        blueprint = db.query(Blueprint).filter(Blueprint.id == blueprint_id).first()
        if blueprint:
            setattr(blueprint, "status", status.value)
            if progress:
                setattr(blueprint, "progress", progress)
            if workflow:
                setattr(blueprint, "workflow", workflow)
            if mermaid_code:
                setattr(blueprint, "mermaid_code", mermaid_code)
            if error_message:
                setattr(blueprint, "error_message", error_message)
            return blueprint
        return None

    @staticmethod
    def get_blueprint_list(db: Session, thread_id: str):
        blueprints = db.query(Blueprint).filter(Blueprint.thread_id == thread_id).all()
        return blueprints

    @staticmethod
    def get_blueprint_by_id(db: Session, blueprint_id: str) -> Optional[Blueprint]:
        return db.query(Blueprint).filter(Blueprint.id == blueprint_id).first()
