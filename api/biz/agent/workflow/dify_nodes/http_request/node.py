from dataclasses import dataclass, field

from ..base import BaseNodeData, OutputVariable
from .type import AuthConfig, HTTPBody, HTTPRetryConfig, HTTPTimeout


@dataclass
class HTTPRequestNodeData(BaseNodeData):
    type: str = "http-request"
    title: str = "HTTP 请求"
    method: str = "get"
    url: str = ""
    authorization: AuthConfig = field(default_factory=AuthConfig)
    headers: str = ""
    params: str = ""
    body: HTTPBody = field(default_factory=HTTPBody)
    ssl_verify: bool = True
    timeout: HTTPTimeout = field(default_factory=HTTPTimeout)
    retry_config: HTTPRetryConfig = field(default_factory=HTTPRetryConfig)

    def __post_init__(self):
        if not self.output_variables:
            self.output_variables = [
                OutputVariable(
                    variable="body",
                    label="响应内容",
                    type="string",
                    description="HTTP响应的内容主体",
                ),
                OutputVariable(
                    variable="status_code",
                    label="响应状态码",
                    type="number",
                    description="HTTP响应的状态码",
                ),
                OutputVariable(
                    variable="headers",
                    label="响应头列表",
                    type="object",
                    description="HTTP响应头的JSON对象",
                ),
                OutputVariable(
                    variable="files",
                    label="文件列表",
                    type="Array[File]",
                    description="文件列表",
                ),
            ]
