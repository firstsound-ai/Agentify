from dataclasses import dataclass, field
from typing import Dict, List

from ..base import BaseNodeData, OutputVariable
from .type import CodeOutput, CodeVariable


@dataclass
class CodeNodeData(BaseNodeData):
    type: str = "code"
    title: str = "代码执行"
    code_variables: List[CodeVariable] = field(default_factory=list)
    code_language: str = "python3"  # 支持 python3 或 javascript
    code: str = "def main() -> dict:\n    return {}\n"
    outputs: Dict[str, CodeOutput] = field(default_factory=dict)
    output_variables: List[OutputVariable] = field(
        default_factory=lambda: [
            OutputVariable(
                variable="result",
                label="执行结果",
                type="json",
                description="代码执行的返回结果",
            )
        ]
    )

    def to_dict(self, exclude_fields: List[str] | None = None) -> dict:
        data_dict = super().to_dict(exclude_fields)
        # 转换 code_variables 为 variables 字段（符合 JSON 格式）
        data_dict["variables"] = [
            {
                "variable": var.variable,
                "value_selector": var.value_selector,
                "value_type": var.value_type,
            }
            for var in self.code_variables
        ]
        # 转换 outputs 为 JSON 格式
        data_dict["outputs"] = {
            key: {"type": output.type, "children": output.children}
            for key, output in self.outputs.items()
        }
        # 移除重复的 code_variables 字段
        data_dict.pop("code_variables", None)
        return data_dict

    def update_output_variables_from_outputs(self):
        """根据outputs字段更新output_variables列表"""
        self.output_variables = []
        for key, output in self.outputs.items():
            self.output_variables.append(
                OutputVariable(
                    variable=key,
                    label=f"{key}输出",
                    type=output.type,
                    description=f"代码执行的{key}结果",
                )
            )
