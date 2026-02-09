from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Enum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # blueprint, knowledge_base, checklist, policy
    title = Column(String(500), nullable=False)
    content = Column(JSON, nullable=False, default={})
    
    # Privacy settings
    privacy = Column(String(50), default="project")  # project, workspace, org, restricted
    restricted_to = Column(ARRAY(UUID(as_uuid=True)), default=[])
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="documents")
