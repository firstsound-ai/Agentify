from typing import Annotated, Any, Dict, List, Optional

from langchain_core.tools import tool

from ..base import Node, NodePosition
from .node import HTTPRequestNodeData
from .type import AuthConfig, HTTPBody, HTTPRetryConfig, HTTPTimeout


# TODO: 更复杂的情况，需要用户填写
@tool
def create_http_request_node(
    node_id: Annotated[str, "节点的唯一标识符 (例如: 'http_request_1')。"],
    x_pos: Annotated[int, "节点在画布上的X坐标。"],
    y_pos: Annotated[int, "节点在画布上的Y坐标。"],
    url: Annotated[
        str,
        "请求的目标URL。可以包含变量引用，例如 'https://api.example.com/users/{{#user_node.user_id#}}'",
    ],
    method: Annotated[
        str,
        "HTTP请求方法。支持 'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'。",
    ] = "GET",
    title: Annotated[str, "节点的显示标题。"] = "HTTP 请求",
    desc: Annotated[str, "节点的描述信息。"] = "发送HTTP请求并获取响应",
    headers: Annotated[str, "请求头，以JSON字符串格式提供。"] = "",
    params: Annotated[str, "查询参数，以JSON字符串格式提供。"] = "",
    authorization_type: Annotated[
        str, "认证类型。支持 'no-auth', 'bearer', 'api-key', 'basic'。"
    ] = "no-auth",
    authorization_config: Optional[Dict[str, Any]] = None,
    body_type: Annotated[
        str,
        "请求体类型。支持 'none', 'form-data', 'x-www-form-urlencoded', 'raw-text', 'json', 'xml'。",
    ] = "none",
    body_data: Optional[List[Any]] = None,
    ssl_verify: Annotated[bool, "是否验证SSL证书。"] = True,
    max_connect_timeout: Annotated[
        int, "最大连接超时时间（秒）。0表示使用默认值。"
    ] = 0,
    max_read_timeout: Annotated[int, "最大读取超时时间（秒）。0表示使用默认值。"] = 0,
    max_write_timeout: Annotated[int, "最大写入超时时间（秒）。0表示使用默认值。"] = 0,
    retry_enabled: Annotated[bool, "是否启用重试机制。"] = True,
    max_retries: Annotated[int, "最大重试次数。"] = 3,
    retry_interval: Annotated[int, "重试间隔（毫秒）。"] = 100,
) -> Dict[str, Any]:
    """
    在工作流中创建一个HTTP请求节点。
    当需要调用外部API、获取网络资源或与其他系统进行HTTP通信时使用此工具。
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
