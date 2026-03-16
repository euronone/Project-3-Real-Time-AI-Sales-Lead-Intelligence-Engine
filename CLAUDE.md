# SalesIQ - Real-Time AI Sales & Lead Intelligence Engine

## Project Overview

SalesIQ is a multi-tenant SaaS platform that listens to sales calls in real time, guides representatives, analyzes conversations, and predicts deal outcomes. B2B sales teams, call centers, and CRM platforms can integrate this system to improve sales performance through AI-driven insights.

### Business Model

- **Multi-tenant SaaS**: Each vendor (tenant) gets an isolated workspace
- **Admin Portal**: Tenant admins manage agents, leads, call flows, and analytics
- **Agent Portal**: Sales reps see real-time guidance, call history, feedback, and deal predictions
- **API-first**: Tenants can integrate SalesIQ into their existing CRM/tools via REST APIs and webhooks

---

## Core Features

### 1. Authentication & Multi-Tenancy

- Tenant registration and onboarding with organization setup
- Role-based access control (RBAC): Super Admin, Tenant Admin, Manager, Agent
- JWT-based authentication with refresh tokens
- Tenant isolation at database level (schema-per-tenant or row-level security)
- SSO support (OAuth2 / SAML) for enterprise tenants
- Invite-based user onboarding within a tenant

### 2. Admin Portal

- **Dashboard**: Tenant-wide KPIs — total calls, conversion rate, active agents, pipeline value, AI score trends
- **Agent Management**: Create/edit/deactivate agents, assign roles, view agent performance scorecards
- **Lead Management**: Create/import leads (CSV/API), assign leads to agents, set lead priority and status
- **Lead Flow Designer**: Visual drag-and-drop flow builder to define call sequences, follow-up cadences, and escalation rules
- **Call Routing Rules**: Configure round-robin, skill-based, or priority-based lead-to-agent assignment
- **Campaign Management**: Group leads into campaigns, set call scripts/templates, track campaign metrics
- **Analytics & Reports**: Conversion funnels, agent leaderboards, call duration trends, AI prediction accuracy, exportable reports (PDF/CSV)
- **Settings**: Tenant branding, notification preferences, integration keys, billing/subscription management
- **Audit Log**: Track all admin actions for compliance

### 3. Agent Portal

- **Agent Dashboard**: Today's call queue, upcoming follow-ups, personal KPIs, recent AI feedback
- **Call Interface**: Click-to-call from the dashboard, integrated softphone via WebRTC/Twilio
- **Real-Time Call Guidance**: Live transcript panel during calls, AI-suggested talking points, objection-handling tips, and next-best-action prompts displayed in real time
- **Post-Call Summary**: Auto-generated call summary, key topics discussed, action items extracted, sentiment timeline
- **AI Feedback & Coaching**: Per-call scorecard (talk ratio, filler words, engagement level, objection handling), improvement suggestions
- **Deal Prediction**: AI-predicted deal outcome (win probability %) with reasoning, updated after every interaction
- **Red Flag Alerts**: Real-time and post-call alerts for negative sentiment, competitor mentions, pricing objections, customer hesitation
- **Lead Detail View**: Full lead history — all calls, emails, notes, deal stage, predicted outcome
- **Notes & Follow-ups**: Add call notes, schedule follow-ups, set reminders

### 4. Call Infrastructure

- **Cloud Telephony Integration**: Twilio Voice SDK for outbound/inbound calls
- **Call Recording**: All calls recorded and stored in cloud storage (AWS S3 / equivalent)
- **Real-Time Audio Streaming**: Twilio Media Streams → WebSocket → backend for live transcription
- **Call Controls**: Hold, mute, transfer, conference, call disposition tagging
- **Call Metadata**: Duration, timestamps, caller/callee info, disposition, recording URL

### 5. Speech-to-Text Pipeline

- **Real-Time Transcription**: OpenAI Whisper API (or Whisper large-v3 self-hosted) for live audio stream transcription
- **Batch Transcription**: Post-call full transcription for recordings (higher accuracy pass)
- **Speaker Diarization**: Identify agent vs. customer speech segments
- **Language Support**: English primary, extensible to other languages
- **Transcript Storage**: Full transcripts stored and indexed for search

### 6. AI Conversation Analysis Engine

- **Transcript Analysis via LLM (OpenAI GPT-4o)**:
  - Sentiment analysis (per-utterance and overall)
  - Topic extraction and categorization
  - Objection detection and classification
  - Key moment identification (pricing discussion, commitment signals, competitor mentions)
  - Talk-to-listen ratio calculation
  - Filler word and dead air detection
- **Real-Time Analysis**: Streaming analysis during live calls for immediate guidance
- **Post-Call Deep Analysis**: Comprehensive analysis after call ends with full transcript context

### 7. Deal Outcome Prediction

