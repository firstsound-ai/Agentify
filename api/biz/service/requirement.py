import json
from typing import Optional

from fastapi import BackgroundTasks
from langchain_core.runnables.config import RunnableConfig
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from biz.agent.requirement.graph import get_requirement_workflow
from biz.agent.requirement.state import GraphState, Questionnaire, RequirementDefinition
from common.dto.requirement import (
    RequirementCreate,
    RequirementTaskResponse,
    UserAnswers,
)
from common.dto.user import UserInfo
from common.enums.error_code import ErrorCode
from common.enums.task import TaskStatus
from common.exceptions.general_exception import GeneralException
from dal.dao.requirement import RequirementDAO
from dal.database import get_db


class RequirementBIZ:
    @staticmethod
    def create_requirement(
        db: Session,
        requirement: RequirementCreate,
        user_info: UserInfo,
        background_tasks: BackgroundTasks,
    ):
        try:
            with db.begin():
                thread_id = RequirementDAO.create_requirement(
                    db, requirement, user_info
                )

            background_tasks.add_task(
                RequirementBIZ._process_requirement_task,
                thread_id,
                requirement.initial_requirement,
            )

            return thread_id
        except SQLAlchemyError as e:
            raise GeneralException(ErrorCode.DATABASE_ERROR, detail=str(e))
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def get_requirement_status(
        db: Session, thread_id: str, user_info: UserInfo
    ) -> RequirementTaskResponse:
        try:
            requirement = RequirementDAO.get_requirement_by_id(db, thread_id)

            if not requirement:
                raise GeneralException(ErrorCode.NOT_FOUND, detail="需求不存在")

            if getattr(requirement, "user_id") != user_info.id:
                raise GeneralException(ErrorCode.FORBIDDEN, detail="无权限访问此需求")

            response = RequirementTaskResponse(
                thread_id=thread_id,
                status=TaskStatus(getattr(requirement, "status")),
                progress=getattr(requirement, "progress") or "处理中...",
            )

            questionnaire_data = getattr(requirement, "questionnaire")
            if questionnaire_data:
                response.questionnaire = Questionnaire.model_validate(
                    questionnaire_data
                )

            final_document_data = getattr(requirement, "final_document")
            if final_document_data:
                response.final_document = RequirementDefinition.model_validate(
                    final_document_data
                )

            error_message = getattr(requirement, "error_message")
            if error_message:
                response.error = error_message

            return response

        except GeneralException:
            raise
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def _process_requirement_task(
        thread_id: str,
        initial_requirement: str,
    ):
        db = next(get_db())

        try:
            RequirementDAO.update_requirement_status(
                db, thread_id, TaskStatus.PROCESSING, "开始处理需求..."
            )

            app = get_requirement_workflow()

            initial_state: GraphState = {
                "user_request": initial_requirement,
                "product_draft": None,
                "questionnaire": None,
                "user_answers": None,
                "additional_requirements": None,  # 添加新字段
                "final_document": None,
                "error": None,
            }

            config = RunnableConfig(configurable={"thread_id": thread_id})
            result = app.invoke(initial_state, config=config)

            if result.get("error"):
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.FAILED,
                    "处理过程中发生错误",
                    error_message=result["error"],
                )
                db.commit()
            elif result.get("questionnaire"):
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.WAITING_FOR_ANSWERS,
                    "问卷已生成，等待用户回答",
                    questionnaire=result["questionnaire"],
                )
                db.commit()
            else:
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.FAILED,
                    "问卷生成失败",
                )
                db.commit()

        except Exception as e:
            RequirementDAO.update_requirement_status(
                db,
                thread_id,
                TaskStatus.FAILED,
                "处理过程中发生错误",
                error_message=str(e),
            )
            db.commit()
        finally:
            db.close()

    @staticmethod
    def submit_answers(
        db: Session,
        thread_id: str,
        user_answers: UserAnswers,
        user_info: UserInfo,
        background_tasks: BackgroundTasks,
    ):
        """提交用户答案并继续处理"""
        try:
            requirement = RequirementDAO.get_requirement_by_id(db, thread_id)

            if not requirement:
                raise GeneralException(ErrorCode.NOT_FOUND, detail="需求不存在")

            if getattr(requirement, "user_id") != user_info.id:
                raise GeneralException(ErrorCode.FORBIDDEN, detail="无权限访问此需求")

            current_status = getattr(requirement, "status")
            if current_status != TaskStatus.WAITING_FOR_ANSWERS.value:
                raise GeneralException(
                    ErrorCode.BAD_REQUEST,
                    detail=f"当前状态不允许提交答案，当前状态: {current_status}",
                )

            # 保存用户答案和额外要求
            user_answers_data = [answer.model_dump() for answer in user_answers.answers]
            RequirementDAO.update_requirement_status(
                db,
                thread_id,
                TaskStatus.PROCESSING,
                "已收到用户答案，正在生成最终文档...",
                user_answers=user_answers_data,
                additional_requirements=user_answers.additional_requirements,
            )
            db.commit()

            # 启动后台任务继续处理
            background_tasks.add_task(
                RequirementBIZ._continue_requirement_task,
                thread_id,
                user_answers.answers,
                user_answers.additional_requirements,
            )

            return {"message": "答案已提交，正在生成最终文档..."}

        except GeneralException:
            raise
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def _continue_requirement_task(
        thread_id: str,
        user_answers: list,
        additional_requirements: Optional[str] = None,
    ):
        """继续处理需求任务 - 恢复LangGraph执行并提供用户答案"""

        # 获取新的数据库连接
        db = next(get_db())

        try:
            from biz.agent.requirement.graph import get_requirement_workflow

            app = get_requirement_workflow()

            # 配置LangGraph运行时
            config = RunnableConfig(configurable={"thread_id": thread_id})

            RequirementDAO.update_requirement_status(
                db, thread_id, TaskStatus.PROCESSING, "正在生成最终需求文档..."
            )

            # 更新状态，提供用户答案和额外要求后继续执行
            # 将 user_answers 转换为 UserAnswer 对象列表
            from langgraph.types import Command

            from biz.agent.requirement.state import UserAnswer

            user_answer_objects = []
            for answer_data in user_answers:
                if isinstance(answer_data, dict):
                    user_answer_objects.append(UserAnswer.model_validate(answer_data))
                else:
                    user_answer_objects.append(answer_data)

            # 使用 Command 来恢复执行，而不是 update_state
            resume_value = {"user_answers": user_answer_objects}
            if additional_requirements:
                resume_value["additional_requirements"] = additional_requirements  # type: ignore

            # 恢复执行被中断的工作流
            result = None
            result = app.invoke(Command(resume=resume_value), config=config)

            print("---输出---")
            print(result)

            # 处理最终文档
            final_document_data = RequirementBIZ._parse_final_document(
                result.get("final_document") if result else None
            )

            if result and result.get("error"):
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.FAILED,
                    "生成最终文档时发生错误",
                    error_message=result["error"],
                )
                db.commit()
            elif final_document_data:
                # 解析文档内容并保存到对应字段
                RequirementBIZ._save_final_document_to_db(
                    db, thread_id, final_document_data
                )
                db.commit()
            else:
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.FAILED,
                    "最终文档生成失败",
                )
                db.commit()

        except Exception as e:
            RequirementDAO.update_requirement_status(
                db,
                thread_id,
                TaskStatus.FAILED,
                "生成最终文档时发生错误",
                error_message=str(e),
            )
            db.commit()
        finally:
            db.close()

    @staticmethod
    def _parse_final_document(final_document_raw):
        """解析最终文档数据"""
        if not final_document_raw:
            return None

        if hasattr(final_document_raw, "content"):
            # 如果是 AI 消息，解析其内容
            try:
                content = str(final_document_raw.content).strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                return json.loads(content.strip())
            except json.JSONDecodeError:
                # 如果解析失败，直接使用内容
                return {"content": str(final_document_raw.content)}
        elif hasattr(final_document_raw, "dict"):
            return final_document_raw.dict()
        elif isinstance(final_document_raw, dict):
            return final_document_raw
        else:
            return {"content": str(final_document_raw)}

    @staticmethod
    def _save_final_document_to_db(
        db: Session, thread_id: str, final_document_data: dict
    ):
        """将最终文档内容解析并保存到数据库对应字段"""
        try:
            # 提取文档字段
            requirement_name = final_document_data.get("requirement_name")
            mission_statement = final_document_data.get("mission_statement")
            user_and_scenario = final_document_data.get("user_and_scenario")
            user_input = final_document_data.get("user_input")
            ai_output = final_document_data.get("ai_output")
            success_criteria = final_document_data.get("success_criteria")
            boundaries_and_limitations = final_document_data.get(
                "boundaries_and_limitations"
            )

            # 保存到数据库
            RequirementDAO.update_requirement_with_final_document(
                db=db,
                thread_id=thread_id,
                final_document=final_document_data,
                requirement_name=requirement_name,
                mission_statement=mission_statement,
                user_and_scenario=user_and_scenario,
                user_input=user_input,
                ai_output=ai_output,
                success_criteria=success_criteria,
                boundaries_and_limitations=boundaries_and_limitations,
            )
        except Exception:
            # 如果解析失败，至少保存原始文档
            RequirementDAO.update_requirement_status(
                db,
                thread_id,
                TaskStatus.COMPLETED,
                "最终需求文档已生成完成（部分字段解析失败）",
                final_document=final_document_data,
            )
