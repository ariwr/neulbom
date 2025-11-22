from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.connection import get_db
from app.models import models, schema, crud
from app.services.auth_service import get_current_active_user, require_level
from app.services.community_service import create_post_with_ai_check, get_posts_list

router = APIRouter(prefix="/api/community", tags=["community"])


@router.post("/verify")
def submit_verification(
    verification: schema.VerificationRequest,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    커뮤니티 가입 심사글 제출 (Level 3 승급 요청)
    - Level 2 (일반 회원) 이상 접근 가능
    """
    # 이미 Level 3인 경우
    if current_user.level >= 3:
        return {"message": "Already verified", "level": current_user.level}
    
    # 심사 제출
    user = crud.submit_verification(db, current_user.id, verification.text)
    
    # TODO: AI 심사 로직 또는 관리자 승인 프로세스
    # 현재는 자동 승인으로 처리 (실제로는 AI/관리자 심사 필요)
    # user = crud.approve_verification(db, current_user.id)
    
    return {
        "message": "Verification submitted",
        "status": user.verification_status
    }


@router.post("/posts", response_model=schema.PostResponse)
def create_post(
    post_data: schema.PostCreate,
    current_user: models.User = Depends(require_level(3)),  # Level 3 이상 필요
    db: Session = Depends(get_db)
):
    """
    게시글 작성 (AI 필터링 적용)
    - Level 3 (검증 회원) 이상 접근 가능
    """
    post = create_post_with_ai_check(
        db=db,
        post_data=post_data,
        author_id=current_user.id
    )
    
    return schema.PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        anonymous_id=post.anonymous_id,
        created_at=post.created_at,
        comment_count=len(post.comments)
    )


@router.get("/posts", response_model=List[schema.PostResponse])
def get_posts(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(require_level(3)),  # Level 3 이상 필요
    db: Session = Depends(get_db)
):
    """
    게시글 목록 조회
    - Level 3 (검증 회원) 이상 접근 가능
    """
    posts = get_posts_list(db, skip=skip, limit=limit)
    
    # 댓글 수 추가
    result = []
    for post in posts:
        result.append(schema.PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            anonymous_id=post.anonymous_id,
            created_at=post.created_at,
            comment_count=len(post.comments)
        ))
    
    return result

