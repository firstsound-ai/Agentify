from dataclasses import dataclass, field
from typing import List

from ..base import BaseNodeData
from .type import IfElseCase


@dataclass
class IfElseNodeData(BaseNodeData):
    type: str = "if-else"
    title: str = "条件分支"
    cases: List[IfElseCase] = field(
        default_factory=lambda: [
            IfElseCase(id="true", case_id="true", logical_operator="and", conditions=[])
        ]
    )

    def to_dict(self, exclude_fields: List[str] | None = None) -> dict:
        data_dict = super().to_dict(exclude_fields)
        data_dict.pop("variables", None)
        return data_dict
