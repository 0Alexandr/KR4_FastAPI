# ЗАДАНИЕ 9.1 — Модель Product для SQLAlchemy

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Product(Base):
    """Модель товара. Изначально: id, title, price, count.
    В миграции 0002 добавляется поле description (NOT NULL)."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    count = Column(Integer, nullable=False, default=0)
    # Поле добавлено в шаге 6 задания 9.1 (миграция 0002)
    description = Column(String, nullable=False, default="Нет описания")

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title}', price={self.price})>"