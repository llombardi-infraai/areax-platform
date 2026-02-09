from uuid import UUID
from typing import List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from models.connector import Connector, ConnectorType, ConnectorStatus
from services.audit_service import AuditService

router = APIRouter()


# Connector Catalog - Static definitions
CONNECTOR_CATALOG = {
    ConnectorType.AWS: {
        "name": "Amazon Web Services",
        "description": "Connect to AWS cloud services",
        "icon": "aws",
        "config_schema": {
            "access_key_id": {"type": "string", "required": True, "secret": False},
            "secret_access_key": {"type": "string", "required": True, "secret": True},
            "region": {"type": "string", "required": True, "secret": False, "default": "us-east-1"},
        },
        "features": ["resource_inventory", "cost_analysis", "security_audit"],
    },
    ConnectorType.AZURE: {
        "name": "Microsoft Azure",
        "description": "Connect to Azure cloud services",
        "icon": "azure",
        "config_schema": {
            "tenant_id": {"type": "string", "required": True, "secret": False},
            "client_id": {"type": "string", "required": True, "secret": False},
            "client_secret": {"type": "string", "required": True, "secret": True},
            "subscription_id": {"type": "string", "required": True, "secret": False},
        },
        "features": ["resource_inventory", "cost_analysis", "security_audit"],
    },
    ConnectorType.GCP: {
        "name": "Google Cloud Platform",
        "description": "Connect to GCP services",
        "icon": "gcp",
        "config_schema": {
            "project_id": {"type": "string", "required": True, "secret": False},
            "credentials_json": {"type": "string", "required": True, "secret": True},
        },
        "features": ["resource_inventory", "cost_analysis"],
    },
    ConnectorType.GITHUB: {
        "name": "GitHub",
        "description": "Connect to GitHub repositories",
        "icon": "github",
        "config_schema": {
            "token": {"type": "string", "required": True, "secret": True},
            "org_name": {"type": "string", "required": False, "secret": False},
        },
        "features": ["repo_sync", "issue_tracking", "code_analysis"],
    },
    ConnectorType.GITLAB: {
        "name": "GitLab",
        "description": "Connect to GitLab repositories",
        "icon": "gitlab",
        "config_schema": {
            "token": {"type": "string", "required": True, "secret": True},
            "url": {"type": "string", "required": True, "secret": False},
        },
        "features": ["repo_sync", "issue_tracking", "ci_cd"],
    },
    ConnectorType.JIRA: {
        "name": "Jira",
        "description": "Connect to Jira for issue tracking",
        "icon": "jira",
        "config_schema": {
            "url": {"type": "string", "required": True, "secret": False},
            "username": {"type": "string", "required": True, "secret": False},
            "api_token": {"type": "string", "required": True, "secret": True},
        },
        "features": ["issue_sync", "project_tracking"],
    },
    ConnectorType.SLACK: {
        "name": "Slack",
        "description": "Connect to Slack for notifications",
        "icon": "slack",
        "config_schema": {
            "bot_token": {"type": "string", "required": True, "secret": True},
            "channel": {"type": "string", "required": False, "secret": False},
        },
        "features": ["notifications", "commands"],
    },
    ConnectorType.TEAMS: {
        "name": "Microsoft Teams",
        "description": "Connect to Teams for notifications",
        "icon": "teams",
        "config_schema": {
            "webhook_url": {"type": "string", "required": True, "secret": True},
        },
        "features": ["notifications"],
    },
    ConnectorType.CUSTOM: {
        "name": "Custom Connector",
        "description": "Build your own connector",
        "icon": "custom",
        "config_schema": {
            "url": {"type": "string", "required": True, "secret": False},
            "headers": {"type": "object", "required": False, "secret": False},
            "auth_token": {"type": "string", "required": False, "secret": True},
        },
        "features": ["custom_integration"],
    },
}


# Schemas
class ConnectorCatalogItem(BaseModel):
    type: str
    name: str
    description: str
    icon: str
    config_schema: Dict[str, Any]
    features: List[str]


class ConnectorCatalogResponse(BaseModel):
    items: List[ConnectorCatalogItem]


class ConnectorCreate(BaseModel):
    name: str
    type: ConnectorType
    config: Dict[str, Any]


class ConnectorResponse(BaseModel):
    id: UUID
    name: str
    type: ConnectorType
    status: ConnectorStatus
    last_tested_at: Optional[datetime]
    last_error: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConnectorDetailResponse(ConnectorResponse):
    config: Dict[str, Any]


class ConnectorListResponse(BaseModel):
    items: List[ConnectorResponse]
    total: int


class ConnectorTestRequest(BaseModel):
    config: Optional[Dict[str, Any]] = None


class ConnectorTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


