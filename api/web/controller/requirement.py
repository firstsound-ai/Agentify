from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from biz.service.requirement import RequirementBIZ
from common.dto.requirement import RequirementCreate, RequirementFields, UserAnswers
from common.dto.user import UserInfo
from common.utils.get_user import get_user_info
from dal.database import get_db
from web.vo.result import Result

router = APIRouter(prefix="/api/requirement")


@router.post("/create")
def create_requirement(
    initial_requirement: RequirementCreate,
    background_tasks: BackgroundTasks,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    thread_id = RequirementBIZ.create_requirement(
        db, initial_requirement, user_info, background_tasks
    )
    return Result.success(data={"thread_id": thread_id})


@router.get("/status/{thread_id}")
def get_requirement_status(
    thread_id: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    result = RequirementBIZ.get_requirement_status(db, thread_id, user_info)
    return Result.success(data=result.model_dump())


@router.post("/submit-answers/{thread_id}")
def submit_answers(
    thread_id: str,
    user_answers: UserAnswers,
    background_tasks: BackgroundTasks,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    result = RequirementBIZ.submit_answers(
        db, thread_id, user_answers, user_info, background_tasks
    )
    return Result.success(data=result)


@router.get("/fields/{thread_id}")
def get_requirement_fields(
    thread_id: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    result = RequirementBIZ.get_requirement_fields(db, thread_id, user_info)
    return Result.success(data=result.model_dump())


@router.post("/fields/{thread_id}")
def update_requirement_fields(
    thread_id: str,
    fields_update: RequirementFields,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    result = RequirementBIZ.update_requirement_fields(
        db, thread_id, fields_update, user_info
    )
    return Result.success(data=result.model_dump())
