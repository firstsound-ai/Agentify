from dataclasses import dataclass, field
from typing import Any, List

from ..base import BaseNodeData, OutputVariable


@dataclass
class DocumentExtractorNodeData(BaseNodeData):
    type: str = "document-extractor"
    title: str = "文档提取器"
    variable_selector: List[Any] = field(default_factory=list)
    is_array_file: bool = False
    output_variables: List[OutputVariable] = field(
        default_factory=lambda: [
            OutputVariable(
                variable="text",
                label="文本输出",
                type="text",
                description="从文档中提取的文本内容",
            )
        ]
    )

    def __post_init__(self):
        # 根据是否为数组文件设置输出变量类型
        if self.is_array_file:
            self.output_variables = [
                OutputVariable(
                    variable="text",
                    label="文本输出",
                    type="array[string]",
                    description="从多个文档中提取的文本内容列表",
                )
            ]
        else:
            self.output_variables = [
                OutputVariable(
                    variable="text",
                    label="文本输出",
                    type="string",
                    description="从文档中提取的文本内容",
                )
            ]
