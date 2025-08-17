from dataclasses import dataclass, field
from typing import Any, List

from ..base import BaseNodeData, OutputVariable
from ..llm.type import (
    LLMModel,
    LLMVision,
)
from .type import QuestionClassifierClass


@dataclass
class QuestionClassifierNodeData(BaseNodeData):
    type: str = "question-classifier"
    title: str = "问题分类器"
    desc: str = ""
    instructions: str = ""

    query_variable_selector: List[Any] = field(default_factory=list)
    topics: List[Any] = field(default_factory=list)
    model: LLMModel = field(default_factory=LLMModel)
    classes: List[QuestionClassifierClass] = field(
        default_factory=lambda: [
            QuestionClassifierClass(id="1", name=""),
            QuestionClassifierClass(id="2", name=""),
        ]
    )
    vision: LLMVision = field(default_factory=LLMVision)

    output_variables: List[OutputVariable] = field(
        default_factory=lambda: [
            OutputVariable(
                variable="class_name",
                label="分类名称",
                type="string",
            ),
            OutputVariable(
                variable="usage",
                label="模型用量信息",
                type="object",
            ),
        ],
    )

    def to_dict(self, exclude_fields: List[str] | None = None) -> dict:
        data_dict = super().to_dict(exclude_fields)
        data_dict.pop("variables", None)
        return data_dict
