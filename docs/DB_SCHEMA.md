# SalesIQ — Database Schema Reference

All tables are implemented as SQLAlchemy 2.0 async ORM models in `backend/app/models/`. Migrations are managed by Alembic in `backend/alembic/versions/`. This document is the reference for the data model — always keep it in sync with model changes.

---

## Multi-Tenancy

All tenant-scoped tables include a `tenant_id UUID (FK → tenants.id)` column. Every query on tenant data **must** filter by `tenant_id`. This is enforced at the service layer, not the database level (no RLS — application-enforced row isolation).

---

## Tables

### tenants
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | Tenant identifier |
| name | VARCHAR(255) | NOT NULL | Organization name |
| slug | VARCHAR(100) | UNIQUE, NOT NULL | URL-safe unique identifier |
| plan | ENUM(free, starter, pro, enterprise) | NOT NULL | Subscription plan |
| settings | JSONB | | Branding, feature flags, notification prefs |
| is_active | BOOLEAN | DEFAULT true | Soft deactivation flag |
| created_at | TIMESTAMP | NOT NULL | Auto-set on insert |
| updated_at | TIMESTAMP | NOT NULL | Auto-updated on change |

### users
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id | Tenant scoping |
| email | VARCHAR(255) | UNIQUE (per tenant) | |
| password_hash | VARCHAR(255) | | bcrypt hashed |
| full_name | VARCHAR(255) | | |
| role | ENUM(super_admin, tenant_admin, manager, agent) | NOT NULL | |
| is_active | BOOLEAN | DEFAULT true | |
| last_login | TIMESTAMP | nullable | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### leads
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id | |
| assigned_agent_id | UUID | FK → users.id, nullable | |
| campaign_id | UUID | FK → campaigns.id, nullable | |
| first_name | VARCHAR(100) | | |
| last_name | VARCHAR(100) | | |
| email | VARCHAR(255) | | |
| phone | VARCHAR(50) | | |
| company | VARCHAR(255) | | |
| title | VARCHAR(255) | | |
| status | ENUM(new, contacted, qualified, proposal, negotiation, won, lost) | DEFAULT 'new' | |
| priority | ENUM(low, medium, high, urgent) | DEFAULT 'medium' | |
| source | VARCHAR(100) | | Where lead came from |
| deal_value | DECIMAL(12,2) | | Estimated deal value |
| custom_fields | JSONB | | Tenant-defined extra fields |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### calls
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id | |
| agent_id | UUID | FK → users.id | |
| lead_id | UUID | FK → leads.id | |
| twilio_call_sid | VARCHAR(100) | UNIQUE | Twilio reference |
| direction | ENUM(inbound, outbound) | NOT NULL | |
| status | ENUM(initiated, ringing, in_progress, completed, failed, no_answer) | NOT NULL | |
| duration_seconds | INTEGER | nullable | Set on completion |
| recording_url | TEXT | nullable | S3 URL (not Twilio URL) |
| recording_sid | VARCHAR(100) | nullable | Twilio recording SID |
| disposition | VARCHAR(100) | nullable | Agent-tagged outcome |
| started_at | TIMESTAMP | nullable | |
| ended_at | TIMESTAMP | nullable | |
| created_at | TIMESTAMP | | |

### call_transcripts
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| call_id | UUID | FK → calls.id | |
| speaker | ENUM(agent, customer) | NOT NULL | Speaker diarization |
| text | TEXT | NOT NULL | Transcript segment |
| start_time | FLOAT | | Seconds from call start |
| end_time | FLOAT | | |
| confidence | FLOAT | | Whisper confidence score (0-1) |
| created_at | TIMESTAMP | | |

