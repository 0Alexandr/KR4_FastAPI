# ЗАДАНИЕ 9.1, шаги 6-8: Добавление поля description (NOT NULL)

"""Шаги 6-8: Добавление поля description к таблице products

Revision ID: 0002_add_description
Revises: 0001_create_products
Create Date: 2025-01-01 11:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_add_description"
down_revision: Union[str, None] = "0001_create_products"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Шаги 7-8: Добавляем колонку description (NOT NULL) к products.
    server_default нужен чтобы существующие строки получили значение."""
    op.add_column(
        "products",
        sa.Column(
            "description",
            sa.String(),
            nullable=False,
            server_default="Нет описания",
        ),
    )


def downgrade() -> None:
    """Откат: удаляем колонку description."""
    op.drop_column("products", "description")