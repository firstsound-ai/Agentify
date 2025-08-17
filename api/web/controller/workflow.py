from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from biz.service.requirement import RequirementBIZ
from biz.service.blueprint import BlueprintBIZ
from common.dto.requirement import RequirementCreate, RequirementFields
from common.dto.user import UserInfo
from common.utils.get_user import get_user_info
from dal.database import get_db
from web.vo.result import Result
from common.utils.dify_client import DifyClient


router = APIRouter(prefix="/api/workflow")

@router.get("/appid/{thread_id}")
def get_appid_by_thread(
    thread_id: str,
    background_tasks: BackgroundTasks,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    client = DifyClient()

    app_type = "advanced-chat"
    app_name = "myapp"
    app_description = "a great app"

    response = client.create_app(app_type, app_name, app_description)
    app_id = response['id']
    BlueprintBIZ.create_node(db, app_id, app_type, app_name, app_description, 
                             background_tasks, user_info, thread_id)
    return Result.success(data={"app_id": app_id})

@router.get("/status/{app_id}")
def get_dify_workflow_status(
    app_id: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    result = BlueprintBIZ.get_dify_workflow_status(db, app_id, user_info)
    return Result.success(data=result)