- **LLM-Based Prediction (Primary)**:
  - Feed call transcript + lead history + CRM data to GPT-4o
  - Structured output: win probability (0-100%), confidence level, key factors, recommended next steps
  - Updated incrementally after each customer interaction
  - Reasoning chain provided for transparency
- **Historical Pattern Matching**:
  - Compare current deal signals against historical won/lost deals
  - Identify similar deal patterns and their outcomes
- **Prediction Dashboard**: Visual pipeline with AI-scored deals, filterable by probability range

### 8. Real-Time Guidance System

- **WebSocket-Driven Live Updates**: Sub-second latency from transcription to guidance display
- **Guidance Types**:
  - Suggested responses to customer objections
  - Recommended questions based on conversation flow
  - Warning alerts (customer frustration detected, off-script deviation)
  - Competitive battle cards triggered by competitor mentions
  - Pricing guidance based on deal context
- **Knowledge Base Integration**: Pull from company-specific playbooks and best practices
- **Configurable Rules Engine**: Admins can define custom triggers and guidance rules

### 9. Notifications & Alerts

- In-app notification center
- Email notifications for critical events (deal at risk, missed follow-up, new lead assigned)
- Webhook notifications for external integrations
- Configurable alert thresholds per tenant

### 10. Integrations & API

- **REST API**: Full CRUD for leads, agents, calls, analytics — documented via OpenAPI/Swagger
- **Webhooks**: Outbound webhooks for call events, deal stage changes, AI alerts
- **CRM Integration**: Salesforce, HubSpot connectors (phase 2)
- **Calendar Integration**: Google Calendar / Outlook for scheduling (phase 2)

---

## Technology Stack

### Frontend (Next.js Application)

| Layer | Technology |
|---|---|
| Framework | Next.js 14+ (App Router) |
| Language | TypeScript (strict mode) |
| Styling | Tailwind CSS 3+ |
| State Management | Zustand (global) + React Query / TanStack Query (server state) |
| Real-Time | Socket.IO client for live transcription & guidance |
| Forms | React Hook Form + Zod validation |
| Charts & Analytics | Recharts |
| Drag-and-Drop | React Flow (lead flow designer) |
| Audio/Call UI | Twilio Client JS SDK |
| HTTP Client | Axios with interceptors for auth |
| Testing | Vitest + React Testing Library + Playwright (E2E) |

### Backend (Python FastAPI)

| Layer | Technology |
|---|---|
| Framework | FastAPI (async) |
| Language | Python 3.12+ |
| ORM | SQLAlchemy 2.0 (async) + Alembic (migrations) |
| Database | PostgreSQL 16 (primary) |
| Cache & Pub/Sub | Redis 7 (caching, session store, real-time pub/sub) |
| Task Queue | Celery with Redis broker (async jobs: transcription, analysis) |
| WebSocket | FastAPI WebSocket + Socket.IO (python-socketio) |
| Auth | python-jose (JWT), passlib (hashing), OAuth2 flows |
| AI/LLM | OpenAI Python SDK (GPT-4o for analysis, Whisper for STT) |
| Telephony | Twilio Python SDK |
| Storage | boto3 (AWS S3 for recordings) |
| Validation | Pydantic v2 |
| Testing | pytest + pytest-asyncio + httpx (async test client) |
| API Docs | Auto-generated OpenAPI / Swagger UI |

### Infrastructure & DevOps

| Layer | Technology |
|---|---|
| Containerization | Docker + Docker Compose (dev), Kubernetes (prod) |
| CI/CD | GitHub Actions |
| Object Storage | AWS S3 (call recordings, exports) |
| CDN | CloudFront (frontend assets) |
| Monitoring | Prometheus + Grafana |
| Logging | Structured logging (structlog) → ELK or CloudWatch |
| Secret Management | AWS Secrets Manager / .env (dev) |

---

## Architecture

### High-Level System Architecture

```
                                    +-----------------------+
                                    |    Next.js Frontend   |
                                    |  (Admin + Agent UI)   |
                                    +----------+------------+
                                               |
                                    REST API / WebSocket
                                               |
                        +----------------------+----------------------+
                        |                                             |
              +---------v----------+                      +-----------v---------+
              |   FastAPI Server   |                      |  Socket.IO Server   |
              |   (REST + Auth)    |                      |  (Real-Time Events) |
              +---------+----------+                      +-----------+---------+
                        |                                             |
         +--------------+----------------+               +------------+
         |              |                |               |
   +-----v-----+ +-----v------+ +------v------+ +------v-------+
   | PostgreSQL | |   Redis    | |   Celery    | | WebSocket    |
   | (Data)     | | (Cache/    | |  Workers    | | Handler      |
   |            | |  Pub/Sub)  | | (AI Jobs)   | | (Live calls) |
   +------------+ +------------+ +------+------+ +------+-------+
                                        |                |
                              +---------v--------+       |
                              |   OpenAI API     |       |
                              | (GPT-4o/Whisper) |       |
                              +------------------+       |
                                                         |
                                              +----------v----------+
                                              |   Twilio Voice      |
                                              | (Calls + Recording  |
                                              |  + Media Streams)   |
                                              +---------------------+
                                                         |
                                              +----------v----------+
                                              |     AWS S3          |
                                              | (Recording Storage) |
                                              +---------------------+
```

