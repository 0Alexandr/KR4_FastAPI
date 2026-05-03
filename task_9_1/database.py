# ЗАДАНИЕ 9.1 — Подключение к базе данных (SQLite)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./products.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # только для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Зависимость FastAPI: открывает сессию и закрывает после запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()