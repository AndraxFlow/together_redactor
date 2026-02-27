from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    """Модель товара (бизнес-логика)"""
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None