"""
입력 검증 유틸리티 함수
- 텍스트 길이 검증
- 공통 검증 로직
"""

from fastapi import HTTPException, status
from typing import Optional


def validate_text_length(
    text: Optional[str],
    field_name: str,
    min_length: int,
    max_length: int,
    allow_empty: bool = False
) -> None:
    """
    텍스트 길이 검증
    
    Args:
        text: 검증할 텍스트
        field_name: 필드 이름 (에러 메시지용)
        min_length: 최소 길이
        max_length: 최대 길이
        allow_empty: 빈 값 허용 여부
        
    Raises:
        HTTPException: 검증 실패 시
    """
    if text is None:
        if not allow_empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name}은(는) 필수 항목입니다."
            )
        return
    
    text_stripped = text.strip()
    
    if not text_stripped and not allow_empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name}은(는) 필수 항목입니다."
        )
    
    if text_stripped and len(text_stripped) < min_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name}은(는) 최소 {min_length}자 이상 작성해주세요."
        )
    
    if len(text) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name}은(는) {max_length}자 이하로 작성해주세요."
        )


def validate_verification_text(text: str) -> None:
    """심사 제출 글 검증"""
    validate_text_length(text, "심사 제출 글", min_length=10, max_length=2000)


def validate_post_title(title: str) -> None:
    """게시글 제목 검증"""
    validate_text_length(title, "제목", min_length=2, max_length=200)


def validate_post_content(content: str) -> None:
    """게시글 내용 검증"""
    validate_text_length(content, "내용", min_length=10, max_length=10000)


def validate_comment_content(content: str) -> None:
    """댓글 내용 검증"""
    validate_text_length(content, "댓글", min_length=2, max_length=2000)

