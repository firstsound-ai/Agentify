import json

from langgraph.types import interrupt

from biz.agent.requirement.prompt import DRAFT_PROMPT, FINALIZE_PROMPT, QUESTIONS_PROMPT
from biz.agent.requirement.state import GraphState
from common.utils.get_llm_model import get_llm_model

llm = get_llm_model(model_name="gemini-2.5-pro", temperature=0.5)

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
    """生成最终需求档案"""
    print("--- 节点: 生成最终需求档案 ---")

    # 处理用户答案数据
    user_answers_data = _extract_user_answers(state)
    answers_str = json.dumps(user_answers_data, ensure_ascii=False, indent=2)

    # 处理问卷数据
    questionnaire_str = _extract_questionnaire(state)

    # 处理额外要求
    additional_requirements = _extract_additional_requirements(state)

    # 调用AI生成最终文档
    response = finalizer_chain.invoke(
        {
            "product_draft": state["product_draft"],
            "questionnaire": questionnaire_str,
            "user_answers": answers_str,
            "additional_requirements": additional_requirements,
        }
    )
    print("生成的最终文档:", response.content)
    return {"final_document": response}


def _extract_user_answers(state: GraphState) -> list:
    """提取并格式化用户答案"""
    from biz.agent.requirement.state import UserAnswer

    user_answers_raw = state.get("user_answers")
    if not user_answers_raw:
        return []

    # 解构从Command传来的数据
    if isinstance(user_answers_raw, dict) and "user_answers" in user_answers_raw:
        user_answers = user_answers_raw.get("user_answers")  # type: ignore
    else:
        user_answers = user_answers_raw

    if not isinstance(user_answers, (list, tuple)):
        return []

    result = []
    for answer in user_answers:
        if isinstance(answer, UserAnswer):
            result.append(
                {
                    "question_id": answer.question_id,
                    "selected_option": answer.selected_option,
                    "custom_input": answer.custom_input,
                }
            )
        elif isinstance(answer, dict):
            result.append(
                {
                    "question_id": answer.get("question_id"),
                    "selected_option": answer.get("selected_option"),
                    "custom_input": answer.get("custom_input"),
                }
            )

    return result


def _extract_questionnaire(state: GraphState) -> str:
    """提取并格式化问卷数据"""
    questionnaire_data = state.get("questionnaire")
    if not questionnaire_data:
        return ""

    if hasattr(questionnaire_data, "model_dump"):
        return json.dumps(questionnaire_data.model_dump(), ensure_ascii=False, indent=2)
    else:
        return json.dumps(questionnaire_data, ensure_ascii=False, indent=2)


def _extract_additional_requirements(state: GraphState) -> str:
    """提取额外要求"""
    user_answers_raw = state.get("user_answers")

    # 从Command传来的数据中提取
    if (
        isinstance(user_answers_raw, dict)
        and "additional_requirements" in user_answers_raw
    ):
        return str(user_answers_raw.get("additional_requirements") or "无额外要求")

    # 从state中直接提取
    return str(state.get("additional_requirements") or "无额外要求")


def user_answers_node(state: GraphState):
    """用户回答处理节点"""
    print("--- 节点: 等待用户回答 ---")

    # 检查是否已经有用户答案（通过Command恢复执行时）
    if state.get("user_answers") is not None:
        return {
            "user_answers": state["user_answers"],
            "additional_requirements": state.get("additional_requirements"),
        }

    # 中断执行，等待用户输入
    user_answers = interrupt(
        value={
            "message": "等待用户回答问卷",
            "questionnaire": state.get("questionnaire"),
            "required": True,
        }
    )

    return (
        {"user_answers": user_answers} if user_answers else {"error": "未收到用户答案"}
    )
