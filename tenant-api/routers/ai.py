from uuid import UUID
from typing import List, Optional, AsyncGenerator
from datetime import datetime
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from models.ai import AIConversation, AIMessage, AIMemory, ConversationStatus, MessageRole
from services.ai_service import AIService
from services.audit_service import AuditService

router = APIRouter()


# Schemas
class ConversationCreate(BaseModel):
    title: Optional[str] = None
    context: Optional[dict] = None


class ConversationResponse(BaseModel):
    id: UUID
    title: Optional[str]
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    messages: List[dict]


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: UUID
    role: MessageRole
    content: str
    tokens_used: int
    latency_ms: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int


class MemoryResponse(BaseModel):
    id: UUID
    key: str
    value: str
    confidence: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class MemoryListResponse(BaseModel):
    items: List[MemoryResponse]
    total: int


class BlueprintStartRequest(BaseModel):
    project_type: str
    initial_description: str


class BlueprintStartResponse(BaseModel):
    session_id: str
    first_question: str


class BlueprintAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


class BlueprintAnswerResponse(BaseModel):
    next_question: Optional[str]
    is_complete: bool
    progress: int  # 0-100


class BlueprintGenerateRequest(BaseModel):
    session_id: str


class BlueprintGenerateResponse(BaseModel):
    blueprint_id: str
    document: dict
    download_url: Optional[str]


# AI Conversation Endpoints
@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new AI conversation."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    conversation = AIConversation(
        org_id=org_id,
        user_id=user_id,
        title=data.title or "New Conversation",
        context=data.context or {},
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        status=conversation.status,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=0,
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    status: Optional[ConversationStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List AI conversations for the user."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    query = select(AIConversation).where(
        and_(AIConversation.org_id == org_id, AIConversation.user_id == user_id)
    )
    
    if status:
        query = query.where(AIConversation.status == status)
    
    # Get total count
    count_result = await db.execute(
        query.with_only_columns(AIConversation.id)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = query.offset(offset).limit(limit).order_by(desc(AIConversation.updated_at))
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    items = []
    for conv in conversations:
        items.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            status=conv.status,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=len(conv.messages) if conv.messages else 0,
        ))
    
    return ConversationListResponse(items=items, total=total)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get conversation details with messages."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    result = await db.execute(
        select(AIConversation).where(
            and_(
                AIConversation.id == conversation_id,
                AIConversation.org_id == org_id,
                AIConversation.user_id == user_id,
            )
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = []
    if conversation.messages:
        for msg in conversation.messages:
            messages.append({
                "id": str(msg.id),
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            })
    
    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        status=conversation.status,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=len(messages),
        messages=messages,
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: UUID,
    data: MessageCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to the AI and get a response."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    # Verify conversation exists
    result = await db.execute(
        select(AIConversation).where(
            and_(
                AIConversation.id == conversation_id,
                AIConversation.org_id == org_id,
                AIConversation.user_id == user_id,
            )
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Save user message
    user_message = AIMessage(
        org_id=org_id,
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=data.content,
    )
    db.add(user_message)
    
    # Get AI response
    ai_service = AIService(db, org_id, user_id)
    response_content, tokens_used, latency_ms = await ai_service.chat(
        conversation_id=conversation_id,
        message=data.content,
    )
    
    # Save AI response
    ai_message = AIMessage(
        org_id=org_id,
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content=response_content,
        tokens_used=tokens_used,
        latency_ms=latency_ms,
    )
    db.add(ai_message)
    await db.commit()
    await db.refresh(ai_message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    await db.commit()
    
    # Audit log
    audit = AuditService(db)
    await audit.log(
        org_id=org_id,
        user_id=user_id,
        action="ai_response",
        resource_type="ai_conversation",
        resource_id=str(conversation_id),
        details={"tokens_used": tokens_used, "latency_ms": latency_ms},
    )
    
    return MessageResponse(
        id=ai_message.id,
        role=ai_message.role,
        content=ai_message.content,
        tokens_used=ai_message.tokens_used,
        latency_ms=ai_message.latency_ms,
        created_at=ai_message.created_at,
    )


# Blueprint Builder Endpoints
@router.post("/blueprint/builder/start", response_model=BlueprintStartResponse)
async def start_blueprint_builder(
    data: BlueprintStartRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a blueprint building session."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    ai_service = AIService(db, org_id, user_id)
    session_id, first_question = await ai_service.start_blueprint_session(
        project_type=data.project_type,
        initial_description=data.initial_description,
    )
    
    return BlueprintStartResponse(
        session_id=session_id,
        first_question=first_question,
    )


@router.post("/blueprint/builder/answer", response_model=BlueprintAnswerResponse)
async def answer_blueprint_question(
    data: BlueprintAnswerRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit an answer to a blueprint question."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    ai_service = AIService(db, org_id, user_id)
    next_question, is_complete, progress = await ai_service.process_blueprint_answer(
        session_id=data.session_id,
        question_id=data.question_id,
        answer=data.answer,
    )
    
    return BlueprintAnswerResponse(
        next_question=next_question,
        is_complete=is_complete,
        progress=progress,
    )


@router.post("/blueprint/builder/generate", response_model=BlueprintGenerateResponse)
async def generate_blueprint(
    data: BlueprintGenerateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate the final blueprint document."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    ai_service = AIService(db, org_id, user_id)
    blueprint_id, document = await ai_service.generate_blueprint(data.session_id)
    
    # Audit log
    audit = AuditService(db)
    await audit.log(
        org_id=org_id,
        user_id=user_id,
        action="create",
        resource_type="blueprint",
        resource_id=blueprint_id,
        details={"session_id": data.session_id},
    )
    
    return BlueprintGenerateResponse(
        blueprint_id=blueprint_id,
        document=document,
        download_url=None,  # Would be generated if stored
    )


# Memory Endpoints
@router.get("/memory", response_model=MemoryListResponse)
async def list_memories(
    key_filter: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List AI memories for the organization."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    query = select(AIMemory).where(
        and_(
            AIMemory.org_id == org_id,
            AIMemory.user_id == user_id,
        )
    )
    
    if key_filter:
        query = query.where(AIMemory.key.ilike(f"%{key_filter}%"))
    
    # Get total count
    count_result = await db.execute(
        query.with_only_columns(AIMemory.id)
    )
    total = len(count_result.scalars().all())
    
    # Get paginated results
    query = query.offset(offset).limit(limit).order_by(desc(AIMemory.created_at))
    result = await db.execute(query)
    memories = result.scalars().all()
    
    items = [MemoryResponse.model_validate(m) for m in memories]
    
    return MemoryListResponse(items=items, total=total)


@router.delete("/memory/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: UUID,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an AI memory."""
    org_id = user.get("org_id")
    user_id = user.get("id")
    
    result = await db.execute(
        select(AIMemory).where(
            and_(
                AIMemory.id == memory_id,
                AIMemory.org_id == org_id,
                AIMemory.user_id == user_id,
            )
        )
    )
    memory = result.scalar_one_or_none()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    await db.delete(memory)
    await db.commit()
    
    return None
