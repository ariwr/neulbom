"""
인증 서비스
- JWT 토큰 발급 및 인증
- 비밀번호 해싱
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.connection import get_db
from app.models import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    # 72바이트 초과 시 자동으로 잘라냄 (안전장치) - bcrypt 72바이트 제한 호환
    if len(plain_password) > 72:
        truncated_bytes = plain_password[:72]
        while truncated_bytes and truncated_bytes[-1] & 0x80 and not (truncated_bytes[-1] & 0x40):
            truncated_bytes = truncated_bytes[:-1]
        plain_password = truncated_bytes
        
    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    비밀번호 해싱
    - bcrypt는 72바이트로 제한되므로 초과 시 자동으로 잘라냄
    """
    password_bytes = password.encode('utf-8')
    
    # 72바이트 초과 시 자동으로 잘라냄 (안전장치)
    if len(password_bytes) > 72:
        # 72바이트로 자르고 다시 문자열로 변환
        # UTF-8 인코딩을 고려하여 안전하게 자름
        truncated_bytes = password_bytes[:72]
        # 마지막 바이트가 잘린 멀티바이트 문자의 일부일 수 있으므로 처리
        while truncated_bytes and truncated_bytes[-1] & 0x80 and not (truncated_bytes[-1] & 0x40):
            truncated_bytes = truncated_bytes[:-1]
        password_bytes = truncated_bytes

    # 소금(salt) 생성 및 해싱
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """JWT 토큰 디코딩"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """현재 로그인한 사용자 가져오기"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """활성 사용자 확인"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_level(required_level: int):
    """등급 기반 접근 제어 데코레이터"""
    async def level_checker(current_user: models.User = Depends(get_current_active_user)) -> models.User:
        if current_user.level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires level {required_level} access"
            )
        return current_user
    return level_checker


async def get_optional_user(
    token: Optional[str] = Security(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """선택적 사용자 인증 (비회원도 접근 가능)"""
    if token is None:
        return None
    try:
        payload = decode_access_token(token)
        if payload is None:
            return None
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user and not user.is_active:
            return None
        return user
    except Exception:
        return None

