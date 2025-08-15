from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from biz.service.blueprint import BlueprintBIZ
from common.dto.user import UserInfo
from common.utils.get_user import get_user_info
from dal.database import get_db
from web.vo.result import Result

router = APIRouter(prefix="/api/blueprint")

@router.post("/create/{thread_id}")
def create_blueprint(
    thread_id: str,
    background_tasks: BackgroundTasks,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db)
):
    blueprint_id = BlueprintBIZ.create_blueprint(
        db, thread_id, user_info, background_tasks
    )
    return Result.success(data={"blueprint_id": blueprint_id})
    
@router.get("/list/{thread_id}")
def get_blueprint_list(
    thread_id: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):  
    result = BlueprintBIZ.get_blueprint_list(
        db, thread_id, user_info
    )
    return Result.success(data={"blueprints": result})

@router.get("/status/{blueprintId}")
def get_blueprint_status(
    blueprintId: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db)
):
    result = BlueprintBIZ.get_blueprint_status(
        db, blueprintId, user_info
    )
    return Result.success(data=result)
