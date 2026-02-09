# Area X Control Plane

A critical authentication and routing service for the Area X platform, built with Go and Gin.

## Features

- **Authentication**: Email/password login with bcrypt hashing
- **JWT Tokens**: RS256 signed tokens with access (15min) and refresh (7 days) tokens
- **MFA/TOTP**: Time-based one-time password support with recovery codes
- **Organization Routing**: Multi-tenant routing with database/host mapping
- **Session Management**: Redis-based session storage with revocation

## Prerequisites

- Go 1.23+
- PostgreSQL 14+
- Redis 6+
- OpenSSL (for generating JWT keys)

## Quick Start

### 1. Generate JWT Keys

```bash
./scripts/generate-keys.sh
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Database Migrations

The service automatically runs migrations on startup.

### 4. Build and Run

```bash
# Build
go build -o control-plane ./cmd/

# Run
./control-plane
```

Or with Docker:

```bash
docker build -t areax-control-plane .
docker run -p 8080:8080 --env-file .env areax-control-plane
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v1/auth/login` | Login with email/password | No |
| POST | `/v1/auth/mfa/setup` | Setup MFA for user | Yes |
| POST | `/v1/auth/mfa/verify` | Verify and enable MFA | Yes |
| POST | `/v1/auth/refresh` | Refresh access token | No |
| POST | `/v1/auth/logout` | Logout and revoke session | Yes |
| GET | `/v1/auth/sessions` | List active sessions | Yes |
| DELETE | `/v1/auth/sessions/:id` | Revoke specific session | Yes |

### Organizations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/v1/orgs` | List user's organizations | Yes |
| POST | `/v1/orgs` | Create new organization | Yes |
| GET | `/v1/orgs/:id/routing` | Get routing info for org | Yes |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

## API Examples

### Login

```bash
curl -X POST http://localhost:8080/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

### Create Organization

```bash
curl -X POST http://localhost:8080/v1/orgs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "name": "My Org",
    "slug": "my-org",
    "region": "us-east-1",
    "database_host": "db.example.com",
    "database_name": "my_org_db",
    "storage_bucket": "my-org-bucket"
  }'
```

### Get Routing Info

```bash
curl http://localhost:8080/v1/orgs/{org_id}/routing \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Response:
```json
{
  "database_host": "db.example.com",
  "database_name": "my_org_db",
  "storage_bucket": "my-org-bucket",
  "region": "us-east-1"
}
```

## Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://localhost:5432/controlplane?sslmode=disable` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_PRIVATE_KEY` | RSA private key for signing | (required) |
| `JWT_PUBLIC_KEY` | RSA public key for verification | (required) |
| `PORT` | HTTP server port | `8080` |

## Testing

```bash
# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Run specific package tests
go test ./internal/auth/...
```

## Database Schema

### Users
- `id` (UUID, PK)
- `email` (VARCHAR, UNIQUE)
- `password_hash` (VARCHAR)
- `mfa_secret` (VARCHAR, nullable)
- `mfa_enabled` (BOOLEAN)
- `recovery_codes` (TEXT[])
- `created_at` (TIMESTAMP)

### Organizations
- `id` (UUID, PK)
- `name` (VARCHAR)
- `slug` (VARCHAR, UNIQUE)
- `region` (VARCHAR)
- `database_host` (VARCHAR)
- `database_name` (VARCHAR)
- `storage_bucket` (VARCHAR)
- `created_at` (TIMESTAMP)

### Memberships
- `id` (UUID, PK)
- `user_id` (UUID, FK)
- `org_id` (UUID, FK)
- `role` (VARCHAR)
- `created_at` (TIMESTAMP)

### Sessions
- `id` (UUID, PK)
- `user_id` (UUID, FK)
- `org_id` (UUID, FK, nullable)
- `token_hash` (VARCHAR, UNIQUE)
- `expires_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)

## Security Features

- Passwords hashed with bcrypt (cost 12)
- RS256 JWT signing (asymmetric keys)
- Parameterized SQL queries (SQL injection safe)
- Session revocation support
- MFA/TOTP support
- CORS protection
- Structured request logging

## Project Structure

```
.
├── cmd/
│   └── main.go              # Application entry point
├── internal/
│   ├── auth/                # Authentication handlers
│   ├── db/                  # Database connection, models, migrations
│   ├── middleware/          # Gin middleware
│   └── orgs/                # Organization handlers
├── pkg/
│   ├── jwt/                 # JWT utilities
│   ├── password/            # Password hashing
│   └── totp/                # TOTP/MFA utilities
├── scripts/
│   └── generate-keys.sh     # JWT key generation
├── Dockerfile
├── go.mod
├── go.sum
└── README.md
```

## License

Proprietary - Area X Platform
