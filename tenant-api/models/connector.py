from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, ARRAY, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Connector(Base):
    __tablename__ = "connectors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(100), nullable=False)  # ghl, metabase, etc.
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="disconnected")  # connected, error, disconnected
    config = Column(JSON, default={})  # settings (no secrets)
    scopes = Column(ARRAY(String), default=[])
    connected_by = Column(UUID(as_uuid=True), nullable=False)
    connected_at = Column(DateTime(timezone=True))
    last_sync_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConnectorToken(Base):
    __tablename__ = "connector_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connector_id = Column(UUID(as_uuid=True), ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False)
    token_encrypted = Column(LargeBinary, nullable=False)
    iv = Column(LargeBinary, nullable=False)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
