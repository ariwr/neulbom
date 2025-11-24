"""
데이터베이스 유틸리티 함수
- 트랜잭션 관리
- 에러 처리 공통화
"""

from typing import Callable, TypeVar, Optional, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def with_transaction(
    db: Session,
    operation: Callable[[], T],
    error_message: str = "작업 처리 중 오류가 발생했습니다.",
    error_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    log_context: Optional[dict] = None
) -> T:
    """
    트랜잭션 관리 데코레이터 함수
    
    Args:
        db: 데이터베이스 세션
        operation: 실행할 함수 (인자 없음)
        error_message: 에러 발생 시 메시지
        error_status: HTTP 상태 코드
        log_context: 로깅 컨텍스트 정보
        
    Returns:
        operation의 반환값
        
    Raises:
        HTTPException: 작업 실패 시
    """
    try:
        result = operation()
        return result
    except HTTPException:
        # HTTPException은 그대로 전파
        raise
    except ValueError as e:
        # ValueError는 400 에러로 변환
        db.rollback()
        context_str = f", {log_context}" if log_context else ""
        logger.warning(f"{error_message} (ValueError){context_str}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        context_str = f", {log_context}" if log_context else ""
        logger.error(f"{error_message}{context_str}: {e}", exc_info=True)
        raise HTTPException(
            status_code=error_status,
            detail=error_message
        )


def safe_rollback(db: Session) -> None:
    """
    안전한 롤백 실행 (롤백 실패 시에도 예외 전파 안 함)
    
    Args:
        db: 데이터베이스 세션
    """
    try:
        db.rollback()
    except Exception as e:
        logger.warning(f"롤백 중 오류 발생 (무시됨): {e}")


def safe_commit(db: Session) -> None:
    """
    안전한 커밋 실행
    
    Args:
        db: 데이터베이스 세션
        
    Raises:
        Exception: 커밋 실패 시
    """
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"커밋 실패: {e}", exc_info=True)
        raise



