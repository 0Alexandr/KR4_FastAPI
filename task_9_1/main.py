# ЗАДАНИЕ 9.1 — FastAPI-приложение для работы с Product
# Запуск: uvicorn task_9_1.main:app --reload --port 8000

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .database import get_db
from .models import Product

app = FastAPI(title="Задание 9.1 — Alembic Migrations")


class ProductCreate(BaseModel):
    title: str
    price: float
    count: int
    description: str


class ProductOut(BaseModel):
    id: int
    title: str
    price: float
    count: int
    description: str
    model_config = {"from_attributes": True}


@app.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    """Возвращает все товары."""
    return db.query(Product).all()


@app.post("/products", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """Создаёт новый товар."""
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Возвращает товар по ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product