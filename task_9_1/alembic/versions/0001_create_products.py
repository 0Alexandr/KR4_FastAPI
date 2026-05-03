# ЗАДАНИЕ 9.1, шаги 4-5: Создание таблицы products + две начальные записи

"""Шаг 4-5: Создание таблицы products

Revision ID: 0001_create_products
Revises:
Create Date: 2025-01-01 10:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001_create_products"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Шаг 4: Создаём таблицу products с полями id, title, price, count."""
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
    )

    # Шаг 5: Добавляем две начальные записи
    op.bulk_insert(
        sa.table(
            "products",
            sa.column("title", sa.String),
            sa.column("price", sa.Float),
            sa.column("count", sa.Integer),
        ),
        [
            {"title": "Ноутбук", "price": 59999.99, "count": 10},
            {"title": "Мышь беспроводная", "price": 1299.50, "count": 50},
        ],
    )


def downgrade() -> None:
    """Откат: удаляем таблицу products."""
    op.drop_table("products")