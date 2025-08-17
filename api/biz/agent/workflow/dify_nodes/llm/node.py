from dataclasses import dataclass, field
from typing import List

from ..base import BaseNodeData, OutputVariable
from .type import (
    LLMCompletionParams,
    LLMContext,
    LLMMemory,
    LLMModel,
    LLMVision,
    PromptTemplateItem,
)


@dataclass
class LLMNodeData(BaseNodeData):
    type: str = "llm"
    title: str = "LLM"
    model: LLMModel = field(
        default_factory=lambda: LLMModel(
            provider="langgenius/siliconflow/siliconflow",
            name="deepseek-ai/DeepSeek-V3",
            mode="chat",
            completion_params=LLMCompletionParams(temperature=0.7),
        )
    )
    prompt_template: List[PromptTemplateItem] = field(
        default_factory=lambda: [PromptTemplateItem(role="system", text="")]
    )
    context: LLMContext = field(default_factory=LLMContext)
    vision: LLMVision = field(default_factory=LLMVision)
    memory: LLMMemory = field(default_factory=LLMMemory)
    output_variables: List[OutputVariable] = field(
        default_factory=lambda: [
            OutputVariable(
                variable="text",
                label="文本输出",
                type="text",
                description="LLM生成的文本内容",
            ),
            OutputVariable(
                variable="usage",
                label="使用统计",
                type="json",
                description="Token使用统计信息",
            ),
        ]
    )
