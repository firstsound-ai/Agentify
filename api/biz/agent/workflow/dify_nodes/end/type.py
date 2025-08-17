from dataclasses import dataclass


@dataclass
class EndOutput:
    variable: str
    value_selector: list[str]
    value_type: str = "string"
