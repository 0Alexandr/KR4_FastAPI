# Контрольная работа №4 — Технологии разработки серверных приложений

---

## 📁 Структура проекта

```
fastapi_kr4/
│
├── task_9_1/               # Задание 9.1 — Alembic: миграции базы данных
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── 0001_create_products.py   # Миграция 1: создание таблицы
│   │   │   └── 0002_add_description.py   # Миграция 2: добавление поля
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── alembic.ini
│   ├── database.py
│   ├── models.py
│   └── main.py
│
├── task_10_1/              # Задание 10.1 — Кастомная обработка ошибок
│   └── main.py
│
├── task_10_2/              # Задание 10.2 — Валидация данных + ошибки валидации
│   └── main.py
│
├── task_11_1/              # Задание 11.1 — Модульные тесты (TestClient)
│   ├── main.py
│   └── test_main.py
│
├── task_11_2/              # Задание 11.2 — Асинхронные тесты (pytest-asyncio + Faker)
│   ├── main.py
│   └── tests/
│       └── test_async.py
│
├── requirements.txt        # Зависимости проекта
├── pytest.ini              # Конфигурация pytest
├── .env.example            # Переменные окружения
├── .gitignore
└── README.md
```

---

## 🚀 Установка и запуск

### Шаг 1: Установить зависимости

```bash
pip install -r requirements.txt
```

### Шаг 2: Скопировать и настроить переменные окружения

```bash
cp .env.example .env
```

---

## 📋 Задание 9.1 — Alembic: миграции базы данных

### Что реализовано

- Модель `Product` с полями: `id`, `title`, `price`, `count`, `description`
- Две миграции Alembic:
  - **0001**: Создание таблицы `products` + две начальные записи
  - **0002**: Добавление поля `description` (NOT NULL)
- FastAPI-приложение с CRUD-эндпоинтами для `Product`

### Запуск миграций

```bash
cd task_9_1

# Применить все миграции (создать таблицу + добавить поле description)
alembic upgrade head

# Проверить текущую версию миграции
alembic current

# Посмотреть историю миграций
alembic history

# Откатить последнюю миграцию
alembic downgrade -1

# Откатить все миграции
alembic downgrade base
```

### Запуск FastAPI-приложения

```bash
cd ..  # вернуться в корень проекта
uvicorn task_9_1.main:app --reload --port 8000
```

Документация API: http://127.0.0.1:8000/docs

### Проверка эндпоинтов

```bash
# Получить все товары
curl http://127.0.0.1:8000/products

# Создать новый товар
curl -X POST http://127.0.0.1:8000/products \
  -H "Content-Type: application/json" \
  -d '{"title": "Клавиатура", "price": 2499.99, "count": 15, "description": "Механическая клавиатура"}'

# Получить товар по ID
curl http://127.0.0.1:8000/products/1
```

---

## 📋 Задание 10.1 — Кастомная обработка ошибок

### Что реализовано

- `CustomExceptionA` (HTTP 400) — нарушение бизнес-условия
- `CustomExceptionB` (HTTP 404) — ресурс не найден
- Обработчики `@app.exception_handler` для обоих исключений
- Pydantic-модель `ErrorResponse` для единого формата ошибок

### Запуск

```bash
uvicorn task_10_1.main:app --reload --port 8001
```

Документация: http://127.0.0.1:8001/docs

### Проверка

```bash
# Тест CustomExceptionA (value <= 0 вызывает ошибку)
curl http://127.0.0.1:8001/check-condition/-5
# Ожидаем: {"success": false, "status_code": 400, "error_type": "CustomExceptionA", ...}

# Тест CustomExceptionA (value > 0 — всё хорошо)
curl http://127.0.0.1:8001/check-condition/10
# Ожидаем: {"success": true, ...}

# Тест CustomExceptionB (товар не найден)
curl http://127.0.0.1:8001/items/999
# Ожидаем: {"success": false, "status_code": 404, "error_type": "CustomExceptionB", ...}

# Существующий товар
curl http://127.0.0.1:8001/items/1
# Ожидаем: {"success": true, "item_id": 1, "name": "Телефон"}
```

---

## 📋 Задание 10.2 — Валидация данных + кастомные ошибки валидации

### Что реализовано

