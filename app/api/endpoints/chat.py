from fastapi import APIRouter, Depends, Response, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from app.models.connection import get_db
from app.models import schema, models
from app.models.crud import (
    create_chat_room, get_user_chat_rooms, get_chat_room_by_id,
    update_chat_room_title, delete_chat_room
)
from app.services.chat_service import get_chat_response
from app.services.auth_service import get_optional_user, require_level

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=schema.ChatResponse)
def send_message(
    message_data: schema.ChatMessage,
    response: Response,
    room_id: Optional[int] = Query(None, description="채팅방 ID (없으면 새로 생성)"),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user)
):
    """
    AI 챗봇 메시지 전송
    - Level 1 (비회원) 이상 접근 가능
    - room_id가 없으면 새 채팅방 생성
    """
    # UTF-8 인코딩 명시
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    
    user_id = current_user.id if current_user else None
    
    # 로그인한 사용자의 경우 채팅방 관리
    chat_room = None
    if user_id:
        if room_id:
            chat_room = get_chat_room_by_id(db, room_id, user_id)
            if not chat_room:
                raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
        else:
            # 새 채팅방 생성 (첫 메시지로 제목 자동 생성)
            title = message_data.message[:30] + "..." if len(message_data.message) > 30 else message_data.message
            chat_room = create_chat_room(db, user_id, title)
    
    chat_response = get_chat_response(
        message=message_data.message,
        history=message_data.history,
        user_id=user_id,
        db=db
    )
    return chat_response


@router.post("/rooms", response_model=schema.ChatRoomResponse)
def create_room(
    room_data: schema.ChatRoomCreate,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    새 채팅방 생성
    - Level 2 (일반 회원) 이상 접근 가능
    """
    chat_room = create_chat_room(db, current_user.id, room_data.title)
    return chat_room


@router.get("/rooms", response_model=schema.ChatRoomListResponse)
def get_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    나의 채팅방 목록 조회
    - Level 2 (일반 회원) 이상 접근 가능
    """
    chat_rooms, total = get_user_chat_rooms(db, current_user.id, skip=skip, limit=limit)
    return schema.ChatRoomListResponse(
        items=chat_rooms,
        total=total
    )


@router.put("/rooms/{room_id}", response_model=schema.ChatRoomResponse)
def update_room(
    room_id: int,
    room_data: schema.ChatRoomUpdate,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    채팅방 제목 수정
    - Level 2 (일반 회원) 이상 접근 가능
    """
    chat_room = update_chat_room_title(db, room_id, current_user.id, room_data.title)
    if not chat_room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
    return chat_room


@router.delete("/rooms/{room_id}")
def delete_room(
    room_id: int,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    채팅방 삭제
    - Level 2 (일반 회원) 이상 접근 가능
    """
    success = delete_chat_room(db, room_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
    return {"message": "채팅방이 삭제되었습니다."}

