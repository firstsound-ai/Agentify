import json
from typing import TYPE_CHECKING

from fastapi import BackgroundTasks
from langchain_core.runnables.config import RunnableConfig
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from biz.agent.requirement.state import GraphState
from common.dto.requirement import (
    RequirementCreate,
    RequirementTaskResponse,
    TaskStatus,
    UserAnswers,
)
from common.dto.user import UserInfo
from common.enums.error_code import ErrorCode
from common.exceptions.general_exception import GeneralException
from dal.dao.requirement import RequirementDAO
from dal.database import get_db


class RequirementBIZ:
    @staticmethod
    async def create_requirement(
        db: Session,
        requirement: RequirementCreate,
        user_info: UserInfo,
        background_tasks: BackgroundTasks,
        checkpointer: "AsyncPostgresSaver",
    ):
        try:
            with db.begin():
                thread_id = RequirementDAO.create_requirement(
                    db, requirement, user_info
                )

            def start_background_processing():
                import asyncio

                new_db = next(get_db())

                # 在新事件循环中运行异步任务
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        RequirementBIZ._process_requirement_task(
                            thread_id,
                            requirement.initial_requirement,
                            new_db,
                            checkpointer,
                        )
                    )
                finally:
                    loop.close()

            background_tasks.add_task(start_background_processing)

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
                from biz.agent.requirement.state import Questionnaire

                response.questionnaire = Questionnaire.model_validate(
                    questionnaire_data
                )

            final_document_data = getattr(requirement, "final_document")
            print(final_document_data)
            if final_document_data:
                from biz.agent.requirement.state import RequirementDefinition

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
    async def _process_requirement_task(
        thread_id: str,
        initial_requirement: str,
        db: Session,
        checkpointer: "AsyncPostgresSaver",
    ):
        """处理需求的后台任务 - 使用LangGraph invoke执行工作流"""

        try:
            RequirementDAO.update_requirement_status(
                db, thread_id, TaskStatus.PROCESSING, "开始处理需求..."
            )

            # 获取LangGraph应用
            from biz.agent.requirement.graph import get_requirement_app

            app = await get_requirement_app(checkpointer)

            # 构建初始状态
            initial_state: GraphState = {
                "user_request": initial_requirement,
                "product_draft": None,
                "questionnaire": None,
                "user_answers": None,
                "final_document": None,
                "error": None,
            }

            # 配置LangGraph运行时
            config = RunnableConfig(configurable={"thread_id": thread_id})

            # 使用LangGraph的invoke方法执行工作流
            # 这会自动执行到interrupt点（user_answers_node）
            result = await app.ainvoke(initial_state, config=config)

            # 检查执行结果
            if result.get("error"):
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.FAILED,
                    "处理过程中发生错误",
                    error_message=result["error"],
                )
            elif result.get("questionnaire"):
                # 问卷生成成功，等待用户回答
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.WAITING_FOR_ANSWERS,
                    "问卷已生成，等待用户回答",
                    questionnaire=result["questionnaire"],
                )
            else:
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.FAILED,
                    "问卷生成失败",
                )

        except Exception as e:
            RequirementDAO.update_requirement_status(
                db,
                thread_id,
                TaskStatus.FAILED,
                "处理过程中发生错误",
                error_message=str(e),
            )
        finally:
            db.close()

    @staticmethod
    def submit_answers(
        db: Session,
        thread_id: str,
        user_answers: UserAnswers,
        user_info: UserInfo,
        background_tasks: BackgroundTasks,
        checkpointer: "AsyncPostgresSaver",
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

            # 保存用户答案
            RequirementDAO.update_requirement_status(
                db,
                thread_id,
                TaskStatus.PROCESSING,
                "已收到用户答案，正在生成最终文档...",
                user_answers=user_answers.answers,
            )

            # 启动后台任务继续处理
            def continue_processing():
                import asyncio

                new_db = next(get_db())

                # 在新事件循环中运行异步任务
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        RequirementBIZ._continue_requirement_task(
                            thread_id, user_answers.answers, new_db, checkpointer
                        )
                    )
                finally:
                    loop.close()

            background_tasks.add_task(continue_processing)

            return {"message": "答案已提交，正在生成最终文档..."}

        except GeneralException:
            raise
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def _continue_requirement_task(
        thread_id: str,
        user_answers: dict,
        db: Session,
        checkpointer: "AsyncPostgresSaver",
    ):
        """继续处理需求任务 - 恢复LangGraph执行并提供用户答案"""

        try:
            # 获取LangGraph应用
            from biz.agent.requirement.graph import get_requirement_app

            app = await get_requirement_app(checkpointer)

            # 配置LangGraph运行时
            config = RunnableConfig(configurable={"thread_id": thread_id})

            RequirementDAO.update_requirement_status(
                db, thread_id, TaskStatus.PROCESSING, "正在生成最终需求文档..."
            )

            # 更新状态，提供用户答案后继续执行
            await app.aupdate_state(config, {"user_answers": user_answers})

            # 继续执行工作流
            result = None
            async for event in app.astream(None, config=config):
                if event:
                    result = event

            # 处理最终文档
            final_document_data = None
            if result and result.get("final_document"):
                final_document_raw = result["final_document"]
                if hasattr(final_document_raw, "content"):
                    # 如果是 AI 消息，解析其内容
                    try:
                        content = str(final_document_raw.content).strip()
                        if content.startswith("```json"):
                            content = content[7:]
                        if content.endswith("```"):
                            content = content[:-3]
                        final_document_data = json.loads(content.strip())
                    except json.JSONDecodeError:
                        # 如果解析失败，直接使用内容
                        final_document_data = {
                            "content": str(final_document_raw.content)
                        }
                elif hasattr(final_document_raw, "dict"):
                    final_document_data = final_document_raw.dict()
                elif isinstance(final_document_raw, dict):
                    final_document_data = final_document_raw
                else:
                    final_document_data = {"content": str(final_document_raw)}

            if result and result.get("error"):
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.FAILED,
                    "生成最终文档时发生错误",
                    error_message=result["error"],
                )
            elif final_document_data:
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.COMPLETED,
                    "最终需求文档已生成完成",
                    final_document=final_document_data,
                )
            else:
                RequirementDAO.update_requirement_status(
                    db,
                    thread_id,
                    TaskStatus.FAILED,
                    "最终文档生成失败",
                )

        except Exception as e:
            RequirementDAO.update_requirement_status(
                db,
                thread_id,
                TaskStatus.FAILED,
                "生成最终文档时发生错误",
                error_message=str(e),
            )
        finally:
            db.close()
