from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.connection import Base


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
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")


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
    
    # 관계
    bookmarks = relationship("Bookmark", back_populates="welfare", cascade="all, delete-orphan")


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

