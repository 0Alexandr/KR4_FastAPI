# ЗАДАНИЕ 11.2 — Асинхронные тесты: pytest-asyncio + httpx.AsyncClient + Faker
# Запуск: pytest task_11_2/tests/ -v

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from faker import Faker

from task_11_2.main import app, reset_db

# Faker с русской локалью для реалистичных данных
fake = Faker("ru_RU")


# --- Фикстуры ---

@pytest.fixture(autouse=True)
def isolate_db():
    """Сбрасывает хранилище перед каждым тестом — изоляция состояния."""
    reset_db()
    yield
    reset_db()


@pytest_asyncio.fixture
async def async_client():
    """AsyncClient с ASGITransport — HTTP без реального сервера (без uvicorn)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def make_user_payload(age: int = None) -> dict:
    """Генерирует данные пользователя через Faker."""
    return {
        "username": fake.user_name(),
        "age": age if age is not None else fake.random_int(min=19, max=80),
    }


# --- Тесты ---

@pytest.mark.asyncio
class TestUserEndpointsAsync:
    """Все асинхронные тесты сгруппированы в один класс."""

    # POST /users

    async def test_create_user_201(self, async_client):
        """201 + корректная структура ответа."""
        payload = make_user_payload()
        response = await async_client.post("/users", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] == payload["username"]
        assert data["age"] == payload["age"]

    async def test_create_user_unique_ids(self, async_client):
        """Два пользователя должны получить разные ID."""
        r1 = await async_client.post("/users", json=make_user_payload())
        r2 = await async_client.post("/users", json=make_user_payload())
        assert r1.json()["id"] != r2.json()["id"]

    async def test_create_user_missing_field(self, async_client):
        """422 при отсутствии обязательного поля."""
        response = await async_client.post("/users", json={"username": fake.user_name()})
        assert response.status_code == 422

    async def test_create_user_boundary_age(self, async_client):
        """Граничные значения возраста: минимальный и максимальный."""
        r_min = await async_client.post("/users", json=make_user_payload(age=1))
        assert r_min.status_code == 201
        r_max = await async_client.post("/users", json=make_user_payload(age=120))
        assert r_max.status_code == 201

    # GET /users/{user_id}

    async def test_get_existing_user_200(self, async_client):
        """200 и корректные данные для существующего пользователя."""
        payload = make_user_payload()
        create_r = await async_client.post("/users", json=payload)
        user_id = create_r.json()["id"]

        get_r = await async_client.get(f"/users/{user_id}")
        assert get_r.status_code == 200
        assert get_r.json()["username"] == payload["username"]

    async def test_get_nonexistent_user_404(self, async_client):
        """404 для несуществующего пользователя."""
        response = await async_client.get("/users/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_get_multiple_users(self, async_client):
        """Каждый из нескольких созданных пользователей доступен по своему ID."""
        users = []
        for _ in range(3):
            r = await async_client.post("/users", json=make_user_payload())
            users.append(r.json())

        for user in users:
            r = await async_client.get(f"/users/{user['id']}")
            assert r.status_code == 200
            assert r.json()["username"] == user["username"]

    # DELETE /users/{user_id}

    async def test_delete_existing_user_204(self, async_client):
        """204 при удалении существующего пользователя."""
        create_r = await async_client.post("/users", json=make_user_payload())
        user_id = create_r.json()["id"]
        delete_r = await async_client.delete(f"/users/{user_id}")
        assert delete_r.status_code == 204

    async def test_get_after_delete_404(self, async_client):
        """После удаления пользователь недоступен — 404."""
        create_r = await async_client.post("/users", json=make_user_payload())
        user_id = create_r.json()["id"]
        await async_client.delete(f"/users/{user_id}")
        assert (await async_client.get(f"/users/{user_id}")).status_code == 404

    async def test_delete_nonexistent_user_404(self, async_client):
        """404 при удалении несуществующего пользователя."""
        assert (await async_client.delete("/users/99999")).status_code == 404

    async def test_double_delete_404(self, async_client):
        """Повторное удаление возвращает 404."""
        create_r = await async_client.post("/users", json=make_user_payload())
        user_id = create_r.json()["id"]
        await async_client.delete(f"/users/{user_id}")
        assert (await async_client.delete(f"/users/{user_id}")).status_code == 404

    async def test_state_isolated(self, async_client):
        """БД пуста в начале каждого теста (изоляция работает)."""
        response = await async_client.get("/users/1")
        assert response.status_code == 404