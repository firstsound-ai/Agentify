from dataclasses import dataclass, field
from typing import List

from ..base import BaseNodeData, NodeVariable


@dataclass
class StartNodeData(BaseNodeData):
    type: str = "start"
    title: str = "开始"
    variables: List[NodeVariable] = field(
        default_factory=lambda: [
            NodeVariable(variable="", label="", required=True, max_length=48)
        ]
    )
    # output_variables: List[OutputVariable] = field(
    #     default_factory=lambda: [
    #         OutputVariable(
    #             variable="query",
    #             label="用户查询",
    #             type="text",
    #             description="用户输入的查询内容",
    #         )
    #     ]
    # )
