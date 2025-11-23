"""
커뮤니티 서비스
- 게시글 AI 클린봇 검수 후 DB 저장 로직
- 위기 감지 및 관리자 알림
"""

from typing import List, Optional, Dict, Any
from app.models.models import PostCategory
from sqlalchemy.orm import Session
import logging
from app.models import models, schema
from app.models.crud import create_post, get_posts, get_post_by_id
from app.ai_core.safety_guard import detect_crisis, analyze_crisis_level
from app.utils.db_utils import safe_rollback

logger = logging.getLogger(__name__)


def create_post_with_ai_check(
    db: Session,
    post_data: schema.PostCreate,
    author_id: int
) -> models.Post:
    """
    게시글 작성 (AI 필터링 적용)
    - 위기 감지 (AI 분석 실패 시에도 게시글 작성 가능)
    - 고위험 게시글 차단 또는 관리자 알림
    
    Raises:
        ValueError: 고위험 게시글이 감지된 경우
    """
    is_crisis = False
    crisis_analysis = None
    
    try:
        # AI 위기 감지 (실패해도 게시글 작성은 계속 진행)
        try:
            crisis_analysis = analyze_crisis_level(post_data.content)
            is_crisis = crisis_analysis.get("is_crisis", False)
            
            # 고위험 게시글은 차단
            if crisis_analysis.get("level") == "high":
                # 관리자 알림 발송
                send_admin_alert(post_id=None, crisis_analysis=crisis_analysis, post_content=post_data.content)
                logger.warning(f"고위험 게시글 차단: author_id={author_id}, detection_method={crisis_analysis.get('detection_method', 'unknown')}")
                # 위기 감지 에러 코드 포함 (JSON 문자열로 변환)
                import json
                error_detail = {
                    "code": "CRISIS_DETECTED",
                    "message": "부적절한 내용이 감지되어 게시글을 등록할 수 없습니다.",
                    "crisis_info": crisis_analysis.get("info")
                }
                raise ValueError(json.dumps(error_detail))
        except ValueError:
            # 위기 게시글 차단은 그대로 전파
            raise
        except Exception as ai_error:
            # AI 분석 실패 시에도 게시글 작성은 계속 진행
            logger.warning(f"AI 위기 감지 분석 실패 (게시글 작성은 계속 진행): {ai_error}")
            # 기본값으로 진행 (is_crisis=False)
            is_crisis = False
        
        # 게시글 생성 (AI 분석 실패 여부와 관계없이 진행)
        post = create_post(
            db=db,
            post_data=post_data,
            author_id=author_id,
            is_crisis=is_crisis
        )
        
        # 중간 위험 게시글 탐지 시 관리자 알림 (AI 분석이 성공한 경우에만)
        if crisis_analysis and crisis_analysis.get("level") == "medium":
            try:
                send_admin_alert(post.id, crisis_analysis, post_data.content)
                logger.info(f"중간 위험 게시글 알림: post_id={post.id}, author_id={author_id}")
            except Exception as alert_error:
                logger.warning(f"관리자 알림 발송 실패 (게시글은 정상 작성됨): {alert_error}")
        
        return post
    except ValueError:
        # 위기 게시글 차단은 그대로 전파
        raise
    except Exception as e:
        logger.error(f"게시글 작성 중 오류 발생: author_id={author_id}, error={e}", exc_info=True)
        safe_rollback(db)
        raise


def get_posts_list(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    sort: str = "latest"  # "latest" or "popular"
) -> List[models.Post]:
    """
    게시글 목록 조회
    - category: 필터링 (None이면 전체)
    - sort: 정렬 방식 ("latest" 또는 "popular")
    """
    from app.models import crud
    return crud.get_posts(db, skip=skip, limit=limit, category=category, sort=sort)


def get_post_detail(
    db: Session,
    post_id: int
) -> Optional[models.Post]:
    """게시글 상세 조회"""
    return get_post_by_id(db, post_id)


def send_admin_alert(post_id: Optional[int], crisis_analysis: Dict[str, Any], post_content: str = "") -> None:
    """
    관리자 알림 발송
    - 로그 기반 알림 (실제 운영 시 이메일/슬랙 등으로 확장 가능)
    
    Args:
        post_id: 게시글 ID (None이면 차단된 게시글)
        crisis_analysis: 위기 분석 결과 딕셔너리
        post_content: 게시글 내용
    """
    try:
        level = crisis_analysis.get("level", "unknown")
        detection_method = crisis_analysis.get("detection_method", "unknown")
        
        alert_message = f"""
[관리자 알림] 위기 게시글 감지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
위기 수준: {level.upper()}
감지 방법: {detection_method}
게시글 ID: {post_id if post_id else "차단됨"}
게시글 내용: {post_content[:200]}...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if level == "high":
            logger.critical(alert_message)
            # 고위험: 즉시 조치 필요
            # TODO: 실제 운영 시 이메일/SMS/슬랙 등으로 알림 발송
        elif level == "medium":
            logger.warning(alert_message)
            # 중간 위험: 모니터링 필요
            # TODO: 실제 운영 시 관리자 대시보드에 알림 표시
        
        # 실제 운영 시 여기에 알림 발송 로직 추가
        # 예: 이메일 발송, 슬랙 메시지, SMS 등
        
    except Exception as e:
        logger.error(f"관리자 알림 발송 중 오류 발생: {e}", exc_info=True)

