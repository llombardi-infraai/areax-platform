# Area X Project Structure

```
areax/
├── control-plane/          # Go service - Auth & Routing
│   ├── cmd/
│   ├── internal/
│   └── go.mod
├── tenant-api/             # Python/FastAPI - Business Logic
│   ├── app/
│   ├── migrations/
│   └── requirements.txt
├── frontend/               # React + TypeScript
│   ├── src/
│   └── package.json
├── shared/                 # Shared types, protos
└── docker-compose.yml      # Local development
```

## Services

### Control Plane (Go + Gin)
- JWT authentication
- MFA (TOTP) verification
- Organization routing
- Session management

### Tenant API (Python + FastAPI)
- Workspaces/Projects
- AI Advisor
- Security Center
- Data Control

### Frontend (React + TypeScript)
- Dashboard
- Security Center UI
- AI Chat Interface
- Blueprint Builder
