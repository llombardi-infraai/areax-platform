from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, UUID4
from typing import List

from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: str = None


class ProjectResponse(BaseModel):
    id: UUID4
    workspace_id: UUID4
    name: str
    description: str = None
    created_at: str


@router.get("/workspaces/{workspace_id}/projects", response_model=List[ProjectResponse])
async def list_projects(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """List projects in a workspace."""
    return []


@router.post("/workspaces/{workspace_id}/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    workspace_id: str,
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Create a new project."""
    return {"id": "00000000-0000-0000-0000-000000000000", "workspace_id": workspace_id, "name": data.name, "created_at": "2024-01-01T00:00:00Z"}


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get a specific project."""
    raise HTTPException(status_code=404, detail="Project not found")
