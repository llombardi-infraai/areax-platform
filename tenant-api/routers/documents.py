from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, UUID4
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter()


class DocumentCreate(BaseModel):
    type: str  # blueprint, knowledge_base, checklist
    title: str
    content: dict
    privacy: str = "project"


class DocumentResponse(BaseModel):
    id: UUID4
    project_id: UUID4
    type: str
    title: str
    content: dict
    privacy: str
    created_at: str


@router.get("/projects/{project_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """List documents in a project."""
    return []


@router.post("/projects/{project_id}/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    project_id: str,
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Create a new document."""
    return {"id": "00000000-0000-0000-0000-000000000000", "project_id": project_id, **data.dict(), "created_at": "2024-01-01T00:00:00Z"}


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Get a specific document."""
    raise HTTPException(status_code=404, detail="Document not found")
