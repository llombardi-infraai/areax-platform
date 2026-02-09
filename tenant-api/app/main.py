from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.database import engine, init_db
from app.middleware.tenant import TenantContextMiddleware
from app.routers import (
    workspaces,
    projects,
    documents,
    ai,
    security,
    data_control,
    notifications,
    connectors,
)
from services.audit_service import AuditService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Area X Tenant API",
    description="Multi-tenant business logic service for Area X",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware (order matters - tenant context must be early)
app.add_middleware(TenantContextMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(workspaces.router, prefix="/v1", tags=["workspaces"])
app.include_router(projects.router, prefix="/v1", tags=["projects"])
app.include_router(documents.router, prefix="/v1", tags=["documents"])
app.include_router(ai.router, prefix="/v1/ai", tags=["ai"])
app.include_router(security.router, prefix="/v1/security", tags=["security"])
app.include_router(data_control.router, prefix="/v1/data", tags=["data-control"])
app.include_router(notifications.router, prefix="/v1", tags=["notifications"])
app.include_router(connectors.router, prefix="/v1", tags=["connectors"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tenant-api"}


@app.get("/")
async def root():
    return {
        "name": "Area X Tenant API",
        "version": "1.0.0",
        "docs": "/docs",
    }