### Real-Time Call Flow

```
1. Agent clicks "Call" on dashboard
2. Frontend → Twilio Client SDK → initiates outbound call via Twilio
3. Twilio connects the call and starts Media Stream (raw audio via WebSocket)
4. Twilio Media Stream → Backend WebSocket handler
5. Backend chunks audio → OpenAI Whisper API (real-time STT)
6. Transcript chunks → OpenAI GPT-4o (streaming analysis)
7. Analysis results (guidance, alerts, sentiment) → Redis Pub/Sub → Socket.IO → Frontend
8. Agent sees live transcript + AI guidance on screen
9. Call ends → Twilio sends recording URL webhook
10. Celery worker: download recording → full Whisper transcription → deep GPT-4o analysis
11. Post-call summary, scorecard, and deal prediction stored in PostgreSQL
12. Agent and admin see full call analysis in their dashboards
```

### Data Flow for Deal Prediction

```
Call Transcript + Lead History + Prior Interactions
                    |
                    v
        +------------------------+
        |   GPT-4o Prediction    |
        |   Prompt Template:     |
        |   - Transcript summary |
        |   - Customer sentiment |
        |   - Objections raised  |
        |   - Commitment signals |
        |   - Historical context |
        +------------------------+
                    |
                    v
        Structured JSON Output:
        {
          "win_probability": 72,
          "confidence": "high",
          "key_factors": [...],
          "red_flags": [...],
          "recommended_actions": [...],
          "reasoning": "..."
        }
```

---

## Directory Structure

