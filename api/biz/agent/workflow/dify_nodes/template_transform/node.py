from dataclasses import dataclass, field
from typing import List

from ..base import BaseNodeData, OutputVariable
from .type import TemplateVariable


@dataclass
class TemplateTransformNodeData(BaseNodeData):
    type: str = "template-transform"
    title: str = "模板转换"
    template_variables: List[TemplateVariable] = field(default_factory=list)
    template: str = "{{ variable }}"  # Jinja2模板内容
    output_variables: List[OutputVariable] = field(
        default_factory=lambda: [
            OutputVariable(
                variable="output",
                label="模板输出",
                type="text",
                description="Jinja2模板渲染的结果",
            )
        ]
    )

    def to_dict(self, exclude_fields: List[str] | None = None) -> dict:
        data_dict = super().to_dict(exclude_fields)
        data_dict["variables"] = [
            {
                "variable": var.variable,
                "value_selector": var.value_selector,
                "value_type": var.value_type,
            }
            for var in self.template_variables
        ]
        data_dict.pop("template_variables", None)
        return data_dict
