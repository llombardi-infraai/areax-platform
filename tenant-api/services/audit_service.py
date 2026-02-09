from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from models.audit import AuditLog, AuditAction, AuditSeverity


class AuditService:
    """Service for creating audit logs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log(
        self,
        org_id: str,
        action: AuditAction | str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        if isinstance(action, str):
            try:
                action = AuditAction(action)
            except ValueError:
                action = AuditAction.READ
        
        log = AuditLog(
            org_id=org_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            severity=severity,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        return log
    
    async def log_permission_denied(
        self,
        org_id: str,
        user_id: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        attempted_action: str = "access",
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Log a permission denied event."""
        return await self.log(
            org_id=org_id,
            user_id=user_id,
            action=AuditAction.PERMISSION_DENIED,
            resource_type=resource_type,
            resource_id=resource_id,
            severity=AuditSeverity.WARNING,
            details={"attempted_action": attempted_action},
            ip_address=ip_address,
        )
    
    async def log_ai_interaction(
        self,
        org_id: str,
        user_id: str,
        conversation_id: str,
        message_type: str,  # "query" or "response"
        tokens_used: int = 0,
        latency_ms: int = 0,
    ) -> AuditLog:
        """Log an AI interaction."""
        action = AuditAction.AI_QUERY if message_type == "query" else AuditAction.AI_RESPONSE
        
        return await self.log(
            org_id=org_id,
            user_id=user_id,
            action=action,
            resource_type="ai_conversation",
            resource_id=conversation_id,
            severity=AuditSeverity.INFO,
            details={
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
            },
        )
