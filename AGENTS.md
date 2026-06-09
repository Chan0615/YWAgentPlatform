# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

## Project Overview

YWAgentPlatform is a unified operations portal (统一运维门户) that provides a single entry point for managing multiple operations sub-applications. It follows an "Alibaba Cloud console" pattern where sub-apps are embedded via iframe with automatic token passing for SSO.

## Tech Stack

| Layer | Stack |
|-------|-------|
| Frontend | Vue 3 + TypeScript + Ant Design Vue 4 + Vite + Pinia |
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) + MySQL 8 |
| Cache | Redis 7 |
| Deployment | Docker Compose + Nginx |

## Development Commands

### Frontend (`/frontend`)

```bash
# Install dependencies
npm install

# Development server (port 5173, proxies /api to localhost:8000)
npm run dev

# Type check only
npm run type-check

# Production build (type check + vite build)
npm run build
```

### Backend (`/backend`)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server (port 8000, auto-reload in DEBUG mode)
python main.py
# or
uvicorn main:app --reload --port 8000
```

### Deployment

```bash
# First-time deployment
./deploy.sh init

# Update all services (git pull + rebuild)
./deploy.sh all

# Update specific service
./deploy.sh backend
./deploy.sh frontend

# Database only (MySQL + Redis)
./deploy.sh db

# View logs/status
./deploy.sh logs [service_name]
./deploy.sh status
```

## Architecture

### Permission Model (RBAC)

Three-level permission hierarchy:
- **App-level** (`app:agenticops`) - Controls access to sub-applications
- **Menu-level** (`menu:system:user`) - Controls sidebar visibility
- **Button-level** (`btn:user:create`) - Controls action button visibility

Relationship: `User ──M:N──▶ Role ──M:N──▶ Permission`

Frontend button control via directive: `v-permission="'btn:user:create'"`

### Sub-application Integration

Sub-apps are loaded via iframe in `AppContainer` view with automatic token injection:
- Portal passes JWT token as URL parameter to sub-app
- Sub-apps read token and authenticate independently
- Currently integrated: AgenticOps, Agent Platform, Daily Tools

### Authentication Flow

- JWT dual-token: Access Token (30min) + Refresh Token (7 days)
- Frontend axios interceptor handles automatic token refresh on 401
- Token stored in localStorage, managed by `@/utils/auth.ts`

### Backend Structure

```
backend/app/
├── api/          # FastAPI routers (auth, users, roles, permissions, applications, audit, dashboard)
├── core/         # config.py (pydantic-settings), database.py (async SQLAlchemy)
├── models/       # SQLAlchemy ORM models
├── schemas/      # Pydantic request/response schemas
├── middleware/   # AuditMiddleware for operation logging
├── services/     # Seed data initialization
└── utils/        # JWT helpers, password hashing
```

### Frontend Structure

```
frontend/src/
├── api/          # Axios request wrapper + API modules
├── directives/   # v-permission directive for button-level access control
├── layouts/      # MainLayout (sidebar + header + content area)
├── router/       # Routes + navigation guards (permission check, token validation)
├── store/        # Pinia stores (user state, app state)
├── utils/        # Token management helpers
└── views/        # Page components (login, dashboard, app-center, app-container, system)
```

## API Endpoints

All APIs prefixed with `/api/v1`:

| Module | Path | Description |
|--------|------|-------------|
| Auth | `/auth` | Login, logout, refresh token, get user info |
| Users | `/users` | User CRUD, role assignment |
| Roles | `/roles` | Role CRUD, permission assignment |
| Permissions | `/permissions` | Permission tree CRUD |
| Applications | `/applications` | Sub-app registration, visible app list |
| Audit | `/audit-logs` | Operation log query (admin only) |
| Dashboard | `/dashboard` | Dashboard statistics |

## Environment Variables

### Backend (`/backend/.env`)

Key variables:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - MySQL connection
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` - Redis connection
- `JWT_SECRET_KEY` - JWT signing key (change in production)
- `DEBUG` - Enable auto-reload and verbose logging
- `CORS_ORIGINS` - Allowed origins (JSON array format)

### Root (`.env`)

Used by docker-compose for container configuration:
- `DB_HOST`, `REDIS_HOST` - Container network addresses
- `MYSQL_ROOT_PASSWORD` - Database root password

## Key Patterns

### Adding a New API Endpoint

1. Create router in `backend/app/api/your_module.py`
2. Define schemas in `backend/app/schemas/`
3. Add model if needed in `backend/app/models/`
4. Register router in `main.py` with `app.include_router()`

### Adding a New Page

1. Create view component in `frontend/src/views/your-page/index.vue`
2. Add route in `frontend/src/router/index.ts` with appropriate `meta.permission`
3. Add API calls in `frontend/src/api/`
4. Use `v-permission` directive for button-level access control

### Path Alias

Frontend uses `@` alias for `src/` directory (configured in both `vite.config.ts` and `tsconfig.json`).
