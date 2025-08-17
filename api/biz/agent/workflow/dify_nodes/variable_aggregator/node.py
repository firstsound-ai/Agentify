from dataclasses import dataclass, field
from typing import List

from ..base import BaseNodeData, OutputVariable
from .type import VariableReference


@dataclass
class VariableAggregatorNodeData(BaseNodeData):
    type: str = "variable-aggregator"
    title: str = "变量聚合器"
    variable_references: List[VariableReference] = field(default_factory=list)
    output_type: str = "string"
    output_variables: List[OutputVariable] = field(
        default_factory=lambda: [
            OutputVariable(
                variable="output",
                label="聚合输出",
                type="string",
                description="聚合后的变量输出",
            )
        ]
    )

    def to_dict(self, exclude_fields: List[str] | None = None) -> dict:
        data_dict = super().to_dict(exclude_fields)
        data_dict["variables"] = [
            {
                "variable": ref.variable,
                "value_selector": ref.value_selector,
                "value_type": ref.value_type,
            }
            for ref in self.variable_references
        ]
        data_dict.pop("variable_references", None)
        return data_dict
