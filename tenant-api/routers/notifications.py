from uuid import UUID
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from models.notification import Notification, NotificationType, NotificationPriority
from services.audit_service import AuditService

router = APIRouter()


# Schemas
class NotificationResponse(BaseModel):
    id: UUID
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: dict
    is_read: bool
    read_at: Optional[datetime]
    action_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    unread_count: int


class NotificationSummary(BaseModel):
    total: int
    unread: int
    by_priority: dict


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    is_read: Optional[bool] = None,
    type: Optional[NotificationType] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the current user."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    query = select(Notification).where(
        and_(Notification.org_id == org_id, Notification.user_id == user_id)
    )
    
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)
    if type:
        query = query.where(Notification.type == type)
    
    # Get total count
    count_result = await db.execute(
        query.with_only_columns(Notification.id)
    )
    total = len(count_result.scalars().all())
    
    # Get unread count
    unread_query = select(Notification).where(
        and_(
            Notification.org_id == org_id,
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    unread_result = await db.execute(
        unread_query.with_only_columns(Notification.id)
    )
    unread_count = len(unread_result.scalars().all())
    
    # Get paginated results
    query = query.offset(offset).limit(limit).order_by(desc(Notification.created_at))
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    items = [NotificationResponse.model_validate(n) for n in notifications]
    
    return NotificationListResponse(
        items=items,
        total=total,
        unread_count=unread_count,
    )


@router.get("/notifications/summary", response_model=NotificationSummary)
async def get_notification_summary(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get notification summary for the current user."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    # Total notifications
    total_result = await db.execute(
        select(func.count(Notification.id)).where(
            and_(Notification.org_id == org_id, Notification.user_id == user_id)
        )
    )
    total = total_result.scalar() or 0
    
    # Unread notifications
    unread_result = await db.execute(
        select(func.count(Notification.id)).where(
            and_(
                Notification.org_id == org_id,
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
    )
    unread = unread_result.scalar() or 0
    
    # By priority
    priority_result = await db.execute(
        select(Notification.priority, func.count(Notification.id))
        .where(
            and_(
                Notification.org_id == org_id,
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        .group_by(Notification.priority)
    )
    by_priority = {row[0].value: row[1] for row in priority_result.all()}
    
    return NotificationSummary(
        total=total,
        unread=unread,
        by_priority=by_priority,
    )


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.org_id == org_id,
                Notification.user_id == user_id,
            )
        )
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await db.commit()
        await db.refresh(notification)
    
    return NotificationResponse.model_validate(notification)


@router.patch("/notifications/read-all")
async def mark_all_notifications_read(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read for the current user."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.org_id == org_id,
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
    )
    notifications = result.scalars().all()
    
    now = datetime.utcnow()
    for notification in notifications:
        notification.is_read = True
        notification.read_at = now
    
    await db.commit()
    
    # Audit log
    audit = AuditService(db)
    await audit.log(
        org_id=org_id,
        user_id=user_id,
        action="update",
        resource_type="notification",
        details={"action": "mark_all_read", "count": len(notifications)},
    )
    
    return {"marked_read": len(notifications)}
