# Area X Platform

Multi-tenant business operating system with AI-powered governance.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    (React + TypeScript)                     │
│                      Port: 5173                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Control Plane                           │
│                       (Go + Gin)                            │
│   Auth │ MFA │ Organizations │ Session Management          │
│                      Port: 8080                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      Tenant API                             │
│                 (Python + FastAPI)                          │
│   Workspaces │ AI Advisor │ Security │ Data Control        │
│                      Port: 8081                             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/llombardi-infraai/areax-platform.git
cd areax-platform
```

### 2. Set up environment variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

Required variables:
```env
# JWT Keys (generate with: ssh-keygen -t rsa -b 4096 -m PEM -f jwt.key)
JWT_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----

JWT_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----

# Moonshot AI API Key
MOONSHOT_API_KEY=sk-your-key-here
```

### 3. Start all services

```bash
docker-compose up -d
```

### 4. Access the application

- **Frontend**: http://localhost:5173
- **Control Plane API**: http://localhost:8080
- **Tenant API**: http://localhost:8081

### 5. Create first user (via API)

```bash
curl -X POST http://localhost:8080/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"securepassword123"}'
```

## Development

### Control Plane (Go)

```bash
cd control-plane
export DATABASE_URL="postgres://areax:areax_password@localhost:5432/control_plane?sslmode=disable"
export REDIS_URL="redis://localhost:6379"
go run cmd/main.go
```

### Tenant API (Python)

```bash
cd tenant-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8081
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

## Services

### Control Plane

Authentication and routing service.

**Features:**
- JWT-based authentication
- TOTP MFA with QR codes
- Organization management
- Session management with Redis

**Endpoints:**
- `POST /v1/auth/login`
- `POST /v1/auth/mfa/setup`
- `POST /v1/auth/mfa/verify`
- `GET /v1/orgs`
- `POST /v1/orgs`

### Tenant API

Business logic service.

**Features:**
- Workspaces & Projects
- AI Business Advisor (Moonshot)
- Security Center & Audit Logs
- Data Control (retention, exports)
- Notifications
- Connector framework

**Endpoints:**
- `GET /v1/workspaces`
- `POST /v1/ai/conversations`
- `GET /v1/security/overview`
- `POST /v1/data/exports`

### Frontend

React-based user interface.

**Features:**
- Authentication with MFA
- Dashboard with quick actions
- Workspace management
- Security Center
- Responsive design

## Database Schema

### Control Plane
- `users` - Global identity
- `organizations` - Tenant directory
- `memberships` - User-Org relationships
- `sessions` - Active sessions

### Tenant (per organization)
- `workspaces` - Department/area groups
- `projects` - Work containers
- `documents` - Blueprints, knowledge base
- `ai_conversations` - AI chat history
- `audit_logs` - Activity tracking
- `notifications` - User notifications
- `connectors` - External integrations

## Environment Variables

### Control Plane
| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8080` |
| `DATABASE_URL` | PostgreSQL connection | - |
| `REDIS_URL` | Redis connection | - |
| `JWT_PRIVATE_KEY` | RS256 private key | - |
| `JWT_PUBLIC_KEY` | RS256 public key | - |

### Tenant API
| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8081` |
| `DATABASE_URL_TEMPLATE` | DB URL template | - |
| `REDIS_URL` | Redis connection | - |
| `MOONSHOT_API_KEY` | Moonshot AI key | - |
| `CONTROL_PLANE_URL` | Control Plane URL | - |

### Frontend
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_CONTROL_API_URL` | Control Plane API | `http://localhost:8080/v1` |
| `VITE_TENANT_API_URL` | Tenant API | `http://localhost:8081/v1` |

## API Documentation

- Control Plane: http://localhost:8080/docs (when running)
- Tenant API: http://localhost:8081/docs (when running)

## License

MIT
