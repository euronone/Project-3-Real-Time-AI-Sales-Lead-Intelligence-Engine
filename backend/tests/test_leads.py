"""Placeholder tests for lead endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_leads(client: AsyncClient, auth_headers: dict) -> None:
    """Test listing leads returns paginated results."""
    response = await client.get("/api/v1/leads", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_lead(client: AsyncClient, auth_headers: dict) -> None:
    """Test creating a new lead."""
    response = await client.post(
        "/api/v1/leads",
        headers=auth_headers,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "company": "Acme Corp",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"


@pytest.mark.asyncio
async def test_import_leads(client: AsyncClient, auth_headers: dict) -> None:
    """Test bulk importing leads."""
    response = await client.post(
        "/api/v1/leads/import",
        headers=auth_headers,
        json={
            "leads": [
                {"first_name": "Jane", "last_name": "Smith"},
                {"first_name": "Bob", "last_name": "Jones"},
            ]
        },
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_lead_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Test getting a non-existent lead returns 404."""
    response = await client.get(
        "/api/v1/leads/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404
