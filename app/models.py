from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Recipe(Base):
    """
    Таблица recipes:
    - id: PK
    - title: название блюда
    - cooking_time: время приготовления в минутах
    - views: сколько раз открывали детальный экран (популярность)
    - description: текстовое описание рецепта
    - ingredients: relationship -> список ингредиентов
    """
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    cooking_time = Column(Integer, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    description = Column(Text, nullable=True)

    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan", lazy="selectin")


class Ingredient(Base):
    """
    Таблица ingredients:
    - id: PK
    - name: название ингредиента
    - quantity: количество / описание (например '2 шт', '100 г')
    - recipe_id: FK -> recipes.id
    """
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(String, nullable=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"))
    recipe = relationship("Recipe", back_populates="ingredients")
