from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel, UUID4

from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter()


class WorkspaceCreate(BaseModel):
    name: str
    description: str = None


class WorkspaceResponse(BaseModel):
    id: UUID4
    name: str
    description: str = None
    created_at: str

    class Config:
        from_attributes = True


@router.get("/workspaces", response_model=List[WorkspaceResponse])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """List all workspaces for the current tenant."""
    # TODO: Implement proper query
    return []


@router.post("/workspaces", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    data: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Create a new workspace."""
    # TODO: Implement proper creation
    return {"id": "00000000-0000-0000-0000-000000000000", "name": data.name, "created_at": "2024-01-01T00:00:00Z"}


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get a specific workspace."""
    # TODO: Implement proper query
    raise HTTPException(status_code=404, detail="Workspace not found")
