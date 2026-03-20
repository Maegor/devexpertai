import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from main import app

BASE_URL = "http://test"
PREFIX = "/internal-users"

USER_PAYLOAD = {
    "name": "Juan Pérez",
    "email": "juan@devexpert.ai",
    "password_hash": "hashed_password_123",
    "role": "Sales",
}


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as c:
        yield c


@pytest_asyncio.fixture
async def usuario(client):
    payload = {**USER_PAYLOAD, "email": "fixture@devexpert.ai"}
    response = await client.post(PREFIX + "/", json=payload)
    assert response.status_code == 201
    return response.json()


# ── Prueba 1: Crear usuario ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_crear_usuario(client):
    response = await client.post(PREFIX + "/", json=USER_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == USER_PAYLOAD["email"]
    assert data["name"] == USER_PAYLOAD["name"]
    assert data["role"] == USER_PAYLOAD["role"]
    assert "id" in data
    assert "password_hash" not in data


# ── Prueba 2: Listar usuarios ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_listar_usuarios(client, usuario):
    response = await client.get(PREFIX + "/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    emails = [u["email"] for u in data]
    assert usuario["email"] in emails


# ── Prueba 3: Borrar usuario ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_borrar_usuario(client, usuario):
    user_id = usuario["id"]

    response = await client.delete(f"{PREFIX}/{user_id}")
    assert response.status_code == 204

    response = await client.get(f"{PREFIX}/{user_id}")
    assert response.status_code == 404


# ── Prueba 4: Editar usuario ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_editar_usuario(client, usuario):
    user_id = usuario["id"]

    response = await client.patch(
        f"{PREFIX}/{user_id}",
        json={"name": "Juan Editado", "role": "Admin"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Juan Editado"
    assert data["role"] == "Admin"
    assert data["email"] == usuario["email"]
