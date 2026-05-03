# ЗАДАНИЕ 10.2 — Валидация данных + кастомная обработка ошибок валидации
# Запуск: uvicorn task_10_2.main:app --reload --port 8002

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, conint, constr
from typing import Optional, Any

app = FastAPI(title="Задание 10.2 — Валидация данных")


# --- Шаг 2: Pydantic-модель пользователя с ограничениями ---

class User(BaseModel):
    """
    username  — строка (обычная проверка)
    age       — conint(gt=18): целое число строго больше 18
    email     — EmailStr: проверка формата электронной почты
    password  — constr(min_length=8, max_length=16): длина 8–16 символов
    phone     — Optional[str]: необязательное поле, дефолт 'Unknown'
    """
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"


class UserResponse(BaseModel):
    success: bool = True
    message: str
    user: dict[str, Any]


class ValidationErrorDetail(BaseModel):
    field: str
    message: str
    invalid_value: Any = None


class ValidationErrorResponse(BaseModel):
    success: bool = False
    status_code: int = 422
    error_type: str = "ValidationError"
    message: str = "Ошибка валидации входных данных"
    errors: list[ValidationErrorDetail]


# --- Шаг 3: Кастомный обработчик ошибок валидации ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Перехватывает ошибки Pydantic и возвращает понятный ответ на русском."""
    print(f"[VALIDATION ERROR] Запрос к {request.url} не прошёл валидацию:")

    error_details = []
    for error in exc.errors():
        field_path = " → ".join(str(loc) for loc in error["loc"] if loc != "body")
        detail = ValidationErrorDetail(
            field=field_path or "тело запроса",
            message=_translate_error(error["type"], error.get("ctx", {})),
            invalid_value=error.get("input"),
        )
        print(f"  - Поле '{detail.field}': {detail.message}")
        error_details.append(detail)

    response = ValidationErrorResponse(errors=error_details)
    return JSONResponse(status_code=422, content=response.model_dump())


def _translate_error(error_type: str, ctx: dict) -> str:
    """Переводит коды ошибок Pydantic в русские сообщения."""
    translations = {
        "missing": "Поле обязательно для заполнения",
        "string_type": "Ожидается строка",
        "int_type": "Ожидается целое число",
        "greater_than": f"Значение должно быть больше {ctx.get('gt', '?')}",
        "string_too_short": f"Минимум {ctx.get('min_length', '?')} символов",
        "string_too_long": f"Максимум {ctx.get('max_length', '?')} символов",
        "value_error": "Некорректное значение",
    }
    return translations.get(error_type, f"Ошибка: {error_type}")


# --- Шаги 1 и 4: Эндпоинты ---

users_storage: list[dict] = []


@app.post("/register", response_model=UserResponse, status_code=201)
def register_user(user: User):
    """Регистрирует пользователя. При невалидных данных возвращает 422."""
    user_data = user.model_dump(exclude={"password"})
    users_storage.append(user_data)
    return UserResponse(
        message=f"Пользователь {user.username} успешно зарегистрирован",
        user=user_data,
    )


@app.get("/users")
def list_users():
    return {"users": users_storage, "total": len(users_storage)}