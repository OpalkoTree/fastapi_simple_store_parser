from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Category(Base):
    """Модель Категории"""

    __tablename__ = 'Categories'

    id = Column(Integer, primary_key=True)
    category_name = Column(String)


class Products(Base):
    """Модель Продукта"""

    __tablename__ = 'Products'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    category_id = Column(Integer, ForeignKey('Categories.id'))
    price = Column(String)
    old_price = Column(String)
    description = Column(String)
    characteristics = Column(String)
    rating = Column(Integer)
    views = Column(Integer)
    status = Column(Boolean)
    images = Column(String)

    category = relationship('Category')
