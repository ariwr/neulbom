from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from datetime import timedelta
import logging
import re

from app.models.connection import get_db
from app.models import models, schema, crud
from app.models.crud import get_user_post_bookmarks
from app.services.auth_service import (
    verify_password,
    create_access_token,
    get_current_active_user,
    require_level
)
from app.core.config import settings
from fastapi import Query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=schema.Token)
def signup(user_data: schema.UserSignup, db: Session = Depends(get_db)):
    """
    회원가입 (Level 2 부여)
    - 이메일 중복 체크 및 트랜잭션 관리
    - 비밀번호 유효성 검증
    - 비밀번호 확인 검증
    """
    # 비밀번호 확인 검증
    if user_data.password != user_data.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="비밀번호와 비밀번호 확인이 일치하지 않습니다."
        )
    
    # 비밀번호 유효성 검증
    password_length = len(user_data.password)
    if password_length < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"비밀번호는 8자 이상이어야 합니다. (현재: {password_length}자)"
        )
    
    # bcrypt는 비밀번호를 72바이트로 제한하므로 바이트 단위로 체크
    password_bytes = user_data.password.encode('utf-8')
    password_bytes_length = len(password_bytes)
    if password_bytes_length > 72:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"비밀번호는 72바이트 이하여야 합니다. (현재: {password_bytes_length}바이트)"
        )
    # 한글 포함 여부 확인
    korean_pattern = re.compile(r'[가-힣]')
    if korean_pattern.search(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="비밀번호는 영어, 숫자, 특수문자의 조합으로만 가능합니다."
        )
    # 비밀번호는 영문(대소문자), 숫자, 특수문자만 허용
    password_pattern = re.compile(r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$')
    if not password_pattern.match(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="비밀번호는 영어, 숫자, 특수문자의 조합으로만 가능합니다."
        )
    
    # 특수문자 포함 여부 확인
    special_char_pattern = re.compile(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]')
    if not special_char_pattern.search(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="비밀번호에 특수문자가 포함되어야 합니다."
        )
    
    try:
        # 이메일 중복 체크
        existing_user = crud.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )
        
        # 사용자 생성 (내부에서 트랜잭션 관리)
        try:
            user = crud.create_user(db, user_data)
        except ValueError as e:
            # crud.create_user에서 발생한 ValueError 처리
            error_message = str(e)
            if "이미 등록된 이메일" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )
            # 비밀번호 길이 관련 오류인 경우 422 상태 코드 반환
            if "72바이트" in error_message or "비밀번호" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=error_message
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_message
            )
        
        # 토큰 생성 (JWT 표준에 따라 sub는 문자열이어야 함)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},  # user.id를 문자열로 변환
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException:
        # HTTPException은 그대로 전파
        raise
    except Exception as e:
        # 예상치 못한 예외 처리
        error_detail = str(e)
        logger.error(f"회원가입 중 예상치 못한 오류 발생: {error_detail}", exc_info=True)
        # DB 롤백 보장
        try:
            db.rollback()
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 처리 중 오류가 발생했습니다: {error_detail}"
        )


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
        data={"sub": str(user.id)},  # user.id를 문자열로 변환 (JWT 표준 준수)
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


@router.get("/users/bookmarks/welfare", response_model=schema.BookmarkListResponse)
def get_welfare_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    내가 북마크한 복지 정보 목록 조회
    - Level 2 (일반 회원) 이상 접근 가능
    """
    bookmarks, total = crud.get_user_bookmarks(db, current_user.id, skip=skip, limit=limit)
    return schema.BookmarkListResponse(
        items=bookmarks,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/users/bookmarks/community", response_model=schema.PostBookmarkListResponse)
def get_community_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(require_level(3)),  # Level 3 이상 필요
    db: Session = Depends(get_db)
):
    """
    내가 북마크한 게시글 목록 조회
    - Level 3 (검증 회원) 이상 접근 가능
    """
    bookmarks, total = get_user_post_bookmarks(db, current_user.id, skip=skip, limit=limit)
    return schema.PostBookmarkListResponse(
        items=bookmarks,
        total=total,
        skip=skip,
        limit=limit
    )