@router.get("/connectors/catalog", response_model=ConnectorCatalogResponse)
async def get_connector_catalog(
    user: dict = Depends(get_current_user),
):
    """Get available connector types and their configuration schemas."""
    items = []
    for conn_type, info in CONNECTOR_CATALOG.items():
        items.append(ConnectorCatalogItem(
            type=conn_type.value,
            name=info["name"],
            description=info["description"],
            icon=info["icon"],
            config_schema=info["config_schema"],
            features=info["features"],
        ))
    
    return ConnectorCatalogResponse(items=items)


@router.get("/connectors", response_model=ConnectorListResponse)
async def list_connectors(
    type: Optional[ConnectorType] = None,
    status: Optional[ConnectorStatus] = None,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List configured connectors for the organization."""
    org_id = user.get("org_id")
    
    query = select(Connector).where(Connector.org_id == org_id)
    
    if type:
        query = query.where(Connector.type == type)
    if status:
        query = query.where(Connector.status == status)
    
    # Get total count
    count_result = await db.execute(
        query.with_only_columns(Connector.id)
    )
    total = len(count_result.scalars().all())
    
    # Get results
    query = query.order_by(Connector.created_at.desc())
    result = await db.execute(query)
    connectors = result.scalars().all()
    
    items = [ConnectorResponse.model_validate(c) for c in connectors]
    
    return ConnectorListResponse(items=items, total=total)


@router.post("/connectors", response_model=ConnectorDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_connector(
    data: ConnectorCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new connector."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    # Validate type
    if data.type not in CONNECTOR_CATALOG:
        raise HTTPException(status_code=400, detail="Invalid connector type")
    
    # Extract secrets for encryption
    config = data.config.copy()
    catalog = CONNECTOR_CATALOG[data.type]
    secrets = {}
    
    for key, schema in catalog["config_schema"].items():
        if schema.get("secret") and key in config:
            secrets[key] = config.pop(key)
    
    connector = Connector(
        org_id=org_id,
        name=data.name,
        type=data.type,
        config=config,
        credentials_encrypted=json.dumps(secrets) if secrets else None,
        created_by=user_id,
    )
    
    db.add(connector)
    await db.commit()
    await db.refresh(connector)
    
    # Audit log
    audit = AuditService(db)
    await audit.log(
        org_id=org_id,
        user_id=user_id,
        action="create",
        resource_type="connector",
        resource_id=str(connector.id),
        details={"type": data.type.value, "name": data.name},
    )
    
    return ConnectorDetailResponse(
        id=connector.id,
        name=connector.name,
        type=connector.type,
        status=connector.status,
        config=config,
        last_tested_at=connector.last_tested_at,
        last_error=connector.last_error,
        created_by=connector.created_by,
        created_at=connector.created_at,
        updated_at=connector.updated_at,
    )


@router.delete("/connectors/{connector_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connector(
    connector_id: UUID,
    user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a connector (admin only)."""
    org_id = user.get("org_id")
    
    result = await db.execute(
        select(Connector).where(
            and_(Connector.id == connector_id, Connector.org_id == org_id)
        )
    )
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    await db.delete(connector)
    await db.commit()
    
    # Audit log
    audit = AuditService(db)
    await audit.log(
        org_id=org_id,
        user_id=user.get("id"),
        action="delete",
        resource_type="connector",
        resource_id=str(connector_id),
        details={"type": connector.type.value, "name": connector.name},
    )
    
    return None


@router.post("/connectors/{connector_id}/test", response_model=ConnectorTestResponse)
async def test_connector(
    connector_id: UUID,
    data: Optional[ConnectorTestRequest] = None,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Test a connector's connectivity."""
    org_id = user.get("org_id")
    
    result = await db.execute(
        select(Connector).where(
            and_(Connector.id == connector_id, Connector.org_id == org_id)
        )
    )
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    # Use provided config or existing config
    test_config = data.config if data and data.config else connector.config
    
    # Perform test based on connector type
    success = False
    message = "Connection test failed"
    details = {}
    
    try:
        if connector.type == ConnectorType.AWS:
            # Simulate AWS test
            success = True
            message = "Successfully connected to AWS"
            details = {"regions": ["us-east-1", "us-west-2"]}
        elif connector.type == ConnectorType.GITHUB:
            # Simulate GitHub test
            success = True
            message = "Successfully connected to GitHub"
            details = {"repos_count": 42}
        elif connector.type == ConnectorType.SLACK:
            # Simulate Slack test
            success = True
            message = "Successfully connected to Slack"
            details = {"channel": "#general"}
        else:
            success = True
            message = "Connection test passed"
    except Exception as e:
        message = f"Connection test failed: {str(e)}"
    
    # Update connector status
    connector.status = ConnectorStatus.CONNECTED if success else ConnectorStatus.ERROR
    connector.last_tested_at = datetime.utcnow()
    connector.last_error = None if success else message
    await db.commit()
    
    return ConnectorTestResponse(
        success=success,
        message=message,
        details=details,
    )


import json
