from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date


# Auth Schemas
class UserSignup(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    email: str
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


class WelfareSearchResponse(BaseModel):
    items: List[WelfareItem]
    total: int


# Community Schemas
class VerificationRequest(BaseModel):
    text: str  # 심사 제출 텍스트


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    anonymous_id: Optional[str] = None
    created_at: datetime
    comment_count: int = 0
    
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

