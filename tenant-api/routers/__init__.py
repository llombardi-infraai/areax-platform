from .workspaces import router as workspaces
from .projects import router as projects
from .documents import router as documents
from .ai import router as ai
from .security import router as security
from .data_control import router as data_control
from .notifications import router as notifications
from .connectors import router as connectors

__all__ = [
    "workspaces",
    "projects",
    "documents",
    "ai",
    "security",
    "data_control",
    "notifications",
    "connectors",
]
