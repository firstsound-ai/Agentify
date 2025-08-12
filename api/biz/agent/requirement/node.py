import json

from langgraph.types import interrupt

from biz.agent.requirement.prompt import DRAFT_PROMPT, FINALIZE_PROMPT, QUESTIONS_PROMPT
from biz.agent.requirement.state import GraphState
from common.utils.get_llm_model import get_llm_model

llm = get_llm_model(model_name="gemini-2.5-flash", temperature=0.5)

draft_chain = DRAFT_PROMPT | llm
questionnaire_chain = QUESTIONS_PROMPT | llm
finalizer_chain = FINALIZE_PROMPT | llm


def generate_draft_node(state: GraphState):
    print("--- 节点: 生成产品草案 ---")
    response = draft_chain.invoke({"user_request": state["user_request"]})
    print("生成的草案:", response.content)
    return {"product_draft": response.content}


def generate_questions_node(state: GraphState):
    print("--- 节点: 生成结构化问卷 ---")
    response = questionnaire_chain.invoke({"product_draft": state["product_draft"]})
    assert isinstance(response.content, str)
    questions = response.content.strip("```json").strip("```")
    questions = json.loads(questions)
    return {"questionnaire": questions}


def finalize_document_node(state: GraphState):
    print("--- 节点: 生成最终需求档案 ---")
    answers_str = json.dumps(state["user_answers"], ensure_ascii=False, indent=2)
    response = finalizer_chain.invoke(
        {"product_draft": state["product_draft"], "user_answers": answers_str}
    )
    return {"final_document": response}


def user_answers_node(state: GraphState):
    """
    用户回答处理节点

    这个节点会中断执行，等待用户提供问卷答案。
    当用户提交答案后，LangGraph会恢复执行并继续到下一个节点。
    """
    print("--- 节点: 等待用户回答 ---")

    # 中断执行，等待用户输入
    # interrupt会暂停图的执行，直到外部系统提供答案
    user_answers = interrupt(
        value={
            "message": "等待用户回答问卷",
            "questionnaire": state.get("questionnaire"),
            "required": True,
        }
    )

    if user_answers:
        print("用户回答:", user_answers)
        return {"user_answers": user_answers}

    # 如果没有答案，返回错误状态
    return {"error": "未收到用户答案"}
