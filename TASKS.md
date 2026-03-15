# SalesIQ — Team Task Breakdown

**Team Size:** 6 members
**Project:** Real-Time AI Sales & Lead Intelligence Engine
**Timeline:** 6 phases (see CLAUDE.md for phase details)

---

## Team Roles

| Member | Role | Primary Focus |
|--------|------|---------------|
| **Member 1** | Backend Lead | Auth, Multi-Tenancy, Core API |
| **Member 2** | Backend Engineer | Call Infrastructure, Twilio, Real-Time |
| **Member 3** | AI/ML Engineer | AI Pipeline, LLM Integration, Predictions |
| **Member 4** | Frontend Lead | Admin Portal, Dashboard, Core UI |
| **Member 5** | Frontend Engineer | Agent Portal, Live Call UI, Real-Time |
| **Member 6** | DevOps + QA | Infrastructure, CI/CD, Testing, Deployment |

---

## Member 1 — Backend Lead (Auth, Multi-Tenancy, Core API)

### Phase 1 — Foundation
- [ ] Set up FastAPI project structure, config, and dependency injection
- [ ] Implement PostgreSQL async database connection (`core/database.py`)
- [ ] Create all SQLAlchemy models with migrations via Alembic
- [ ] Implement tenant model with row-level isolation
- [ ] Build auth system: JWT access/refresh tokens (`core/security.py`)
- [ ] Build registration endpoint (creates tenant + admin user)
- [ ] Build login / refresh / forgot-password / reset-password endpoints
- [ ] Implement RBAC middleware and `require_role` dependency (`core/permissions.py`)
- [ ] Implement tenant context middleware (extract tenant from JWT, enforce isolation)
- [ ] Build User CRUD API (`api/v1/users.py`)
- [ ] Build Tenant settings API (`api/v1/tenants.py`)
- [ ] Add request logging middleware with correlation IDs
- [ ] Set up structured logging with `structlog`

### Phase 2 — Core CRUD APIs
- [ ] Build Lead CRUD API with filtering and pagination (`api/v1/leads.py`)
- [ ] Build Lead CSV import endpoint (`POST /leads/import`)
- [ ] Build Lead assignment endpoint (`POST /leads/{id}/assign`)
- [ ] Build Campaign CRUD API (`api/v1/campaigns.py`)
- [ ] Build Lead Flow CRUD API (`api/v1/lead_flows.py`)
- [ ] Build Call Routing Rules CRUD API (`api/v1/call_routing.py`)
- [ ] Build Notification API — list, mark read, mark all read (`api/v1/notifications.py`)
- [ ] Build Webhook CRUD API (`api/v1/webhooks.py`)
- [ ] Build Audit Log API and service (`api/v1/audit_log` + `services/audit_service.py`)
- [ ] Implement pagination utility (`utils/pagination.py`)

### Phase 5 — Advanced
- [ ] Build Analytics endpoints — dashboard KPIs, conversion funnel, agent leaderboard, call trends
- [ ] Implement webhook dispatch service (outbound webhooks on events)
- [ ] Add rate limiting to API endpoints
- [ ] API documentation review and OpenAPI schema cleanup

### Ongoing
- [ ] Code reviews for all backend PRs
- [ ] Database schema reviews and migration management
- [ ] Backend architecture decisions

---

## Member 2 — Backend Engineer (Call Infrastructure & Real-Time)

### Phase 2 — Call Infrastructure
- [ ] Set up Twilio account and configure phone numbers
- [ ] Implement `TwilioService` — make_call, get_capability_token, handle callbacks
- [ ] Build call initiation endpoint (`POST /api/v1/calls/initiate`)
- [ ] Build Twilio voice webhook handler (TwiML response for call routing)
- [ ] Build Twilio status callback handler (call state transitions)
- [ ] Build Twilio recording callback handler (recording completed → store URL)
- [ ] Implement `StorageService` — upload recordings to S3, generate presigned URLs
- [ ] Build call history API (`GET /api/v1/calls`, `GET /api/v1/calls/{id}`)
- [ ] Build recording playback endpoint (presigned S3 URL)
- [ ] Build call disposition endpoint (`POST /api/v1/calls/{id}/disposition`)