```
salesiq/
├── CLAUDE.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── .github/
│   └── workflows/
│       ├── ci-frontend.yml
│       ├── ci-backend.yml
│       └── deploy.yml
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── .env.local.example
│   ├── public/
│   │   ├── images/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx                    # Root layout with providers
│   │   │   ├── page.tsx                      # Landing / login redirect
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   ├── register/page.tsx
│   │   │   │   └── forgot-password/page.tsx
│   │   │   ├── (dashboard)/
│   │   │   │   ├── layout.tsx                # Dashboard shell (sidebar + header)
│   │   │   │   ├── admin/
│   │   │   │   │   ├── page.tsx              # Admin dashboard home
│   │   │   │   │   ├── agents/
│   │   │   │   │   │   ├── page.tsx          # Agent list
│   │   │   │   │   │   └── [id]/page.tsx     # Agent detail / edit
│   │   │   │   │   ├── leads/
│   │   │   │   │   │   ├── page.tsx          # Lead list + import
│   │   │   │   │   │   └── [id]/page.tsx     # Lead detail
│   │   │   │   │   ├── lead-flows/
│   │   │   │   │   │   ├── page.tsx          # Flow list
│   │   │   │   │   │   └── [id]/page.tsx     # Flow designer (drag-and-drop)
│   │   │   │   │   ├── campaigns/
│   │   │   │   │   │   ├── page.tsx
│   │   │   │   │   │   └── [id]/page.tsx
│   │   │   │   │   ├── analytics/
│   │   │   │   │   │   └── page.tsx          # Reports & analytics
│   │   │   │   │   ├── call-routing/
│   │   │   │   │   │   └── page.tsx          # Call routing rules
│   │   │   │   │   ├── settings/
│   │   │   │   │   │   └── page.tsx          # Tenant settings
│   │   │   │   │   └── audit-log/
│   │   │   │   │       └── page.tsx
│   │   │   │   └── agent/
│   │   │   │       ├── page.tsx              # Agent dashboard home
│   │   │   │       ├── calls/
│   │   │   │       │   ├── page.tsx          # Call queue + history
│   │   │   │       │   └── [id]/page.tsx     # Call detail + AI analysis
│   │   │   │       ├── active-call/
│   │   │   │       │   └── page.tsx          # Live call screen (transcript + guidance)
│   │   │   │       ├── leads/
│   │   │   │       │   ├── page.tsx          # Assigned leads
│   │   │   │       │   └── [id]/page.tsx     # Lead detail + history
│   │   │   │       ├── predictions/
│   │   │   │       │   └── page.tsx          # Deal predictions pipeline
│   │   │   │       └── coaching/
│   │   │   │           └── page.tsx          # AI coaching & feedback
│   │   │   └── api/                          # Next.js API routes (BFF if needed)
│   │   │       └── auth/[...nextauth]/route.ts
│   │   ├── components/
│   │   │   ├── ui/                           # Reusable UI primitives
│   │   │   │   ├── button.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── modal.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── dropdown.tsx
│   │   │   │   ├── toast.tsx
│   │   │   │   └── loading.tsx
│   │   │   ├── layout/
│   │   │   │   ├── sidebar.tsx
│   │   │   │   ├── header.tsx
│   │   │   │   ├── breadcrumb.tsx
│   │   │   │   └── notification-bell.tsx
│   │   │   ├── calls/
│   │   │   │   ├── call-controls.tsx         # Mute, hold, transfer buttons
│   │   │   │   ├── live-transcript.tsx       # Real-time transcript panel
│   │   │   │   ├── ai-guidance-panel.tsx     # Live AI suggestions
│   │   │   │   ├── call-summary-card.tsx
│   │   │   │   ├── call-scorecard.tsx
│   │   │   │   └── sentiment-timeline.tsx
│   │   │   ├── leads/
│   │   │   │   ├── lead-table.tsx
│   │   │   │   ├── lead-card.tsx
│   │   │   │   ├── lead-import-modal.tsx
│   │   │   │   └── lead-flow-canvas.tsx      # React Flow based designer
│   │   │   ├── agents/
│   │   │   │   ├── agent-table.tsx
│   │   │   │   └── agent-scorecard.tsx
│   │   │   ├── analytics/
│   │   │   │   ├── kpi-card.tsx
│   │   │   │   ├── conversion-funnel.tsx
│   │   │   │   ├── agent-leaderboard.tsx
│   │   │   │   └── prediction-accuracy-chart.tsx
│   │   │   └── predictions/
│   │   │       ├── deal-pipeline.tsx
│   │   │       ├── win-probability-gauge.tsx
│   │   │       └── red-flag-alert.tsx
│   │   ├── hooks/
│   │   │   ├── use-auth.ts
│   │   │   ├── use-socket.ts                # Socket.IO connection hook
│   │   │   ├── use-live-transcript.ts
│   │   │   ├── use-call.ts                  # Twilio call management
│   │   │   └── use-notifications.ts
│   │   ├── lib/
│   │   │   ├── api.ts                       # Axios instance + interceptors
│   │   │   ├── socket.ts                    # Socket.IO client setup
│   │   │   ├── twilio.ts                    # Twilio device initialization
│   │   │   ├── utils.ts
│   │   │   └── constants.ts
│   │   ├── stores/
│   │   │   ├── auth-store.ts
│   │   │   ├── call-store.ts
│   │   │   └── notification-store.ts
│   │   ├── types/
│   │   │   ├── api.ts                       # API response types
│   │   │   ├── models.ts                    # Domain model types
│   │   │   ├── call.ts
│   │   │   ├── lead.ts
│   │   │   └── prediction.ts
│   │   └── styles/
│   │       └── globals.css
│   └── tests/
│       ├── unit/
│       └── e2e/
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── .env.example
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app factory + startup
│   │   ├── config.py                        # Settings via pydantic-settings
│   │   ├── dependencies.py                  # Dependency injection (DB session, current user, etc.)
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py                    # Top-level API router aggregator
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py                  # Login, register, refresh, SSO
│   │   │       ├── tenants.py               # Tenant CRUD, settings
│   │   │       ├── users.py                 # User management within tenant
│   │   │       ├── agents.py                # Agent CRUD, assignment
│   │   │       ├── leads.py                 # Lead CRUD, import, assignment
│   │   │       ├── lead_flows.py            # Lead flow CRUD, flow execution
│   │   │       ├── campaigns.py             # Campaign CRUD
│   │   │       ├── calls.py                 # Call records, recordings, transcripts
│   │   │       ├── call_routing.py          # Call routing rules
│   │   │       ├── analytics.py             # Analytics endpoints
│   │   │       ├── predictions.py           # Deal prediction endpoints
│   │   │       ├── notifications.py         # Notification preferences, history
│   │   │       ├── webhooks.py              # Outbound webhook config
│   │   │       └── twilio_webhooks.py       # Inbound Twilio event handlers
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # SQLAlchemy base, tenant mixin
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── lead.py
│   │   │   ├── lead_flow.py
│   │   │   ├── campaign.py
│   │   │   ├── call.py
│   │   │   ├── call_transcript.py
│   │   │   ├── call_analysis.py
│   │   │   ├── deal_prediction.py
│   │   │   ├── notification.py
│   │   │   ├── webhook.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── lead.py
│   │   │   ├── lead_flow.py
│   │   │   ├── campaign.py
│   │   │   ├── call.py
│   │   │   ├── analysis.py
│   │   │   ├── prediction.py
│   │   │   └── common.py                    # Pagination, filters, etc.
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py              # Authentication logic
│   │   │   ├── tenant_service.py
│   │   │   ├── user_service.py
│   │   │   ├── lead_service.py
│   │   │   ├── call_service.py              # Call orchestration
│   │   │   ├── transcription_service.py     # OpenAI Whisper integration
│   │   │   ├── analysis_service.py          # GPT-4o call analysis
│   │   │   ├── prediction_service.py        # Deal outcome prediction
│   │   │   ├── guidance_service.py          # Real-time agent guidance generation
│   │   │   ├── notification_service.py
│   │   │   ├── webhook_service.py
│   │   │   ├── twilio_service.py            # Twilio Voice SDK wrapper
│   │   │   └── storage_service.py           # S3 upload/download
│   │   │
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── prompts/
│   │   │   │   ├── analysis_prompt.py       # Call analysis prompt templates
│   │   │   │   ├── prediction_prompt.py     # Deal prediction prompt templates
│   │   │   │   ├── guidance_prompt.py       # Real-time guidance prompt templates
│   │   │   │   └── summary_prompt.py        # Post-call summary prompt
│   │   │   ├── openai_client.py             # OpenAI SDK wrapper (GPT-4o + Whisper)
│   │   │   └── pipeline.py                  # Orchestrates STT → analysis → prediction
│   │   │
│   │   ├── realtime/
│   │   │   ├── __init__.py
│   │   │   ├── socket_manager.py            # Socket.IO server setup + event handlers
│   │   │   ├── call_stream_handler.py       # Twilio Media Stream WebSocket consumer
│   │   │   └── event_publisher.py           # Redis pub/sub → Socket.IO bridge
│   │   │
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py                # Celery configuration
│   │   │   ├── transcription_tasks.py       # Async batch transcription
│   │   │   ├── analysis_tasks.py            # Post-call deep analysis
│   │   │   ├── prediction_tasks.py          # Batch prediction recalculation
│   │   │   └── notification_tasks.py        # Async notification dispatch
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py                  # Password hashing, JWT creation/verification
│   │   │   ├── permissions.py               # RBAC permission checks
│   │   │   ├── exceptions.py                # Custom exception classes
│   │   │   ├── middleware.py                # Tenant context, CORS, request logging
│   │   │   └── database.py                  # Async SQLAlchemy engine + session factory
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── pagination.py
│   │       └── audio.py                     # Audio format conversion helpers
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_leads.py
│       ├── test_calls.py
│       ├── test_analysis.py
│       ├── test_predictions.py
│       └── test_realtime.py
│
└── docs/
    ├── api-reference.md
    ├── deployment.md
    └── architecture.md
```

