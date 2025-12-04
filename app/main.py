from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas, crud, database

app = FastAPI(
    title="Culinary Book API",
    description="Асинхронный API кулинарной книги. Предназначен для фронтенда: список рецептов и детальная страница.",
    version="1.0.0"
)


# При старте приложения инициализируем БД (таблицы)
@app.on_event("startup")
async def on_startup():
    await database.init_db()

get_db = database.get_db


@app.get("/recipes", response_model=List[schemas.RecipeListItem], summary="Список всех рецептов")
async def list_recipes(db: AsyncSession = Depends(get_db)):  # noqa: B008
    """
    Возвращает список рецептов, отсортированный по популярности (views DESC), затем по времени приготовления.
    Для первого экрана (таблица): title, views, cooking_time.
    """
    return await crud.get_recipes(db)


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeResponse, summary="Детальная информация рецепта")
async def retrieve_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):  # noqa: B008
    """
    Возвращает детальную информацию по рецепту:
    - title
    - cooking_time
    - ingredients (список объектов {id, name, quantity})
    - description

    При каждом успешном запросе поле views увеличивается на единицу.
    """
    recipe = await crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe


@app.post("/recipes", response_model=schemas.RecipeResponse, status_code=status.HTTP_201_CREATED,
          summary="Создать новый рецепт")
async def create_recipe(recipe_in: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)): # noqa: B008
    """
    Создает новый рецепт вместе с ингредиентами.
    Тело запроса: RecipeCreate (title, cooking_time, ingredients[], description).
    """
    return await crud.create_recipe(db, recipe_in)
