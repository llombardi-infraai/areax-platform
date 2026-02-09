# Area X Tenant API

Multi-tenant business logic service for Area X. Handles workspaces, projects, AI advisor, and data controls.

## Architecture

This service receives requests from the Control Plane (after authentication). Each request includes:
- JWT token (already validated by Control Plane or re-validated here)
- Organization ID (tenant context)
- Database connection info (from Control Plane routing)

## Features

- **Workspaces & Projects**: Manage organizational structure
- **Documents**: Store and version blueprints, knowledge base, requirements
- **AI Advisor**: Conversational AI powered by Moonshot API with memory
- **Security Center**: Audit logging and security overview
- **Data Control**: Exports, deletions, and retention policies
- **Notifications**: User notification system
- **Connectors**: External system integrations (AWS, Azure, GitHub, etc.)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd tenant-api
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8081
```

### Environment Variables

```bash
# Database
DATABASE_URL_TEMPLATE=postgresql+asyncpg://user:pass@{host}/{db}

# Redis
REDIS_URL=redis://localhost:6379

# AI Service (Moonshot)
MOONSHOT_API_KEY=your-api-key
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
MOONSHOT_MODEL=moonshot-v1-128k

# Control Plane
CONTROL_PLANE_URL=http://localhost:8080

# JWT
JWT_PUBLIC_KEY=<RS256 public key>
JWT_ALGORITHM=RS256

# File Storage
FILE_STORAGE_BUCKET=areax-files
FILE_STORAGE_ENDPOINT=https://nyc3.digitaloceanspaces.com
FILE_STORAGE_ACCESS_KEY=
FILE_STORAGE_SECRET_KEY=

# Server
PORT=8081
HOST=0.0.0.0

# CORS
CORS_ORIGINS=["*"]

# Logging
LOG_LEVEL=INFO

# Security
ENCRYPTION_KEY=<32-byte-key>
```

## API Documentation

Once running, API documentation is available at:
- Swagger UI: http://localhost:8081/docs
- ReDoc: http://localhost:8081/redoc

## API Endpoints

### Workspaces & Projects
```
GET    /v1/workspaces
POST   /v1/workspaces
GET    /v1/workspaces/{id}
PATCH  /v1/workspaces/{id}
DELETE /v1/workspaces/{id}
GET    /v1/workspaces/{id}/projects
POST   /v1/workspaces/{id}/projects
GET    /v1/projects/{id}
PATCH  /v1/projects/{id}
DELETE /v1/projects/{id}
```

### Documents
```
GET    /v1/projects/{id}/documents
POST   /v1/projects/{id}/documents
GET    /v1/documents/{id}
PATCH  /v1/documents/{id}
DELETE /v1/documents/{id}
```

### AI Advisor
```
POST   /v1/ai/conversations
GET    /v1/ai/conversations
GET    /v1/ai/conversations/{id}
POST   /v1/ai/conversations/{id}/messages
POST   /v1/ai/blueprint/builder/start
POST   /v1/ai/blueprint/builder/answer
POST   /v1/ai/blueprint/builder/generate
GET    /v1/ai/memory
DELETE /v1/ai/memory/{id}
```

### Security Center
```
GET /v1/security/overview
GET /v1/security/audit-logs
GET /v1/security/users
```

### Data Control
```
GET    /v1/data/retention
PATCH  /v1/data/retention
POST   /v1/data/exports
GET    /v1/data/exports
GET    /v1/data/exports/{id}/download
POST   /v1/data/deletions
GET    /v1/data/deletions
```

### Notifications
```
GET    /v1/notifications
GET    /v1/notifications/summary
PATCH  /v1/notifications/{id}/read
PATCH  /v1/notifications/read-all
```

### Connectors
```
GET    /v1/connectors/catalog
GET    /v1/connectors
POST   /v1/connectors
DELETE /v1/connectors/{id}
POST   /v1/connectors/{id}/test
```

## Docker

Build and run with Docker:

```bash
# Build
docker build -t tenant-api .

# Run
docker run -p 8081:8081 \
  -e DATABASE_URL_TEMPLATE="postgresql+asyncpg://user:pass@{host}/{db}" \
  -e MOONSHOT_API_KEY="your-key" \
  tenant-api
```

## Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app tests/
```

## Database Migrations

Using Alembic for migrations:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Architecture Decisions

### Tenant Isolation
Every database query includes an `org_id` filter to ensure strict tenant isolation.

### Async/Await
Full async support using SQLAlchemy 2.0 async ORM throughout the application.

### Context Variables
Tenant context (org_id, user_id, db_url) is stored in context variables for automatic propagation without passing through every function.

### Permission System
- Deny-by-default
- Role-based permissions (Owner, Admin, Member, Viewer)
- Object-level permission checks for workspace/project/document access

### Audit Logging
Every write operation creates an audit log entry with user, action, resource, and details.

### AI Memory
Facts extracted from conversations are stored per user/org scope for personalization.

## Development

### Code Style

Format code with Black:
```bash
black app/ models/ routers/ services/
```

Check types with mypy:
```bash
mypy app/
```

Lint with flake8:
```bash
flake8 app/
```

## License

Proprietary - Area X Platform
