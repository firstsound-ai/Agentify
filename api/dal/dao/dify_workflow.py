from typing import Optional, Dict
from uuid import uuid4

from sqlalchemy.orm import Session

from common.dto.blueprint import TaskStatus
from common.dto.user import UserInfo
from dal.po.dify_workflow import DifyWorkflow


class DifyWorkflowDAO:
    @staticmethod
    def create_dify_workflow(db: Session, 
                        thread_id: str,
                        app_id: str, 
                        app_type: str,
                        app_name: str,
                        app_description: str,
                        user_info: UserInfo) -> str:
        new_dify_workflow = DifyWorkflow(
            app_id=app_id,
            app_type=app_type,
            app_name=app_name,
            app_description=app_description,
            thread_id=thread_id,
            status=TaskStatus.PENDING.value,
        )
        db.add(new_dify_workflow)

    @staticmethod
    def get_dify_workflow_by_id(db: Session, 
                                app_id: str):
        dify_workflow = db.query(DifyWorkflow).filter(DifyWorkflow.app_id == app_id).first()
        return dify_workflow

    @staticmethod
    def update_dify_workflow(
        db: Session,
        app_id: str=None,
        app_name: str=None,
        app_description: str=None,
        status: TaskStatus=None,
        nodes: Dict=None,
        edges: Dict=None
    ):
        dify_workflow = db.query(DifyWorkflow).filter(DifyWorkflow.app_id == app_id).first()

        if dify_workflow:
            setattr(dify_workflow, "status", status.value)
            if app_name: 
                setattr(dify_workflow, "app_name", app_name)
            if app_description:
                setattr(dify_workflow, "app_description", app_description)
            if nodes:
                setattr(dify_workflow, "nodes", nodes)
            if edges:
                setattr(dify_workflow, "edges", edges)
        return None
