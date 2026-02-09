from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from models.audit import AuditLog, AuditAction, AuditSeverity
from services.audit_service import AuditService

router = APIRouter()


# Schemas
class SecurityOverviewResponse(BaseModel):
    total_audit_events: int
    events_last_24h: int
    critical_events: int
    warning_events: int
    top_actions: List[dict]
    recent_ips: List[str]


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: Optional[str]
    action: AuditAction
    resource_type: str
    resource_id: Optional[str]
    severity: AuditSeverity
    details: dict
    created_at: datetime
    ip_address: Optional[str]
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int


class UserSecurityInfo(BaseModel):
    user_id: str
    email: str
    role: str
    last_active: Optional[datetime]
    total_actions: int


class UserListResponse(BaseModel):
    items: List[UserSecurityInfo]
    total: int


@router.get("/overview", response_model=SecurityOverviewResponse)
async def get_security_overview(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get security overview for the organization."""
    org_id = user.get("org_id")
    
    # Total events
    total_result = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.org_id == org_id)
    )
    total_events = total_result.scalar() or 0
    
    # Events in last 24h
    last_24h = datetime.utcnow() - timedelta(hours=24)
    last_24h_result = await db.execute(
        select(func.count(AuditLog.id)).where(
            and_(AuditLog.org_id == org_id, AuditLog.created_at >= last_24h)
        )
    )
    events_last_24h = last_24h_result.scalar() or 0
    
    # Critical events
    critical_result = await db.execute(
        select(func.count(AuditLog.id)).where(
            and_(AuditLog.org_id == org_id, AuditLog.severity == AuditSeverity.CRITICAL)
        )
    )
    critical_events = critical_result.scalar() or 0
    
    # Warning events
    warning_result = await db.execute(
        select(func.count(AuditLog.id)).where(
            and_(AuditLog.org_id == org_id, AuditLog.severity == AuditSeverity.WARNING)
        )
    )
    warning_events = warning_result.scalar() or 0
    
    # Top actions
    actions_result = await db.execute(
        select(AuditLog.action, func.count(AuditLog.id).label("count"))
        .where(AuditLog.org_id == org_id)
        .group_by(AuditLog.action)
        .order_by(desc("count"))
        .limit(5)
    )
    top_actions = [{"action": row[0].value, "count": row[1]} for row in actions_result.all()]
    
    # Recent IPs
    ips_result = await db.execute(
        select(AuditLog.ip_address)
        .where(
            and_(
                AuditLog.org_id == org_id,
                AuditLog.ip_address != None
            )
        )
        .distinct()
        .limit(10)
    )
    recent_ips = [row[0] for row in ips_result.all() if row[0]]
    
    return SecurityOverviewResponse(
        total_audit_events=total_events,
        events_last_24h=events_last_24h,
        critical_events=critical_events,
        warning_events=warning_events,
        top_actions=top_actions,
        recent_ips=recent_ips,
    )


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    severity: Optional[AuditSeverity] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List audit logs for the organization."""
    org_id = user.get("org_id")
    
    query = select(AuditLog).where(AuditLog.org_id == org_id)
    
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if severity:
        query = query.where(AuditLog.severity == severity)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    
    # Get total count
    count_result = await db.execute(
        query.with_only_columns(AuditLog.id)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = query.offset(offset).limit(limit).order_by(desc(AuditLog.created_at))
    result = await db.execute(query)
    logs = result.scalars().all()
    
    items = [AuditLogResponse.model_validate(log) for log in logs]
    
    return AuditLogListResponse(items=items, total=total)


@router.get("/users", response_model=UserListResponse)
async def list_security_users(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List users with security information (admin only)."""
    org_id = user.get("org_id")
    
    # Get unique users from audit logs
    users_result = await db.execute(
        select(
            AuditLog.user_id,
            func.max(AuditLog.created_at).label("last_active"),
            func.count(AuditLog.id).label("total_actions")
        )
        .where(
            and_(
                AuditLog.org_id == org_id,
                AuditLog.user_id != None
            )
        )
        .group_by(AuditLog.user_id)
        .offset(offset)
        .limit(limit)
    )
    
    items = []
    for row in users_result.all():
        user_id = row[0]
        last_active = row[1]
        total_actions = row[2]
        
        items.append(UserSecurityInfo(
            user_id=user_id,
            email=user_id,  # Would be populated from user service
            role="member",
            last_active=last_active,
            total_actions=total_actions,
        ))
    
    # Get total count
    total_result = await db.execute(
        select(func.count(func.distinct(AuditLog.user_id))).where(AuditLog.org_id == org_id)
    )
    total = total_result.scalar() or 0
    
    return UserListResponse(items=items, total=total)
