from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class LLMCompletionParams:
    temperature: float = 0.7


@dataclass
class LLMModel:
    provider: str = ""
    name: str = ""
    mode: str = "chat"
    completion_params: LLMCompletionParams = field(default_factory=LLMCompletionParams)


@dataclass
class PromptTemplateItem:
    role: str
    text: str


@dataclass
class LLMContext:
    enabled: bool = False
    variable_selector: List[Any] = field(default_factory=list)


@dataclass
class LLMVision:
    enabled: bool = False


@dataclass
class LLMMemoryWindow:
    enabled: bool = False
    size: int = 10


# TODO: Memory 设置还有问题
@dataclass
class LLMMemory:
    window: LLMMemoryWindow = field(default_factory=LLMMemoryWindow)
    query_prompt_template: str = "{{#sys.query#}}\n\n{{#sys.files#}}"
    role_prefix: Dict[str, str] = field(
        default_factory=lambda: {"user": "", "assistant": ""}
    )
