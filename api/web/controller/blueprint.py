import json

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from biz.service.blueprint import BlueprintBIZ
from common.dto.blueprint import PromptRequest
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
    db: Session = Depends(get_db),
):
    # blueprint_id = BlueprintBIZ.create_blueprint(
    #     db, thread_id, user_info, background_tasks
    # )
    blueprint_id = "073e09e7-35b2-4c05-a053-e401ccb92174"
    return Result.success(data={"blueprint_id": blueprint_id})


@router.get("/list/{thread_id}")
def get_blueprint_list(
    thread_id: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    result = BlueprintBIZ.get_blueprint_list(db, thread_id, user_info)
    return Result.success(data={"blueprints": result})


@router.get("/latest/{thread_id}")
def get_latest_blueprint(
    thread_id: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    result = BlueprintBIZ.get_latest_blueprint(db, thread_id)
    return Result.success(data=result)


@router.get("/status/{blueprintId}")
def get_blueprint_status(
    blueprintId: str,
    user_info: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db),
):
    result = BlueprintBIZ.get_blueprint_status(db, blueprintId, user_info)
    return Result.success(data=result)


@router.post("/chat/completions/{thread_id}")
async def stream_chat(
    thread_id: str,
    request_body: PromptRequest,  # 从JSON Body获取
    db: Session = Depends(get_db),
):
    print("received the request")
    # latest_blueprint = BlueprintBIZ.get_latest_blueprint(db, thread_id)
    # workflow = getattr(latest_blueprint, "workflow")

    def event_generator():
        messages = [
            "好的",
            "，",
            "已",
            "收到",
            "您的",
            "需求",
            "，",
            "添加",
            "一个",
            "新的",
            "节点",
            "来写博客",
            "的引言",
            "会让最终",
            "的报告",
            "质量",
            "更高。",
            "让我",
            "为",
            "您",
            "更新",
            "工作",
            "流",
            "步骤",
            "和",
            "流程图",
        ]

        for chunk in messages:
            sse_data = f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}"
            yield sse_data

        import time

        time.sleep(3)
        final_workflow = {
            "workflowId": "wf_seo_blog_gen_real_001",
            "workflowName": "自动化SEO博客生成器",
            "startNodeId": "node_001",
            "nodes": {
                "node_001": {
                    "nodeTitle": "捕获用户输入",
                    "nodeType": "TRIGGER_USER_INPUT",
                    "nodeDescription": "获取关键词、可选标题、受众、语气和需规避的品牌词。",
                    "edges": [
                        {"sourceHandle": "default", "targetNodeId": "node_cond_002"}
                    ],
                },
                "node_cond_002": {
                    "nodeTitle": "检查用户是否提供标题",
                    "nodeType": "CONDITION_BRANCH",
                    "nodeDescription": "判断依据：'标题'字段是否为空。",
                    "edges": [
                        {"sourceHandle": "onSuccess", "targetNodeId": "node_003_a"},
                        {"sourceHandle": "onFailure", "targetNodeId": "node_003_b"},
                    ],
                },
                "node_003_a": {
                    "nodeTitle": "搜索以生成标题",
                    "nodeType": "ACTION_WEB_SEARCH",
                    "nodeDescription": "当标题为空时，使用'关键词'进行搜索，为生成标题提供上下文。",
                    "edges": [
                        {"sourceHandle": "default", "targetNodeId": "node_004_a"}
                    ],
                },
                "node_003_b": {
                    "nodeTitle": "从标题生成关键词",
                    "nodeType": "ACTION_LLM_TRANSFORM",
                    "nodeDescription": "当标题已有时，从'标题'中提炼出核心搜索短语。",
                    "edges": [{"sourceHandle": "default", "targetNodeId": "node_005"}],
                },
                "node_004_a": {
                    "nodeTitle": "生成SEO优化标题",
                    "nodeType": "ACTION_LLM_TRANSFORM",
                    "nodeDescription": "基于搜索结果，为用户的'关键词'生成一个新标题。",
                    "edges": [{"sourceHandle": "default", "targetNodeId": "node_005"}],
                },
                "node_005": {
                    "nodeTitle": "生成最终搜索语句",
                    "nodeType": "ACTION_LLM_TRANSFORM",
                    "nodeDescription": "融合已有信息（用户标题或生成标题）和'受众'，生成一个用于深度研究的、更精确的搜索查询。",
                    "edges": [{"sourceHandle": "default", "targetNodeId": "node_006"}],
                },
                "node_006": {
                    "nodeTitle": "为文章内容进行深度搜索",
                    "nodeType": "ACTION_WEB_SEARCH",
                    "nodeDescription": "使用生成的最终搜索语句执行Google搜索，获取权威信息。",
                    "edges": [{"sourceHandle": "default", "targetNodeId": "node_007"}],
                },
                "node_007": {
                    "nodeTitle": "生成文章大纲",
                    "nodeType": "ACTION_LLM_TRANSFORM",
                    "nodeDescription": "基于深度搜索结果，并结合全部用户输入，生成详细的文章大纲。",
                    "edges": [{"sourceHandle": "default", "targetNodeId": "node_008"}],
                },
                "node_008": {
                    "nodeTitle": "撰写文章引言",
                    "nodeType": "ACTION_LLM_TRANSFORM",
                    "nodeDescription": "根据大纲，独立生成文章的引言部分。",
                    "edges": [{"sourceHandle": "default", "targetNodeId": "node_009"}],
                },
                "node_009": {
                    "nodeTitle": "撰写文章主体",
                    "nodeType": "ACTION_LLM_TRANSFORM",
                    "nodeDescription": "根据大纲，独立生成文章的主体部分。",
                    "edges": [
                        {
                            "sourceHandle": "default",
                            "targetNodeId": "node_final_010",
                        }
                    ],
                },
                "node_final_010": {
                    "nodeTitle": "整合内容并格式化输出",
                    "nodeType": "OUTPUT_FORMAT",
                    "nodeDescription": "将引言和主体部分合并，最终输出为一篇完整的Markdown格式文章。",
                    "edges": [],
                },
            },
        }
        final_mermaid = """graph TD
    node001["node_001: 捕获用户输入<br>(TRIGGER_USER_INPUT)"]
    nodeCond002{{"node_cond_002: 检查用户是否提供标题<br>(CONDITION_BRANCH)<br>判断依据：'标题'字段是否为空。"}}
    node003a["node_003_a: 搜索以生成标题<br>(ACTION_WEB_SEARCH)"]
    node003b["node_003_b: 从标题生成关键词<br>(ACTION_LLM_TRANSFORM)"]
    node004a["node_004_a: 生成SEO优化标题<br>(ACTION_LLM_TRANSFORM)"]
    node005["node_005: 生成最终搜索语句<br>(ACTION_LLM_TRANSFORM)"]
    node006["node_006: 为文章内容进行深度搜索<br>(ACTION_WEB_SEARCH)"]
    node007["node_007: 生成文章大纲<br>(ACTION_LLM_TRANSFORM)"]
    node008["node_008: 撰写文章引言<br>(ACTION_LLM_TRANSFORM)"]
    node009["node_009: 撰写文章主体<br>(ACTION_LLM_TRANSFORM)"]
    nodeFinal010["node_final_010: 整合内容并格式化输出<br>(OUTPUT_FORMAT)"]

    node001 -->|default| nodeCond002
    nodeCond002 -->|"标题为空(onSuccess)"| node003a
    nodeCond002 -->|"已有标题(onFailure)"| node003b
    node003a -->|default| node004a
    node003b -->|default| node005
    node004a -->|default| node005
    node005 -->|default| node006
    node006 -->|default| node007
    node007 -->|default| node008
    node008 -->|default| node009
    node009 -->|default| nodeFinal010
"""
        BlueprintBIZ.update_blueprint_by_thread(
            thread_id, final_workflow, final_mermaid
        )
        sse_data = f"data: {json.dumps({'chunk': '工作流和流程图已更新完毕！'}, ensure_ascii=False)}"
        yield sse_data

        # try:
        #     # 转换消息为LangChain的Message对象
        #     # messages = [HumanMessage(content=request_body.prompt)]
        #     # 初始化状态
        #     initial_state = {
        #         "initial_messages": request_body.prompt,
        #         "workflow": workflow,
        #         "refined_workflow": None,
        #         "decision": None,
        #         "mermaid_code": None,
        #     }
        #     # 获取工作流应用
        #     chat_workflow = get_chat_workflow()
        #     config = RunnableConfig(configurable={"thread_id": thread_id})
        #     decision = None
        #     # 运行工作流并生成事件流
        #     for output in chat_workflow.stream(
        #         initial_state, config=config, stream_mode="messages"
        #     ):
        #         if output[0] and output[0].content:
        #             # 构建SSE格式数据
        #             if output[0].content in ["update", "end"]:
        #                 decision = output[0].content

        #             if decision is None:
        #                 sse_data = f"data: {json.dumps({'chunk': output[0].content}, ensure_ascii=False)}"
        #                 yield sse_data

        #     from dal.checkpointer import get_checkpointer

        #     checkpointer = get_checkpointer()
        #     checkpoint = checkpointer.get({"configurable": {"thread_id": thread_id}})

        #     if checkpoint:
        #         if decision == "end":
        #             sse_data = f"data: {json.dumps({'chunk': '目前无需更新工作流。'}, ensure_ascii=False)}"
        #             yield sse_data
        #         else:
        #             print("开始更新")
        #             final_workflow = checkpoint["channel_values"].get(
        #                 "refined_workflow"
        #             )
        #             final_mermaid = checkpoint["channel_values"].get("mermaid_code")

        #             print("checkpoint", checkpoint["channel_values"])

        #             if final_workflow and final_mermaid:
        #                 BlueprintBIZ.update_blueprint_by_thread(
        #                     thread_id, final_workflow, final_mermaid
        #                 )
        #                 print("已经更新")
        #                 sse_data = f"data: {json.dumps({'chunk': '工作流和流程图已更新完毕！'}, ensure_ascii=False)}"
        #                 yield sse_data

        # except Exception as e:
        #     import traceback

        #     traceback.print_exc()
        #     # 错误处理
        #     error_data = json.dumps(
        #         {
        #             "error": str(e),
        #             "chunk": "",
        #         },
        #         ensure_ascii=False,
        #     )
        #     yield f"data: {error_data}"

    return EventSourceResponse(event_generator())
