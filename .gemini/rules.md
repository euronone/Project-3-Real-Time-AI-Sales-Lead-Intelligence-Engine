# SalesIQ — Gemini AI Coding Rules

## Product Context

SalesIQ is a Real-Time AI Sales & Lead Intelligence Engine. Multi-tenant SaaS platform that listens to sales calls in real time, guides representatives with AI suggestions, analyzes conversations, and predicts deal outcomes. Refer to CLAUDE.md for full architecture and feature details.

## Architecture Overview

- **Backend:** Python 3.12 + FastAPI (async) + SQLAlchemy 2.0 + AsyncPG + Alembic + Celery + python-socketio
- **Frontend:** Next.js 14 (App Router) + TypeScript (strict) + Tailwind CSS + TanStack Query + Zustand + Axios
- **Database:** PostgreSQL 16 (multi-tenant, row-level tenant isolation)
- **Cache/Broker:** Redis (Celery broker, Pub/Sub for real-time events, caching)
- **External APIs:** OpenAI (GPT-4o + Whisper), Twilio Voice SDK
- **Real-time:** Socket.IO (python-socketio + socket.io-client)
- **Storage:** S3-compatible for call recordings

## Core Engineering Principles

1. Think like an architect first, then implement like a senior engineer.
2. Follow clean architecture: routes → services → repositories → models.
3. Keep controllers/routes thin; business logic in services.
4. Prefer scalable, modular, production-ready code over shortcuts.
5. Extend existing patterns before introducing new ones.
6. Use type hints (Python) and TypeScript types everywhere.
7. Add structured logging on critical paths.
8. Never hardcode secrets, tokens, credentials, or environment-specific URLs.

## Backend Rules

- Routes handle HTTP/WebSocket concerns only.
- Business logic lives in `backend/app/services/`.
- Database access via SQLAlchemy async sessions with dependency injection.
- Validation via Pydantic v2 schemas in `backend/app/schemas/`.
- Async I/O for all external calls (OpenAI, Twilio, Redis).
- RESTful APIs versioned at `/api/v1/`.
- Celery tasks in `backend/app/tasks/` for heavy processing (transcription, analysis, prediction).

## Frontend Rules

- TypeScript strict mode; no `any` types.
- Server state via TanStack React Query; client state via Zustand stores.
- API calls centralized in `frontend/src/lib/api.ts` (Axios with JWT interceptor).
- Real-time updates via Socket.IO client in `frontend/src/lib/socket.ts`.
- Reusable components in `frontend/src/components/ui/`.
- Two portals: Admin (`/(dashboard)/admin/`) and Agent (`/(dashboard)/agent/`).

## Database Rules

- All schema changes through Alembic migrations.
- Every entity: id (UUID), created_at, updated_at.
- Multi-tenant: tenant_id on all tenant-scoped tables; enforce in queries.
- Use enums for finite states (call_status, lead_status, user_role).
- Avoid N+1 queries; use joinedload/selectinload.

## Real-Time Call Pipeline

1. Agent clicks "Call" → Twilio Client SDK initiates call.
2. Twilio Media Streams → Backend WebSocket handler → audio chunks.
3. Audio → Whisper STT → transcript → GPT-4o → sentiment + guidance.
4. Results → Redis Pub/Sub → Socket.IO → Frontend live panel.
5. Call ends → Celery task → full transcription + deep analysis + deal prediction.

## Security Rules

- RBAC: Super Admin, Tenant Admin, Manager, Agent.
- Tenant isolation: every query filters by tenant_id.
- Call recordings: encrypted storage, access-controlled, audit-logged.
- Never log PII, passwords, or tokens.
- Validate all inputs; sanitize before sending to OpenAI.
- Rate limit expensive/AI endpoints.

## Testing Rules

- Backend: pytest + pytest-asyncio; mock OpenAI/Twilio; use test database.
- Frontend: Vitest + React Testing Library; Playwright for E2E.
- Never depend on live external APIs in test runs.

## Do Not

- Put SQL/ORM logic in route files.
- Put business logic in Pydantic schemas.
- Hardcode any secrets or URLs.
- Send raw audio to LLM prompts (use STT first).
- Expose internal errors to end users.
- Skip tenant_id filtering in queries.
- Change architecture without explicit approval.
