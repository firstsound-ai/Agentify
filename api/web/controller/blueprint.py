from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
import json

from biz.service.blueprint import BlueprintBIZ
from biz.service.llm import LLMBIZ
from common.dto.user import UserInfo
from common.utils.get_user import get_user_info
from dal.database import get_db
from web.vo.result import Result

from pydantic import BaseModel
from biz.agent.blueprint.chat_graph import get_chat_workflow
from langchain_core.runnables.config import RunnableConfig
from common.dto.blueprint import PromptRequest
from pydantic import BaseModel

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

@router.get("/latest/{thread_id}")
def get_latest_blueprint(
    thread_id: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db)
):
    result = BlueprintBIZ.get_latest_blueprint(
        db, thread_id
    )
    return Result.success(data=result)

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

@router.post("/chat/completions/{thread_id}")
async def stream_chat(
    thread_id: str,
    request_body: PromptRequest,  # 从JSON Body获取
    db: Session = Depends(get_db)
):
    latest_blueprint = BlueprintBIZ.get_latest_blueprint(db, thread_id)
    workflow = getattr(latest_blueprint, "workflow")
    workflow = json.dumps(workflow, ensure_ascii=False)

    def event_generator():
        try:
            # 转换消息为LangChain的Message对象
            # messages = [HumanMessage(content=request_body.prompt)]
            # 初始化状态
            initial_state = {
                "initial_messages": request_body.prompt,
                "workflow": workflow,
                "refined_workflow": None,
                "decision": None,
                "mermaid_code": None
            }
            # 获取工作流应用
            chat_workflow = get_chat_workflow()
            config = RunnableConfig(configurable={"thread_id": thread_id})

            # 运行工作流并生成事件流
            for output in chat_workflow.stream(initial_state, config=config, stream_mode="messages"):
                if output[0] and output[0].content:
                    # 构建SSE格式数据
                    sse_data = f"data: {json.dumps({'chunk': output[0].content}, ensure_ascii=False)}\n\n"
                    yield sse_data

            from dal.checkpointer import get_checkpointer
            checkpointer = get_checkpointer()
            checkpoint = checkpointer.get({"configurable": {"thread_id": thread_id}})

            if checkpoint:
                decision = checkpoint["channel_values"].get("decision")

                if decision == "end":
                    sse_data = f"data: {json.dumps({'chunk': "No need for update."}, ensure_ascii=False)}\n\n"
                    yield sse_data
                else:
                    final_workflow = checkpoint["channel_values"].get("refined_workflow")
                    final_mermaid = checkpoint["channel_values"].get("mermaid_code")

                    if final_workflow and final_mermaid:
                        BlueprintBIZ.update_blueprint_by_thread(thread_id, final_workflow, final_mermaid)
                        print("已经更新")
                        sse_data = f"data: {json.dumps({'chunk': "Workflow and mermaid have been updated."}, ensure_ascii=False)}\n\n"
                        yield sse_data

        except Exception as e:
            import traceback
            traceback.print_exc()
            # 错误处理
            error_data = json.dumps({
                "error": str(e),
                "chunk": "",
            }, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    return EventSourceResponse(event_generator())
