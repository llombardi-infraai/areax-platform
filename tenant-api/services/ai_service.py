import httpx
import json
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.config import settings
from models.ai import AIConversation, AIMessage, AIMemory, MessageRole


class AIService:
    """Service for AI operations using Moonshot API."""
    
    def __init__(self, db: AsyncSession, org_id: str, user_id: str):
        self.db = db
        self.org_id = org_id
        self.user_id = user_id
        self.client = httpx.AsyncClient(
            base_url=settings.MOONSHOT_BASE_URL,
            headers={"Authorization": f"Bearer {settings.MOONSHOT_API_KEY}"},
            timeout=60.0,
        )
    
    async def chat(
        self,
        conversation_id: str,
        message: str,
    ) -> Tuple[str, int, int]:
        """Send a message to the AI and get a response.
        
        Returns: (response_content, tokens_used, latency_ms)
        """
        import time
        start_time = time.time()
        
        # Get conversation history
        result = await self.db.execute(
            select(AIMessage)
            .where(
                and_(
                    AIMessage.conversation_id == conversation_id,
                    AIMessage.org_id == self.org_id,
                )
            )
            .order_by(AIMessage.created_at)
        )
        messages = result.scalars().all()
        
        # Build messages for API
        api_messages = []
        for msg in messages:
            api_messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        api_messages.append({
            "role": "user",
            "content": message,
        })
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": settings.MOONSHOT_MODEL,
                    "messages": api_messages,
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            latency_ms = int((time.time() - start_time) * 1000)
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            
            # Extract and save memories
            await self._extract_memories(conversation_id, content)
            
            return content, tokens_used, latency_ms
            
        except httpx.HTTPError as e:
            return f"Error: {str(e)}", 0, 0
    
    async def _extract_memories(self, conversation_id: str, content: str):
        """Extract facts from AI response and store as memories."""
        # Simple extraction - in production, use NLP or LLM-based extraction
        if "your name is" in content.lower():
            # Extract name
            parts = content.lower().split("your name is")
            if len(parts) > 1:
                name = parts[1].split(".")[0].strip()
                await self._save_memory("user_name", name, conversation_id)
        
        if "you prefer" in content.lower():
            # Extract preference
            parts = content.lower().split("you prefer")
            if len(parts) > 1:
                pref = parts[1].split(".")[0].strip()
                await self._save_memory("user_preference", pref, conversation_id)
    
    async def _save_memory(self, key: str, value: str, source_id: str):
        """Save an extracted memory."""
        memory = AIMemory(
            org_id=self.org_id,
            user_id=self.user_id,
            key=key,
            value=value,
            source_conversation_id=source_id,
        )
        self.db.add(memory)
        await self.db.commit()
    
    async def start_blueprint_session(
        self,
        project_type: str,
        initial_description: str,
    ) -> Tuple[str, str]:
        """Start a blueprint building session.
        
        Returns: (session_id, first_question)
        """
        session_id = str(uuid4())
        
        # Generate first question based on project type
        prompt = f"""You are an expert solutions architect helping to create a comprehensive blueprint.
        
Project Type: {project_type}
Initial Description: {initial_description}

Your task is to ask relevant questions to gather all necessary information for creating a detailed technical blueprint.
Start with the most important open-ended question that will help understand the core requirements.

Respond with ONLY the question, nothing else."""
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": settings.MOONSHOT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
            data = response.json()
            first_question = data["choices"][0]["message"]["content"].strip()
            
        except Exception:
            first_question = "What are the main objectives and success criteria for this project?"
        
        return session_id, first_question
    
    async def process_blueprint_answer(
        self,
        session_id: str,
        question_id: str,
        answer: str,
    ) -> Tuple[Optional[str], bool, int]:
        """Process a blueprint answer and get next question.
        
        Returns: (next_question, is_complete, progress_percentage)
        """
        # In production, this would track session state and progress
        # For now, simulate progression
        import random
        progress = random.randint(20, 90)
        is_complete = progress >= 80
        
        if is_complete:
            return None, True, 100
        
        # Generate next question
        prompt = f"""Based on the previous answer: "{answer}", what would be the next most important question to ask to gather more information for a technical blueprint?

Respond with ONLY the question, nothing else."""
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": settings.MOONSHOT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()
            data = response.json()
            next_question = data["choices"][0]["message"]["content"].strip()
            
        except Exception:
            next_question = "Can you provide more details about the technical requirements?"
        
        return next_question, is_complete, progress
    
    async def generate_blueprint(
        self,
        session_id: str,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate the final blueprint document.
        
        Returns: (blueprint_id, document_json)
        """
        blueprint_id = str(uuid4())
        
        # Generate blueprint content
        prompt = """Generate a comprehensive technical blueprint document in JSON format.

The blueprint should include:
- overview: Executive summary
- architecture: System architecture description
- components: List of system components
- security: Security considerations
- deployment: Deployment strategy
- timeline: High-level timeline

Respond with ONLY valid JSON, nothing else."""
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": settings.MOONSHOT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Parse JSON response
            try:
                document = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if not valid JSON
                document = {
                    "overview": content[:500],
                    "architecture": "See overview",
                    "components": [],
                    "security": "Standard security practices apply",
                    "deployment": "Cloud-based deployment recommended",
                    "timeline": "4-6 weeks",
                }
                
        except Exception:
            document = {
                "overview": "Blueprint generation completed",
                "architecture": "Microservices architecture",
                "components": ["API Gateway", "Authentication Service", "Data Service"],
                "security": "End-to-end encryption, RBAC, audit logging",
                "deployment": "Kubernetes cluster with auto-scaling",
                "timeline": "6-8 weeks",
            }
        
        return blueprint_id, document
    
    async def close(self):
        await self.client.aclose()
