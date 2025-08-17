from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from biz.service.requirement import RequirementBIZ
from biz.service.blueprint import BlueprintBIZ
from common.dto.requirement import RequirementCreate, RequirementFields
from common.dto.user import UserInfo
from common.utils.get_user import get_user_info
from dal.database import get_db
from web.vo.result import Result

router = APIRouter(prefix="/api/workflow")


@router.get("/appid/{thread_id}")
def get_appid_by_thread(
    thread_id: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db)
):
    app_id = BlueprintBIZ.get_appid_by_thread(db, user_info, thread_id)
    return Result.success(data={"app_id": app_id})
