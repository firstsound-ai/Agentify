from dataclasses import dataclass
from typing import Any, List

from ..base import BaseNodeData


@dataclass
class LoopCondition:
    """循环跳出条件"""

    id: str
    varType: str
    variable_selector: List[str]
    comparison_operator: str
    value: Any


@dataclass
class LoopVariable:
    """循环变量定义"""

    id: str
    label: str
    var_type: str  # string, number, boolean 等
    value_type: str  # constant 或 variable
    value: Any  # 如果是常量，直接是值；如果是变量，是 List[str] 选择器


@dataclass
class LoopStartNodeData(BaseNodeData):
    """循环开始节点数据"""

    type: str = "loop-start"
    title: str = ""
    desc: str = ""
    isInLoop: bool = True
