from typing import List

from pydantic import BaseModel


class Category(BaseModel):
    """Схема Категории"""

    id: int
    category_name: str

    class Config:
        orm_mode = True


class Product(BaseModel):
    """Схема Продукта"""

    id: int
    title: str
    category_id: int
    price: str
    old_price: str
    description: str
    characteristics: str
    rating: int
    views: int
    status: bool
    images: str

    class Config:
        orm_mode = True
