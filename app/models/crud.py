from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
import secrets
import string

from app.models import models
from app.models import schema
from app.services.auth_service import get_password_hash


# User CRUD
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """이메일로 사용자 조회"""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schema.UserSignup) -> models.User:
    """새 사용자 생성 (Level 2로 시작)"""
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
) -> models.User:
    """커뮤니티 심사 제출"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    db_user.verification_text = verification_text
    db_user.verification_status = "pending"
    db.commit()
    db.refresh(db_user)
    return db_user


def approve_verification(db: Session, user_id: int) -> models.User:
    """심사 승인 (Level 3 승급)"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    db_user.level = 3
    db_user.verification_status = "approved"
    db.commit()
    db.refresh(db_user)
    return db_user


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
def create_bookmark(db: Session, user_id: int, welfare_id: int) -> models.Bookmark:
    """북마크 생성"""
    # 중복 체크
    existing = db.query(models.Bookmark).filter(
        and_(
            models.Bookmark.user_id == user_id,
            models.Bookmark.welfare_id == welfare_id
        )
    ).first()
    
    if existing:
        return existing
    
    db_bookmark = models.Bookmark(user_id=user_id, welfare_id=welfare_id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


def get_user_bookmarks(db: Session, user_id: int) -> List[models.Bookmark]:
    """사용자의 북마크 목록 조회"""
    return db.query(models.Bookmark).filter(models.Bookmark.user_id == user_id).all()


# Post CRUD
def create_post(
    db: Session,
    post_data: schema.PostCreate,
    author_id: int,
    is_crisis: bool = False
) -> models.Post:
    """게시글 생성"""
    # 익명 ID 생성
    anonymous_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    
    db_post = models.Post(
        **post_data.dict(),
        author_id=author_id,
        anonymous_id=anonymous_id,
        is_crisis=is_crisis,
        crisis_checked=True
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> List[models.Post]:
    """게시글 목록 조회"""
    return db.query(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()


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
    anonymous_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    
    db_comment = models.Comment(
        **comment_data.dict(),
        post_id=post_id,
        author_id=author_id,
        anonymous_id=anonymous_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_post(db: Session, post_id: int) -> List[models.Comment]:
    """게시글의 댓글 목록 조회"""
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