---

## Database Schema (Key Entities)

### tenants
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Tenant identifier |
| name | VARCHAR(255) | Organization name |
| slug | VARCHAR(100) | URL-safe unique identifier |
| plan | ENUM | free, starter, pro, enterprise |
| settings | JSONB | Branding, preferences, feature flags |
| is_active | BOOLEAN | Tenant active status |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### users
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK → tenants) | Tenant isolation |
| email | VARCHAR(255) | Unique within tenant |
| password_hash | VARCHAR(255) | |
| full_name | VARCHAR(255) | |
| role | ENUM | super_admin, tenant_admin, manager, agent |
| is_active | BOOLEAN | |
| last_login | TIMESTAMP | |
| created_at | TIMESTAMP | |

### leads
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK) | |
| assigned_agent_id | UUID (FK → users) | Nullable |
| campaign_id | UUID (FK → campaigns) | Nullable |
| first_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | |
| email | VARCHAR(255) | |
| phone | VARCHAR(50) | |
| company | VARCHAR(255) | |
| title | VARCHAR(255) | |
| status | ENUM | new, contacted, qualified, proposal, negotiation, won, lost |
| priority | ENUM | low, medium, high, urgent |
| source | VARCHAR(100) | Where lead came from |
| deal_value | DECIMAL | Estimated deal value |
| custom_fields | JSONB | Tenant-defined extra fields |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### calls
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK) | |
| agent_id | UUID (FK → users) | |
| lead_id | UUID (FK → leads) | |
| twilio_call_sid | VARCHAR(100) | Twilio reference |
| direction | ENUM | inbound, outbound |
| status | ENUM | initiated, ringing, in_progress, completed, failed, no_answer |
| duration_seconds | INTEGER | |
| recording_url | TEXT | S3 URL |
| recording_sid | VARCHAR(100) | |
| disposition | VARCHAR(100) | Agent-tagged outcome |
| started_at | TIMESTAMP | |
| ended_at | TIMESTAMP | |
| created_at | TIMESTAMP | |

### call_transcripts
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| call_id | UUID (FK → calls) | |
| speaker | ENUM | agent, customer |
| text | TEXT | Transcript segment |
| start_time | FLOAT | Seconds from call start |
| end_time | FLOAT | |
| confidence | FLOAT | STT confidence score |
| created_at | TIMESTAMP | |

### call_analyses
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| call_id | UUID (FK → calls) | One-to-one |
| summary | TEXT | AI-generated call summary |
| sentiment_overall | FLOAT | -1.0 to 1.0 |
| sentiment_timeline | JSONB | Array of {time, score} |
| topics | JSONB | Extracted topics |
| objections | JSONB | Detected objections |
| key_moments | JSONB | Important moments with timestamps |
| talk_ratio_agent | FLOAT | % of time agent spoke |
| filler_word_count | INTEGER | |
| agent_score | FLOAT | 0-100 performance score |
| feedback | TEXT | AI coaching feedback |
| red_flags | JSONB | Array of detected red flags |
| action_items | JSONB | Extracted action items |
| created_at | TIMESTAMP | |