### Phase 4 — Real-Time System
- [ ] Set up Socket.IO server with FastAPI (`realtime/socket_manager.py`)
- [ ] Implement Twilio Media Streams WebSocket handler (`realtime/call_stream_handler.py`)
- [ ] Build audio chunk buffering and forwarding to Whisper
- [ ] Implement Redis pub/sub event publisher (`realtime/event_publisher.py`)
- [ ] Build Redis subscriber → Socket.IO bridge (forward events to frontend rooms)
- [ ] Implement `join_call_room` / `leave_call_room` Socket.IO events
- [ ] Implement `transcript_chunk` emission to connected clients
- [ ] Implement `ai_guidance` emission to connected clients
- [ ] Implement `red_flag_alert` emission
- [ ] Implement `call_status_changed` emission
- [ ] Implement `notification` push via Socket.IO
- [ ] Audio format conversion utilities (`utils/audio.py` — mulaw to wav)
- [ ] Load test WebSocket connections (100+ concurrent)

### Phase 5 — Advanced
- [ ] Implement call transfer and conference functionality
- [ ] Build inbound call handling flow
- [ ] Implement call queue management for agents

### Ongoing
- [ ] Monitor Twilio usage and costs
- [ ] Troubleshoot real-time latency issues

---

## Member 3 — AI/ML Engineer (AI Pipeline, LLM, Predictions)

### Phase 3 — AI Pipeline (Core)
- [ ] Set up OpenAI SDK client wrapper (`ai/openai_client.py`)
- [ ] Implement batch transcription service — download recording → Whisper API → transcript
- [ ] Implement speaker diarization (agent vs customer separation)
- [ ] Store transcripts in `call_transcripts` table with speaker labels and timestamps
- [ ] Design and implement call analysis prompt (`ai/prompts/analysis_prompt.py`)
  - Sentiment analysis (per-utterance + overall)
  - Topic extraction
  - Objection detection and classification
  - Key moment identification
  - Talk-to-listen ratio
  - Filler word detection
- [ ] Build `AnalysisService.analyze_call()` — full post-call analysis via GPT-4o
- [ ] Store analysis results in `call_analyses` table
- [ ] Design post-call summary prompt (`ai/prompts/summary_prompt.py`)
- [ ] Build agent feedback/scorecard generation from analysis
- [ ] Design deal prediction prompt (`ai/prompts/prediction_prompt.py`)
  - Input: transcript summary + lead history + prior interactions + deal value
  - Output: win_probability, confidence, key_factors, red_flags, recommended_actions, reasoning
- [ ] Build `PredictionService.predict_deal()` — GPT-4o structured output
- [ ] Store predictions in `deal_predictions` table
- [ ] Build prediction API endpoints (`api/v1/predictions.py`)
- [ ] Build Celery tasks for async transcription (`tasks/transcription_tasks.py`)
- [ ] Build Celery tasks for async analysis (`tasks/analysis_tasks.py`)
- [ ] Build Celery tasks for async prediction (`tasks/prediction_tasks.py`)
- [ ] Build the full AI pipeline orchestrator (`ai/pipeline.py`) — STT → analysis → prediction

### Phase 4 — Real-Time AI
- [ ] Implement streaming transcription — chunk audio → Whisper in near-real-time
- [ ] Design real-time guidance prompt (`ai/prompts/guidance_prompt.py`)
  - Suggested responses to objections
  - Recommended questions based on flow
  - Warning alerts (frustration, off-script)
  - Competitive battle cards triggered by mentions
- [ ] Build `GuidanceService.generate_guidance()` — streaming GPT-4o during live calls
- [ ] Implement real-time sentiment tracking during calls
- [ ] Implement red flag detection during live calls
- [ ] Optimize prompt tokens and latency for real-time use (< 2s response)
- [ ] Build `deal_prediction_updated` event emission after each call

