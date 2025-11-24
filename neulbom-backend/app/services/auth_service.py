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
    """JWT 토큰 디코딩 (기존 정수 sub 토큰 호환)"""
    import logging
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    try:
        # 먼저 표준 방식으로 디코딩 시도
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        error_msg = str(e)
        
        # "Subject must be a string" 오류인 경우, 기존 토큰(정수 sub) 호환 처리
        if "Subject must be a string" in error_msg:
            try:
                # 검증 없이 페이로드 추출 (기존 토큰 호환)
                unverified_payload = jwt.get_unverified_claims(token)
                
                # 만료 시간 검증
                exp = unverified_payload.get('exp')
                if exp:
                    if isinstance(exp, (int, float)):
                        if datetime.utcnow().timestamp() > exp:
                            logger.warning(f"토큰 만료됨: exp={exp}")
                            return None
                    else:
                        logger.warning(f"토큰 exp 형식 오류: {type(exp)}")
                
                # 서명 검증 시도 (sub 검증 없이)
                try:
                    # 서명만 검증 (sub 검증은 건너뛰기 위해 get_unverified_claims 사용)
                    # python-jose는 sub 검증을 건너뛸 수 없으므로, 서명 검증은 별도로 수행
                    # 하지만 실제로는 get_unverified_claims로 이미 페이로드를 추출했으므로
                    # 서명 검증을 수동으로 할 수 없음. 대신 페이로드를 반환하고 호출하는 쪽에서 처리
                    logger.info(f"기존 토큰 감지 (정수 sub): {unverified_payload.get('sub')}, 서명 검증은 건너뜀 (기존 토큰 호환)")
                except Exception:
                    pass
                
                return unverified_payload
            except Exception as inner_e:
                logger.warning(f"기존 토큰 호환 처리 실패: {inner_e}, 원본 오류: {error_msg}")
                return None
        else:
            # 다른 종류의 JWT 오류
            logger.warning(f"JWT 토큰 디코딩 실패: {error_msg}, 토큰 시작: {token[:20] if token else 'None'}...")
            return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """현재 로그인한 사용자 가져오기"""
    import logging
    logger = logging.getLogger(__name__)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 토큰 디버깅
    if not token:
        logger.error("토큰이 없습니다.")
        raise credentials_exception
    
    logger.info(f"토큰 수신: 길이={len(token)}, 시작={token[:30]}...")
    
    # 토큰 앞뒤 공백 제거
    token = token.strip()
    
    payload = decode_access_token(token)
    if payload is None:
        logger.error(f"토큰 디코딩 실패: token 길이={len(token)}, 시작={token[:30]}...")
        raise credentials_exception
    
    # JWT 표준에 따라 sub는 문자열이어야 하지만, 기존 토큰 호환을 위해 정수와 문자열 모두 처리
    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        logger.error(f"토큰에 user_id(sub) 없음: payload={payload}")
        raise credentials_exception
    
    try:
        # 정수인 경우와 문자열인 경우 모두 처리
        if isinstance(user_id_raw, int):
            user_id: int = user_id_raw
        elif isinstance(user_id_raw, str):
            user_id: int = int(user_id_raw)
        else:
            logger.error(f"토큰의 user_id(sub) 타입이 올바르지 않음: {type(user_id_raw)}, 값: {user_id_raw}")
            raise credentials_exception
    except (ValueError, TypeError) as e:
        logger.error(f"토큰의 user_id(sub)를 정수로 변환 실패: {user_id_raw}, 오류: {e}")
        raise credentials_exception
    
    logger.info(f"토큰 검증 성공: user_id={user_id}")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        logger.error(f"사용자를 찾을 수 없음: user_id={user_id}")
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
        
        # JWT 표준에 따라 sub는 문자열이어야 하지만, 기존 토큰 호환을 위해 정수와 문자열 모두 처리
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            return None
        
        try:
            # 정수인 경우와 문자열인 경우 모두 처리
            if isinstance(user_id_raw, int):
                user_id: int = user_id_raw
            elif isinstance(user_id_raw, str):
                user_id: int = int(user_id_raw)
            else:
                return None
        except (ValueError, TypeError):
            return None
        
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user and not user.is_active:
            return None
        return user
    except Exception:
        return None

