from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class IfElseCondition:
    id: str
    variable_selector: List[str]
    comparison_operator: str
    value: Any
    varType: str


@dataclass
class IfElseCase:
    id: str
    case_id: str
    logical_operator: str
    conditions: List[IfElseCondition] = field(default_factory=list)
