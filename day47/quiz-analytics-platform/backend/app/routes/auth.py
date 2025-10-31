from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.quiz import User
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/users", response_model=list[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
