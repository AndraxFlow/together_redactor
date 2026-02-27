from fastapi import APIRouter, HTTPException
from models import Item

router = APIRouter(prefix="/api", tags=["api"])

# Пример простого GET маршрута
@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Привет, {name}!"}

# Пример POST маршрута с использованием модели Item
@router.post("/process-item/")
async def process_item(item: Item):
    # Здесь могла бы быть сложная бизнес-логика
    total_price = item.price + (item.tax or 0)
    return {
        "name": item.name,
        "total_price": total_price,
        "message": "Item processed successfully"
    }

# ЗДЕСЬ БУДУТ ВЕЛИКИЕ СВЕРШЕНИЯ