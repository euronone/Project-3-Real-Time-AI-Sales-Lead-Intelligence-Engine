# Product Requirements Document: SalesIQ — Real-Time AI Sales & Lead Intelligence Engine

## Overview

SalesIQ is a multi-tenant SaaS platform that listens to sales calls in real time, guides sales representatives, analyzes conversations, and predicts deal outcomes. B2B sales teams, call centers, and CRM platforms integrate SalesIQ to improve performance through AI-driven insights.

All implementation must align with this PRD and the referenced tech stack in CLAUDE.md.

---

## User-Facing Interfaces

SalesIQ has **two** user-facing portals served by a single Next.js application:

| Interface | Audience | Delivery | Scope |
|-----------|----------|----------|-------|
| **Admin Portal** | Tenant admins, managers | Web (Next.js `/admin/*`) | Agent management, lead management, campaigns, call flows, routing, analytics, settings, audit log |
| **Agent Portal** | Sales reps | Web (Next.js `/agent/*`) | Call queue, live call UI, AI guidance, deal predictions, coaching, lead detail |

Both portals share: the same Next.js app, design system, API client, authentication, and layout shell. Role-based routing controls access.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14+ (App Router), TypeScript strict, Tailwind CSS |
| State | Zustand (global), TanStack Query (server state) |
| Real-Time (FE) | Socket.IO client, Twilio Client JS SDK |
| Forms | React Hook Form + Zod |
| Charts | Recharts |
| Flow Designer | React Flow |
| Backend | Python 3.12+, FastAPI (async) |
| ORM | SQLAlchemy 2.0 async + Alembic |
| Database | PostgreSQL 16 |
| Cache / Queue | Redis 7 (cache, pub/sub, Celery broker) |
| Async Tasks | Celery |
| AI — Text | OpenAI GPT-4o (analysis, prediction, guidance, summary) |
| AI — STT | OpenAI Whisper API |
| Telephony | Twilio Voice SDK + Media Streams |
| Storage | AWS S3 (call recordings) |
| Deployment | Docker + AWS (ECS/EKS, RDS, ElastiCache, S3, CloudFront) |

---

## Feature List

### 1. Authentication & Multi-Tenancy
- Tenant registration and onboarding with organization setup
- Role-based access control (RBAC): Super Admin, Tenant Admin, Manager, Agent
- JWT-based authentication with refresh tokens
- Tenant isolation at database level (row-level `tenant_id` filtering)
- Invite-based user onboarding within a tenant
- **Phase 2:** SSO support (OAuth2 / SAML) for enterprise tenants

### 2. Admin Portal
- **Dashboard:** Tenant-wide KPIs — total calls, conversion rate, active agents, pipeline value, AI score trends
- **Agent Management:** Create/edit/deactivate agents, assign roles, view performance scorecards
- **Lead Management:** Create/import leads (CSV), assign to agents, set priority and status, view full history
- **Lead Flow Designer:** Visual drag-and-drop builder (React Flow) to define call sequences, follow-up cadences, escalation rules
- **Call Routing Rules:** Configure round-robin, skill-based, or priority-based lead-to-agent assignment
- **Campaign Management:** Group leads into campaigns, set call scripts/templates, track campaign metrics
- **Analytics & Reports:** Conversion funnels, agent leaderboards, call duration trends, AI prediction accuracy, CSV export
- **Settings:** Tenant branding, notification preferences, integration keys, outbound webhook configuration
- **Audit Log:** Immutable log of all admin actions for compliance

### 3. Agent Portal
- **Dashboard:** Today's call queue, upcoming follow-ups, personal KPIs, recent AI feedback
- **Call Interface:** Click-to-call, integrated softphone via WebRTC/Twilio Client JS SDK
- **Real-Time Call Guidance:** Live transcript panel, AI-suggested talking points, objection-handling tips, next-best-action prompts — sub-2-second latency
- **Post-Call Summary:** Auto-generated AI summary, key topics, action items, sentiment timeline
- **AI Feedback & Coaching:** Per-call scorecard (talk ratio, filler words, engagement, objection handling), improvement suggestions, coaching history
- **Deal Prediction:** Win probability % with key factors and reasoning, updated after every call
- **Red Flag Alerts:** Real-time and post-call alerts for negative sentiment, competitor mentions, pricing objections, customer hesitation
- **Lead Detail View:** Full lead history — all calls, notes, deal stage, predicted outcome
- **Notes & Follow-ups:** Add call notes, schedule follow-ups, set reminders

