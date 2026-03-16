# SalesIQ API Reference

## Interactive Documentation

The backend auto-generates OpenAPI documentation from FastAPI route definitions:

- **Swagger UI (dev):** http://localhost:8000/docs
- **ReDoc (dev):** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

All endpoints are versioned under `/api/v1/`. Authentication required on all endpoints except `/api/v1/auth/login` and `/api/v1/auth/register`.

---

## Authentication

All protected endpoints require: `Authorization: Bearer <access_token>`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register new tenant + admin user |
| POST | `/api/v1/auth/login` | Login, returns JWT access + refresh tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token using refresh token |
| POST | `/api/v1/auth/forgot-password` | Send password reset email |
| POST | `/api/v1/auth/reset-password` | Reset password with token |

---

## Users & Agents

| Method | Endpoint | Role Required | Description |
|---|---|---|---|
| GET | `/api/v1/users` | admin, manager | List tenant users |
| POST | `/api/v1/users` | admin | Create/invite user |
| GET | `/api/v1/users/{id}` | admin, manager | User detail |
| PATCH | `/api/v1/users/{id}` | admin | Update user |
| DELETE | `/api/v1/users/{id}` | admin | Deactivate user |
| GET | `/api/v1/agents` | admin, manager | List agents with performance metrics |
| GET | `/api/v1/agents/{id}/scorecard` | admin, manager | Agent performance scorecard |

---

## Leads

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/leads` | List leads (filterable: status, priority, agent, campaign; paginated) |
| POST | `/api/v1/leads` | Create lead |
| POST | `/api/v1/leads/import` | Bulk import from CSV |
| GET | `/api/v1/leads/{id}` | Lead detail with full call history |
| PATCH | `/api/v1/leads/{id}` | Update lead |
| POST | `/api/v1/leads/{id}/assign` | Assign lead to agent |
| DELETE | `/api/v1/leads/{id}` | Archive/soft-delete lead |

---

## Calls

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/calls/initiate` | Initiate outbound call (returns Twilio token + call SID) |
| GET | `/api/v1/calls/token` | Get Twilio capability token for frontend Twilio Device |
| GET | `/api/v1/calls` | List call records (agent sees own; admin/manager sees all) |
| GET | `/api/v1/calls/{id}` | Call detail with metadata |
| GET | `/api/v1/calls/{id}/transcript` | Full transcript (all utterances) |
| GET | `/api/v1/calls/{id}/analysis` | AI analysis results |
| GET | `/api/v1/calls/{id}/recording` | Presigned S3 URL for audio playback |
| POST | `/api/v1/calls/{id}/disposition` | Set call disposition tag |

---

## Twilio Webhooks (internal — validated by Twilio signature)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/twilio/voice` | Twilio voice webhook — returns TwiML |
| POST | `/api/v1/twilio/status` | Call status callback |
| POST | `/api/v1/twilio/recording` | Recording completed callback |
| WS | `/api/v1/twilio/media-stream` | Twilio Media Stream WebSocket |

---

## Analytics

| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/v1/analytics/dashboard` | admin, manager | Tenant-wide KPIs |
| GET | `/api/v1/analytics/conversion-funnel` | admin, manager | Funnel metrics by lead status |
| GET | `/api/v1/analytics/agent-leaderboard` | admin, manager | Agent performance ranking |
| GET | `/api/v1/analytics/call-trends` | admin, manager | Call volume and duration over time |
| GET | `/api/v1/analytics/prediction-accuracy` | admin, manager | AI prediction accuracy trend |

---

## Deal Predictions

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/predictions/pipeline` | All leads with AI scores (filterable by probability range) |
| GET | `/api/v1/predictions/lead/{lead_id}` | Prediction history for a lead |
| POST | `/api/v1/predictions/lead/{lead_id}/refresh` | Force re-prediction |

---

## Lead Flows

| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/v1/lead-flows` | admin | List flows |
| POST | `/api/v1/lead-flows` | admin | Create flow |
| GET | `/api/v1/lead-flows/{id}` | admin | Flow with React Flow definition |
| PATCH | `/api/v1/lead-flows/{id}` | admin | Update flow / save canvas |
| DELETE | `/api/v1/lead-flows/{id}` | admin | Delete flow |

---

## Campaigns

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/campaigns` | List campaigns |
| POST | `/api/v1/campaigns` | Create campaign |
| GET | `/api/v1/campaigns/{id}` | Campaign detail + metrics |
| PATCH | `/api/v1/campaigns/{id}` | Update campaign |
| POST | `/api/v1/campaigns/{id}/leads` | Add leads to campaign |

---

## Call Routing

| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/v1/call-routing/rules` | admin | List routing rules |
| POST | `/api/v1/call-routing/rules` | admin | Create rule |
| PATCH | `/api/v1/call-routing/rules/{id}` | admin | Update rule |
| DELETE | `/api/v1/call-routing/rules/{id}` | admin | Delete rule |

---

## Notifications

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/notifications` | List user's notifications |
| PATCH | `/api/v1/notifications/{id}/read` | Mark as read |
| PATCH | `/api/v1/notifications/read-all` | Mark all as read |

---

## Outbound Webhooks

| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/v1/webhooks` | admin | List configured webhooks |
| POST | `/api/v1/webhooks` | admin | Create webhook subscription |
| PATCH | `/api/v1/webhooks/{id}` | admin | Update webhook |
| DELETE | `/api/v1/webhooks/{id}` | admin | Delete webhook |

---

## Tenant Settings

| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/v1/tenant/settings` | admin | Get tenant settings |
| PATCH | `/api/v1/tenant/settings` | admin | Update settings |
| GET | `/api/v1/tenant/audit-log` | admin | Paginated audit log |

---

## Socket.IO Events

**Connection:** `io(NEXT_PUBLIC_SOCKET_URL, { auth: { token: "<jwt>" } })`

### Client → Server
| Event | Payload | Description |
|---|---|---|
| `join_call_room` | `{ call_sid: string }` | Join live call room |
| `leave_call_room` | `{ call_sid: string }` | Leave live call room |

### Server → Client
| Event | Payload | Description |
|---|---|---|
| `transcript_chunk` | `{ speaker, text, start_time, end_time, confidence }` | Live transcript segment |
| `ai_guidance` | `{ type, content, confidence }` | Real-time AI suggestion |
| `sentiment_update` | `{ score, label, timestamp }` | Live sentiment change |
| `red_flag_alert` | `{ type, description, severity }` | Red flag detected |
| `call_status_changed` | `{ status, call_sid, timestamp }` | Call state transition |
| `notification` | `{ type, title, message, data }` | In-app notification push |
| `deal_prediction_updated` | `{ lead_id, win_probability, confidence }` | New prediction ready |

---

## Common Response Formats

```json
// Success (list)
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}

// Success (single)
{ "id": "uuid", "...": "..." }

// Error
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

All timestamps are ISO 8601 UTC. All IDs are UUIDs.
