import os
import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from db import get_db
from models import Food
from schemas import FoodOut

router = APIRouter(prefix="/foods", tags=["foods"])

USDA_API_KEY = os.getenv("USDA_API_KEY")

def _extract_macros_from_fdc(food: dict):
    # FoodData Central nutrients vary; we try to map by nutrient name.
    nutrients = food.get("foodNutrients", []) or []
    by_name = {n.get("nutrientName"): n.get("value") for n in nutrients if n.get("nutrientName")}

    calories = by_name.get("Energy")
    protein = by_name.get("Protein")
    carbs = by_name.get("Carbohydrate, by difference")
    fat = by_name.get("Total lipid (fat)")

    return calories, protein, carbs, fat

@router.get("/search", response_model=list[FoodOut])
def search_foods(q: str = Query(min_length=2), db: Session = Depends(get_db)):
    # 1) Return cached results first (simple LIKE search)
    cached = db.execute(
        select(Food).where(Food.name.ilike(f"%{q}%")).limit(10)
    ).scalars().all()

    if cached:
        return [
            FoodOut(
                id=f.id,
                name=f.name,
                calories_100g=f.calories_100g,
                protein_100g=f.protein_100g,
                carbs_100g=f.carbs_100g,
                fat_100g=f.fat_100g,
                source=f.source,
            )
            for f in cached
        ]

    # 2) If not cached, call USDA API
    if not USDA_API_KEY:
        raise HTTPException(status_code=500, detail="USDA_API_KEY not set")

    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    resp = requests.get(url, params={"api_key": USDA_API_KEY, "query": q, "pageSize": 10}, timeout=20)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"USDA API error: {resp.status_code}")

    data = resp.json()
    foods = data.get("foods", []) or []

    results: list[FoodOut] = []
    for item in foods:
        fdc_id = str(item.get("fdcId")) if item.get("fdcId") else None
        name = item.get("description") or item.get("lowercaseDescription") or q

        calories, protein, carbs, fat = _extract_macros_from_fdc(item)

        # cache into DB
        f = Food(
            name=name,
            source="usda",
            external_id=fdc_id,
            calories_100g=calories,
            protein_100g=protein,
            carbs_100g=carbs,
            fat_100g=fat,
        )
        db.add(f)
        db.flush()  # get id

        results.append(
            FoodOut(
                id=f.id,
                name=f.name,
                calories_100g=f.calories_100g,
                protein_100g=f.protein_100g,
                carbs_100g=f.carbs_100g,
                fat_100g=f.fat_100g,
                source=f.source,
            )
        )

    db.commit()
    return results