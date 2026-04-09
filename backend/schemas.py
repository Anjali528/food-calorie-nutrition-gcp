from pydantic import BaseModel, EmailStr
from datetime import datetime

class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class FoodOut(BaseModel):
    id: int
    name: str
    calories_100g: float | None = None
    protein_100g: float | None = None
    carbs_100g: float | None = None
    fat_100g: float | None = None
    source: str

class MealItemIn(BaseModel):
    food_id: int | None = None
    custom_name: str | None = None
    quantity_g: float
    predicted: bool = False

class MealCreateIn(BaseModel):
    meal_time: datetime
    items: list[MealItemIn]

class MealItemOut(BaseModel):
    id: int
    food_id: int | None = None
    custom_name: str | None = None
    quantity_g: float
    predicted: bool
    calories_total: float | None = None
    protein_total: float | None = None
    carbs_total: float | None = None
    fat_total: float | None = None

class MealOut(BaseModel):
    id: int
    meal_time: datetime
    items: list[MealItemOut]