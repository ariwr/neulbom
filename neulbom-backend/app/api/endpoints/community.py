from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

from app.models.connection import get_db
from app.models import models, schema, crud
from app.models.crud import (
    toggle_post_like, toggle_post_bookmark,
    get_user_liked_post_ids, get_user_bookmarked_post_ids
)
from app.services.auth_service import get_current_active_user, require_level
from app.services.community_service import create_post_with_ai_check, get_posts_list, get_post_detail
from app.services.verification_service import verify_with_ai
from app.utils.validators import (
    validate_verification_text,
    validate_post_title,
    validate_post_content,
    validate_comment_content
)
from app.utils.response_helpers import (
    create_post_response,
    create_posts_response,
    create_comment_response,
    create_comments_response
)
from app.utils.db_utils import safe_rollback, with_transaction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/community", tags=["community"])


@router.post("/verify", response_model=Dict[str, Any])
def submit_verification(
    verification: schema.VerificationRequest,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    커뮤니티 가입 심사글 제출 (Level 3 승급 요청)
    - Level 2 (일반 회원) 이상 접근 가능
    - AI 자동 심사 후 즉시 승인/거절 결정
    """
    # 입력 검증
    validate_verification_text(verification.text)
    
    # 이미 Level 3인 경우
    if current_user.level >= 3:
        logger.info(f"이미 검증된 사용자 심사 시도: user_id={current_user.id}")
        return {
            "message": "이미 검증된 회원입니다.",
            "level": current_user.level,
            "status": "approved"
        }
    
    try:
        # 심사 제출
        user = crud.submit_verification(db, current_user.id, verification.text)
        logger.info(f"심사 제출 완료: user_id={current_user.id}, text_length={len(verification.text)}")
        
        # AI 자동 심사
        try:
            ai_result = verify_with_ai(verification.text)
            logger.info(f"AI 심사 결과: user_id={current_user.id}, approved={ai_result['approved']}, confidence={ai_result.get('confidence', 0)}")
            
            if ai_result["approved"]:
                # 승인: Level 3로 승급
                user = crud.approve_verification(db, current_user.id)
                logger.info(f"심사 승인 완료: user_id={current_user.id}, level={user.level}")
                return {
                    "message": "심사가 승인되었습니다. 커뮤니티에 입장하실 수 있습니다.",
                    "status": "approved",
                    "level": user.level,
                    "reason": ai_result.get("reason", "AI 심사 결과 승인되었습니다."),
                    "confidence": ai_result.get("confidence", 0.7)
                }
            else:
                # 거절: 상태만 업데이트
                user.verification_status = "rejected"
                db.commit()
                db.refresh(user)
                logger.warning(f"심사 거절: user_id={current_user.id}, reason={ai_result.get('reason', '')}")
                return {
                    "message": "심사가 거절되었습니다.",
                    "status": "rejected",
                    "level": user.level,
                    "reason": ai_result.get("reason", "심사 기준에 맞지 않습니다."),
                    "confidence": ai_result.get("confidence", 0.7)
                }
        except Exception as e:
            logger.error(f"AI 심사 중 오류 발생: user_id={current_user.id}, error={e}", exc_info=True)
            safe_rollback(db)
            # 오류 발생 시 pending 상태 유지
            return {
                "message": "심사 제출이 완료되었습니다. 검토 후 결과를 알려드리겠습니다.",
                "status": "pending",
                "level": user.level
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"심사 제출 중 오류 발생: user_id={current_user.id}, error={e}", exc_info=True)
        safe_rollback(db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="심사 제출 처리 중 오류가 발생했습니다."
        )


@router.post("/posts", response_model=schema.PostResponse)
def create_post(
    post_data: schema.PostCreate,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> schema.PostResponse:
    """
    게시글 작성 (AI 필터링 적용)
    - Level 2 (일반 회원) 이상 접근 가능
    - 고위험 게시글은 자동 차단
    """
    # 입력 검증
    validate_post_title(post_data.title)
    validate_post_content(post_data.content)
    
    def _create_post():
        post = create_post_with_ai_check(
            db=db,
            post_data=post_data,
            author_id=current_user.id
        )
        logger.info(f"게시글 작성 완료: post_id={post.id}, author_id={current_user.id}")
        return post
    
    try:
        post = _create_post()
        return create_post_response(post, current_user.id, db)
    except ValueError as e:
        # 위기 게시글 차단
        error_str = str(e)
        logger.warning(f"위기 게시글 차단: author_id={current_user.id}, reason={error_str}")
        
        # 에러 코드 파싱 시도
        import json
        try:
            error_detail = json.loads(error_str)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        except (json.JSONDecodeError, TypeError):
            # JSON이 아닌 경우 일반 에러 메시지로 처리
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "CRISIS_DETECTED", "message": error_str}
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"게시글 작성 중 오류 발생: author_id={current_user.id}, error={e}", exc_info=True)
        safe_rollback(db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 작성 중 오류가 발생했습니다."
        )


@router.get("/posts", response_model=List[schema.PostResponse])
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="카테고리 필터 (information/worry/free)"),
    sort: str = Query("latest", description="정렬 방식 (latest/popular)"),
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> List[schema.PostResponse]:
    """
    게시글 목록 조회
    - Level 2 (일반 회원) 이상 접근 가능
    - category: 전체/정보공유/고민상담/자유 필터링
    - sort: latest(최신순) vs popular(좋아요순) 정렬
    """
    try:
        # sort 검증
        if sort not in ["latest", "popular"]:
            sort = "latest"
        
        posts = get_posts_list(db, skip=skip, limit=limit, category=category, sort=sort)
        logger.debug(f"게시글 목록 조회: user_id={current_user.id}, skip={skip}, limit={limit}, category={category}, sort={sort}, count={len(posts)}")
        
        # N+1 문제 해결: Bulk 조회로 좋아요/북마크 상태 한 번에 가져오기
        post_ids = [post.id for post in posts]
        liked_ids = get_user_liked_post_ids(db, current_user.id, post_ids)
        bookmarked_ids = get_user_bookmarked_post_ids(db, current_user.id, post_ids)
        
        # 메모리 상에서 PostResponse 생성
        result = []
        for post in posts:
            result.append(schema.PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                category=post.category.value if hasattr(post.category, 'value') else str(post.category),
                view_count=post.view_count or 0,
                like_count=post.like_count or 0,
                anonymous_id=post.anonymous_id,
                created_at=post.created_at,
                comment_count=len(post.comments) if hasattr(post, 'comments') else 0,
                is_liked=post.id in liked_ids,
                is_bookmarked=post.id in bookmarked_ids
            ))
        
        return result
    except Exception as e:
        logger.error(f"게시글 목록 조회 중 오류 발생: user_id={current_user.id}, error={e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 목록 조회 중 오류가 발생했습니다."
        )


@router.get("/posts/{post_id}", response_model=schema.PostResponse)
def get_post(
    post_id: int,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> schema.PostResponse:
    """
    게시글 상세 조회
    - Level 2 (일반 회원) 이상 접근 가능
    """
    try:
        post = get_post_detail(db, post_id)
        if not post:
            logger.warning(f"게시글 조회 실패: post_id={post_id}, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )
        
        logger.debug(f"게시글 상세 조회: post_id={post_id}, user_id={current_user.id}")
        
        # 조회수 증가
        post.view_count = (post.view_count or 0) + 1
        db.commit()
        
        return create_post_response(post, current_user.id, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"게시글 상세 조회 중 오류 발생: post_id={post_id}, user_id={current_user.id}, error={e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 조회 중 오류가 발생했습니다."
        )


@router.put("/posts/{post_id}", response_model=schema.PostResponse)
def update_post(
    post_id: int,
    post_data: schema.PostCreate,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> schema.PostResponse:
    """
    게시글 수정
    - Level 2 (일반 회원) 이상 접근 가능
    - 본인이 작성한 게시글만 수정 가능
    """
    # 입력 검증
    validate_post_title(post_data.title)
    validate_post_content(post_data.content)
    
    try:
        post = crud.update_post(db, post_id, current_user.id, post_data)
        if not post:
            logger.warning(f"게시글 수정 실패: post_id={post_id}, user_id={current_user.id} (권한 없음 또는 존재하지 않음)")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없거나 수정 권한이 없습니다."
            )
        
        logger.info(f"게시글 수정 완료: post_id={post_id}, user_id={current_user.id}")
        return create_post_response(post, current_user.id, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"게시글 수정 중 오류 발생: post_id={post_id}, user_id={current_user.id}, error={e}", exc_info=True)
        safe_rollback(db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 수정 중 오류가 발생했습니다."
        )


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    게시글 삭제
    - Level 2 (일반 회원) 이상 접근 가능
    - 본인이 작성한 게시글만 삭제 가능
    """
    try:
        success = crud.delete_post(db, post_id, current_user.id)
        if not success:
            logger.warning(f"게시글 삭제 실패: post_id={post_id}, user_id={current_user.id} (권한 없음 또는 존재하지 않음)")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없거나 삭제 권한이 없습니다."
            )
        
        logger.info(f"게시글 삭제 완료: post_id={post_id}, user_id={current_user.id}")
        return {"message": "게시글이 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"게시글 삭제 중 오류 발생: post_id={post_id}, user_id={current_user.id}, error={e}", exc_info=True)
        safe_rollback(db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="게시글 삭제 중 오류가 발생했습니다."
        )


@router.post("/posts/{post_id}/comments", response_model=schema.CommentResponse)
def create_comment(
    post_id: int,
    comment_data: schema.CommentCreate,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> schema.CommentResponse:
    """
    댓글 작성
    - Level 2 (일반 회원) 이상 접근 가능
    """
    # 입력 검증
    validate_comment_content(comment_data.content)
    
    try:
        # 게시글 존재 확인
        post = get_post_detail(db, post_id)
        if not post:
            logger.warning(f"댓글 작성 실패: post_id={post_id} 존재하지 않음, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )
        
        # AI 위기 감지 (댓글도 모니터링)
        from app.ai_core.safety_guard import analyze_crisis_level
        crisis_analysis = analyze_crisis_level(comment_data.content)
        
        # 위기 댓글은 차단
        if crisis_analysis["level"] == "high":
            logger.warning(f"위기 댓글 차단: post_id={post_id}, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="부적절한 내용이 감지되어 댓글을 등록할 수 없습니다."
            )
        
        comment = crud.create_comment(db, comment_data, post_id, current_user.id)
        logger.info(f"댓글 작성 완료: comment_id={comment.id}, post_id={post_id}, user_id={current_user.id}")
        return create_comment_response(comment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"댓글 작성 중 오류 발생: post_id={post_id}, user_id={current_user.id}, error={e}", exc_info=True)
        safe_rollback(db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 작성 중 오류가 발생했습니다."
        )


@router.get("/posts/{post_id}/comments", response_model=List[schema.CommentResponse])
def get_comments(
    post_id: int,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> List[schema.CommentResponse]:
    """
    댓글 목록 조회
    - Level 2 (일반 회원) 이상 접근 가능
    """
    try:
        # 게시글 존재 확인
        post = get_post_detail(db, post_id)
        if not post:
            logger.warning(f"댓글 목록 조회 실패: post_id={post_id} 존재하지 않음, user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게시글을 찾을 수 없습니다."
            )
        
        comments = crud.get_comments_by_post(db, post_id)
        logger.debug(f"댓글 목록 조회: post_id={post_id}, user_id={current_user.id}, count={len(comments)}")
        return create_comments_response(comments)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"댓글 목록 조회 중 오류 발생: post_id={post_id}, user_id={current_user.id}, error={e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 목록 조회 중 오류가 발생했습니다."
        )


@router.put("/comments/{comment_id}", response_model=schema.CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: schema.CommentCreate,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> schema.CommentResponse:
    """
    댓글 수정
    - Level 2 (일반 회원) 이상 접근 가능
    - 본인이 작성한 댓글만 수정 가능
    """
    # 입력 검증
    validate_comment_content(comment_data.content)
    
    try:
        comment = crud.update_comment(db, comment_id, current_user.id, comment_data)
        if not comment:
            logger.warning(f"댓글 수정 실패: comment_id={comment_id}, user_id={current_user.id} (권한 없음 또는 존재하지 않음)")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="댓글을 찾을 수 없거나 수정 권한이 없습니다."
            )
        
        logger.info(f"댓글 수정 완료: comment_id={comment_id}, user_id={current_user.id}")
        return create_comment_response(comment)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"댓글 수정 중 오류 발생: comment_id={comment_id}, user_id={current_user.id}, error={e}", exc_info=True)
        safe_rollback(db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 수정 중 오류가 발생했습니다."
        )


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    댓글 삭제
    - Level 2 (일반 회원) 이상 접근 가능
    - 본인이 작성한 댓글만 삭제 가능
    """
    try:
        success = crud.delete_comment(db, comment_id, current_user.id)
        if not success:
            logger.warning(f"댓글 삭제 실패: comment_id={comment_id}, user_id={current_user.id} (권한 없음 또는 존재하지 않음)")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="댓글을 찾을 수 없거나 삭제 권한이 없습니다."
            )
        
        logger.info(f"댓글 삭제 완료: comment_id={comment_id}, user_id={current_user.id}")
        return {"message": "댓글이 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"댓글 삭제 중 오류 발생: comment_id={comment_id}, user_id={current_user.id}, error={e}", exc_info=True)
        safe_rollback(db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="댓글 삭제 중 오류가 발생했습니다."
        )


@router.post("/posts/{post_id}/like")
def toggle_like(
    post_id: int,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    게시글 좋아요 토글
    - Level 2 (일반 회원) 이상 접근 가능
    - 이미 좋아요를 눌렀으면 취소, 아니면 추가
    """
    try:
        is_liked, is_new = toggle_post_like(db, current_user.id, post_id)
        logger.info(f"좋아요 토글: post_id={post_id}, user_id={current_user.id}, is_liked={is_liked}")
        return {
            "message": "좋아요가 추가되었습니다." if is_liked else "좋아요가 취소되었습니다.",
            "is_liked": is_liked,
            "is_new": is_new
        }
    except ValueError as e:
        logger.warning(f"좋아요 토글 실패: post_id={post_id}, user_id={current_user.id}, error={str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"좋아요 토글 중 오류 발생: post_id={post_id}, user_id={current_user.id}, error={e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="좋아요 처리 중 오류가 발생했습니다."
        )


@router.post("/posts/{post_id}/bookmark")
def toggle_bookmark(
    post_id: int,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    게시글 북마크 토글
    - Level 2 (일반 회원) 이상 접근 가능
    - 이미 북마크했으면 삭제, 아니면 추가
    """
    try:
        bookmark, is_new = toggle_post_bookmark(db, current_user.id, post_id)
        logger.info(f"북마크 토글: post_id={post_id}, user_id={current_user.id}, is_new={is_new}")
        return {
            "message": "북마크가 추가되었습니다." if is_new else "북마크가 삭제되었습니다.",
            "is_bookmarked": is_new,
            "bookmark_id": bookmark.id if bookmark else None
        }
    except Exception as e:
        logger.error(f"북마크 토글 중 오류 발생: post_id={post_id}, user_id={current_user.id}, error={e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="북마크 처리 중 오류가 발생했습니다."
        )

