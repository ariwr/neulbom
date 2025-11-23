from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date


# Auth Schemas
class UserSignup(BaseModel):
    name: str  # 이름
    email: EmailStr
    password: str
    password_confirm: str  # 비밀번호 확인
    age: Optional[int] = None  # 나이
    region: Optional[str] = None  # 거주 지역
    care_target: Optional[str] = None  # 돌봄 대상


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    age: Optional[int] = None
    region: Optional[str] = None
    care_target: Optional[str] = None
    level: int
    verification_status: str
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    age: Optional[int] = None
    region: Optional[str] = None
    care_target: Optional[str] = None


# Chat Schemas
class ChatMessage(BaseModel):
    message: str
    history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    reply: str
    is_crisis: bool = False
    crisis_info: Optional[dict] = None
    room_id: Optional[int] = None  # 새 채팅방 생성 시 room_id 반환


# Welfare Schemas
class WelfareItem(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    source_link: Optional[str] = None
    region: Optional[str] = None
    apply_start: Optional[date] = None
    apply_end: Optional[date] = None
    is_always: bool = False
    status: str = "active"
    
    class Config:
        from_attributes = True


class WelfareDetail(BaseModel):
    """복지 정보 상세 조회용 스키마"""
    id: int
    title: str
    summary: Optional[str] = None
    full_text: Optional[str] = None  # 서비스 요약 (full_text에서 추출)
    source_link: Optional[str] = None
    region: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    care_target: Optional[str] = None
    apply_start: Optional[date] = None
    apply_end: Optional[date] = None
    is_always: bool = False
    status: str = "active"
    category: Optional[str] = None
    
    class Config:
        from_attributes = True


class WelfareSearchResponse(BaseModel):
    items: List[WelfareItem]
    total: int


# Community Schemas
class VerificationRequest(BaseModel):
    text: str  # 심사 제출 텍스트


class PostCreate(BaseModel):
    title: str
    content: str
    category: str  # 'information', 'worry', 'free'


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    view_count: int = 0
    like_count: int = 0
    anonymous_id: Optional[str] = None
    created_at: datetime
    comment_count: int = 0
    is_liked: bool = False  # 현재 사용자가 좋아요를 눌렀는지 여부
    is_bookmarked: bool = False  # 현재 사용자가 북마크했는지 여부
    
    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    anonymous_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Bookmark Schemas
class BookmarkItem(BaseModel):
    id: int
    welfare_id: int
    welfare: WelfareItem
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookmarkListResponse(BaseModel):
    """북마크 목록 응답"""
    items: List[BookmarkItem]
    total: int
    skip: int
    limit: int


# Chat Room Schemas
class ChatRoomCreate(BaseModel):
    title: Optional[str] = None  # 제목이 없으면 첫 메시지로 자동 생성


class ChatRoomUpdate(BaseModel):
    title: str


class ChatRoomResponse(BaseModel):
    id: int
    title: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChatRoomListResponse(BaseModel):
    """채팅방 목록 응답"""
    items: List[ChatRoomResponse]
    total: int


# Post Bookmark Schemas
class PostBookmarkItem(BaseModel):
    id: int
    post_id: int
    post: PostResponse
    created_at: datetime
    
    class Config:
        from_attributes = True


class PostBookmarkListResponse(BaseModel):
    """게시글 북마크 목록 응답"""
    items: List[PostBookmarkItem]
    total: int
    skip: int
    limit: int