from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models.connection import get_db
from app.models import models, schema, crud
from app.services.auth_service import (
    verify_password,
    create_access_token,
    get_current_active_user,
    require_level
)
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=schema.Token)
def signup(user_data: schema.UserSignup, db: Session = Depends(get_db)):
    """회원가입 (Level 2 부여)"""
    # 이메일 중복 체크
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 사용자 생성
    user = crud.create_user(db, user_data)
    
    # 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schema.Token)
def login(user_data: schema.UserLogin, db: Session = Depends(get_db)):
    """로그인 (Access Token 발급)"""
    user = crud.get_user_by_email(db, user_data.email)
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=schema.UserProfile)
def get_my_profile(current_user: models.User = Depends(get_current_active_user)):
    """내 프로필 조회 (나이, 지역, 등급)"""
    return current_user


@router.put("/users/me", response_model=schema.UserProfile)
def update_my_profile(
    profile_update: schema.UserProfileUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """내 프로필 수정"""
    updated_user = crud.update_user_profile(db, current_user.id, profile_update)
    return updated_user

