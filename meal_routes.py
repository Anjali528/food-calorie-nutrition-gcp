from datetime import datetime, date, time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from db import get_db
from deps import get_current_user
from models import Meal, MealItem, Food
from schemas import MealCreateIn, MealOut, MealItemOut

router = APIRouter(prefix="/meals", tags=["meals"])

@router.post("", response_model=MealOut)
def create_meal(payload: MealCreateIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    meal = Meal(user_id=user.id, meal_time=payload.meal_time)
    db.add(meal)
    db.flush()

    out_items = []
    for item in payload.items:
        calories_total = protein_total = carbs_total = fat_total = None

        if item.food_id is not None:
            food = db.execute(select(Food).where(Food.id == item.food_id)).scalar_one_or_none()
            if not food:
                raise HTTPException(status_code=404, detail=f"Food {item.food_id} not found")

            factor = item.quantity_g / 100.0
            calories_total = (food.calories_100g or 0) * factor
            protein_total = (food.protein_100g or 0) * factor
            carbs_total = (food.carbs_100g or 0) * factor
            fat_total = (food.fat_100g or 0) * factor

        mi = MealItem(
            meal_id=meal.id,
            food_id=item.food_id,
            custom_name=item.custom_name,
            quantity_g=item.quantity_g,
            predicted=item.predicted,
            calories_total=calories_total,
            protein_total=protein_total,
            carbs_total=carbs_total,
            fat_total=fat_total,
        )
        db.add(mi)
        db.flush()

        out_items.append(
            MealItemOut(
                id=mi.id,
                food_id=mi.food_id,
                custom_name=mi.custom_name,
                quantity_g=mi.quantity_g,
                predicted=mi.predicted,
                calories_total=mi.calories_total,
                protein_total=mi.protein_total,
                carbs_total=mi.carbs_total,
                fat_total=mi.fat_total,
            )
        )

    db.commit()
    return MealOut(id=meal.id, meal_time=meal.meal_time, items=out_items)


@router.get("/today")
def get_today_summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    today = date.today()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)

    meals = db.execute(
        select(Meal).where(
            Meal.user_id == user.id,
            Meal.meal_time >= start,
            Meal.meal_time <= end,
        )
    ).scalars().all()

    meal_ids = [m.id for m in meals]
    if not meal_ids:
        return {
            "date": str(today),
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "meals_count": 0,
        }

    totals = db.execute(
        select(
            func.coalesce(func.sum(MealItem.calories_total), 0),
            func.coalesce(func.sum(MealItem.protein_total), 0),
            func.coalesce(func.sum(MealItem.carbs_total), 0),
            func.coalesce(func.sum(MealItem.fat_total), 0),
        ).where(MealItem.meal_id.in_(meal_ids))
    ).one()

    return {
        "date": str(today),
        "calories": float(totals[0]),
        "protein": float(totals[1]),
        "carbs": float(totals[2]),
        "fat": float(totals[3]),
        "meals_count": len(meals),
    }

@router.get("/today/detail")
def get_today_meals(db: Session = Depends(get_db), user=Depends(get_current_user)):
    from sqlalchemy.orm import joinedload
    
    today = date.today()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)

    meals = db.execute(
        select(Meal).where(
            Meal.user_id == user.id,
            Meal.meal_time >= start,
            Meal.meal_time <= end,
        ).order_by(Meal.meal_time.desc()).options(joinedload(Meal.items).joinedload(MealItem.food))
    ).unique().scalars().all()

    result = []
    for meal in meals:
        meal_data = {
            "id": meal.id,
            "meal_time": meal.meal_time.isoformat(),
            "items": [
                {
                    "id": item.id,
                    "food_id": item.food_id,
                    "food_name": item.food.name if item.food else (item.custom_name or "Unknown"),
                    "custom_name": item.custom_name,
                    "quantity_g": item.quantity_g,
                    "predicted": item.predicted,
                    "calories_total": item.calories_total,
                    "protein_total": item.protein_total,
                    "carbs_total": item.carbs_total,
                    "fat_total": item.fat_total,
                }
                for item in meal.items
            ]
        }
        result.append(meal_data)
    
    return result


@router.delete("/{meal_id}")
def delete_meal(meal_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    meal = db.execute(
        select(Meal).where(Meal.id == meal_id, Meal.user_id == user.id)
    ).scalar_one_or_none()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    # Delete meal items first
    db.query(MealItem).filter(MealItem.meal_id == meal_id).delete()
    
    # Delete meal
    db.delete(meal)
    db.commit()
    
    return {"message": "Meal deleted successfully"}