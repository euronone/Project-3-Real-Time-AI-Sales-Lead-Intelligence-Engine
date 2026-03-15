"""Placeholder tests for call endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_calls(client: AsyncClient, auth_headers: dict) -> None:
    """Test listing calls returns paginated results."""
    response = await client.get("/api/v1/calls", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_call_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Test getting a non-existent call returns 404."""
    response = await client.get(
        "/api/v1/calls/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_call_transcript_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Test getting transcript for non-existent call returns 404."""
    response = await client.get(
        "/api/v1/calls/00000000-0000-0000-0000-000000000000/transcript",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_call_analysis_not_found(client: AsyncClient, auth_headers: dict) -> None:
    """Test getting analysis for non-existent call returns 404."""
    response = await client.get(
        "/api/v1/calls/00000000-0000-0000-0000-000000000000/analysis",
        headers=auth_headers,
    )
    assert response.status_code == 404
