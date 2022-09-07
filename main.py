from typing import List

from uvicorn import run
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from services import (create_database, get_database, get_all_category, get_category_by_id, get_all_products,
                      get_product_by_category, get_product_by_id, get_product_by_name, ParseCategories,
                      ParseCategory, ParseProducts, ParseProduct)
from schemas import Category, Product

app = FastAPI()
create_database()


@app.get('/get_all_categories/', response_model=List[Category])
async def get_all_products_api(
        database: Session = Depends(get_database)):
    """Эндпоинт получения всех категорий"""

    return get_all_category(database)


@app.get('/get_category_by/{category_id}/', response_model=Category)
async def get_data_by_slug_api(
        category_id: int,
        database: Session = Depends(get_database)):
    """Эндпоинт получения категории по id"""

    return get_category_by_id(database, category_id)


@app.post('/parse_categories/')
async def parse_categories_api(
        database: Session = Depends(get_database)):
    """Эндпоинт парсинга категорий"""

    if categories := ParseCategories().parse_data():
        for category in categories:
            ParseCategory(category).create_data(database)

        return JSONResponse({'msg': 'All data successfully parsed!'}, 200)

    return JSONResponse({'error': 'Something went wrong!'}, 400)


@app.get('/get_all_products/', response_model=List[Product])
async def get_all_products_api(
        database: Session = Depends(get_database)):
    """Эндпоинт получения всех товаров"""

    return get_all_products(database)


@app.get('/get_products_by_category/{slug}/', response_model=List[Product])
async def get_products_by_category(
        slug: int,
        database: Session = Depends(get_database)):
    """Эндпоинт получения всех товаров по слагу категории"""

    return get_product_by_category(database, slug)


@app.get('/get_product_by/{slug}/', response_model=Product)
async def get_products_by_slug_api(
        slug: int | str,
        database: Session = Depends(get_database)):
    """Эндпоинт получения товара по id или имени"""

    if type(slug) == int:
        return get_product_by_id(database, slug)

    if type(slug) == str:
        return get_product_by_name(database, slug)

    return JSONResponse({'error': f'Incorrect slug - {slug}.'}, 400)


@app.post('/parse_products/{slug}/{count_of_data}/')
async def parse_products_api(
        slug: str,
        count_of_data: int,
        database: Session = Depends(get_database)):
    """Эндпоинт парсинга товарав по слагу категории и количеству товаров"""

    if products := ParseProducts().parse_data(slug, count_of_data):
        for product_id in products:
            ParseProduct(product_id).create_data(database)

        return JSONResponse({'msg': 'All data successfully parsed!'}, 200)

    return JSONResponse({'error': 'Something went wrong!'}, 400)


if __name__ == '__main__':
    run('main:app', reload=True)
