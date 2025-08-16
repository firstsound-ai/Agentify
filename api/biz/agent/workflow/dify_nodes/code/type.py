from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CodeVariable:
    variable: str
    value_selector: list[str]  # 解析后的选择器路径，如 ["sys", "query"]
    value_type: str = "string"


@dataclass
class CodeOutput:
    type: str
    children: Optional[Any] = None
