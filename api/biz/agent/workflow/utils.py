from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class EdgeDefinition:
    """边的定义"""

    id: str
    type: str
    source: str
    target: str
    sourceHandle: str
    targetHandle: str
    data: Dict[str, Any]
    zIndex: int = 0


def create_workflow_edges(
    sop_definition: Dict[str, Any], dify_nodes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    根据SOP定义和Dify节点定义生成边的关系

    Args:
        sop_definition: SOP定义，包含workflowId、nodes等信息
        dify_nodes: Dify节点定义列表

    Returns:
        边的定义列表
    """
    edges = []

    # 构建节点类型映射
    node_types = {node["id"]: node["data"]["type"] for node in dify_nodes}

    # 处理SOP中的边定义
    sop_nodes = sop_definition.get("nodes", {})

    for source_node_id, node_data in sop_nodes.items():
        # 跳过不存在的源节点
        if source_node_id not in node_types:
            continue

        source_type = node_types[source_node_id]

        # 处理该节点的所有边
        for edge in node_data.get("edges", []):
            target_node_id = edge.get("targetNodeId")

            # 跳过不存在的目标节点
            if target_node_id not in node_types:
                continue

            target_type = node_types[target_node_id]
            # BUG: source的类型不匹配
            source_handle = (
                "source"  # 不一定都是source，可能是true/false等，需要再次检查
            )
            target_handle = "target"

            # 创建边定义
            edge_definition = {
                "id": f"{source_node_id}-{source_handle}-{target_node_id}-{target_handle}",
                "type": "custom",
                "source": source_node_id,
                "target": target_node_id,
                "sourceHandle": source_handle,
                "targetHandle": target_handle,
                "data": {
                    "sourceType": source_type,
                    "targetType": target_type,
                    "isInLoop": False,
                },
                "zIndex": 0,
            }

            edges.append(edge_definition)

    return edges
