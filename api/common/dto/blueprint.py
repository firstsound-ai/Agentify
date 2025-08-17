from typing import List, Dict, Optional

from pydantic import BaseModel

from common.enums.task import TaskStatus


class Edge(BaseModel):
    sourceHandle: str
    targetNodeId: str


class Node(BaseModel):
    nodeTitle: str
    nodeType: str
    nodeDescription: str
    edges: List[Edge]


class Workflow(BaseModel):
    workflowId: str
    workflowName: str
    startNodeId: str
    nodes: Dict[str, Node]  # 节点ID到Node对象的映射


class BlueprintResponse(BaseModel):
    blueprint_id: str
    status: TaskStatus
    workflow: Optional[Workflow] = None
    mermaid_code: Optional[str] = None
    error: Optional[str] = None
    progress: str


class PromptRequest(BaseModel):
    prompt: str
