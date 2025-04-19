"""
User management routes for authentication, profile, and avatar operations.

Provides endpoints for user registration, login, email verification, profile retrieval,
and avatar updates using JWT, Cloudinary, and rate limiting.
"""

import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

from auth import get_current_user, create_access_token, create_refresh_token, verify_password, SECRET_KEY, ALGORITHM
from crud import create_user, get_user_by_email
from database import get_db
from models import User
from schemas import UserCreate, UserInDB, Token

load_dotenv()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Email configuration
mail_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USER"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD"),
    MAIL_FROM=os.getenv("SMTP_USER"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", "587")),
    MAIL_SERVER=os.getenv("SMTP_HOST"),
    MAIL_STARTTLS=True, 
    MAIL_SSL_TLS=False 
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and send a verification email.
    """
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    new_user = create_user(db, user)
    
    # Create verification token
    verification_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email},
        expires_delta=timedelta(hours=24)
    )
    
    # Send verification email
    verification_url = (
        f"http://localhost:8000/auth/verify/"
        f"{verification_token}"
    )
    message = MessageSchema(
        subject="Verify Your Email",
        recipients=[new_user.email],
        body=f"Please verify your email by clicking the link: <a href='{verification_url}'>Verify</a>",
        subtype="html"
    )
    
    fm = FastMail(mail_conf)
    await fm.send_message(message)
    
    return UserInDB.from_orm(new_user)

@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: Session = Depends(get_db)):
    """
    Authenticate a user and return JWT tokens.
    """
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/verify/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify a user's email using a token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None or email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        ) from exc
    
    user = db.query(User).filter(User.id == user_id, User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.verified:
        return {"message": "Email already verified"}
    
    user.verified = True
    db.commit()
    return {"message": "Email successfully verified"}

@router.get("/users/me", response_model=UserInDB, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_users_me(current_user: UserInDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get the current user's profile (rate-limited to 10 requests per minute).
    """
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInDB.from_orm(db_user)

@router.patch("/users/avatar", response_model=UserInDB)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's avatar using Cloudinary.
    """
    try:
        upload_result = cloudinary.uploader.upload(file.file, folder="avatars")
        avatar_url = upload_result["secure_url"]
        
        db_user = db.query(User).filter(User.id == current_user.id).first()
        db_user.avatar = avatar_url
        db.commit()
        db.refresh(db_user)
        
        return UserInDB.from_orm(db_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e

        