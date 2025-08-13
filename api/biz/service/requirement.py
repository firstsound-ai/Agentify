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
    RequirementFields,
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
        db = next(get_db())

        try:
            from langgraph.types import Command

            from biz.agent.requirement.graph import get_requirement_workflow
            from biz.agent.requirement.state import UserAnswer

            app = get_requirement_workflow()
            config = RunnableConfig(configurable={"thread_id": thread_id})

            RequirementDAO.update_requirement_status(
                db, thread_id, TaskStatus.PROCESSING, "正在生成最终需求文档..."
            )

            # 准备恢复数据
            user_answer_objects = [
                UserAnswer.model_validate(answer)
                if isinstance(answer, dict)
                else answer
                for answer in user_answers
            ]

            resume_value = {"user_answers": user_answer_objects}
            if additional_requirements:
                resume_value["additional_requirements"] = additional_requirements  # type: ignore

            # 恢复执行工作流
            result = app.invoke(Command(resume=resume_value), config=config)

            # 处理结果
            RequirementBIZ._handle_workflow_result(db, thread_id, result)

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
    def _handle_workflow_result(db: Session, thread_id: str, result: dict):
        """处理工作流执行结果"""
        if result and result.get("error"):
            RequirementDAO.update_requirement_status(
                db,
                thread_id,
                TaskStatus.FAILED,
                "生成最终文档时发生错误",
                error_message=result["error"],
            )
        elif final_document := RequirementBIZ._parse_final_document(
            result.get("final_document")
        ):
            RequirementBIZ._save_final_document_to_db(db, thread_id, final_document)
        else:
            RequirementDAO.update_requirement_status(
                db, thread_id, TaskStatus.FAILED, "最终文档生成失败"
            )
        db.commit()

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

    @staticmethod
    def _validate_requirement_access(requirement, user_info: UserInfo):
        """验证需求访问权限和状态的通用方法"""
        if not requirement:
            raise GeneralException(ErrorCode.NOT_FOUND, detail="需求不存在")

        if getattr(requirement, "user_id") != user_info.id:
            raise GeneralException(ErrorCode.FORBIDDEN, detail="无权限访问此需求")

        if getattr(requirement, "status") != TaskStatus.COMPLETED.value:
            raise GeneralException(
                ErrorCode.BAD_REQUEST, detail="只有已完成的需求才能编辑"
            )

    @staticmethod
    def _requirement_to_fields(requirement) -> RequirementFields:
        """将数据库对象转换为字段模型"""
        return RequirementFields.model_validate(requirement)

    @staticmethod
    def get_requirement_fields(db: Session, thread_id: str, user_info: UserInfo):
        """获取需求的可编辑字段"""
        try:
            requirement = RequirementDAO.get_requirement_fields(db, thread_id)
            RequirementBIZ._validate_requirement_access(requirement, user_info)
            return RequirementBIZ._requirement_to_fields(requirement)
        except GeneralException:
            raise
        except SQLAlchemyError as e:
            raise GeneralException(ErrorCode.DATABASE_ERROR, detail=str(e))
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def update_requirement_fields(
        db: Session,
        thread_id: str,
        fields_update: RequirementFields,
        user_info: UserInfo,
    ):
        """更新需求的可编辑字段"""
        try:
            with db.begin():
                # 先获取并验证权限
                requirement = RequirementDAO.get_requirement_fields(db, thread_id)
                RequirementBIZ._validate_requirement_access(requirement, user_info)

                # 执行更新
                updated_requirement = RequirementDAO.update_requirement_fields(
                    db, thread_id, **fields_update.model_dump(exclude_none=True)
                )

                if not updated_requirement:
                    raise GeneralException(ErrorCode.DATABASE_ERROR, detail="更新失败")

                return RequirementBIZ._requirement_to_fields(updated_requirement)
        except GeneralException:
            raise
        except SQLAlchemyError as e:
            raise GeneralException(ErrorCode.DATABASE_ERROR, detail=str(e))
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))