### Phase 5 — Refinement
- [ ] Tune analysis prompts based on test calls
- [ ] Build prediction accuracy tracking (compare predictions vs actual outcomes)
- [ ] Implement batch re-prediction for pipeline recalculation
- [ ] Add knowledge base / playbook injection into guidance prompts
- [ ] Evaluate and optimize OpenAI API costs

### Ongoing
- [ ] Monitor AI output quality
- [ ] Iterate on prompts based on real call data
- [ ] Track and report prediction accuracy metrics

---

## Member 4 — Frontend Lead (Admin Portal & Core UI)

### Phase 1 — Foundation
- [ ] Set up Next.js project with TypeScript, Tailwind, ESLint
- [ ] Build reusable UI component library (`components/ui/`)
  - Button, Input, Modal, Table, Card, Badge, Dropdown, Toast, Loading
- [ ] Build dashboard layout shell — Sidebar, Header, Breadcrumb (`components/layout/`)
- [ ] Set up Axios API client with auth interceptors (`lib/api.ts`)
- [ ] Set up TanStack Query provider and configuration
- [ ] Set up Zustand auth store (`stores/auth-store.ts`)
- [ ] Build Login page with form validation (react-hook-form + zod)
- [ ] Build Registration page
- [ ] Build Forgot Password page
- [ ] Implement auth flow — login, store token, redirect, protected routes
- [ ] Implement role-based route guards (admin vs agent redirect)

### Phase 2 — Admin Portal
- [ ] Build Admin Dashboard page — KPI cards, summary stats (`admin/page.tsx`)
- [ ] Build KPI Card component with trend indicator (`analytics/kpi-card.tsx`)
- [ ] Build Agent Management — list table, create/edit modal, deactivate (`admin/agents/`)
- [ ] Build Agent Table component with search and filters
- [ ] Build Lead Management — list table, detail view, status management (`admin/leads/`)
- [ ] Build Lead Table component with filters (status, priority, agent, date)
- [ ] Build Lead Import Modal — CSV upload and mapping (`leads/lead-import-modal.tsx`)
- [ ] Build Lead Detail page — full history, assigned agent, deal value
- [ ] Build Campaign Management — list, create/edit, lead assignment (`admin/campaigns/`)
- [ ] Build Tenant Settings page — branding, notifications, API keys (`admin/settings/`)

### Phase 5 — Advanced Admin
- [ ] Build Lead Flow Designer page with React Flow canvas (`admin/lead-flows/[id]/`)
- [ ] Build Lead Flow Canvas component (`leads/lead-flow-canvas.tsx`)
- [ ] Build Call Routing Rules page — rule list, create/edit (`admin/call-routing/`)
- [ ] Build Analytics page — Conversion Funnel, Agent Leaderboard, Call Trends charts
- [ ] Build Conversion Funnel chart (`analytics/conversion-funnel.tsx`)
- [ ] Build Agent Leaderboard table (`analytics/agent-leaderboard.tsx`)
- [ ] Build Prediction Accuracy chart (`analytics/prediction-accuracy-chart.tsx`)
- [ ] Build Audit Log page — filterable table (`admin/audit-log/`)
- [ ] Build Notification Bell dropdown (`layout/notification-bell.tsx`)

### Ongoing
- [ ] UI/UX design decisions and consistency
- [ ] Code reviews for all frontend PRs
- [ ] Responsive design and mobile compatibility

---

## Member 5 — Frontend Engineer (Agent Portal & Real-Time UI)

### Phase 2 — Agent Portal Base
- [ ] Build Agent Dashboard page — call queue, today's stats, recent feedback (`agent/page.tsx`)
- [ ] Build Call History page — list with filters, status badges (`agent/calls/`)
- [ ] Build Call Detail page — recording playback, transcript view, analysis display
- [ ] Build Call Summary Card component (`calls/call-summary-card.tsx`)
- [ ] Build Call Scorecard component (`calls/call-scorecard.tsx`)
- [ ] Build Assigned Leads page (`agent/leads/`)
- [ ] Build Lead Detail page (agent view) — history, notes, follow-ups

