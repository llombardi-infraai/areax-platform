from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    recipient_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(String(100), nullable=False)  # security, data, platform, connector, ai
    severity = Column(String(50), default="info")  # info, warning, critical
    title = Column(String(255), nullable=False)
    content = Column(Text)
    link_path = Column(String(500))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
