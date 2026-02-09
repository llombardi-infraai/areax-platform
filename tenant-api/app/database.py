from typing import AsyncGenerator, Optional
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings

# Context variable for tenant database URL
tenant_db_url_var: ContextVar[Optional[str]] = ContextVar("tenant_db_url", default=None)
tenant_org_id_var: ContextVar[Optional[str]] = ContextVar("tenant_org_id", default=None)
tenant_user_id_var: ContextVar[Optional[str]] = ContextVar("tenant_user_id", default=None)

Base = declarative_base()

# Engine will be created per-tenant
_engine = None
_session_maker = None


def get_engine(db_url: Optional[str] = None):
    """Get or create async engine for the current tenant."""
    url = db_url or tenant_db_url_var.get()
    if not url:
        raise ValueError("No database URL provided for tenant")
    
    return create_async_engine(
        url,
        echo=False,
        poolclass=NullPool,  # Stateless for multi-tenant
        future=True,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for current tenant context."""
    db_url = tenant_db_url_var.get()
    if not db_url:
        raise ValueError("No tenant database URL in context")
    
    engine = get_engine(db_url)
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Default engine for migrations/admin
engine = create_async_engine(
    settings.DATABASE_URL_TEMPLATE.format(host="localhost", db="areax_default"),
    echo=False,
    poolclass=NullPool,
)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async for session in get_session():
        yield session
