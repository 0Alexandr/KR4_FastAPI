# ЗАДАНИЕ 10.1 — Пользовательская обработка ошибок в FastAPI
# Запуск: uvicorn task_10_1.main:app --reload --port 8001

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Задание 10.1 — Кастомная обработка ошибок")


# --- Шаг 1: Пользовательские классы исключений ---

class CustomExceptionA(Exception):
    """Исключение A — нарушено бизнес-условие. HTTP 400."""
    def __init__(self, message: str = "Условие не выполнено"):
        self.message = message
        self.status_code = 400
        super().__init__(self.message)


class CustomExceptionB(Exception):
    """Исключение B — ресурс не найден. HTTP 404."""
    def __init__(self, resource: str = "ресурс"):
        self.message = f"{resource} не найден"
        self.status_code = 404
        super().__init__(self.message)


# --- Шаг 3: Pydantic-модель ответа об ошибке ---

class ErrorResponse(BaseModel):
    """Единый формат ответа при ошибке."""
    success: bool = False
    status_code: int
    error_type: str
    message: str
    details: Any = None


# --- Шаг 2: Обработчики исключений ---

@app.exception_handler(CustomExceptionA)
async def handle_exception_a(request: Request, exc: CustomExceptionA) -> JSONResponse:
    print(f"[ERROR] CustomExceptionA на {request.url}: {exc.message}")
    response = ErrorResponse(
        status_code=exc.status_code,
        error_type="CustomExceptionA",
        message=exc.message,
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


@app.exception_handler(CustomExceptionB)
async def handle_exception_b(request: Request, exc: CustomExceptionB) -> JSONResponse:
    print(f"[ERROR] CustomExceptionB на {request.url}: {exc.message}")
    response = ErrorResponse(
        status_code=exc.status_code,
        error_type="CustomExceptionB",
        message=exc.message,
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


# --- Шаг 4: Эндпоинты ---

items_db: dict[int, str] = {1: "Телефон", 2: "Планшет", 3: "Ноутбук"}


@app.get("/check-condition/{value}", summary="Проверка условия → CustomExceptionA")
def check_condition(value: int):
    """value <= 0 вызывает CustomExceptionA (400), иначе 200."""
    if value <= 0:
        raise CustomExceptionA(message=f"Значение должно быть положительным, получено: {value}")
    return {"success": True, "value": value, "message": "Условие выполнено"}


@app.get("/items/{item_id}", summary="Получить товар → CustomExceptionB")
def get_item(item_id: int):
    """Товар не найден → CustomExceptionB (404)."""
    if item_id not in items_db:
        raise CustomExceptionB(resource=f"Товар с id={item_id}")
    return {"success": True, "item_id": item_id, "name": items_db[item_id]}


@app.get("/items", summary="Список всех товаров")
def list_items():
    return {"items": [{"id": k, "name": v} for k, v in items_db.items()]}