"""
응답 생성 헬퍼 함수
- 공통 응답 생성 로직
"""

from typing import List, Optional
from app.models import models, schema


def create_post_response(post: models.Post, user_id: Optional[int] = None, db=None) -> schema.PostResponse:
    """
    Post 모델을 PostResponse로 변환
    
    Args:
        post: Post 모델 인스턴스
        user_id: 현재 사용자 ID (좋아요/북마크 상태 확인용)
        db: 데이터베이스 세션 (좋아요/북마크 상태 확인용)
        
    Returns:
        PostResponse 스키마
    """
    is_liked = False
    is_bookmarked = False
    
    if user_id and db:
        # 순환 import 방지를 위해 함수 내부에서 import
        from app.models.crud import check_post_liked, check_post_bookmarked
        is_liked = check_post_liked(db, user_id, post.id)
        is_bookmarked = check_post_bookmarked(db, user_id, post.id)
    
    return schema.PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        category=post.category.value if hasattr(post.category, 'value') else str(post.category),
        view_count=post.view_count or 0,
        like_count=post.like_count or 0,
        anonymous_id=post.anonymous_id,
        created_at=post.created_at,
        comment_count=len(post.comments) if hasattr(post, 'comments') else 0,
        is_liked=is_liked,
        is_bookmarked=is_bookmarked
    )


def create_posts_response(posts: List[models.Post], user_id: Optional[int] = None, db=None) -> List[schema.PostResponse]:
    """
    Post 모델 리스트를 PostResponse 리스트로 변환
    
    Args:
        posts: Post 모델 인스턴스 리스트
        user_id: 현재 사용자 ID (좋아요/북마크 상태 확인용)
        db: 데이터베이스 세션 (좋아요/북마크 상태 확인용)
        
    Returns:
        PostResponse 스키마 리스트
    """
    return [create_post_response(post, user_id, db) for post in posts]


def create_comment_response(comment: models.Comment) -> schema.CommentResponse:
    """
    Comment 모델을 CommentResponse로 변환
    
    Args:
        comment: Comment 모델 인스턴스
        
    Returns:
        CommentResponse 스키마
    """
    return schema.CommentResponse(
        id=comment.id,
        content=comment.content,
        anonymous_id=comment.anonymous_id,
        created_at=comment.created_at
    )


def create_comments_response(comments: List[models.Comment]) -> List[schema.CommentResponse]:
    """
    Comment 모델 리스트를 CommentResponse 리스트로 변환
    
    Args:
        comments: Comment 모델 인스턴스 리스트
        
    Returns:
        CommentResponse 스키마 리스트
    """
    return [create_comment_response(comment) for comment in comments]

