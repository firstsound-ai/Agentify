import json


from biz.agent.blueprint.prompt import WORKFLOW_PROMPT, MERMAID_PROMPT
from biz.agent.blueprint.state import GraphState
from common.utils.get_llm_model import get_llm_model

# llm = get_llm_model(model_name="gemini-2.5-flash", temperature=0.5)
llm = get_llm_model(model_name="Qwen/Qwen3-30B-A3B-Instruct-2507", temperature=0.5)

workflow_chain = WORKFLOW_PROMPT | llm
mermaid_chain = MERMAID_PROMPT | llm


def generate_workflow_node(state: GraphState):
    print("--- 节点：生成工作流蓝图 ---")
    response = workflow_chain.invoke({"final_document": state["final_document"]})
    # print("生成的workflow:\n", response.content)

    assert isinstance(response.content, str)
    workflow = response.content.strip("```json").strip("```")
    workflow = json.loads(workflow)
    print(f"workflow\n{workflow}")
    return {"workflow": workflow}


def generate_mermaid_node(state: GraphState):
    print("--- 节点：生成mermaid流程图代码 ---")
    response = mermaid_chain.invoke({"workflow": state["workflow"]})
    print("生成的mermaid", response.content)
    return {"mermaid_code": response.content}
