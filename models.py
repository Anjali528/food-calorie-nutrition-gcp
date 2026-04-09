from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, BigInteger, TIMESTAMP, func, ForeignKey, Boolean, Float

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())

class Food(Base):
    __tablename__ = "foods"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, index=True)
    source: Mapped[str] = mapped_column(Text)  # 'usda' or 'predicted'
    external_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    calories_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    
    # Relationship
    meal_items: Mapped[list["MealItem"]] = relationship(back_populates="food")

class Meal(Base):
    __tablename__ = "meals"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    meal_time: Mapped[str] = mapped_column(TIMESTAMP)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    
    # Relationship
    items: Mapped[list["MealItem"]] = relationship(back_populates="meal")

class MealItem(Base):
    __tablename__ = "meal_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    meal_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("meals.id"))
    food_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("foods.id"), nullable=True)
    custom_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity_g: Mapped[float] = mapped_column(Float)
    predicted: Mapped[bool] = mapped_column(Boolean, default=False)
    calories_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    meal: Mapped["Meal"] = relationship(back_populates="items")
    food: Mapped["Food | None"] = relationship(back_populates="meal_items")