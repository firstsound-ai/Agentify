from dataclasses import dataclass


@dataclass
class DocumentExtractorOutput:
    """文档提取器输出配置"""

    text: str = "string"  # 单文件输出类型为 string
    text_list: str = "array[string]"  # 多文件输出类型为 array[string]
