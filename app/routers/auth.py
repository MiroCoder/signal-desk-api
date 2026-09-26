from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
)
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login_user(
        credentials: UserLogin,
        db: Session = Depends(get_db)
):
    statement = select(User).where(User.email == credentials.email)
    user = db.scalar(statement)
    if user is None:
        raise HTTPException(status_code=401, detail="No such user")
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    access_token = create_access_token(user.id)
    return {"access_token": access_token,
            "token_type": "bearer"}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
def register_user(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    statement = select(User).where(User.email == user.email)
    existing_user = db.scalar(statement)
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
