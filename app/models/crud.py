from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Tuple
from datetime import date, datetime
import secrets
import string
import logging

from app.models import models
from app.models import schema
from app.services.auth_service import get_password_hash
from app.utils.db_utils import safe_rollback, safe_commit

logger = logging.getLogger(__name__)


# User CRUD
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """이메일로 사용자 조회"""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schema.UserSignup) -> models.User:
    """
    새 사용자 생성 (Level 2로 시작)
    - 트랜잭션 관리 및 예외 처리 포함
    """
    try:
        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            email=user.email,
            hashed_password=hashed_password,
            level=2  # 회원가입 시 Level 2 부여
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        # DB 제약 조건 위반 (이메일 중복 등)
        db.rollback()
        logger.error(f"사용자 생성 실패 (IntegrityError): {e}")
        # 이메일 중복인지 확인
        if "UNIQUE constraint failed" in str(e) or "unique constraint" in str(e).lower():
            raise ValueError("이미 등록된 이메일입니다.")
        raise ValueError("사용자 생성 중 데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        # 기타 예외 발생 시 롤백
        db.rollback()
        logger.error(f"사용자 생성 실패: {e}", exc_info=True)
        raise ValueError(f"사용자 생성 중 오류가 발생했습니다: {str(e)}")


def update_user_profile(
    db: Session,
    user_id: int,
    profile_update: schema.UserProfileUpdate
) -> models.User:
    """사용자 프로필 업데이트"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    if profile_update.age is not None:
        db_user.age = profile_update.age
    if profile_update.region is not None:
        db_user.region = profile_update.region
    if profile_update.care_target is not None:
        db_user.care_target = profile_update.care_target
    
    db.commit()
    db.refresh(db_user)
    return db_user


def submit_verification(
    db: Session,
    user_id: int,
    verification_text: str
) -> Optional[models.User]:
    """커뮤니티 심사 제출"""
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            return None
        
        db_user.verification_text = verification_text
        db_user.verification_status = "pending"
        safe_commit(db)
        db.refresh(db_user)
        return db_user
    except Exception as e:
        safe_rollback(db)
        logger.error(f"심사 제출 실패: user_id={user_id}, error={e}", exc_info=True)
        raise


def approve_verification(db: Session, user_id: int) -> Optional[models.User]:
    """심사 승인 (Level 3 승급)"""
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            return None
        
        db_user.level = 3
        db_user.verification_status = "approved"
        safe_commit(db)
        db.refresh(db_user)
        return db_user
    except Exception as e:
        safe_rollback(db)
        logger.error(f"심사 승인 실패: user_id={user_id}, error={e}", exc_info=True)
        raise


# Welfare CRUD
def search_welfares(
    db: Session,
    keyword: Optional[str] = None,
    region: Optional[str] = None,
    age: Optional[int] = None,
    care_target: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[models.Welfare]:
    """복지 정보 검색"""
    query = db.query(models.Welfare)
    
    if keyword:
        query = query.filter(
            or_(
                models.Welfare.title.contains(keyword),
                models.Welfare.summary.contains(keyword)
            )
        )
    
    if region:
        query = query.filter(models.Welfare.region.contains(region))
    
    if age:
        query = query.filter(
            or_(
                models.Welfare.age_min.is_(None),
                models.Welfare.age_min <= age
            ),
            or_(
                models.Welfare.age_max.is_(None),
                models.Welfare.age_max >= age
            )
        )
    
    if care_target:
        query = query.filter(models.Welfare.care_target.contains(care_target))
    
    return query.offset(skip).limit(limit).all()


def get_welfare_by_id(db: Session, welfare_id: int) -> Optional[models.Welfare]:
    """복지 정보 ID로 조회"""
    return db.query(models.Welfare).filter(models.Welfare.id == welfare_id).first()


def create_welfare(db: Session, welfare_data: dict) -> models.Welfare:
    """복지 정보 생성"""
    db_welfare = models.Welfare(**welfare_data)
    db.add(db_welfare)
    db.commit()
    db.refresh(db_welfare)
    return db_welfare


def create_or_update_welfare(db: Session, welfare_data: dict) -> models.Welfare:
    """복지 정보 생성 또는 업데이트 (제목 기준 중복 체크)"""
    # 제목으로 기존 항목 찾기
    existing = db.query(models.Welfare).filter(
        models.Welfare.title == welfare_data.get('title')
    ).first()
    
    if existing:
        # 기존 항목 업데이트
        for key, value in welfare_data.items():
            if hasattr(existing, key) and value is not None:
                setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # 새 항목 생성
        return create_welfare(db, welfare_data)


def get_active_welfares(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> List[models.Welfare]:
    """현재 신청 가능한 복지 정보만 조회"""
    today = date.today()
    
    query = db.query(models.Welfare).filter(
        models.Welfare.status == 'active'
    ).filter(
        or_(
            models.Welfare.is_always == True,
            models.Welfare.apply_end >= today,
            models.Welfare.apply_end.is_(None)
        )
    )
    
    return query.order_by(models.Welfare.apply_end.asc()).offset(skip).limit(limit).all()


# Bookmark CRUD
def create_bookmark(db: Session, user_id: int, welfare_id: int) -> Tuple[models.Bookmark, bool]:
    """
    북마크 생성
    - 중복 체크: 이미 북마크된 경우 기존 북마크 반환
    - 반환: (북마크 객체, 새로 생성되었는지 여부)
    """
    # 중복 체크
    existing = db.query(models.Bookmark).filter(
        and_(
            models.Bookmark.user_id == user_id,
            models.Bookmark.welfare_id == welfare_id
        )
    ).first()
    
    if existing:
        # 이미 존재하는 북마크 반환
        return existing, False
    
    # 새 북마크 생성
    db_bookmark = models.Bookmark(user_id=user_id, welfare_id=welfare_id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark, True


def get_user_bookmarks(
    db: Session, 
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[models.Bookmark], int]:
    """
    사용자의 북마크 목록 조회 (welfare 관계 포함)
    - 삭제된 복지 정보는 필터링
    - DB 레벨에서 정렬 및 페이지네이션 처리
    - 반환: (북마크 리스트, 총 개수)
    """
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    
    # 총 개수 조회 (삭제되지 않은 복지 정보만)
    total_count = db.query(func.count(models.Bookmark.id)).join(
        models.Welfare
    ).filter(
        models.Bookmark.user_id == user_id
    ).scalar() or 0
    
    # 북마크 조회 (삭제되지 않은 복지 정보만, 최신순 정렬)
    bookmarks = db.query(models.Bookmark).options(
        joinedload(models.Bookmark.welfare)
    ).join(
        models.Welfare
    ).filter(
        models.Bookmark.user_id == user_id
    ).order_by(
        models.Bookmark.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return bookmarks, total_count


def delete_bookmark(db: Session, user_id: int, welfare_id: int) -> bool:
    """북마크 삭제"""
    bookmark = db.query(models.Bookmark).filter(
        and_(
            models.Bookmark.user_id == user_id,
            models.Bookmark.welfare_id == welfare_id
        )
    ).first()
    
    if not bookmark:
        return False
    
    db.delete(bookmark)
    db.commit()
    return True


# Post CRUD
def create_post(
    db: Session,
    post_data: schema.PostCreate,
    author_id: int,
    is_crisis: bool = False
) -> models.Post:
    """게시글 생성"""
    try:
        # 익명 ID 생성
        anonymous_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        # 카테고리 Enum 변환
        from app.models.models import PostCategory
        category_enum = PostCategory(post_data.category) if post_data.category else PostCategory.FREE
        
        db_post = models.Post(
            title=post_data.title,
            content=post_data.content,
            category=category_enum,
            author_id=author_id,
            anonymous_id=anonymous_id,
            is_crisis=is_crisis,
            crisis_checked=True,
            view_count=0,
            like_count=0
        )
        db.add(db_post)
        safe_commit(db)
        db.refresh(db_post)
        return db_post
    except Exception as e:
        safe_rollback(db)
        logger.error(f"게시글 생성 실패: author_id={author_id}, error={e}", exc_info=True)
        raise


def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    sort: str = "latest"  # "latest" or "popular"
) -> List[models.Post]:
    """
    게시글 목록 조회
    - category: 필터링 (None이면 전체, 'information', 'worry', 'free')
    - sort: 정렬 방식 ("latest" 최신순 또는 "popular" 좋아요순)
    """
    query = db.query(models.Post)
    
    # 카테고리 필터링
    if category:
        query = query.filter(models.Post.category == category)
    
    # 정렬
    if sort == "popular":
        query = query.order_by(models.Post.like_count.desc(), models.Post.created_at.desc())
    else:  # latest
        query = query.order_by(models.Post.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


def get_post_by_id(db: Session, post_id: int) -> Optional[models.Post]:
    """게시글 ID로 조회"""
    return db.query(models.Post).filter(models.Post.id == post_id).first()


# Comment CRUD
def create_comment(
    db: Session,
    comment_data: schema.CommentCreate,
    post_id: int,
    author_id: int
) -> models.Comment:
    """댓글 생성"""
    try:
        anonymous_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        db_comment = models.Comment(
            **comment_data.dict(),
            post_id=post_id,
            author_id=author_id,
            anonymous_id=anonymous_id
        )
        db.add(db_comment)
        safe_commit(db)
        db.refresh(db_comment)
        return db_comment
    except Exception as e:
        safe_rollback(db)
        logger.error(f"댓글 생성 실패: post_id={post_id}, author_id={author_id}, error={e}", exc_info=True)
        raise


def get_comments_by_post(db: Session, post_id: int) -> List[models.Comment]:
    """게시글의 댓글 목록 조회"""
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).order_by(models.Comment.created_at.asc()).all()


def update_post(
    db: Session,
    post_id: int,
    author_id: int,
    post_data: schema.PostCreate
) -> Optional[models.Post]:
    """게시글 수정 (작성자만 수정 가능)"""
    try:
        db_post = db.query(models.Post).filter(
            and_(
                models.Post.id == post_id,
                models.Post.author_id == author_id
            )
        ).first()
        
        if not db_post:
            return None
        
        from app.models.models import PostCategory
        category_enum = PostCategory(post_data.category) if post_data.category else PostCategory.FREE
        
        db_post.title = post_data.title
        db_post.content = post_data.content
        db_post.category = category_enum
        safe_commit(db)
        db.refresh(db_post)
        return db_post
    except Exception as e:
        safe_rollback(db)
        logger.error(f"게시글 수정 실패: post_id={post_id}, author_id={author_id}, error={e}", exc_info=True)
        raise


def delete_post(
    db: Session,
    post_id: int,
    author_id: int
) -> bool:
    """게시글 삭제 (작성자만 삭제 가능)"""
    try:
        db_post = db.query(models.Post).filter(
            and_(
                models.Post.id == post_id,
                models.Post.author_id == author_id
            )
        ).first()
        
        if not db_post:
            return False
        
        db.delete(db_post)
        safe_commit(db)
        return True
    except Exception as e:
        safe_rollback(db)
        logger.error(f"게시글 삭제 실패: post_id={post_id}, author_id={author_id}, error={e}", exc_info=True)
        raise


def get_comment_by_id(db: Session, comment_id: int) -> Optional[models.Comment]:
    """댓글 ID로 조회"""
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()


def update_comment(
    db: Session,
    comment_id: int,
    author_id: int,
    comment_data: schema.CommentCreate
) -> Optional[models.Comment]:
    """댓글 수정 (작성자만 수정 가능)"""
    try:
        db_comment = db.query(models.Comment).filter(
            and_(
                models.Comment.id == comment_id,
                models.Comment.author_id == author_id
            )
        ).first()
        
        if not db_comment:
            return None
        
        db_comment.content = comment_data.content
        safe_commit(db)
        db.refresh(db_comment)
        return db_comment
    except Exception as e:
        safe_rollback(db)
        logger.error(f"댓글 수정 실패: comment_id={comment_id}, author_id={author_id}, error={e}", exc_info=True)
        raise


def delete_comment(
    db: Session,
    comment_id: int,
    author_id: int
) -> bool:
    """댓글 삭제 (작성자만 삭제 가능)"""
    try:
        db_comment = db.query(models.Comment).filter(
            and_(
                models.Comment.id == comment_id,
                models.Comment.author_id == author_id
            )
        ).first()
        
        if not db_comment:
            return False
        
        db.delete(db_comment)
        safe_commit(db)
        return True
    except Exception as e:
        safe_rollback(db)
        logger.error(f"댓글 삭제 실패: comment_id={comment_id}, author_id={author_id}, error={e}", exc_info=True)
        raise


# PostLike CRUD
def toggle_post_like(db: Session, user_id: int, post_id: int) -> Tuple[bool, bool]:
    """
    게시글 좋아요 토글
    - 이미 좋아요를 눌렀으면 취소, 아니면 추가
    - 반환: (좋아요 여부, 새로 추가되었는지 여부)
    """
    try:
        # 기존 좋아요 확인
        existing_like = db.query(models.PostLike).filter(
            and_(
                models.PostLike.user_id == user_id,
                models.PostLike.post_id == post_id
            )
        ).first()
        
        post = get_post_by_id(db, post_id)
        if not post:
            raise ValueError("게시글을 찾을 수 없습니다.")
        
        if existing_like:
            # 좋아요 취소
            db.delete(existing_like)
            post.like_count = max(0, (post.like_count or 0) - 1)
            safe_commit(db)
            return False, False
        else:
            # 중복 체크 (동시성 문제 방지)
            duplicate_check = db.query(models.PostLike).filter(
                and_(
                    models.PostLike.user_id == user_id,
                    models.PostLike.post_id == post_id
                )
            ).first()
            if duplicate_check:
                # 이미 추가된 경우
                return True, False
            
            # 좋아요 추가
            new_like = models.PostLike(user_id=user_id, post_id=post_id)
            db.add(new_like)
            post.like_count = (post.like_count or 0) + 1
            safe_commit(db)
            return True, True
    except IntegrityError as e:
        # 중복 좋아요 시도 시 무시
        safe_rollback(db)
        logger.warning(f"중복 좋아요 시도: user_id={user_id}, post_id={post_id}")
        # 이미 좋아요가 있는 것으로 간주
        return True, False
    except Exception as e:
        safe_rollback(db)
        logger.error(f"좋아요 토글 실패: user_id={user_id}, post_id={post_id}, error={e}", exc_info=True)
        raise


def check_post_liked(db: Session, user_id: int, post_id: int) -> bool:
    """사용자가 게시글에 좋아요를 눌렀는지 확인"""
    like = db.query(models.PostLike).filter(
        and_(
            models.PostLike.user_id == user_id,
            models.PostLike.post_id == post_id
        )
    ).first()
    return like is not None


# PostBookmark CRUD
def toggle_post_bookmark(db: Session, user_id: int, post_id: int) -> Tuple[models.PostBookmark, bool]:
    """
    게시글 북마크 토글
    - 이미 북마크했으면 삭제, 아니면 추가
    - 반환: (북마크 객체 또는 None, 새로 추가되었는지 여부)
    """
    try:
        # 기존 북마크 확인
        existing_bookmark = db.query(models.PostBookmark).filter(
            and_(
                models.PostBookmark.user_id == user_id,
                models.PostBookmark.post_id == post_id
            )
        ).first()
        
        if existing_bookmark:
            # 북마크 삭제
            db.delete(existing_bookmark)
            safe_commit(db)
            return None, False
        else:
            # 북마크 추가
            new_bookmark = models.PostBookmark(user_id=user_id, post_id=post_id)
            db.add(new_bookmark)
            safe_commit(db)
            db.refresh(new_bookmark)
            return new_bookmark, True
    except Exception as e:
        safe_rollback(db)
        logger.error(f"북마크 토글 실패: user_id={user_id}, post_id={post_id}, error={e}", exc_info=True)
        raise


def check_post_bookmarked(db: Session, user_id: int, post_id: int) -> bool:
    """사용자가 게시글을 북마크했는지 확인"""
    bookmark = db.query(models.PostBookmark).filter(
        and_(
            models.PostBookmark.user_id == user_id,
            models.PostBookmark.post_id == post_id
        )
    ).first()
    return bookmark is not None


def get_user_post_bookmarks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[models.PostBookmark], int]:
    """
    사용자의 게시글 북마크 목록 조회
    - 반환: (북마크 리스트, 총 개수)
    """
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    
    # 총 개수 조회
    total_count = db.query(func.count(models.PostBookmark.id)).filter(
        models.PostBookmark.user_id == user_id
    ).scalar() or 0
    
    # 북마크 조회 (최신순 정렬)
    bookmarks = db.query(models.PostBookmark).options(
        joinedload(models.PostBookmark.post)
    ).filter(
        models.PostBookmark.user_id == user_id
    ).order_by(
        models.PostBookmark.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return bookmarks, total_count


# ChatRoom CRUD
def create_chat_room(db: Session, user_id: int, title: Optional[str] = None) -> models.ChatRoom:
    """채팅방 생성"""
    try:
        if not title:
            title = f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        chat_room = models.ChatRoom(
            user_id=user_id,
            title=title,
            is_active=True
        )
        db.add(chat_room)
        safe_commit(db)
        db.refresh(chat_room)
        return chat_room
    except Exception as e:
        safe_rollback(db)
        logger.error(f"채팅방 생성 실패: user_id={user_id}, error={e}", exc_info=True)
        raise


def get_user_chat_rooms(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[models.ChatRoom], int]:
    """
    사용자의 채팅방 목록 조회
    - 반환: (채팅방 리스트, 총 개수)
    """
    from sqlalchemy import func
    
    # 총 개수 조회 (활성화된 채팅방만)
    total_count = db.query(func.count(models.ChatRoom.id)).filter(
        and_(
            models.ChatRoom.user_id == user_id,
            models.ChatRoom.is_active == True
        )
    ).scalar() or 0
    
    # 채팅방 조회 (최신순 정렬)
    chat_rooms = db.query(models.ChatRoom).filter(
        and_(
            models.ChatRoom.user_id == user_id,
            models.ChatRoom.is_active == True
        )
    ).order_by(
        models.ChatRoom.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return chat_rooms, total_count


def get_chat_room_by_id(db: Session, room_id: int, user_id: int) -> Optional[models.ChatRoom]:
    """채팅방 조회 (본인 것만)"""
    return db.query(models.ChatRoom).filter(
        and_(
            models.ChatRoom.id == room_id,
            models.ChatRoom.user_id == user_id,
            models.ChatRoom.is_active == True
        )
    ).first()


def update_chat_room_title(db: Session, room_id: int, user_id: int, title: str) -> Optional[models.ChatRoom]:
    """채팅방 제목 수정"""
    try:
        chat_room = get_chat_room_by_id(db, room_id, user_id)
        if not chat_room:
            return None
        
        chat_room.title = title
        safe_commit(db)
        db.refresh(chat_room)
        return chat_room
    except Exception as e:
        safe_rollback(db)
        logger.error(f"채팅방 제목 수정 실패: room_id={room_id}, user_id={user_id}, error={e}", exc_info=True)
        raise


def delete_chat_room(db: Session, room_id: int, user_id: int) -> bool:
    """채팅방 삭제 (is_active=False 처리)"""
    try:
        chat_room = get_chat_room_by_id(db, room_id, user_id)
        if not chat_room:
            return False
        
        chat_room.is_active = False
        safe_commit(db)
        return True
    except Exception as e:
        safe_rollback(db)
        logger.error(f"채팅방 삭제 실패: room_id={room_id}, user_id={user_id}, error={e}", exc_info=True)
        raise


# WelfareViewLog CRUD
def create_welfare_view_log(db: Session, user_id: int, welfare_id: int) -> models.WelfareViewLog:
    """복지 정보 열람 기록 생성"""
    try:
        # 중복 체크 (같은 사용자가 같은 복지 정보를 여러 번 조회해도 기록은 남김)
        view_log = models.WelfareViewLog(
            user_id=user_id,
            welfare_id=welfare_id
        )
        db.add(view_log)
        
        # 복지 정보의 조회수 증가
        welfare = get_welfare_by_id(db, welfare_id)
        if welfare:
            welfare.view_count = (welfare.view_count or 0) + 1
        
        safe_commit(db)
        db.refresh(view_log)
        return view_log
    except Exception as e:
        safe_rollback(db)
        logger.error(f"복지 정보 열람 기록 생성 실패: user_id={user_id}, welfare_id={welfare_id}, error={e}", exc_info=True)
        raise


def get_user_recent_welfare_views(
    db: Session,
    user_id: int,
    limit: int = 10
) -> List[models.WelfareViewLog]:
    """
    사용자의 최근 본 복지 정보 조회
    - 중복 제거 (같은 복지 정보는 최신 것만)
    """
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    
    # 최근 열람 기록 조회 (중복 제거)
    subquery = db.query(
        models.WelfareViewLog.welfare_id,
        func.max(models.WelfareViewLog.viewed_at).label('max_viewed_at')
    ).filter(
        models.WelfareViewLog.user_id == user_id
    ).group_by(
        models.WelfareViewLog.welfare_id
    ).subquery()
    
    view_logs = db.query(models.WelfareViewLog).options(
        joinedload(models.WelfareViewLog.welfare)
    ).join(
        subquery,
        and_(
            models.WelfareViewLog.welfare_id == subquery.c.welfare_id,
            models.WelfareViewLog.viewed_at == subquery.c.max_viewed_at
        )
    ).filter(
        models.WelfareViewLog.user_id == user_id
    ).order_by(
        models.WelfareViewLog.viewed_at.desc()
    ).limit(limit).all()
    
    return view_logs


def get_popular_welfares(
    db: Session,
    limit: int = 10
) -> List[models.Welfare]:
    """
    인기 복지 정보 조회 (조회수 기준)
    """
    return db.query(models.Welfare).order_by(
        models.Welfare.view_count.desc()
    ).limit(limit).all()
