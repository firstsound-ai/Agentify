from dataclasses import dataclass, field
from typing import List

from ..base import BaseNodeData, OutputVariable


@dataclass
class AnswerNodeData(BaseNodeData):
    type: str = "answer"
    title: str = "直接回复"
    answer: str = ""
    output_variables: List[OutputVariable] = field(
        default_factory=lambda: [
            OutputVariable(
                variable="answer",
                label="回复内容",
                type="text",
                description="最终返回给用户的回复内容",
            )
        ]
    )
