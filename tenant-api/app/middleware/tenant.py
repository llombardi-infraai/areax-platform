import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.config import settings
from app.database import tenant_org_id_var, tenant_user_id_var, tenant_db_url_var

logger = logging.getLogger(__name__)


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract tenant context from request headers.
    
    Headers expected from Control Plane:
    - X-Organization-ID: The tenant organization ID
    - X-User-ID: The authenticated user ID
    - X-Database-URL: The tenant-specific database connection URL
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Extract tenant context from headers
        org_id = request.headers.get("X-Organization-ID")
        user_id = request.headers.get("X-User-ID")
        db_url = request.headers.get("X-Database-URL")
        
        # Set context variables
        org_token = None
        user_token = None
        db_token = None
        
        try:
            if org_id:
                org_token = tenant_org_id_var.set(org_id)
            if user_id:
                user_token = tenant_user_id_var.set(user_id)
            if db_url:
                db_token = tenant_db_url_var.set(db_url)
            elif org_id:
                # Generate DB URL from template
                template = settings.DATABASE_URL_TEMPLATE
                generated_url = template.format(
                    host=f"db-{org_id}",
                    db=f"areax_{org_id.replace('-', '_')}"
                )
                db_token = tenant_db_url_var.set(generated_url)
            
            # Log tenant context for debugging
            logger.debug(
                f"Request: {request.method} {request.url.path} | "
                f"Org: {org_id} | User: {user_id}"
            )
            
            response = await call_next(request)
            
            # Add tenant headers to response for debugging
            if org_id:
                response.headers["X-Tenant-Org"] = org_id
            
            return response
            
        finally:
            # Reset context variables
            if org_token:
                tenant_org_id_var.reset(org_token)
            if user_token:
                tenant_user_id_var.reset(user_token)
            if db_token:
                tenant_db_url_var.reset(db_token)
