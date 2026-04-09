from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from db import get_db
from models import User
from schemas import RegisterIn, LoginIn, TokenOut
from security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    u = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(u)
    db.commit()
    return {"message": "registered"}

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    u = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(sub=str(u.id))
    return TokenOut(access_token=token)