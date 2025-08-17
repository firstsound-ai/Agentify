import uuid

from sqlalchemy import JSON, Column, DateTime, String, Text, Boolean
from sqlalchemy.sql import func

from dal.database import Base


class DifyWorkflow(Base):
    __tablename__ = "dify_workflow"

    app_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )  # app_id
    app_type = Column(String(50))
    app_name = Column(String(50))
    app_description = Column(String(50))

    thread_id = Column(String(36), nullable=False)
    
    status = Column(String(50), nullable=False, default="pending")

    nodes = Column(JSON, nullable=True)  # the workflow of this blueprint
    edges = Column(JSON, nullable=True)  # the workflow of this blueprint

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
