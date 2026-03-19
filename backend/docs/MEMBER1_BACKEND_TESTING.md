# Member 1 backend — how to test thoroughly

## 1. Automated tests (recommended first)

From `backend/` with a virtualenv and dev dependencies:

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

**Member 1–focused suite:**

```bash
pytest tests/test_member1_backend.py tests/test_auth.py -v
```

What this covers:

| Area | Tests |
|------|--------|
| JWT `full_name`, `role`, `sub` | `test_register_jwt_*`, `test_login_jwt_*`, `test_refresh_jwt_*` |
| Users RBAC | Agent 403 on list/create; manager list OK, create 403; tenant admin create OK |
| Tenants RBAC | Tenant admin list OK, create 403; super admin create/delete; tenant admin delete 403 |
| Correlation ID middleware | Echo `X-Correlation-ID` on login; server-generated UUID when omitted |
| `ROLE_PERMISSIONS` map | Agent vs super_admin permission sets |
| Mu-law → WAV (no `audioop`) | `test_mulaw_to_wav_produces_valid_wav` |

**Note:** HTTP tests use **SQLite** (`aiosqlite`) and the **inner FastAPI app** (`socketio_app.other_asgi_app`) so `get_db` overrides work. Production still uses PostgreSQL + JSONB/native UUID.

---

## 2. Local API + real Postgres (Docker)

1. Start stack (from repo root, adjust compose file name if yours differs):

   ```bash
   docker compose up -d postgres redis
   ```

2. Set `DATABASE_URL` / `.env` for async Postgres (same as your project’s `core/database.py`).

3. Run migrations:

   ```bash
   cd backend
   alembic upgrade head
   ```

4. Start API:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Smoke checks**

   - Open `http://localhost:8000/docs` — try **register**, **login**, **refresh**.
   - Decode access token (e.g. [jwt.io](https://jwt.io)) and confirm claims: `sub`, `tenant_id`, `role`, **`full_name`**, `type`, `exp`.

6. **RBAC (needs tokens for each role)**

   - As **agent**: `GET /api/v1/users` → **403**.
   - As **tenant_admin**: `GET /api/v1/users` → **200**; `POST /api/v1/tenants` → **403**.
   - As **super_admin**: `POST /api/v1/tenants` → **201**; `DELETE /api/v1/tenants/{id}` → **200** (for a test tenant).

   Use `Authorization: Bearer <access_token>` on all protected routes.

7. **Logging / correlation**

   - Send `X-Correlation-ID: my-trace-123` on any non-skipped path; response should include the same header.
   - Optionally send `X-Tenant-ID` on unauthenticated calls; logs should include `tenant_id` when present (see `RequestLoggingMiddleware`).

---

## 3. Quick `curl` examples

Replace `BASE` and JSON as needed.

```bash
# Register
curl -s -X POST "$BASE/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: manual-test-1" \
  -d '{"email":"u@example.com","password":"securepassword123","full_name":"Test User","organization_name":"Acme","organization_slug":"acme"}'

# Login
curl -s -X POST "$BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"u@example.com","password":"securepassword123"}'

# Users (admin token)
curl -s "$BASE/api/v1/users" -H "Authorization: Bearer ACCESS_TOKEN_HERE"
```

---

## 4. Optional: coverage

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

---

## 5. Model / DB sanity

- **Automated:** `pytest` creates all tables on SQLite each test (validates mappings).
- **Production:** after model/type changes, regenerate/verify Alembic migrations against Postgres so JSONB/UUID match deployment.
