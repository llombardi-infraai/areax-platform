# Area X Tenant API

FastAPI-based multi-tenant business logic service for Area X.

## Overview

This service handles:
- Workspaces and Projects
- Documents (Blueprints, Knowledge Base)
- AI Business Advisor (Moonshot API)
- Security Center & Audit Logs
- Data Control (Retention, Export, Deletion)
- Notifications
- Connector Framework

## Architecture

- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy 2.0 async
- **Cache**: Redis
- **AI**: Moonshot API (OpenAI-compatible)
- **Auth**: JWT (validated against Control Plane)

## Environment Variables

```bash
# Database
DATABASE_URL_TEMPLATE=postgresql+asyncpg://user:pass@{host}/{db}

# Redis
REDIS_URL=redis://localhost:6379

# AI Service
MOONSHOT_API_KEY=your_key_here
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
MOONSHOT_MODEL=moonshot-v1-128k

# Control Plane
CONTROL_PLANE_URL=http://localhost:8080
JWT_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----

# File Storage
FILE_STORAGE_BUCKET=areax-files
FILE_STORAGE_ENDPOINT=https://nyc3.digitaloceanspaces.com

# Server
PORT=8081
HOST=0.0.0.0
LOG_LEVEL=INFO
```

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run with uvicorn:
```bash
uvicorn app.main:app --reload --port 8081
```

3. Access API docs at: http://localhost:8081/docs

## Running with Docker

```bash
docker build -t areax-tenant-api .
docker run -p 8081:8081 --env-file .env areax-tenant-api
```

## API Endpoints

### Workspaces & Projects
- `GET /v1/workspaces` - List workspaces
- `POST /v1/workspaces` - Create workspace
- `GET /v1/workspaces/{id}` - Get workspace
- `GET /v1/workspaces/{id}/projects` - List projects
- `POST /v1/workspaces/{id}/projects` - Create project

### Documents
- `GET /v1/projects/{id}/documents` - List documents
- `POST /v1/projects/{id}/documents` - Create document
- `GET /v1/documents/{id}` - Get document

### AI Advisor
- `POST /v1/ai/conversations` - Start conversation
- `GET /v1/ai/conversations` - List conversations
- `POST /v1/ai/conversations/{id}/messages` - Send message
- `POST /v1/ai/blueprint/builder/start` - Start blueprint interview
- `POST /v1/ai/blueprint/builder/generate` - Generate blueprint

### Security
- `GET /v1/security/overview` - Security overview
- `GET /v1/security/audit-logs` - Audit logs

### Data Control
- `GET /v1/data/retention` - Retention settings
- `POST /v1/data/exports` - Request export
- `GET /v1/data/exports` - List exports

### Notifications
- `GET /v1/notifications` - List notifications
- `PATCH /v1/notifications/{id}/read` - Mark as read

### Connectors
- `GET /v1/connectors/catalog` - Available connectors
- `GET /v1/connectors` - List connected integrations
- `POST /v1/connectors` - Connect integration

## Tenant Context

This service receives tenant context from the Control Plane via headers:
- `X-Organization-ID`: The tenant organization ID
- `X-User-ID`: The authenticated user ID
- `X-Database-URL`: The tenant-specific database URL

The `TenantContextMiddleware` extracts these headers and sets them in the request context.
