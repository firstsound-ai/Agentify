from dataclasses import dataclass, field
from typing import List

from ..base import BaseNodeData, OutputVariable
from .type import LoopCondition, LoopVariable


# BUG: 循环节点暂时有问题
@dataclass
class LoopNodeData(BaseNodeData):
    type: str = "loop"
    title: str = "循环"
    start_node_id: str = ""
    break_conditions: List[LoopCondition] = field(default_factory=list)
    loop_count: int = 10
    logical_operator: str = "or"  # and 或 or，决定多个跳出条件的关系
    error_handle_mode: str = "terminated"  # terminated 或 continue
    loop_variables: List[LoopVariable] = field(default_factory=list)

    def __post_init__(self):
        # 根据循环变量动态生成输出变量
        if not self.output_variables:
            self.output_variables = []

        # 为每个循环变量创建对应的输出变量
        for loop_var in self.loop_variables:
            output_var = OutputVariable(
                variable=loop_var.label,
                label=f"循环变量 {loop_var.label}",
                type="string" if loop_var.var_type == "string" else loop_var.var_type,
                description=f"循环中的变量 {loop_var.label}",
            )
            if output_var not in self.output_variables:
                self.output_variables.append(output_var)

    def to_dict(self, exclude_fields: List[str] | None = None) -> dict:
        data_dict = super().to_dict(exclude_fields)
        data_dict.pop("variables", None)
        return data_dict
