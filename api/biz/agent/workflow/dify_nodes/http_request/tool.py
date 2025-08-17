from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from ..base import Node, NodePosition
from .node import HTTPRequestNodeData
from .type import AuthConfig, HTTPBody, HTTPRetryConfig, HTTPTimeout


# TODO: 更复杂的情况，需要用户填写
@tool
def create_http_request_node(
    node_id: str,
    x_pos: int,
    y_pos: int,
    url: str,
    method: str = "GET",
    title: str = "HTTP 请求",
    desc: str = "发送HTTP请求并获取响应",
    headers: str = "",
    params: str = "",
    authorization_type: str = "no-auth",
    authorization_config: Optional[Dict[str, Any]] = None,
    body_type: str = "none",
    body_data: Optional[List[Any]] = None,
    ssl_verify: bool = True,
    max_connect_timeout: int = 0,
    max_read_timeout: int = 0,
    max_write_timeout: int = 0,
    retry_enabled: bool = True,
    max_retries: int = 3,
    retry_interval: int = 100,
) -> Dict[str, Any]:
    """
    在工作流中创建一个HTTP请求节点。
    当需要调用外部API、获取网络资源或与其他系统进行HTTP通信时使用此工具。

    Args:
        node_id (str): 节点的唯一标识符 (例如: "http_request_1")。
        x_pos (int): 节点在画布上的X坐标。
        y_pos (int): 节点在画布上的Y坐标。
        url (str): 请求的目标URL。可以包含变量引用，例如 'https://api.example.com/users/{{#user_node.user_id#}}'。
        method (str, optional): HTTP请求方法。支持 "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"。默认为 "GET"。
        title (str, optional): 节点的显示标题。默认为 "HTTP 请求"。
        desc (str, optional): 节点的描述信息。默认为 "发送HTTP请求并获取响应"。
        headers (str, optional): 请求头，以JSON字符串格式提供。例如: '{"Content-Type": "application/json", "Authorization": "Bearer {{#token_node.token#}}"}'。
        params (str, optional): 查询参数，以JSON字符串格式提供。例如: '{"page": "1", "limit": "10"}'。
        authorization_type (str, optional): 认证类型。支持 "no-auth", "bearer", "api-key", "basic"。默认为 "no-auth"。
        authorization_config (Dict[str, Any], optional): 认证配置。根据authorization_type提供相应配置。
        body_type (str, optional): 请求体类型。支持 "none", "form-data", "x-www-form-urlencoded", "raw-text", "json", "xml"。默认为 "none"。
        body_data (List[Any], optional): 请求体数据。格式取决于body_type。
        ssl_verify (bool, optional): 是否验证SSL证书。默认为 True。
        max_connect_timeout (int, optional): 最大连接超时时间（秒）。0表示使用默认值。
        max_read_timeout (int, optional): 最大读取超时时间（秒）。0表示使用默认值。
        max_write_timeout (int, optional): 最大写入超时时间（秒）。0表示使用默认值。
        retry_enabled (bool, optional): 是否启用重试机制。默认为 True。
        max_retries (int, optional): 最大重试次数。默认为 3。
        retry_interval (int, optional): 重试间隔（毫秒）。默认为 100。

    Returns:
        Dict[str, Any]: 代表该HTTP请求节点的字典结构，包含节点信息、观察结果和输出变量引用。

    Examples:
        # 简单的GET请求
        create_http_request_node(
            node_id="get_user_info",
            x_pos=100,
            y_pos=200,
            url="https://api.example.com/users/{{#user_id#}}",
            method="GET"
        )

        # 带认证的POST请求
        create_http_request_node(
            node_id="create_user",
            x_pos=300,
            y_pos=200,
            url="https://api.example.com/users",
            method="POST",
            headers='{"Content-Type": "application/json"}',
            authorization_type="bearer",
            authorization_config={"token": "{{#auth_node.access_token#}}"},
            body_type="json",
            body_data=[{"name": "{{#user_name#}}", "email": "{{#user_email#}}"}]
        )
    """
    # 设置默认值
    if authorization_config is None:
        authorization_config = {}
    if body_data is None:
        body_data = []

    # 创建认证配置
    auth_config = AuthConfig(
        type=authorization_type,
        config=authorization_config if authorization_config else None,
    )

    # 创建请求体配置
    http_body = HTTPBody(type=body_type, data=body_data)

    # 创建超时配置
    timeout_config = HTTPTimeout(
        max_connect_timeout=max_connect_timeout,
        max_read_timeout=max_read_timeout,
        max_write_timeout=max_write_timeout,
    )

    # 创建重试配置
    retry_config = HTTPRetryConfig(
        retry_enabled=retry_enabled,
        max_retries=max_retries,
        retry_interval=retry_interval,
    )

    # 创建HTTP请求节点数据
    http_request_node_data = HTTPRequestNodeData(
        title=title,
        desc=desc,
        method=method.upper(),
        url=url,
        authorization=auth_config,
        headers=headers,
        params=params,
        body=http_body,
        ssl_verify=ssl_verify,
        timeout=timeout_config,
        retry_config=retry_config,
    )

    # 创建节点
    http_request_node = Node(
        id=node_id,
        position=NodePosition(x=x_pos, y=y_pos),
        data=http_request_node_data,
        width=244,
        height=83,
    )

    print(http_request_node)

    return {
        "node": http_request_node.to_dict(),
        "observation": f"已经创建了一个名为'{title}'的HTTP请求节点。请求方法为{method.upper()}，目标URL为：{url}",
        "output": http_request_node.get_output_variable_references(),
    }
