from sqlalchemy.orm import Session
from src.database.models import User
from src.database.db import get_db
from fastapi import Depends


def add_user(username: str, email: str, password: str, db: Session):
    new_user = User(username=username, email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user