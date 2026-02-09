"""
Tests for workspace endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_workspaces(client: AsyncClient, auth_headers: dict):
    """Test listing workspaces."""
    response = await client.get("/v1/workspaces", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_workspace(client: AsyncClient, auth_headers: dict):
    """Test creating a workspace."""
    payload = {
        "name": "Test Workspace",
        "description": "A test workspace",
    }
    response = await client.post("/v1/workspaces", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Workspace"
    assert data["description"] == "A test workspace"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_workspace_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting a non-existent workspace."""
    response = await client.get(
        "/v1/workspaces/550e8400-e29b-41d4-a716-446655440000",
        headers=auth_headers,
    )
    assert response.status_code == 404
