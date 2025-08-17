import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ToolConfig:
    title: str
    x_pos: int
    y_pos: int
    desc: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    extra_params: Dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    def __init__(self, config: ToolConfig):
        self.config = config
        self.tool_dir = Path(__file__).parent / self.get_tool_name()
        self.template_path = self.tool_dir / "tool.json"

    @abstractmethod
    def get_tool_name(self) -> str:
        pass

    # def get_tool_output_references(self, node_id: str) -> Dict[str, str]:
    # return {
    #     "text": f"#{{#{node_id}.text#}}",
    #     "files": f"#{{#{node_id}.files#}}",
    #     "json": f"#{{#{node_id}.json#}}",
    # }
    # FIXME: TypeError: can only concatenate list (not "dict") to list
    def get_tool_output_references(self, node_id: str) -> List[str]:
        return [
            f"#{{#{node_id}.text#}}",
            f"#{{#{node_id}.files#}}",
            f"#{{#{node_id}.json#}}",
        ]

    def load_template(self) -> Dict[str, Any]:
        if not self.template_path.exists():
            raise FileNotFoundError(f"工具模板文件不存在: {self.template_path}")

        with open(self.template_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_template_fields(self, template: Dict[str, Any]) -> Dict[str, Any]:
        template["id"] = self.config.id
        template["data"]["title"] = self.config.title
        template["data"]["desc"] = self.config.desc
        template["position"]["x"] = self.config.x_pos
        template["position"]["y"] = self.config.y_pos
        template["positionAbsolute"]["x"] = self.config.x_pos
        template["positionAbsolute"]["y"] = self.config.y_pos

        if self.config.extra_params:
            self._deep_update(template, self.config.extra_params)

        return template

    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def generate_config(self) -> Dict[str, Any]:
        template = self.load_template()
        return self.update_template_fields(template)

    def to_dict(self) -> Dict[str, Any]:
        return self.generate_config()
