from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from models.audit import AuditLog


class AuditService:
    """Service for creating audit logs."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log(
        self,
        action: str,
        actor_id: str,
        actor_role: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        target_name: Optional[str] = None,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        result: str = "success",
        reason: Optional[str] = None,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        log = AuditLog(
            workspace_id=workspace_id,
            project_id=project_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            before_state=before_state,
            after_state=after_state,
            result=result,
            reason=reason,
        )
        self.db.add(log)
        await self.db.commit()
        return log
