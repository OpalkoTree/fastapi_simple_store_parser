from dataclasses import dataclass, field
from typing import List, Optional

import requests
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

import models
from models import Category, Products
from database import Base, engine, SessionLocal

ua = UserAgent()


def create_database():
    """Функция создания базы данных"""

    return Base.metadata.create_all(bind=engine)


def get_database():
    """Функция получения базы данных"""

    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()


@dataclass
class Request:
    """Сервис отправки запросов по url"""

    url: str
    data: Optional[dict] = None

    response: dict = field(init=False, default_factory=dict)

    def post(self):
        request = requests.post(
            self.url,
            json=self.data,
            headers={'User-Agent': ua.chrome}
        )

        if request.ok:
            self.response = request.json()
            return self.response

        print(f'ERROR:{" " * 5}{request}')

    def get(self):
        request = requests.get(
            self.url,
            headers={'User-Agent': ua.chrome}
        )

        if request.ok:
            self.response = request.json()
            return self.response

        print(f'ERROR:{" " * 5}{request}')


@dataclass
class ParseCategory:
    """Сервис парсинга одной категории"""

    slug: str

    id: int = field(init=False)
    category_name: str = field(init=False)

    def __post_init__(self):
        self.parse_data()

    def parse_data(self) -> None:
        url = f'https://www.itbox.ua/api/v1/categories/{self.slug}/?'

        if request := Request(url).get():
            self.id = request['Category']['ExternalId']
            self.category_name = request['Category']['Name']

    def create_data(self, database: Session) -> None:
        new_row = Category(id=self.id, category_name=self.category_name)
        database.add(new_row)
        database.commit()

        print(f'INFO:{" " * 5} category - {self.category_name} successfully added!')


@dataclass
class ParseCategories:
    """Сервис парсинга категорий"""

    slugs: List[str] = field(init=False, default_factory=list)

    def parse_data(self) -> List[str]:
        url = 'https://www.itbox.ua/api/v1/menu/?'

        if request := Request(url).get():
            if menu := request['MenuTpl']['Desktop']:
                soup = BeautifulSoup(menu, 'lxml')
                if menu := soup.find(class_='menu-column'):
                    slugs = [
                        category['href'].split('/')[-2]
                        for category in menu.find_all('a', title=True)
                    ]
                    self.slugs = slugs

                return self.slugs


@dataclass
class ParseProduct:
    """Сервис парсинга одного товара"""

    id: int
    title: str = field(init=False)
    category_id: int = field(init=False)
    price: str = field(init=False)
    old_price: str = field(init=False)
    description: str = field(init=False)
    characteristics: str = field(init=False)
    rating: int = field(init=False)
    views: int = field(init=False)
    status: bool = field(init=False)
    images: str = field(init=False)

    def __post_init__(self):
        self.parse_data()

    def parse_data(self) -> None:
        url = f'https://www.itbox.ua/api/v1/products/{self.id}?'

        if request := Request(url).get():
            if status := request.get('Status'):
                self.status = True if status == 1 else False

            if product := request.get('Product'):
                self.title = product['NameUa']
                self.category_id = product['CategoryExternalId']
                self.price = product['Price']
                self.old_price = product['OldPrice']
                self.description = product['DescriptionUa']
                self.characteristics = product['BriefDescriptionUa']
                self.rating = product['Rating']['Average']
                self.views = product['TodayViews']

                if pictures := product.get('Pictures'):
                    images = [
                        image['PictureEnlargedPath']
                        for image in pictures
                    ]

                    self.images = str(images)

    def create_data(self, database: Session) -> None:
        new_row = Products(
            id=self.id, title=self.title, category_id=self.category_id, price=self.price,
            old_price=self.old_price, description=self.description, characteristics=self.characteristics,
            rating=self.rating, views=self.views, status=self.status, images=self.images
        )
        database.add(new_row)
        database.commit()

        print(f'INFO:{" " * 5} product - {self.title} successfully added!')


@dataclass
class ParseProducts:
    """Сервис парсинга товаров"""

    ids: List[int] = field(init=False, default_factory=list)

    def parse_data(self, slug: str, count: int) -> List[int]:
        url = f'https://www.itbox.ua/api/v1/categories/{slug}/?'

        if request := Request(url).get():
            if products := request.get('Products'):
                self.ids = [
                    int(product['Id'])
                    for product in products[:count]
                ]

            return self.ids


def get_all_category(database: Session) -> list:
    """Запрос получения всех категорий"""

    return database.query(Category).all()


def get_category_by_id(database: Session, category_id: int) -> list | JSONResponse:
    """Запрос получения категории по id"""

    if categories := database.query(Category).filter(Category.id == category_id).first():
        return categories

    return JSONResponse({'error': f'No data with id - {category_id}.'}, 400)


def get_all_products(database: Session) -> list:
    """Запрос получения всех продуктов"""

    return database.query(Products).all()


def get_product_by_category(database: Session, category_id:  int) -> list | JSONResponse:
    """Запрос получения всех продуктов по категории"""

    if product := database.query(Products).filter(Products.category_id == category_id).all():
        return product

    return JSONResponse({'error': f'No data with category - {category_id}.'}, 400)


def get_product_by_name(database: Session, name: str) -> models.Products | JSONResponse:
    """Запрос получения продукта по имени"""

    if product := database.query(Products).filter(Products.title == name).first():
        print(type(product))
        return product

    return JSONResponse({'error': f'No data with name - {name}.'}, 400)


def get_product_by_id(database: Session, product_id: int) -> models.Products | JSONResponse:
    """Запрос получения продукта по id"""

    if product := database.query(Products).filter(Products.id == product_id).first():
        return product

    return JSONResponse({'error': f'No data with id {product_id}.'}, 400)