### deal_predictions
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| lead_id | UUID (FK → leads) | |
| call_id | UUID (FK → calls) | Nullable — trigger call |
| win_probability | FLOAT | 0-100 |
| confidence | ENUM | low, medium, high |
| key_factors | JSONB | Factors driving prediction |
| red_flags | JSONB | Risk factors |
| recommended_actions | JSONB | Next steps |
| reasoning | TEXT | LLM reasoning chain |
| created_at | TIMESTAMP | |

### lead_flows
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK) | |
| name | VARCHAR(255) | |
| description | TEXT | |
| flow_definition | JSONB | Node/edge graph from React Flow |
| is_active | BOOLEAN | |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

### campaigns
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK) | |
| name | VARCHAR(255) | |
| description | TEXT | |
| script_template | TEXT | Call script for agents |
| status | ENUM | draft, active, paused, completed |
| start_date | DATE | |
| end_date | DATE | |
| created_at | TIMESTAMP | |

### audit_logs
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK) | |
| user_id | UUID (FK) | |
| action | VARCHAR(100) | e.g., lead.created, agent.deactivated |
| entity_type | VARCHAR(50) | |
| entity_id | UUID | |
| changes | JSONB | Before/after snapshot |
| ip_address | VARCHAR(45) | |
| created_at | TIMESTAMP | |

### notifications
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | UUID (FK) | |
| user_id | UUID (FK) | Target user |
| type | VARCHAR(50) | e.g., deal_at_risk, new_lead, missed_followup |
| title | VARCHAR(255) | |
| message | TEXT | |
| data | JSONB | Contextual payload |
| is_read | BOOLEAN | |
| created_at | TIMESTAMP | |

---

## API Endpoints (v1)

### Authentication
- `POST /api/v1/auth/register` — Register new tenant + admin user
- `POST /api/v1/auth/login` — Login, returns JWT pair
- `POST /api/v1/auth/refresh` — Refresh access token
- `POST /api/v1/auth/forgot-password` — Send password reset email
- `POST /api/v1/auth/reset-password` — Reset password with token

### Users & Agents
- `GET /api/v1/users` — List tenant users (admin)
- `POST /api/v1/users` — Create user / invite agent (admin)
- `GET /api/v1/users/{id}` — Get user detail
- `PATCH /api/v1/users/{id}` — Update user
- `DELETE /api/v1/users/{id}` — Deactivate user
- `GET /api/v1/agents` — List agents with performance metrics
- `GET /api/v1/agents/{id}/scorecard` — Agent performance scorecard

### Leads
- `GET /api/v1/leads` — List leads (filterable, paginated)
- `POST /api/v1/leads` — Create lead
- `POST /api/v1/leads/import` — Bulk import from CSV
- `GET /api/v1/leads/{id}` — Lead detail with full history
- `PATCH /api/v1/leads/{id}` — Update lead
- `POST /api/v1/leads/{id}/assign` — Assign lead to agent
- `DELETE /api/v1/leads/{id}` — Archive lead

### Lead Flows
- `GET /api/v1/lead-flows` — List flows
- `POST /api/v1/lead-flows` — Create flow
- `GET /api/v1/lead-flows/{id}` — Get flow with definition
- `PATCH /api/v1/lead-flows/{id}` — Update flow
- `DELETE /api/v1/lead-flows/{id}` — Delete flow

### Campaigns
- `GET /api/v1/campaigns` — List campaigns
- `POST /api/v1/campaigns` — Create campaign
- `GET /api/v1/campaigns/{id}` — Campaign detail + metrics
- `PATCH /api/v1/campaigns/{id}` — Update campaign
- `POST /api/v1/campaigns/{id}/leads` — Add leads to campaign

### Calls
- `POST /api/v1/calls/initiate` — Start outbound call
- `GET /api/v1/calls` — List call records
- `GET /api/v1/calls/{id}` — Call detail + transcript + analysis
- `GET /api/v1/calls/{id}/transcript` — Full transcript
- `GET /api/v1/calls/{id}/analysis` — AI analysis results
- `GET /api/v1/calls/{id}/recording` — Presigned S3 URL for playback
- `POST /api/v1/calls/{id}/disposition` — Set call disposition

### Twilio Webhooks (internal)
- `POST /api/v1/twilio/voice` — Twilio voice webhook (TwiML response)
- `POST /api/v1/twilio/status` — Call status callback
- `POST /api/v1/twilio/recording` — Recording completed callback
- `WebSocket /api/v1/twilio/media-stream` — Twilio Media Stream connection

