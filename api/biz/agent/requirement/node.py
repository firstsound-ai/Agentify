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

    # 格式化用户答案为JSON字符串
    user_answers_data = []
    user_answers_raw = state.get("user_answers")

    # 调试输出
    print(f"DEBUG: user_answers 类型: {type(user_answers_raw)}")
    print(f"DEBUG: user_answers 内容: {user_answers_raw}")

    # 如果 user_answers 是一个字典（从 Command resume 传来），需要解构
    if isinstance(user_answers_raw, dict) and "user_answers" in user_answers_raw:
        user_answers = user_answers_raw.get("user_answers")  # type: ignore
    else:
        user_answers = user_answers_raw

    if user_answers:
        from biz.agent.requirement.state import UserAnswer

        # 确保 user_answers 是一个列表
        if isinstance(user_answers, (list, tuple)):
            for answer in user_answers:
                # 处理不同类型的答案数据
                if isinstance(answer, UserAnswer):
                    user_answers_data.append(
                        {
                            "question_id": answer.question_id,
                            "selected_option": answer.selected_option,
                            "custom_input": answer.custom_input,
                        }
                    )
                elif isinstance(answer, dict):
                    user_answers_data.append(
                        {
                            "question_id": answer.get("question_id"),
                            "selected_option": answer.get("selected_option"),
                            "custom_input": answer.get("custom_input"),
                        }
                    )
                else:
                    print(f"警告: 未知的答案类型 {type(answer)}: {answer}")
                    continue
        else:
            print(f"错误: user_answers 不是列表类型: {type(user_answers)}")
            return {"error": f"user_answers 数据类型错误: {type(user_answers)}"}

    answers_str = json.dumps(user_answers_data, ensure_ascii=False, indent=2)

    # 格式化问卷为JSON字符串
    questionnaire_str = ""
    if state["questionnaire"]:
        questionnaire_data = state["questionnaire"]
        if hasattr(questionnaire_data, "model_dump"):
            questionnaire_str = json.dumps(
                questionnaire_data.model_dump(), ensure_ascii=False, indent=2
            )
        else:
            questionnaire_str = json.dumps(
                questionnaire_data, ensure_ascii=False, indent=2
            )

    # 获取额外要求
    additional_requirements_raw = state.get("additional_requirements", "")

    # 如果 additional_requirements 在 user_answers 字典中，需要解构
    if (
        isinstance(user_answers_raw, dict)
        and "additional_requirements" in user_answers_raw
    ):
        additional_requirements = (
            user_answers_raw.get("additional_requirements", "") or "无额外要求"
        )  # type: ignore
    else:
        additional_requirements = additional_requirements_raw or "无额外要求"

    # 调试输出
    print(f"DEBUG: additional_requirements 类型: {type(additional_requirements)}")
    print(f"DEBUG: additional_requirements 内容: {additional_requirements}")

    # 确保 additional_requirements 是字符串类型
    if not isinstance(additional_requirements, str):
        print(
            f"警告: additional_requirements 不是字符串类型: {type(additional_requirements)}"
        )
        additional_requirements = (
            str(additional_requirements) if additional_requirements else "无额外要求"
        )

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


def user_answers_node(state: GraphState):
    """
    用户回答处理节点

    这个节点会中断执行，等待用户提供问卷答案。
    当用户提交答案后，LangGraph会恢复执行并继续到下一个节点。
    """
    print("--- 节点: 等待用户回答 ---")

    # 检查是否已经有用户答案（通过 Command 恢复执行时）
    if state.get("user_answers") is not None:
        print("用户回答已提供:", state["user_answers"])
        return {
            "user_answers": state["user_answers"],
            "additional_requirements": state.get("additional_requirements"),
        }

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