### Phase 3 — AI Display Components
- [ ] Build Sentiment Timeline chart using Recharts (`calls/sentiment-timeline.tsx`)
- [ ] Build Deal Pipeline view — kanban or table with AI scores (`predictions/deal-pipeline.tsx`)
- [ ] Build Win Probability Gauge component (`predictions/win-probability-gauge.tsx`)
- [ ] Build Red Flag Alert component (`predictions/red-flag-alert.tsx`)
- [ ] Build AI Coaching page — feedback history, improvement trends (`agent/coaching/`)
- [ ] Build Predictions page — pipeline view with filters (`agent/predictions/`)

### Phase 4 — Real-Time Call UI
- [ ] Set up Socket.IO client connection hook (`hooks/use-socket.ts`)
- [ ] Set up Twilio Client JS SDK initialization (`lib/twilio.ts`, `hooks/use-call.ts`)
- [ ] Build Active Call page layout — split panels for transcript + guidance (`agent/active-call/`)
- [ ] Build Call Controls component — mute, hold, end, transfer (`calls/call-controls.tsx`)
- [ ] Build Live Transcript panel — auto-scrolling, speaker labels, timestamps (`calls/live-transcript.tsx`)
- [ ] Build AI Guidance Panel — real-time suggestion cards (`calls/ai-guidance-panel.tsx`)
- [ ] Implement `use-live-transcript` hook — consume `transcript_chunk` events
- [ ] Implement live sentiment indicator during calls
- [ ] Implement red flag alert popups during calls
- [ ] Build click-to-call from lead detail / call queue
- [ ] Build Zustand call store for active call state (`stores/call-store.ts`)
- [ ] Build Zustand notification store (`stores/notification-store.ts`)
- [ ] Implement `use-notifications` hook with Socket.IO push

### Phase 5 — Polish
- [ ] Add call recording playback with waveform visualization
- [ ] Add keyboard shortcuts for call controls
- [ ] Optimize real-time UI rendering performance (virtualized lists, memoization)
- [ ] Add loading states, empty states, and error boundaries across agent views

### Ongoing
- [ ] User testing and feedback on agent experience
- [ ] Real-time UI performance profiling

---

## Member 6 — DevOps + QA (Infrastructure, Testing, Deployment)

### Phase 1 — Infrastructure Setup
- [ ] Set up Git repository with branch protection rules (main, develop)
- [ ] Configure Docker Compose for local development (PostgreSQL, Redis, backend, frontend)
- [ ] Write backend Dockerfile (Python 3.12, multi-stage build)
- [ ] Write frontend Dockerfile (Node 20, multi-stage build for prod)
- [ ] Set up GitHub Actions CI pipeline — backend (lint + test)
- [ ] Set up GitHub Actions CI pipeline — frontend (lint + typecheck + build)
- [ ] Configure `.env.example` files with all required variables
- [ ] Set up pre-commit hooks (ruff for Python, eslint for TS)
- [ ] Create database initialization scripts

### Phase 2 — Testing Foundation
- [ ] Set up pytest with async fixtures, test database, and test client (`tests/conftest.py`)
- [ ] Write auth endpoint tests (register, login, refresh, protected route)
- [ ] Write lead CRUD endpoint tests
- [ ] Write call endpoint tests
- [ ] Set up frontend testing — Vitest + React Testing Library
- [ ] Write tests for auth flow (login form, token storage, redirect)
- [ ] Write tests for core UI components (Button, Table, Modal)

### Phase 3 — Integration Testing
- [ ] Write integration tests for AI pipeline (mock OpenAI responses)
- [ ] Write tests for transcription → analysis → prediction flow
- [ ] Write tests for Twilio webhook handlers (mock Twilio payloads)
- [ ] Set up test coverage reporting and thresholds

