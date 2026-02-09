from sqlalchemy import Column, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Export(Base):
    __tablename__ = "exports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    export_type = Column(String(50), nullable=False)  # org, user
    scope = Column(String(50), nullable=False)  # org, workspace, project
    scope_id = Column(UUID(as_uuid=True))
    status = Column(String(50), default="pending")  # pending, processing, ready, expired
    file_path = Column(String(500))
    file_size = Column(BigInteger)
    expires_at = Column(DateTime(timezone=True))
    downloaded_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class DeletionRequest(Base):
    __tablename__ = "deletion_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    target_type = Column(String(50), nullable=False)  # object, user, org
    target_id = Column(UUID(as_uuid=True), nullable=False)
    reason = Column(Text)
    status = Column(String(50), default="pending")  # pending, approved, rejected, completed
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    executed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RetentionSetting(Base):
    __tablename__ = "retention_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_type = Column(String(100), nullable=False, unique=True)
    days = Column(BigInteger, nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
