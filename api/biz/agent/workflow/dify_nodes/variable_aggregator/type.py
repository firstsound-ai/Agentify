from dataclasses import dataclass


@dataclass
class VariableReference:
    variable: str
    value_selector: list[str]
    value_type: str = "string"
