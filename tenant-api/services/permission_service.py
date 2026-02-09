from typing import Optional, List
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models.workspace import Workspace
from models.project import Project
from models.document import Document


class Permission(str, Enum):
    WORKSPACE_READ = "workspace:read"
    WORKSPACE_WRITE = "workspace:write"
    WORKSPACE_DELETE = "workspace:delete"
    PROJECT_READ = "project:read"
    PROJECT_WRITE = "project:write"
    PROJECT_DELETE = "project:delete"
    DOCUMENT_READ = "document:read"
    DOCUMENT_WRITE = "document:write"
    DOCUMENT_DELETE = "document:delete"
    AI_CONVERSATION = "ai:conversation"
    EXPORT_DATA = "data:export"
    DELETE_DATA = "data:delete"
    MANAGE_RETENTION = "data:retention:manage"
    MANAGE_CONNECTORS = "connector:manage"
    VIEW_AUDIT = "security:audit:view"
    MANAGE_USERS = "security:user:manage"


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


# Permission matrix
ROLE_PERMISSIONS = {
    Role.OWNER: [p for p in Permission],
    Role.ADMIN: [
        Permission.WORKSPACE_READ,
        Permission.WORKSPACE_WRITE,
        Permission.WORKSPACE_DELETE,
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.PROJECT_DELETE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
        Permission.DOCUMENT_DELETE,
        Permission.AI_CONVERSATION,
        Permission.EXPORT_DATA,
        Permission.DELETE_DATA,
        Permission.MANAGE_RETENTION,
        Permission.MANAGE_CONNECTORS,
        Permission.VIEW_AUDIT,
        Permission.MANAGE_USERS,
    ],
    Role.MEMBER: [
        Permission.WORKSPACE_READ,
        Permission.WORKSPACE_WRITE,
        Permission.PROJECT_READ,
        Permission.PROJECT_WRITE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
        Permission.AI_CONVERSATION,
        Permission.EXPORT_DATA,
    ],
    Role.VIEWER: [
        Permission.WORKSPACE_READ,
        Permission.PROJECT_READ,
        Permission.DOCUMENT_READ,
    ],
}


class PermissionService:
    """Service for checking permissions."""
    
    def __init__(self):
        pass
    
    def has_permission(self, user_role: str, permission: Permission) -> bool:
        """Check if a role has a specific permission."""
        try:
            role = Role(user_role)
            return permission in ROLE_PERMISSIONS.get(role, [])
        except ValueError:
            return False
    
    def get_role_permissions(self, user_role: str) -> List[Permission]:
        """Get all permissions for a role."""
        try:
            role = Role(user_role)
            return ROLE_PERMISSIONS.get(role, [])
        except ValueError:
            return []
    
    async def can_access_workspace(
        self,
        db: AsyncSession,
        org_id: str,
        workspace_id: str,
        user_id: str,
        user_role: str,
        permission: Permission = Permission.WORKSPACE_READ,
    ) -> bool:
        """Check if user can access a workspace."""
        # Check role permission
        if not self.has_permission(user_role, permission):
            return False
        
        # Verify workspace exists in org
        result = await db.execute(
            select(Workspace).where(
                and_(
                    Workspace.id == workspace_id,
                    Workspace.org_id == org_id,
                )
            )
        )
        workspace = result.scalar_one_or_none()
        
        if not workspace:
            return False
        
        # Check object-level permissions
        if workspace.created_by == user_id:
            return True
        
        # Admin can access all
        if user_role in [Role.ADMIN.value, Role.OWNER.value]:
            return True
        
        return self.has_permission(user_role, permission)
    
    async def can_access_project(
        self,
        db: AsyncSession,
        org_id: str,
        project_id: str,
        user_id: str,
        user_role: str,
        permission: Permission = Permission.PROJECT_READ,
    ) -> bool:
        """Check if user can access a project."""
        if not self.has_permission(user_role, permission):
            return False
        
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.org_id == org_id,
                )
            )
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return False
        
        if project.created_by == user_id:
            return True
        
        if user_role in [Role.ADMIN.value, Role.OWNER.value]:
            return True
        
        return self.has_permission(user_role, permission)
    
    async def can_access_document(
        self,
        db: AsyncSession,
        org_id: str,
        document_id: str,
        user_id: str,
        user_role: str,
        permission: Permission = Permission.DOCUMENT_READ,
    ) -> bool:
        """Check if user can access a document."""
        if not self.has_permission(user_role, permission):
            return False
        
        result = await db.execute(
            select(Document).where(
                and_(
                    Document.id == document_id,
                    Document.org_id == org_id,
                )
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            return False
        
        if document.created_by == user_id:
            return True
        
        if user_role in [Role.ADMIN.value, Role.OWNER.value]:
            return True
        
        return self.has_permission(user_role, permission)
