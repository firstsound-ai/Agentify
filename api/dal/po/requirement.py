import uuid

from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlalchemy.sql import func

from dal.database import Base


class Requirement(Base):
    __tablename__ = "requirement"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    initial_requirement = Column(Text, nullable=False)
    requirement_name = Column(String(255), nullable=True)
    mission_statement = Column(Text, nullable=True)
    user_and_scenario = Column(Text, nullable=True)
    user_input = Column(Text, nullable=True)
    ai_output = Column(Text, nullable=True)
    success_criteria = Column(Text, nullable=True)
    boundaries_and_limitations = Column(Text, nullable=True)

    status = Column(String(50), nullable=False, default="pending")
    progress = Column(String(255), nullable=True, default="初始化中...")
    questionnaire = Column(JSON, nullable=True)
    user_answers = Column(JSON, nullable=True)
    final_document = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    user_id = Column(String(36), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
