# ЗАДАНИЕ 11.1 — Модульные тесты с pytest + TestClient
# Запуск: pytest task_11_1/test_main.py -v

import pytest
from fastapi.testclient import TestClient
from task_11_1.main import app, db


@pytest.fixture(autouse=True)
def clear_db():
    """Очищает хранилище перед каждым тестом (изоляция состояния)."""
    db.clear()
    yield
    db.clear()


@pytest.fixture
def client():
    return TestClient(app)


class TestCreateUser:
    """Тесты для POST /users."""

    def test_create_user_success(self, client):
        """201 при корректных данных + проверка структуры ответа."""
        response = client.post("/users", json={"username": "alice", "age": 25})
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "alice"
        assert data["age"] == 25
        assert "id" in data

    def test_create_user_unique_ids(self, client):
        """Два пользователя должны получить разные ID."""
        r1 = client.post("/users", json={"username": "bob", "age": 30})
        r2 = client.post("/users", json={"username": "carol", "age": 22})
        assert r1.json()["id"] != r2.json()["id"]

    def test_create_user_missing_field(self, client):
        """422 при отсутствии обязательного поля."""
        response = client.post("/users", json={"username": "dave"})
        assert response.status_code == 422

    def test_create_user_invalid_age_type(self, client):
        """422 при неверном типе поля age."""
        response = client.post("/users", json={"username": "eve", "age": "not_a_number"})
        assert response.status_code == 422


class TestGetUser:
    """Тесты для GET /users/{user_id}."""

    def test_get_existing_user(self, client):
        """200 и корректные данные для существующего пользователя."""
        create_r = client.post("/users", json={"username": "frank", "age": 40})
        user_id = create_r.json()["id"]

        get_r = client.get(f"/users/{user_id}")
        assert get_r.status_code == 200
        assert get_r.json()["username"] == "frank"

    def test_get_nonexistent_user(self, client):
        """404 для несуществующего пользователя."""
        response = client.get("/users/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_user_response_structure(self, client):
        """Ответ содержит ровно поля: id, username, age."""
        create_r = client.post("/users", json={"username": "grace", "age": 28})
        get_r = client.get(f"/users/{create_r.json()['id']}")
        assert set(get_r.json().keys()) == {"id", "username", "age"}


class TestDeleteUser:
    """Тесты для DELETE /users/{user_id}."""

    def test_delete_existing_user(self, client):
        """204 при удалении существующего пользователя."""
        create_r = client.post("/users", json={"username": "henry", "age": 35})
        delete_r = client.delete(f"/users/{create_r.json()['id']}")
        assert delete_r.status_code == 204

    def test_get_after_delete_returns_404(self, client):
        """После удаления GET возвращает 404."""
        create_r = client.post("/users", json={"username": "iris", "age": 19})
        user_id = create_r.json()["id"]
        client.delete(f"/users/{user_id}")
        assert client.get(f"/users/{user_id}").status_code == 404

    def test_delete_nonexistent_user(self, client):
        """404 при удалении несуществующего пользователя."""
        assert client.delete("/users/99999").status_code == 404

    def test_double_delete_returns_404(self, client):
        """Повторное удаление возвращает 404."""
        create_r = client.post("/users", json={"username": "jack", "age": 50})
        user_id = create_r.json()["id"]
        client.delete(f"/users/{user_id}")
        assert client.delete(f"/users/{user_id}").status_code == 404