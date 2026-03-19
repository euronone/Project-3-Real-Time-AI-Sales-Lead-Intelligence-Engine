# SalesIQ — System Architecture

## Purpose

This document describes the high-level architecture for SalesIQ. All implementation must place components in the correct layers described here. For full feature context, see `docs/PRD.md`. For coding conventions, see `CLAUDE.md`.

---

## High-Level View

```
┌──────────────────────────────────────────────────────────────────────┐
│  Clients: Admin Portal (web), Agent Portal (web)                      │
│  Both served by a single Next.js application (role-based routing)     │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                         REST API / WebSocket (Socket.IO)
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌─────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  FastAPI Server │      │  Socket.IO Server │      │  Twilio Webhooks │
│  (REST + Auth)  │      │  (Real-Time Push) │      │  (Voice events)  │
└────────┬────────┘      └────────┬─────────┘      └────────┬─────────┘
         │                        │                          │
         └────────────┬───────────┘              ┌───────────┘
                      ▼                          ▼
         ┌────────────────────────────────────────────────────┐
         │                Services Layer                        │
         │  auth, lead, call, analysis, prediction, guidance,   │
         │  twilio, storage, notification, webhook, tenant, user │
         └────────────────────┬───────────────────────────────┘
                              │
       ┌──────────────────────┼──────────────────────────────────┐
       ▼                      ▼                                  ▼
┌──────────────┐   ┌─────────────────────┐          ┌──────────────────┐
│  PostgreSQL  │   │  Redis              │          │  Celery Workers  │
│  (SQLAlchemy │   │  - Cache            │          │  - transcription │
│   ORM, async)│   │  - Pub/Sub bridge   │          │  - analysis      │
│              │   │  - Celery broker    │          │  - prediction    │
└──────────────┘   └─────────────────────┘          │  - notifications │
                                                     └────────┬─────────┘
                                                              │
                                               ┌─────────────┴──────────────┐
                                               ▼                            ▼
                                    ┌──────────────────┐        ┌─────────────────────┐
                                    │  OpenAI API      │        │  Twilio Voice       │
                                    │  GPT-4o: analysis│        │  Calls + Recording  │
                                    │  Whisper: STT    │        │  Media Streams      │
                                    └──────────────────┘        └──────────┬──────────┘
                                                                            │
                                                                 ┌──────────▼──────────┐
                                                                 │  AWS S3             │
                                                                 │  Recording Storage  │
                                                                 └─────────────────────┘
```

---

## Component Roles

### Frontend — Next.js (TypeScript + Tailwind)

**Two portals in one app:**
- **Admin Portal** (`/admin/*`): Tenant admins and managers. Agent management, lead management, lead flow designer, campaigns, call routing rules, analytics dashboards, tenant settings, audit log.
- **Agent Portal** (`/agent/*`): Sales reps. Call queue, active call UI (live transcript + AI guidance), call history + analysis, assigned leads, deal predictions, AI coaching.

**Layers:**
- `src/app/` — Routes (App Router)
- `src/components/ui/` — Reusable design system primitives
- `src/components/{calls,leads,agents,analytics,predictions}/` — Feature components
- `src/hooks/` — Custom hooks (auth, socket, call, transcript, notifications)
- `src/lib/` — API client, Socket.IO setup, Twilio init, utilities
- `src/stores/` — Zustand stores (auth, call, notifications)
- `src/types/` — TypeScript domain types

### Backend — FastAPI (Python 3.12+, async)

**Layers:**
- `app/api/v1/` — Thin HTTP/WebSocket route handlers (request parsing, response shaping)
- `app/services/` — Business logic (auth, lead, call, analysis, prediction, guidance, twilio, storage, notification, webhook, user, tenant)
- `app/ai/` — AI pipeline (openai_client, pipeline.py, prompts/)
- `app/realtime/` — Socket.IO server, Twilio Media Stream handler, Redis pub/sub bridge
- `app/tasks/` — Celery async workers (transcription, analysis, prediction, notifications)
- `app/models/` — SQLAlchemy ORM models
- `app/schemas/` — Pydantic v2 request/response schemas
- `app/core/` — Config, security, RBAC permissions, exceptions, middleware, DB engine

### Real-Time Event Pipeline

```
Twilio Media Stream (audio)
        │
        ▼
call_stream_handler.py
  → mulaw→WAV conversion
  → audio chunking
        │
        ▼
transcription_service.py
  → OpenAI Whisper API
  → transcript segment
        │
        ├─────────────────────────────────────────┐
        ▼                                         ▼
event_publisher.py                     guidance_service.py
  → Redis pub/sub                        → GPT-4o (streaming)
  (transcript channel)                   → guidance suggestion
        │                                         │
        ▼                                         ▼
socket_manager.py                      event_publisher.py
  → Socket.IO room emit                   → Redis pub/sub
  (transcript_chunk)                      (guidance channel)
        │                                         │
        └──────────────┬──────────────────────────┘
                       ▼
              Frontend Agent Portal
              (Live Transcript + AI Guidance Panel)
```

### Post-Call AI Pipeline (Celery)

```
Twilio recording callback
        │
        ▼
transcription_tasks.transcribe_call(call_id)
  → download recording from S3
  → OpenAI Whisper (full pass, batch)
  → store call_transcripts
        │
        ▼
analysis_tasks.analyze_call(call_id)
  → OpenAI GPT-4o (analysis prompt)
  → sentiment, topics, objections, key moments, scorecard
  → store call_analyses
        │
        ▼
prediction_tasks.predict_deal(lead_id, call_id)
  → OpenAI GPT-4o (prediction prompt)
  → win_probability, confidence, key_factors, red_flags
  → store deal_predictions
  → emit deal_prediction_updated via Socket.IO
        │
        ▼
notification_tasks.notify_deal_update(...)
  → in-app notification
  → optional email / outbound webhook
```

---

## Data Stores

| Store | Purpose |
|---|---|
| **PostgreSQL 16** | Source of truth for all entities: tenants, users, leads, calls, transcripts, analyses, predictions, campaigns, lead flows, notifications, audit logs |
| **Redis 7** | Real-time pub/sub (bridge AI workers → Socket.IO), Celery broker/result backend, application cache, rate limiting |
| **AWS S3** | Call recordings (binary audio), exported reports (CSV/PDF) |

---

## Cross-Cutting Concerns

- **Authentication:** JWT (access + refresh tokens) via `app/core/security.py`
- **Authorization:** RBAC via `app/core/permissions.py`; tenant isolation via `tenant_id` on every DB query
- **Observability:** `structlog` structured logging with `request_id` + `tenant_id` correlation IDs; Prometheus metrics
- **Security:** No secrets in code; Twilio signature validation; S3 presigned URLs; see `.cursor/rules/70-security.mdc`
- **Multi-tenancy:** Row-level `tenant_id` filtering on all SQLAlchemy queries; Redis keys namespaced by tenant; Socket.IO rooms validated per tenant

---

## References

- **PRD:** `docs/PRD.md`
- **API:** `docs/API_SPEC.md` and `docs/api-reference.md`
- **Deployment:** `docs/DEPLOYMENT.md` and `docs/deployment.md`
- **Full feature spec + directory structure + DB schema:** `CLAUDE.md`
- **Cursor Rules:** `.cursor/rules/*.mdc`
