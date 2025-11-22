from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.connection import Base
import enum


class PostCategory(str, enum.Enum):
    """게시글 카테고리"""
    INFORMATION = "information"  # 정보공유
    WORRY = "worry"  # 고민상담
    FREE = "free"  # 자유


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # 프로필 정보
    age = Column(Integer, nullable=True)
    region = Column(String, nullable=True)  # 거주 지역
    care_target = Column(String, nullable=True)  # 돌봄 대상 (예: "청소년", "노인", "장애인")
    
    # 등급 시스템 (1: 비회원, 2: 일반회원, 3: 검증회원)
    level = Column(Integer, default=1, nullable=False)
    
    # 커뮤니티 심사 상태
    verification_status = Column(String, default="pending")  # pending, approved, rejected
    verification_text = Column(Text, nullable=True)  # 심사 제출 텍스트
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    post_bookmarks = relationship("PostBookmark", back_populates="user", cascade="all, delete-orphan")
    post_likes = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    chat_rooms = relationship("ChatRoom", back_populates="user", cascade="all, delete-orphan")
    welfare_view_logs = relationship("WelfareViewLog", back_populates="user", cascade="all, delete-orphan")


class Welfare(Base):
    """복지 정보 모델"""
    __tablename__ = "welfares"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    summary = Column(Text, nullable=True)  # LLM 요약본
    full_text = Column(Text, nullable=True)  # 원본 텍스트
    source_link = Column(String, nullable=True)
    
    # 필터링 정보
    region = Column(String, nullable=True, index=True)
    age_min = Column(Integer, nullable=True)
    age_max = Column(Integer, nullable=True)
    care_target = Column(String, nullable=True)
    
    # 신청기간 정보 (복지로 크롤링용)
    apply_start = Column(Date, nullable=True)  # 신청 시작일
    apply_end = Column(Date, nullable=True)  # 신청 종료일
    is_always = Column(Boolean, default=False)  # 상시 신청 여부
    status = Column(String, default="active")  # 'active'(진행중), 'closed'(마감), 'expired'(만료)
    
    # 데이터 분류 (RAG 품질 향상용)
    category = Column(String, nullable=True, index=True)  # 'SERVICE'(실제 복지), 'NEWS'(뉴스/단순정보), 'UNCERTAIN'(미분류)
    
    # RAG 관련
    embedding = Column(JSON, nullable=True)  # 벡터 임베딩 (JSON 배열)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 조회수 (복지 정보 열람 기록용)
    view_count = Column(Integer, default=0, nullable=False)
    
    # 관계
    bookmarks = relationship("Bookmark", back_populates="welfare", cascade="all, delete-orphan")
    view_logs = relationship("WelfareViewLog", back_populates="welfare", cascade="all, delete-orphan")


class Bookmark(Base):
    """북마크 모델"""
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    welfare_id = Column(Integer, ForeignKey("welfares.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User", back_populates="bookmarks")
    welfare = relationship("Welfare", back_populates="bookmarks")


class Post(Base):
    """커뮤니티 게시글 모델"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    # 카테고리 (정보공유/고민상담/자유)
    category = Column(SQLEnum(PostCategory), nullable=False, default=PostCategory.FREE, index=True)
    
    # 조회수 및 좋아요 수
    view_count = Column(Integer, default=0, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    
    # AI 모니터링
    is_crisis = Column(Boolean, default=False)
    crisis_checked = Column(Boolean, default=False)
    
    # 익명 처리
    anonymous_id = Column(String, nullable=True)  # 익명 식별자
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    bookmarks = relationship("PostBookmark", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    """댓글 모델"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    
    # 익명 처리
    anonymous_id = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    post = relationship("Post", back_populates="comments")


class PostLike(Base):
    """게시글 좋아요 모델 (N:M 관계)"""
    __tablename__ = "post_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User", back_populates="post_likes")
    post = relationship("Post", back_populates="likes")
    
    # 복합 유니크 제약조건 (중복 좋아요 방지)
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class PostBookmark(Base):
    """게시글 북마크 모델"""
    __tablename__ = "post_bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User", back_populates="post_bookmarks")
    post = relationship("Post", back_populates="bookmarks")


class ChatRoom(Base):
    """채팅방 모델"""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)  # 대화방 제목
    is_active = Column(Boolean, default=True, nullable=False)  # 삭제 여부
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    user = relationship("User", back_populates="chat_rooms")
    # TODO: ChatLog 모델과의 관계 추가 (필요시)


class WelfareViewLog(Base):
    """복지 정보 열람 기록 모델"""
    __tablename__ = "welfare_view_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    welfare_id = Column(Integer, ForeignKey("welfares.id"), nullable=False)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # 관계
    user = relationship("User", back_populates="welfare_view_logs")
    welfare = relationship("Welfare", back_populates="view_logs")

