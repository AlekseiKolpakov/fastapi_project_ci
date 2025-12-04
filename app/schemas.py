from typing import List, Optional

from pydantic import BaseModel, Field


class IngredientCreate(BaseModel):
    name: str = Field(..., example="Соль")
    quantity: Optional[str] = Field(None, example="1 ч.л.")


class IngredientResponse(IngredientCreate):
    id: int

    class Config:
        orm_mode = True


class RecipeCreate(BaseModel):
    title: str = Field(..., example="Омлет")
    cooking_time: int = Field(..., example=10, description="Время приготовления в минутах")
    ingredients: List[IngredientCreate] = Field(..., example=[{"name": "Яйцо", "quantity": "2 шт"}])
    description: Optional[str] = Field(None, example="Вкусный омлет с зеленью.")


class RecipeListItem(BaseModel):
    id: int
    title: str
    cooking_time: int
    views: int

    class Config:
        orm_mode = True


class RecipeResponse(BaseModel):
    id: int
    title: str
    cooking_time: int
    views: int
    ingredients: List[IngredientResponse]
    description: Optional[str]

    class Config:
        orm_mode = True
