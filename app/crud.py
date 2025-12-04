from typing import List, Optional, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from . import models, schemas


# --- read list of recipes (для первого экрана) ---
async def get_recipes(db: AsyncSession) -> List[models.Recipe]:
    """
    Возвращает список всех рецептов, отсортированных по:
    1) views (desc) — больше просмотров выше
    2) cooking_time (asc) — при равных views, меньшее время выше
    """
    stmt = (
        select(models.Recipe)
        .options(selectinload(models.Recipe.ingredients))
        .order_by(models.Recipe.views.desc(), models.Recipe.cooking_time)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# --- read single recipe and increment views ---
async def get_recipe(db: AsyncSession, recipe_id: int) -> Optional[models.Recipe]:
    """
    Возвращает один рецепт по id. Если найден — увеличивает поле views на 1 и коммитит.
    """
    stmt = select(models.Recipe).where(models.Recipe.id == recipe_id).options(selectinload(models.Recipe.ingredients))
    result = await db.execute(stmt)
    recipe = result.scalar_one_or_none()
    if recipe:
        # безопасно увеличить views
        recipe.views = cast(int, (recipe.views or 0) + 1)
        await db.commit()
        # refresh чтобы relationship/атрибуты обновились (expire_on_commit=False обычно достаточно)
        await db.refresh(recipe)
    return recipe


# --- create recipe with ingredients ---
async def create_recipe(db: AsyncSession, recipe_in: schemas.RecipeCreate) -> models.Recipe:
    """
    Создает рецепт и все его ингредиенты в одной транзакции.
    Возвращает созданный объект Recipe.
    """
    db_recipe = models.Recipe(
        title=recipe_in.title, cooking_time=recipe_in.cooking_time, description=recipe_in.description, views=0
    )
    db.add(db_recipe)
    # flush чтобы получить id (не обязателен, но удобно)
    await db.flush()

    ingredients = []
    for ing in recipe_in.ingredients:
        db_ing = models.Ingredient(name=ing.name, quantity=ing.quantity, recipe=db_recipe)
        db.add(db_ing)
        ingredients.append(db_ing)

    await db.commit()
    # обновим объект из БД и загрузим отношения
    await db.refresh(db_recipe)
    return db_recipe