### Phase 4 — Real-Time Testing
- [ ] Write WebSocket connection tests
- [ ] Write Socket.IO event emission/reception tests
- [ ] Load test: simulate 50+ concurrent WebSocket connections
- [ ] Latency benchmarking for real-time transcription pipeline

### Phase 5 — E2E & Monitoring
- [ ] Set up Playwright for E2E testing
- [ ] Write E2E tests: login → create lead → initiate call → view analysis
- [ ] Write E2E tests: admin create agent → agent sees dashboard
- [ ] Set up Prometheus metrics collection on backend
- [ ] Set up Grafana dashboards (API latency, error rates, active connections)
- [ ] Configure structured logging pipeline (structlog → CloudWatch or ELK)
- [ ] Set up health check endpoints (`/health`, `/ready`)

### Phase 6 — Production Deployment
- [ ] Create production Docker Compose configuration
- [ ] Set up AWS infrastructure (or chosen cloud): ECS/EKS, RDS, ElastiCache, S3
- [ ] Configure production environment variables and secrets management
- [ ] Set up SSL/TLS certificates and domain configuration
- [ ] Configure CDN for frontend static assets
- [ ] Set up automated database backup schedule
- [ ] Create deployment runbook documentation
- [ ] Set up alerting (PagerDuty/Slack) for critical errors
- [ ] Performance testing in staging environment

### Ongoing
- [ ] Monitor CI/CD pipeline health
- [ ] Dependency updates and security patches
- [ ] Infrastructure cost monitoring

---

## Cross-Team Dependencies

```
Member 1 (Auth/API) ──────► Member 4 (Admin UI)      [API contracts]
Member 1 (Auth/API) ──────► Member 5 (Agent UI)      [API contracts]
Member 2 (Calls/RT) ──────► Member 3 (AI Pipeline)   [Audio stream handoff]
Member 2 (Calls/RT) ──────► Member 5 (Agent UI)      [Socket.IO events]
Member 3 (AI)       ──────► Member 5 (Agent UI)      [Analysis data shape]
Member 3 (AI)       ──────► Member 1 (API)           [Prediction endpoints]
Member 6 (DevOps)   ──────► ALL                      [CI/CD, infra, testing]
```

### Key Integration Points (Sync Required)

| Integration | Members | What to Align On |
|---|---|---|
| API Contracts | 1 ↔ 4, 5 | Request/response schemas, endpoint URLs, error formats |
| Socket.IO Events | 2 ↔ 5 | Event names, payload shapes, room naming |
| Audio Pipeline | 2 ↔ 3 | Audio format, chunk size, streaming protocol |
| AI Output Schema | 3 ↔ 1, 5 | Analysis JSON structure, prediction fields |
| Auth Flow | 1 ↔ 4 | JWT storage, refresh logic, role-based routing |
| Call Flow | 2 ↔ 5 | Twilio device setup, call state machine, UI states |

---

## Sprint Schedule (Suggested 2-Week Sprints)

| Sprint | Dates | Phase | Focus |
|--------|-------|-------|-------|
| Sprint 1 | Week 1-2 | Phase 1 | Project setup, auth, DB models, UI foundation |
| Sprint 2 | Week 3-4 | Phase 1-2 | CRUD APIs, admin portal pages, Twilio setup |
| Sprint 3 | Week 5-6 | Phase 2-3 | Call infrastructure, AI pipeline (batch) |
| Sprint 4 | Week 7-8 | Phase 3-4 | AI analysis complete, real-time system |
| Sprint 5 | Week 9-10 | Phase 4-5 | Live call UI, advanced features |
| Sprint 6 | Week 11-12 | Phase 5-6 | Analytics, integrations, E2E testing, deploy |

---

## Definition of Done

- [ ] Code reviewed and approved by at least 1 team member
- [ ] Unit tests written and passing
- [ ] No TypeScript / Python type errors
- [ ] API endpoints documented in OpenAPI schema
- [ ] Works in Docker Compose local environment
- [ ] No hardcoded secrets or credentials
