import re
import uuid
from dataclasses import asdict, dataclass, field
from typing import List, Optional, Set

DEFAULT_EXCLUDE_FIELDS: Set[str] = {
    "output_variables",
}


@dataclass
class NodeVariable:
    variable: str
    label: str
    type: str = "text-input"
    required: bool = False
    max_length: int = 48


@dataclass
class OutputVariable:
    variable: str  # 变量名，如 "text", "result", "data"
    label: str  # 显示标签，如 "文本输出", "分析结果"
    type: str = "text"  # 输出类型，如 "text", "json", "number", "boolean"
    description: str = ""  # 变量描述


@dataclass
class NodePosition:
    x: int
    y: int


@dataclass
class BaseNodeData:
    type: str
    title: str
    desc: str = ""
    variables: List[NodeVariable] = field(default_factory=list)
    output_variables: List[OutputVariable] = field(default_factory=list, repr=False)
    selected: bool = False

    def to_dict(self, exclude_fields: Optional[List[str]] = None) -> dict:
        if exclude_fields is None:
            exclude_fields = list(DEFAULT_EXCLUDE_FIELDS)

        data_dict = asdict(self)
        for field_name in exclude_fields:
            data_dict.pop(field_name, None)
        return data_dict

    def to_dict_full(self) -> dict:
        return asdict(self)


@dataclass
class Node:
    data: BaseNodeData
    position: NodePosition
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "custom"
    targetPosition: str = "left"
    sourcePosition: str = "right"
    positionAbsolute: NodePosition = field(init=False)
    width: int = 244
    height: int = 54
    selected: bool = False
    # zIndex: Optional[int] = None
    # parentId: Optional[str] = None
    # selectable: Optional[bool] = None
    draggable: Optional[bool] = True

    def __post_init__(self):
        self.positionAbsolute = NodePosition(x=self.position.x, y=self.position.y)

    def to_dict(self, exclude_fields: Optional[List[str]] = None) -> dict:
        result = asdict(self)
        if hasattr(self.data, "to_dict"):
            result["data"] = self.data.to_dict(exclude_fields)

        return result

    def to_dict_full(self) -> dict:
        result = asdict(self)
        if hasattr(self.data, "to_dict_full"):
            result["data"] = self.data.to_dict_full()

        return result

    def get_output_variables(self) -> List[OutputVariable]:
        return self.data.output_variables

    def get_output_variable_names(self) -> List[str]:
        return [var.variable for var in self.data.output_variables]

    def get_output_variable_references(self) -> List[str]:
        return [
            f"{{{{#{self.id}.{var.variable}#}}}}" for var in self.data.output_variables
        ]


def parse_variable(selector_str: str) -> List[str]:
    match = re.search(r"{{#([\w.-]+)#}}", selector_str)
    if match:
        variable_path = match.group(1)
        return variable_path.split(".")
    return [selector_str]
