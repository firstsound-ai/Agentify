import json

from fastapi import BackgroundTasks
from langchain_core.runnables.config import RunnableConfig
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from biz.agent.blueprint.graph import get_blueprint_workflow
from biz.agent.workflow.graph import get_workflow_agent
from biz.agent.blueprint.state import GraphState
from common.dto.blueprint import BlueprintResponse, Workflow
from common.dto.user import UserInfo
from common.enums.error_code import ErrorCode
from common.enums.task import TaskStatus
from common.exceptions.general_exception import GeneralException
from dal.dao.requirement import RequirementDAO
from dal.dao.blueprint import BlueprintDAO
from dal.database import get_db


class BlueprintBIZ:
    @staticmethod
    def create_blueprint(
        db: Session,
        thread_id: str,
        user_info: UserInfo,
        background_tasks: BackgroundTasks,
    ):
        try:
            with db.begin():
                requirement = RequirementDAO.get_requirement_by_id(db, thread_id)

                if not requirement:
                    raise GeneralException(ErrorCode.NOT_FOUND, detail="需求不存在")

                if getattr(requirement, "user_id") != user_info.id:
                    raise GeneralException(
                        ErrorCode.FORBIDDEN, detail="无权限访问此需求"
                    )

                if getattr(requirement, "final_document") is None:
                    raise GeneralException(ErrorCode.NOT_FOUND, detail="文档尚未生成")

                blueprint_id = BlueprintDAO.create_blueprint(db, thread_id, user_info)

            background_tasks.add_task(
                BlueprintBIZ._process_blueprint_task,
                blueprint_id,
                requirement.final_document,
            )

            return blueprint_id
        except SQLAlchemyError as e:
            raise GeneralException(ErrorCode.DATABASE_ERROR, detail=str(e))
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def get_blueprint_list(
        db: Session,
        thread_id: str,
        user_info: UserInfo,
    ):
        try:
            requirement = RequirementDAO.get_requirement_by_id(db, thread_id)

            if not requirement:
                raise GeneralException(ErrorCode.NOT_FOUND, detail="需求不存在")

            if getattr(requirement, "user_id") != user_info.id:
                raise GeneralException(ErrorCode.FORBIDDEN, detail="无权限访问此需求")

            blueprint_list = BlueprintDAO.get_blueprint_list(db, thread_id)
            result = [bp.__dict__ for bp in blueprint_list]
            required_fields = ["status", "id", "created_at"]
            clean_result = [
                {k: v for k, v in item.items() if k in required_fields}
                for item in result
            ]
            return clean_result

        except GeneralException:
            raise
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def get_latest_blueprint(
        db: Session,
        thread_id: str,
    ):
        try:
            blueprint = BlueprintDAO.get_lastest_blueprint(db, thread_id)

            response = BlueprintResponse(
                blueprint_id=blueprint.id,
                status=TaskStatus(getattr(blueprint, "status")),
                progress=getattr(blueprint, "progress") or "处理中...",
            )

            workflow_data = getattr(blueprint, "workflow")
            if workflow_data:
                response.workflow = Workflow.model_validate(workflow_data)

            mermaid_code_data = getattr(blueprint, "mermaid_code")
            if mermaid_code_data:
                response.mermaid_code = mermaid_code_data

            error_message = getattr(blueprint, "error_message")
            if error_message:
                response.error = error_message

            return response

        except GeneralException:
            raise
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def get_blueprint_status(
        db: Session, blueprint_id: str, user_info: UserInfo
    ) -> BlueprintResponse:
        try:
            blueprint = BlueprintDAO.get_blueprint_by_id(db, blueprint_id)

            if not blueprint:
                raise GeneralException(ErrorCode.NOT_FOUND, detail="蓝图不存在")

            response = BlueprintResponse(
                blueprint_id=blueprint_id,
                status=TaskStatus(getattr(blueprint, "status")),
                progress=getattr(blueprint, "progress") or "处理中...",
            )

            workflow_data = getattr(blueprint, "workflow")
            print("wd", workflow_data)

            if workflow_data:
                response.workflow = Workflow.model_validate(workflow_data)


            mermaid_code_data = getattr(blueprint, "mermaid_code")
            if mermaid_code_data:
                response.mermaid_code = mermaid_code_data

            error_message = getattr(blueprint, "error_message")
            if error_message:
                response.error = error_message

            return response

        except GeneralException:
            raise
        except Exception as e:
            raise GeneralException(ErrorCode.INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def update_blueprint_by_thread(thread_id, final_workflow, final_mermaid):
        db = next(get_db())
        BlueprintDAO.save_new_blueprint(
            db, thread_id, workflow=final_workflow, mermaid_code=final_mermaid
        )
        db.commit()

    @staticmethod
    def _process_blueprint_task(blueprint_id: str, final_document: str):
        db = next(get_db())

        try:
            BlueprintDAO.update_blueprint_status(
                db, blueprint_id, TaskStatus.PROCESSING, "开始处理需求..."
            )
            app = get_blueprint_workflow()

            initial_state: GraphState = {
                "final_document": json.dumps(final_document),
                "workflow": None,
                "mermaid_code": None,
                "error": None,
            }

            config = RunnableConfig(configurable={"thread_id": blueprint_id})
            result = app.invoke(initial_state, config=config)

            if result.get("error"):
                BlueprintDAO.update_blueprint_status(
                    db,
                    blueprint_id,
                    TaskStatus.FAILED,
                    "处理过程中发生错误",
                    error_message=result["error"],
                )
                db.commit()
            elif result.get("workflow") and result.get("mermaid_code"):
                BlueprintDAO.update_blueprint_status(
                    db,
                    blueprint_id,
                    TaskStatus.COMPLETED,
                    "工作流和流程图均已生成",
                    workflow=result["workflow"],
                    mermaid_code=result["mermaid_code"],
                )
                db.commit()
            else:
                BlueprintDAO.update_requirement_status(
                    db,
                    blueprint_id,
                    TaskStatus.FAILED,
                    "蓝图生成失败！",
                )
                db.commit()

        except Exception as e:
            import traceback

            error_traceback = traceback.format_exc()

            BlueprintDAO.update_blueprint_status(
                db,
                blueprint_id,
                TaskStatus.FAILED,
                "处理过程中发生错误",
                error_message=str(e),
            )
            print(error_traceback)
            db.commit()
        finally:
            db.close()

    def get_appid_by_thread(db: Session, user_info: UserInfo, thread_id: str):
        requirement = RequirementDAO.get_requirement_by_id(db, thread_id)

        requirement_doc_keys = [
            "requirement_name",
            "mission_statement",
            "user_and_scenario",
            "user_input",
            "ai_output",
            "success_criteria",
            "boundaries_and_limitations",
        ]

        requirement_doc_json = {
            key: getattr(requirement, key) for key in requirement_doc_keys
        }

        blueprint = BlueprintDAO.get_lastest_blueprint(db, thread_id)
        
        sop_json = getattr(blueprint, "workflow")

        app = get_workflow_agent()

        initial_input = {
            "requirement_doc": requirement_doc_json,
            "sop": sop_json,
            "nodes_created": [],
            "available_variables": [],
            "messages": [],
        }

        config = RunnableConfig(configurable={"thread_id": thread_id})
        final_state = app.invoke(initial_input, config=config)

        print("node init")
        print(json.dumps(final_state["nodes_created"], indent=2, ensure_ascii=False))
        return None
