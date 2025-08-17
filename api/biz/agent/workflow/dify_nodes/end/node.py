from dataclasses import dataclass, field
from typing import List

from ..base import BaseNodeData, OutputVariable
from .type import EndOutput


@dataclass
class EndNodeData(BaseNodeData):
    type: str = "end"
    title: str = "结束"
    outputs: List[EndOutput] = field(default_factory=list)
    output_variables: List[OutputVariable] = field(default_factory=list)

    def to_dict(self, exclude_fields: List[str] | None = None) -> dict:
        data_dict = super().to_dict(exclude_fields)
        data_dict["outputs"] = [
            {
                "variable": output.variable,
                "value_selector": output.value_selector,
                "value_type": output.value_type,
            }
            for output in self.outputs
        ]
        return data_dict
