"""
커뮤니티 서비스
- 게시글 AI 클린봇 검수 후 DB 저장 로직
- 위기 감지 및 관리자 알림
"""

from sqlalchemy.orm import Session
from app.models import models, schema
from app.models.crud import create_post, get_posts, get_post_by_id
from app.ai_core.safety_guard import detect_crisis, analyze_crisis_level


def create_post_with_ai_check(
    db: Session,
    post_data: schema.PostCreate,
    author_id: int
) -> models.Post:
    """
    게시글 작성 (AI 필터링 적용)
    - 위기 감지
    - 고위험 게시글 탐지 시 관리자 알림
    """
    # AI 위기 감지
    crisis_analysis = analyze_crisis_level(post_data.content)
    is_crisis = crisis_analysis["is_crisis"]
    
    # 게시글 생성
    post = create_post(
        db=db,
        post_data=post_data,
        author_id=author_id,
        is_crisis=is_crisis
    )
    
    # 고위험 게시글 탐지 시 관리자 알림
    if crisis_analysis["level"] == "high":
        # TODO: 관리자 알림 발송
        # send_admin_alert(post.id, crisis_analysis)
        pass
    
    return post


def get_posts_list(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> List[models.Post]:
    """게시글 목록 조회"""
    return get_posts(db, skip=skip, limit=limit)


def get_post_detail(
    db: Session,
    post_id: int
) -> Optional[models.Post]:
    """게시글 상세 조회"""
    return get_post_by_id(db, post_id)


def send_admin_alert(post_id: int, crisis_analysis: dict):
    """
    관리자 알림 발송
    - TODO: 이메일, 슬랙, 또는 다른 알림 채널 구현
    """
    # TODO: 실제 알림 구현
    # 예: 이메일 발송, 슬랙 메시지 등
    pass

