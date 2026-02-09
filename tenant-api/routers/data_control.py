from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from models.data_control import (
    Export, ExportStatus, ExportFormat,
    DeletionRequest, DeletionRequestStatus,
    DataRetentionPolicy
)
from services.export_service import ExportService
from services.audit_service import AuditService

router = APIRouter()


# Schemas
class RetentionPolicyResponse(BaseModel):
    id: UUID
    audit_logs_days: int
    conversation_history_days: int
    export_files_days: int
    soft_delete_days: int
    auto_purge_enabled: bool
    settings: dict
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RetentionPolicyUpdate(BaseModel):
    audit_logs_days: Optional[int] = None
    conversation_history_days: Optional[int] = None
    export_files_days: Optional[int] = None
    soft_delete_days: Optional[int] = None
    auto_purge_enabled: Optional[bool] = None
    settings: Optional[dict] = None


class ExportCreate(BaseModel):
    name: str
    description: Optional[str] = None
    format: ExportFormat = ExportFormat.JSON
    filters: Optional[dict] = None


class ExportResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: ExportStatus
    format: ExportFormat
    file_size: int
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ExportListResponse(BaseModel):
    items: List[ExportResponse]
    total: int


class DeletionRequestCreate(BaseModel):
    resource_type: str
    resource_id: str
    reason: Optional[str] = None


class DeletionRequestResponse(BaseModel):
    id: UUID
    resource_type: str
    resource_id: str
    reason: Optional[str]
    status: DeletionRequestStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class DeletionRequestListResponse(BaseModel):
    items: List[DeletionRequestResponse]
    total: int


@router.get("/retention", response_model=RetentionPolicyResponse)
async def get_retention_policy(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get data retention policy for the organization."""
    org_id = user.get("org_id")
    
    result = await db.execute(
        select(DataRetentionPolicy).where(DataRetentionPolicy.org_id == org_id)
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        # Create default policy
        policy = DataRetentionPolicy(
            org_id=org_id,
            updated_by=user.get("id"),
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
    
    return RetentionPolicyResponse.model_validate(policy)


@router.patch("/retention", response_model=RetentionPolicyResponse)
async def update_retention_policy(
    data: RetentionPolicyUpdate,
    user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update data retention policy (admin only)."""
    org_id = user.get("org_id")
    
    result = await db.execute(
        select(DataRetentionPolicy).where(DataRetentionPolicy.org_id == org_id)
    )
    policy = result.scalar_one_or_none()
    
    if not policy:
        policy = DataRetentionPolicy(
            org_id=org_id,
            updated_by=user.get("id"),
        )
        db.add(policy)
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field != "settings" or value is not None:
            setattr(policy, field, value)
    
    policy.updated_by = user.get("id")
    policy.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(policy)
    
    # Audit log
    audit = AuditService(db)
    await audit.log(
        org_id=org_id,
        user_id=user.get("id"),
        action="update",
        resource_type="retention_policy",
        resource_id=str(policy.id),
        details=update_data,
    )
    
    return RetentionPolicyResponse.model_validate(policy)


@router.post("/exports", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def create_export(
    data: ExportCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new data export request."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    export = Export(
        org_id=org_id,
        user_id=user_id,
        name=data.name,
        description=data.description,
        format=data.format,
        filters=data.filters or {},
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    
    db.add(export)
    await db.commit()
    await db.refresh(export)
    
    # Start async export job
    export_service = ExportService(db)
    await export_service.start_export(export.id)
    
    # Audit log
    audit = AuditService(db)
    await audit.log(
        org_id=org_id,
        user_id=user_id,
        action="export",
        resource_type="export",
        resource_id=str(export.id),
        details={"format": data.format.value, "filters": data.filters},
    )
    
    return ExportResponse.model_validate(export)


@router.get("/exports", response_model=ExportListResponse)
async def list_exports(
    status: Optional[ExportStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List data exports for the organization."""
    org_id = user.get("org_id")
    
    query = select(Export).where(Export.org_id == org_id)
    
    if status:
        query = query.where(Export.status == status)
    
    # Get total count
    count_result = await db.execute(
        query.with_only_columns(Export.id)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = query.offset(offset).limit(limit).order_by(Export.created_at.desc())
    result = await db.execute(query)
    exports = result.scalars().all()
    
    items = [ExportResponse.model_validate(e) for e in exports]
    
    return ExportListResponse(items=items, total=total)


@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: UUID,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get download URL for an export."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    result = await db.execute(
        select(Export).where(
            and_(
                Export.id == export_id,
                Export.org_id == org_id,
            )
        )
    )
    export = result.scalar_one_or_none()
    
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    
    if export.user_id != user_id and user.get("role") not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Not authorized to download this export")
    
    if export.status != ExportStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Export is not ready for download")
    
    if export.expires_at and export.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Export has expired")
    
    # Generate presigned URL
    export_service = ExportService(db)
    download_url = await export_service.get_download_url(export_id)
    
    return {"download_url": download_url}


@router.post("/deletions", response_model=DeletionRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_deletion_request(
    data: DeletionRequestCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a data deletion request."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    deletion = DeletionRequest(
        org_id=org_id,
        user_id=user_id,
        requested_by=user_id,
        resource_type=data.resource_type,
        resource_id=data.resource_id,
        reason=data.reason,
    )
    
    db.add(deletion)
    await db.commit()
    await db.refresh(deletion)
    
    # Audit log
    audit = AuditService(db)
    await audit.log(
        org_id=org_id,
        user_id=user_id,
        action="delete",
        resource_type="deletion_request",
        resource_id=str(deletion.id),
        details={
            "resource_type": data.resource_type,
            "resource_id": data.resource_id,
            "reason": data.reason,
        },
    )
    
    return DeletionRequestResponse.model_validate(deletion)


@router.get("/deletions", response_model=DeletionRequestListResponse)
async def list_deletion_requests(
    status: Optional[DeletionRequestStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List deletion requests for the organization."""
    org_id = user.get("org_id")
    
    query = select(DeletionRequest).where(DeletionRequest.org_id == org_id)
    
    if status:
        query = query.where(DeletionRequest.status == status)
    
    # Get total count
    count_result = await db.execute(
        query.with_only_columns(DeletionRequest.id)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = query.offset(offset).limit(limit).order_by(DeletionRequest.created_at.desc())
    result = await db.execute(query)
    deletions = result.scalars().all()
    
    items = [DeletionRequestResponse.model_validate(d) for d in deletions]
    
    return DeletionRequestListResponse(items=items, total=total)
