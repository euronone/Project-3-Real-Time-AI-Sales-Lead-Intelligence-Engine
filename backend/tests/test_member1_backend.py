"""Thorough tests for Member 1 backend: JWT claims, RBAC, middleware, audio, permissions map."""

import io
import uuid

import pytest
import wave
from httpx import AsyncClient

from app.core.permissions import ROLE_PERMISSIONS, Permission
from app.core.security import decode_token
from app.models.user import UserRole
from app.utils.audio import convert_mulaw_to_wav


def _decode_access_token_from_response(data: dict) -> dict:
    assert "access_token" in data
    return decode_token(data["access_token"])


@pytest.mark.asyncio
async def test_register_jwt_includes_full_name(client: AsyncClient) -> None:
    slug = f"reg-{uuid.uuid4().hex[:8]}"
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"reg_{uuid.uuid4().hex[:8]}@example.com",
            "password": "securepassword123",
            "full_name": "Registered User",
            "organization_name": "Reg Org",
            "organization_slug": slug,
        },
    )
    assert response.status_code == 201
    payload = _decode_access_token_from_response(response.json())
    assert payload.get("full_name") == "Registered User"
    assert payload.get("role") == UserRole.TENANT_ADMIN.value
    assert payload.get("type") == "access"


@pytest.mark.asyncio
async def test_login_jwt_includes_full_name(client: AsyncClient, test_user) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    payload = _decode_access_token_from_response(response.json())
    assert payload.get("full_name") == "Test Admin"
    assert payload.get("sub") == str(test_user.id)


@pytest.mark.asyncio
async def test_refresh_jwt_includes_full_name(client: AsyncClient, test_user) -> None:
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    payload = _decode_access_token_from_response(response.json())
    assert payload.get("full_name") == "Test Admin"


@pytest.mark.asyncio
async def test_users_list_agent_forbidden(
    client: AsyncClient, agent_auth_headers: dict[str, str]
) -> None:
    r = await client.get("/api/v1/users", headers=agent_auth_headers)
    assert r.status_code == 403
    assert "Insufficient" in r.json().get("detail", "")


@pytest.mark.asyncio
async def test_users_list_manager_allowed(
    client: AsyncClient, manager_auth_headers: dict[str, str]
) -> None:
    r = await client.get("/api/v1/users", headers=manager_auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_users_create_agent_forbidden(
    client: AsyncClient, agent_auth_headers: dict[str, str]
) -> None:
    r = await client.post(
        "/api/v1/users",
        headers=agent_auth_headers,
        json={
            "email": "newagent@example.com",
            "password": "password123",
            "full_name": "New Agent",
            "role": "agent",
        },
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_users_create_tenant_admin_allowed(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    r = await client.post(
        "/api/v1/users",
        headers=auth_headers,
        json={
            "email": f"invited_{uuid.uuid4().hex[:8]}@example.com",
            "password": "password123",
            "full_name": "Invited Agent",
            "role": "agent",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["full_name"] == "Invited Agent"
    assert body["role"] == "agent"


@pytest.mark.asyncio
async def test_users_manager_cannot_create_user(
    client: AsyncClient, manager_auth_headers: dict[str, str]
) -> None:
    r = await client.post(
        "/api/v1/users",
        headers=manager_auth_headers,
        json={
            "email": f"mgrblock_{uuid.uuid4().hex[:8]}@example.com",
            "password": "password123",
            "full_name": "Should Fail",
            "role": "agent",
        },
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_tenants_list_tenant_admin_ok(
    client: AsyncClient, auth_headers: dict[str, str], test_tenant
) -> None:
    r = await client.get("/api/v1/tenants", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_tenant.id)


@pytest.mark.asyncio
async def test_tenants_create_tenant_admin_forbidden(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    slug = f"no-{uuid.uuid4().hex[:8]}"
    r = await client.post(
        "/api/v1/tenants",
        headers=auth_headers,
        json={"name": "Blocked Org", "slug": slug, "plan": "free"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_tenants_create_super_admin_allowed(
    client: AsyncClient, super_admin_auth_headers: dict[str, str]
) -> None:
    slug = f"super-{uuid.uuid4().hex[:8]}"
    r = await client.post(
        "/api/v1/tenants",
        headers=super_admin_auth_headers,
        json={"name": "Super Created", "slug": slug, "plan": "free"},
    )
    assert r.status_code == 201
    assert r.json()["slug"] == slug


@pytest.mark.asyncio
async def test_tenants_delete_super_admin_only(
    client: AsyncClient,
    super_admin_auth_headers: dict[str, str],
    auth_headers: dict[str, str],
    db_session,
) -> None:
    """Super admin can delete; tenant admin cannot (route guard)."""
    from app.models.tenant import Tenant

    tid = uuid.uuid4()
    t = Tenant(id=tid, name="To Delete", slug=f"del-{uuid.uuid4().hex[:8]}")
    db_session.add(t)
    await db_session.commit()

    r_admin = await client.delete(f"/api/v1/tenants/{tid}", headers=auth_headers)
    assert r_admin.status_code == 403

    r_super = await client.delete(f"/api/v1/tenants/{tid}", headers=super_admin_auth_headers)
    assert r_super.status_code == 200


@pytest.mark.asyncio
async def test_login_response_includes_correlation_id_header(client: AsyncClient, test_user) -> None:
    cid = "test-correlation-abc-123"
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "testpassword123"},
        headers={"X-Correlation-ID": cid},
    )
    assert response.status_code == 200
    assert response.headers.get("x-correlation-id") == cid


@pytest.mark.asyncio
async def test_login_generates_correlation_id_when_missing(client: AsyncClient, test_user) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    assert response.headers.get("x-correlation-id")
    # UUID format from server
    uuid.UUID(response.headers["x-correlation-id"])


def test_role_permissions_agent_cannot_manage_users() -> None:
    perms = ROLE_PERMISSIONS[UserRole.AGENT]
    assert Permission.MANAGE_USERS not in perms
    assert Permission.MAKE_CALLS in perms


def test_role_permissions_super_admin_has_manage_tenants() -> None:
    perms = ROLE_PERMISSIONS[UserRole.SUPER_ADMIN]
    assert Permission.MANAGE_TENANTS in perms


def test_mulaw_to_wav_produces_valid_wav() -> None:
    """Pure-Python mu-law path (replaces stdlib audioop)."""
    # Silence-ish mu-law byte
    mulaw = bytes([0xFF] * 160)
    wav_bytes = convert_mulaw_to_wav(mulaw, sample_rate=8000)
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"
    with wave.open(io.BytesIO(wav_bytes), "rb") as w:
        assert w.getnchannels() == 1
        assert w.getframerate() == 8000
        assert w.getsampwidth() == 2
