from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

from db import SessionLocal
from models import User
from security import hash_password

db = SessionLocal()
try:
    u = User(
        name="Anjali Desai",
        email="msci.2332@unigoa.ac.in",
        password_hash=hash_password("desai21"),
    )
    db.add(u)
    db.commit()
    print("Inserted user id:", u.id)
except Exception as e:
    db.rollback()
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR:", e)
    raise
finally:
    db.close()