### 4. Call Infrastructure
- Twilio Voice SDK (outbound/inbound calls, capability tokens, TwiML)
- Call recording stored in AWS S3; presigned URLs for playback
- Twilio Media Streams → WebSocket → backend for live audio streaming
- Call controls: hold, mute, end, transfer, conference, call disposition tagging
- Call metadata: duration, timestamps, caller/callee, disposition, recording URL

### 5. Speech-to-Text Pipeline
- Real-time transcription: OpenAI Whisper via Twilio Media Streams audio chunks
- Batch transcription: post-call full pass on recording (higher accuracy)
- Speaker diarization: identify agent vs. customer speech segments
- Transcript storage: per-utterance with timestamps, confidence, and speaker label

### 6. AI Conversation Analysis Engine
- Sentiment analysis (per-utterance and overall)
- Topic extraction and categorization
- Objection detection and classification
- Key moment identification (pricing, commitment signals, competitor mentions)
- Talk-to-listen ratio calculation
- Filler word and dead-air detection
- Real-time streaming analysis during live calls for immediate guidance
- Post-call deep analysis with full transcript context

### 7. Deal Outcome Prediction
- GPT-4o structured output: `win_probability`, `confidence`, `key_factors`, `red_flags`, `recommended_actions`, `reasoning`
- Updated incrementally after each customer interaction
- Historical pattern context in the prediction prompt
- Prediction pipeline view: filterable by probability range, sortable by score
- **Phase 2:** Prediction accuracy tracking — compare predicted vs. actual outcomes over time

### 8. Real-Time Guidance System
- WebSocket-driven, sub-2-second latency from transcript to guidance display
- Guidance types: objection responses, recommended questions, warning alerts, competitive battle cards, pricing guidance
- Knowledge base / playbook injection into guidance prompts (**Phase 2:** admin-configurable)
- Configurable rules engine for custom trigger/guidance definitions (**Phase 2**)

### 9. Notifications & Alerts
- In-app notification center (Socket.IO push)
- Email notifications for critical events (deal at risk, missed follow-up, new lead assigned)
- Outbound webhook notifications for external integrations

### 10. Integrations & API
- REST API: full CRUD for leads, agents, calls, analytics — OpenAPI/Swagger auto-documented
- Outbound webhooks: signed events for call.completed, analysis.ready, prediction.updated, lead.status_changed, red_flag.detected
- **Phase 2:** Salesforce, HubSpot CRM connectors
- **Phase 2:** Google Calendar / Outlook for follow-up scheduling

---

## Security & Compliance

- PII in call recordings and transcripts — S3 encryption, presigned URL access only
- RBAC enforced at service layer — not just route level
- JWT with short-lived access tokens + refresh token rotation
- Twilio webhook signature validation
- Audit logs for all sensitive admin actions (immutable)
- GDPR-ready: support data export and deletion per tenant
- No secrets in code — AWS Secrets Manager for production

---

## Implementation Phases

| Phase | Focus |
|---|---|
| Phase 1 (Done) | Foundation: DB models, auth, RBAC, multi-tenancy, Lead/Agent/Campaign CRUD |
| Phase 2 (Done) | Call infrastructure: Twilio, S3, call history |
| Phase 3 (Done) | AI pipeline: Whisper STT, GPT-4o analysis, prediction, Celery tasks |
| Phase 4 (Done) | Real-time: Media Streams, Socket.IO, Redis pub/sub, live guidance |
| Phase 5 (Done) | Advanced: lead flow designer, routing rules, analytics, notifications, audit |
| Phase 6 — Frontend | Build complete Next.js frontend (Admin + Agent portals) |
| Phase 7 — Polish | E2E tests, CRM integrations (Phase 2), production deployment |
