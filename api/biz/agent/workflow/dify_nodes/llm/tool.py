from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from ..base import Node, NodePosition
from .node import LLMNodeData
from .type import (
    LLMCompletionParams,
    LLMModel,
    PromptTemplateItem,
)


@tool
def create_llm_node(
    node_id: str,
    x_pos: int,
    y_pos: int,
    prompt_messages: List[Dict[str, str]],
    title: str = "语言模型",
    model_provider: str = "langgenius/siliconflow/siliconflow",
    model_name: str = "deepseek-ai/DeepSeek-V3",
    temperature: float = 0.7,
    stop_sequences: Optional[List[str]] = None,
    desc: str = "执行语言模型推理",
) -> Dict[str, Any]:
    """
    在工作流中创建一个大语言模型（LLM）节点。
    当用户需要使用AI进行文本生成、分析、分类、摘要或进行多轮对话的其中一步时，使用此工具。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "llm_step_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        prompt_messages (List[Dict[str, str]]): 定义LLM提示词的消息列表。每个字典包含'role'和'text'。
            'role' 可以是 "system", "user", 或 "assistant"。
            'text' 是该角色的具体内容，可以引用其他节点的输出，例如 '{{#sys.query#}}' 或 '{{#previous_node.output#}}'。
            示例: [{"role": "system", "text": "你是一个专业的翻译家。"}, {"role": "user", "text": "将'{{#sys.query#}}'翻译成中文。"}]
        title (str, optional): 节点的显示标题。默认为 "语言模型"。
        model_provider (str, optional): LLM模型的提供商。默认为 "langgenius/siliconflow/siliconflow"。
        model_name (str, optional): LLM模型的具体名称。默认为 "deepseek-ai/DeepSeek-V3"。
        temperature (float, optional): 控制生成文本的随机性 (0.0-2.0)。值越高越随机。默认为 0.7。
        desc (str, optional): 节点的可选描述信息。默认为 "执行语言模型推理"。

    Returns:
        Dict[str, Any]: 代表该LLM节点的字典结构，可用于工作流编排。
    """
    if stop_sequences is None:
        stop_sequences = []

    prompt_template = [
        PromptTemplateItem(role=msg.get("role", "user"), text=msg.get("text", ""))
        for msg in prompt_messages
    ]

    completion_params = LLMCompletionParams(temperature=temperature)

    llm_node_data = LLMNodeData(
        title=title,
        desc=desc,
        model=LLMModel(
            provider=model_provider,
            name=model_name,
            completion_params=completion_params,
        ),
        prompt_template=prompt_template,
    )

    llm_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=llm_node_data,
        width=320,
        height=180,
    )

    print(llm_node)

    # return llm_node.to_dict()

    return {
        "node": llm_node.to_dict(),
        "observation": f"已经创建了一个名为{title}的LLM节点。节点的描述为：{desc}",
        "output": llm_node.get_output_variable_references(),
    }
