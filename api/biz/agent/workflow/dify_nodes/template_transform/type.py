from dataclasses import dataclass


@dataclass
class TemplateVariable:
    variable: str
    value_selector: list[str]  # 解析后的选择器路径，如 ["sys", "query"]
    value_type: str = "string"