### call_analyses
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| call_id | UUID | FK → calls.id, UNIQUE | One-to-one with calls |
| summary | TEXT | | AI-generated call summary |
| sentiment_overall | FLOAT | | -1.0 to 1.0 |
| sentiment_timeline | JSONB | | Array of `{time_sec, score, label}` |
| topics | JSONB | | Extracted topics array |
| objections | JSONB | | Detected objections array |
| key_moments | JSONB | | `{timestamp, type, description}` |
| talk_ratio_agent | FLOAT | | % of time agent spoke (0-100) |
| filler_word_count | INTEGER | | |
| agent_score | FLOAT | | 0-100 overall performance score |
| feedback | TEXT | | AI coaching feedback text |
| red_flags | JSONB | | Array of detected red flags |
| action_items | JSONB | | Extracted action items array |
| created_at | TIMESTAMP | | |

### deal_predictions
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| lead_id | UUID | FK → leads.id | |
| call_id | UUID | FK → calls.id, nullable | Triggering call |
| win_probability | FLOAT | 0-100 | |
| confidence | ENUM(low, medium, high) | | |
| key_factors | JSONB | | Positive factors array |
| red_flags | JSONB | | Risk factors array |
| recommended_actions | JSONB | | Next steps array |
| reasoning | TEXT | | LLM reasoning chain (1-3 sentences) |
| created_at | TIMESTAMP | | |

### campaigns
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id | |
| name | VARCHAR(255) | NOT NULL | |
| description | TEXT | | |
| script_template | TEXT | | Call script for agents |
| status | ENUM(draft, active, paused, completed) | DEFAULT 'draft' | |
| start_date | DATE | nullable | |
| end_date | DATE | nullable | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### lead_flows
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id | |
| name | VARCHAR(255) | NOT NULL | |
| description | TEXT | | |
| flow_definition | JSONB | | React Flow node/edge graph |
| is_active | BOOLEAN | DEFAULT false | Only one active flow per tenant recommended |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### notifications
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id | |
| user_id | UUID | FK → users.id | Target user |
| type | VARCHAR(50) | | e.g. deal_at_risk, new_lead, missed_followup |
| title | VARCHAR(255) | | |
| message | TEXT | | |
| data | JSONB | | Contextual payload |
| is_read | BOOLEAN | DEFAULT false | |
| created_at | TIMESTAMP | | |

### audit_logs
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id | |
| user_id | UUID | FK → users.id | Actor |
| action | VARCHAR(100) | NOT NULL | e.g. lead.created, agent.deactivated |
| entity_type | VARCHAR(50) | | e.g. lead, user, campaign |
| entity_id | UUID | nullable | Affected entity |
| changes | JSONB | | Before/after snapshot |
| ip_address | VARCHAR(45) | | |
| created_at | TIMESTAMP | NOT NULL | |

**Note:** Audit logs are append-only — never update or delete records.

### webhooks
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id | |
| name | VARCHAR(255) | | Human-readable label |
| url | TEXT | NOT NULL | Tenant's endpoint URL |
| secret | VARCHAR(255) | | HMAC signing secret (stored encrypted) |
| events | JSONB | | Array of subscribed event types |
| is_active | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

---

## Key Relationships Summary

```
tenants (1) ──────── (N) users
users   (1) ──────── (N) leads            [assigned_agent_id]
campaigns(1) ─────── (N) leads            [campaign_id]
leads   (1) ──────── (N) calls
calls   (1) ──────── (N) call_transcripts
calls   (1) ──────── (1) call_analyses
leads   (1) ──────── (N) deal_predictions
calls   (1) ──────── (N) deal_predictions [triggering call]
tenants (1) ──────── (N) campaigns
tenants (1) ──────── (N) lead_flows
tenants (1) ──────── (N) webhooks
tenants (1) ──────── (N) audit_logs
users   (1) ──────── (N) notifications
```

---

## Migration Rules

- Every schema change needs an Alembic migration in `backend/alembic/versions/`.
- Never modify existing migration files — create a new revision.
- Run `alembic upgrade head` on deploy.
- Migration naming convention: `{NNNN}_{short_description}.py` (e.g. `0002_add_disposition_to_calls.py`).
