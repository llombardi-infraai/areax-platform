from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, INET
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    actor_id = Column(UUID(as_uuid=True), nullable=False)
    actor_role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    target_type = Column(String(100))
    target_id = Column(UUID(as_uuid=True))
    target_name = Column(String(255))
    before_state = Column(JSON)
    after_state = Column(JSON)
    result = Column(String(50), default="success")  # success, denied, failed
    reason = Column(Text)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