### Analytics
- `GET /api/v1/analytics/dashboard` — Dashboard KPIs
- `GET /api/v1/analytics/conversion-funnel` — Funnel metrics
- `GET /api/v1/analytics/agent-leaderboard` — Agent ranking
- `GET /api/v1/analytics/call-trends` — Call volume and duration trends
- `GET /api/v1/analytics/prediction-accuracy` — AI prediction accuracy over time

### Predictions
- `GET /api/v1/predictions/pipeline` — All deals with AI predictions
- `GET /api/v1/predictions/lead/{lead_id}` — Prediction history for lead
- `POST /api/v1/predictions/lead/{lead_id}/refresh` — Force re-prediction

### Call Routing
- `GET /api/v1/call-routing/rules` — List routing rules
- `POST /api/v1/call-routing/rules` — Create routing rule
- `PATCH /api/v1/call-routing/rules/{id}` — Update rule
- `DELETE /api/v1/call-routing/rules/{id}` — Delete rule

### Notifications
- `GET /api/v1/notifications` — List user notifications
- `PATCH /api/v1/notifications/{id}/read` — Mark as read
- `PATCH /api/v1/notifications/read-all` — Mark all as read

### Webhooks (Outbound)
- `GET /api/v1/webhooks` — List configured webhooks
- `POST /api/v1/webhooks` — Create webhook subscription
- `PATCH /api/v1/webhooks/{id}` — Update webhook
- `DELETE /api/v1/webhooks/{id}` — Delete webhook

### Tenant Settings
- `GET /api/v1/tenant/settings` — Get tenant settings
- `PATCH /api/v1/tenant/settings` — Update settings
- `GET /api/v1/tenant/audit-log` — Audit log (admin)

---

## Real-Time Events (Socket.IO)

### Client → Server
- `join_call_room` — Agent joins a call's live room
- `leave_call_room` — Agent leaves a call's live room

### Server → Client
- `transcript_chunk` — New transcript segment during live call
- `ai_guidance` — Real-time guidance suggestion
- `sentiment_update` — Live sentiment score change
- `red_flag_alert` — Immediate alert for detected red flag
- `call_status_changed` — Call state transition
- `notification` — General notification push
- `deal_prediction_updated` — New prediction available

---

## Environment Variables

### Backend (.env)
```
# App
APP_ENV=development
APP_SECRET_KEY=<random-secret>
APP_CORS_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/salesiq

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=<random-secret>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o
OPENAI_WHISPER_MODEL=whisper-1

# Twilio
TWILIO_ACCOUNT_SID=<sid>
TWILIO_AUTH_TOKEN=<token>
TWILIO_PHONE_NUMBER=<phone>
TWILIO_API_KEY_SID=<api-key>
TWILIO_API_KEY_SECRET=<api-secret>

# AWS S3
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_S3_BUCKET=salesiq-recordings
AWS_S3_REGION=us-east-1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SOCKET_URL=http://localhost:8000
NEXT_PUBLIC_TWILIO_DEVICE_TOKEN_URL=http://localhost:8000/api/v1/calls/token
```

---

## Development Commands

```bash
# Backend
cd backend
pip install -e ".[dev]"              # Install with dev deps
alembic upgrade head                  # Run migrations
uvicorn app.main:app --reload         # Start dev server (port 8000)
celery -A app.tasks.celery_app worker --loglevel=info   # Start Celery worker
pytest                                # Run tests

# Frontend
cd frontend
npm install                           # Install deps
npm run dev                           # Start Next.js dev (port 3000)
npm run build                         # Production build
npm run test                          # Run tests
npm run lint                          # Lint

# Docker (full stack)
docker-compose up -d                  # Start all services
docker-compose logs -f backend        # Follow backend logs
```

---

## Implementation Phases

### Phase 1 — Foundation (MVP)
- Project scaffolding (Next.js + FastAPI + Docker Compose)
- Database models + migrations
- Authentication (JWT + RBAC)
- Multi-tenancy (row-level tenant isolation)
- Admin: Agent and Lead CRUD
- Basic admin and agent dashboards

### Phase 2 — Call Infrastructure
- Twilio integration (outbound calls, recording)
- Call recording storage (S3)
- Call history and playback
- Call controls in agent UI

### Phase 3 — AI Pipeline
- OpenAI Whisper integration (batch transcription of recordings)
- GPT-4o call analysis (post-call summary, sentiment, objections)
- Agent feedback and scorecard generation
- Deal outcome prediction

### Phase 4 — Real-Time
- Twilio Media Streams (live audio)
- Real-time transcription via Whisper
- Streaming analysis + guidance via GPT-4o
- Socket.IO live transcript and guidance panels
- Red flag alerts during calls

### Phase 5 — Advanced Features
- Lead flow designer (visual builder)
- Campaign management
- Call routing rules engine
- Analytics dashboards with charts
- Notification system
- Audit logging

### Phase 6 — Integrations & Polish
- Webhook system (outbound)
- REST API documentation (OpenAPI)
- CSV export for reports
- Performance optimization
- E2E testing
- Production deployment configuration

