"""
예외 처리
- 커스텀 예외 클래스
"""

from fastapi import HTTPException, status


class NeulbomException(HTTPException):
    """늘봄 기본 예외 클래스"""
    pass


class UserNotFoundError(NeulbomException):
    """사용자를 찾을 수 없음"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


class WelfareNotFoundError(NeulbomException):
    """복지 정보를 찾을 수 없음"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Welfare not found"
        )


class PostNotFoundError(NeulbomException):
    """게시글을 찾을 수 없음"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )


class InsufficientLevelError(NeulbomException):
    """권한 부족"""
    def __init__(self, required_level: int):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires level {required_level} access"
        )

