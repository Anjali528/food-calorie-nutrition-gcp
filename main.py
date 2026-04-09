from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_routes import router as auth_router
from food_routes import router as food_router
from meal_routes import router as meal_router

app = FastAPI(title="Food Calorie Tracker API", debug=True)

# Add CORS middleware HERE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Then include routers
app.include_router(auth_router)
app.include_router(food_router)
app.include_router(meal_router)

@app.get("/")
def root():
    return {"status": "ok"}