---

## Coding Conventions

### Backend (Python)
- Use async/await everywhere — all DB queries, HTTP calls, file I/O
- Type hints on all function signatures
- Pydantic models for all request/response schemas
- Service layer pattern: routes → services → repositories
- All database queries go through SQLAlchemy async sessions
- Tenant isolation enforced at query level (filter by tenant_id)
- Custom exceptions with proper HTTP status mapping
- Structured logging with correlation IDs

### Frontend (TypeScript)
- Strict TypeScript — no `any` types
- Server Components by default, Client Components only when needed (interactivity, hooks)
- API calls via TanStack Query with typed query keys
- Tailwind utility classes — no custom CSS unless necessary
- Component files: PascalCase, one component per file
- Hooks: `use-*.ts` in hooks/ directory
- Zod schemas mirror backend Pydantic schemas for client-side validation

---

## Guardrails for Claude Code

These rules enforce the same constraints as `.cursor/rules/`. Follow them on every change.

### Architecture — where code belongs
- Routes are thin: only request parsing, response shaping, and `Depends(...)` calls. No business logic.
- Business logic → `app/services/`. AI logic → `app/ai/`. Real-time → `app/realtime/`. Async jobs → `app/tasks/`.
- Prompt templates → `app/ai/prompts/` only. Never inline prompt text inside service or task files.
- New API endpoints go in `app/api/v1/` and must be registered in `app/api/router.py`.
- Frontend: extend `components/ui/` primitives before creating new patterns.

### Multi-tenancy — never break these
- Every SQLAlchemy query on tenant-scoped data **must** filter by `tenant_id`.
- `tenant_id` is extracted from the authenticated user via `Depends(get_current_user)` in `app/dependencies.py` — never from the request body.
- If a resource's `tenant_id` does not match the caller's `tenant_id`, return 403. No exceptions.
- Redis pub/sub channels and cache keys must be namespaced by `tenant_id`.

### AI pipeline — task dispatch rules
- Never call OpenAI (Whisper or GPT-4o) synchronously inside an HTTP request handler.
- Post-call transcription, analysis, and prediction must be dispatched to Celery tasks immediately after the Twilio recording callback.
- Celery task order: `transcription_tasks` → `analysis_tasks` → `prediction_tasks` → `notification_tasks`.
- All Celery tasks must be idempotent — running twice on the same `call_id` must not create duplicates.
- Always validate GPT-4o structured JSON output against the Pydantic schema before writing to the database. On validation failure: log raw response, store null/error, do not crash the pipeline.

### Real-time — Socket.IO event rules
- Never emit Socket.IO events from HTTP route handlers. The only valid path is: service → `event_publisher.py` → Redis pub/sub → `socket_manager.py` → Socket.IO room.
- Socket.IO rooms are scoped per call (`call:{call_sid}`) and validated per tenant before allowing join.
- Event names are a contract with the frontend — do not rename without coordinating both sides:
  `transcript_chunk`, `ai_guidance`, `sentiment_update`, `red_flag_alert`, `call_status_changed`, `notification`, `deal_prediction_updated`.

### Twilio — voice and webhooks
- All Twilio SDK calls go through `app/services/twilio_service.py` only.
- All S3 operations go through `app/services/storage_service.py` only.
- Twilio webhook handlers must validate the `X-Twilio-Signature` header before processing any payload.
- Never serve raw Twilio recording URLs to clients — always generate presigned S3 URLs via `StorageService`.
- Real-time guidance latency target: sub-second aspiration (feature spec); engineering floor is < 2 seconds end-to-end from audio chunk arrival to Socket.IO emission. If > 2 seconds, investigate and optimise before shipping.

### Database — SQLAlchemy and migrations
- Every schema change needs an Alembic migration in `alembic/versions/`. Never modify production schema manually.
- Never modify existing migration files — always create a new revision.
- Use `selectinload` / `joinedload` for relationships to avoid N+1 queries.
- Do not use the synchronous SQLAlchemy engine anywhere — the entire backend is async.

### Security — hard rules
- Never hardcode secrets, API keys, or credentials anywhere in code. All secrets via `app/config.py` from env vars.
- Never commit `.env` or `.env.local` files.
- Never log transcript text, customer names, phone numbers, JWT tokens, or raw API keys.
- Never return internal stack traces or exception detail to API clients — log them, return a sanitized message.
- Do not trust LLM output in critical flows without Pydantic validation first.

### Testing
- Never call live OpenAI, Twilio, or AWS S3 APIs in tests — mock all external services.
- Every new service method needs at least a basic happy-path test.
- Multi-tenancy isolation must be tested on every new endpoint — verify tenant A cannot access tenant B's data.

### Response style
- Prefer precise, minimal, production-ready changes. Do not rewrite unrelated code.
- When adding a new feature, also note which `.env.example` variables, Alembic migrations, and frontend types need updating.
- Do not produce demo/toy code when production code is requested.
