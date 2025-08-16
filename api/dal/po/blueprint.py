import uuid

from sqlalchemy import JSON, Column, DateTime, String, Text, Boolean
from sqlalchemy.sql import func

from dal.database import Base


class Blueprint(Base):
    __tablename__ = "blueprint"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4())) # blueprint_id
    thread_id = Column(String(36))
    blueprint_name = Column(String(255), nullable=False)

    status = Column(String(50), nullable=False, default="pending")
    progress = Column(String(255), nullable=True, default="初始化中...")

    workflow = Column(JSON, nullable=True) # the workflow of this blueprint

    mermaid_code = Column(Text, nullable=True)

    error_message = Column(Text, nullable=True)

    user_id = Column(String(36), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    is_current = Column(Boolean, nullable=False, default=True)
