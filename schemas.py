from typing import List

from pydantic import BaseModel


class Category(BaseModel):
    id: int
    category_name: str

    class Config:
        orm_mode = True


class Product(BaseModel):
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