- Pydantic-модель `User` с ограничениями:
  - `age`: строго больше 18 (`conint(gt=18)`)
  - `email`: проверка формата (`EmailStr`)
  - `password`: длина от 8 до 16 символов (`constr`)
  - `phone`: необязательное поле (`Optional[str]`)
- Кастомный обработчик `RequestValidationError` с русскими сообщениями
- Эндпоинты: `POST /register`, `GET /users`

### Запуск

```bash
uvicorn task_10_2.main:app --reload --port 8002
```

Документация: http://127.0.0.1:8002/docs

### Проверка

```bash
# Валидный запрос — регистрация
curl -X POST http://127.0.0.1:8002/register \
  -H "Content-Type: application/json" \
  -d '{"username": "ivan_petrov", "age": 25, "email": "ivan@example.com", "password": "securepass1"}'

# Невалидный запрос — возраст меньше 18
curl -X POST http://127.0.0.1:8002/register \
  -H "Content-Type: application/json" \
  -d '{"username": "young_user", "age": 16, "email": "young@example.com", "password": "pass12345"}'

# Невалидный email
curl -X POST http://127.0.0.1:8002/register \
  -H "Content-Type: application/json" \
  -d '{"username": "bad_email", "age": 20, "email": "not-an-email", "password": "pass12345"}'

# Пароль слишком короткий
curl -X POST http://127.0.0.1:8002/register \
  -H "Content-Type: application/json" \
  -d '{"username": "short_pass", "age": 20, "email": "user@example.com", "password": "123"}'
```

---

## 📋 Задание 11.1 — Модульные тесты с pytest + TestClient

### Что реализовано

- 11 тестов для трёх эндпоинтов (`POST /users`, `GET /users/{id}`, `DELETE /users/{id}`)
- Тесты организованы в классы: `TestCreateUser`, `TestGetUser`, `TestDeleteUser`
- Изоляция состояния между тестами через фикстуру `clear_db`

### Запуск тестов

```bash
# Все тесты задания 11.1
pytest task_11_1/test_main.py -v

# С детальным выводом
pytest task_11_1/test_main.py -v --tb=short
```

### Ожидаемый результат

```
task_11_1/test_main.py::TestCreateUser::test_create_user_success PASSED
task_11_1/test_main.py::TestCreateUser::test_create_user_returns_correct_id PASSED
task_11_1/test_main.py::TestCreateUser::test_create_user_missing_field PASSED
task_11_1/test_main.py::TestCreateUser::test_create_user_invalid_age_type PASSED
task_11_1/test_main.py::TestGetUser::test_get_existing_user PASSED
task_11_1/test_main.py::TestGetUser::test_get_nonexistent_user PASSED
task_11_1/test_main.py::TestGetUser::test_get_user_response_structure PASSED
task_11_1/test_main.py::TestDeleteUser::test_delete_existing_user PASSED
task_11_1/test_main.py::TestDeleteUser::test_delete_then_get_returns_404 PASSED
task_11_1/test_main.py::TestDeleteUser::test_delete_nonexistent_user PASSED
task_11_1/test_main.py::TestDeleteUser::test_double_delete_returns_404 PASSED

11 passed
```

---

## 📋 Задание 11.2 — Асинхронные тесты: pytest-asyncio + httpx + Faker

### Что реализовано

- 12 асинхронных тестов (`async def`)
- Используется `httpx.AsyncClient` с `ASGITransport` (без реального сервера)
- Данные генерируются через `Faker` (русская локаль)
- Изоляция состояния через `reset_db()` и `autouse` фикстуру

### Запуск тестов

```bash
# Все тесты задания 11.2
pytest task_11_2/tests/ -v

# Все тесты проекта сразу (11.1 + 11.2)
pytest -v
```

### Ожидаемый результат

```
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_create_user_201 PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_create_user_id_auto_increments PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_create_user_missing_required_field PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_create_user_with_boundary_age PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_get_existing_user_200 PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_get_nonexistent_user_404 PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_get_user_after_multiple_creates PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_delete_existing_user_204 PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_get_after_delete_returns_404 PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_delete_nonexistent_user_404 PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_double_delete_second_returns_404 PASSED
task_11_2/tests/test_async.py::TestUserEndpointsAsync::test_state_isolated_between_tests PASSED

12 passed
```
