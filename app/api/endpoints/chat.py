from fastapi import APIRouter, Depends, Response, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from app.models.connection import get_db
from app.models import schema, models
from app.models.crud import (
    create_chat_room, get_user_chat_rooms, get_chat_room_by_id,
    update_chat_room_title, delete_chat_room, get_chat_logs_by_room
)
from app.services.chat_service import get_chat_response, save_chat_log
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
    import logging
    logger = logging.getLogger(__name__)
    
    # UTF-8 인코딩 명시
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    
    user_id = current_user.id if current_user else None
    
    # 로그인한 사용자의 경우 채팅방 관리 및 기록 저장
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
    
    # 히스토리 가져오기: DB에서 가져오거나 프론트엔드에서 전달받은 히스토리 사용
    history = message_data.history or []
    
    # DB에서 히스토리 가져오기 (room_id가 있고 DB에 기록이 있는 경우)
    if chat_room:
        from app.models.crud import get_chat_logs_by_room
        db_history = get_chat_logs_by_room(db, chat_room.id)
        if db_history:
            # DB 히스토리를 사용 (더 정확함)
            history = db_history
            logger.debug(f"DB에서 히스토리 가져옴: {len(history)}개 메시지")
        else:
            # DB에 히스토리가 없으면 프론트엔드에서 전달받은 히스토리 사용
            logger.debug(f"프론트엔드에서 전달받은 히스토리 사용: {len(history)}개 메시지")
    else:
        # 비회원이거나 새 채팅방인 경우 프론트엔드 히스토리 사용
        logger.debug(f"프론트엔드 히스토리 사용: {len(history)}개 메시지")
    
    logger.info(f"챗봇 응답 생성 시작: message_length={len(message_data.message)}, history_count={len(history)}")
    
    chat_response = get_chat_response(
        message=message_data.message,
        history=history,
        user_id=user_id,
        db=db
    )
    
    # 채팅 기록 저장 (로그인한 사용자이고 채팅방이 있는 경우만)
    if user_id and chat_room:
        save_chat_log(
            db=db,
            room_id=chat_room.id,
            user_message=message_data.message,
            bot_reply=chat_response.reply,
            is_crisis=chat_response.is_crisis
        )
    
    # room_id를 응답에 포함
    response_dict = chat_response.dict()
    if chat_room:
        response_dict["room_id"] = chat_room.id
    
    logger.info(f"챗봇 응답 완료: reply_length={len(chat_response.reply)}, is_crisis={chat_response.is_crisis}, room_id={chat_room.id if chat_room else None}")
    
    return response_dict


@router.post("/rooms", response_model=schema.ChatRoomResponse)
def create_room(
    room_data: schema.ChatRoomCreate,
    current_user: models.User = Depends(get_optional_user),  # 로그인한 사용자 누구나
    db: Session = Depends(get_db)
):
    """
    새 채팅방 생성
    - 로그인한 사용자만 접근 가능 (Level 제한 없음)
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
        
    chat_room = create_chat_room(db, current_user.id, room_data.title)
    return chat_room


@router.get("/rooms", response_model=schema.ChatRoomListResponse)
def get_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(get_optional_user),  # 로그인한 사용자 누구나
    db: Session = Depends(get_db)
):
    """
    나의 채팅방 목록 조회
    - 로그인한 사용자만 접근 가능
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    chat_rooms, total = get_user_chat_rooms(db, current_user.id, skip=skip, limit=limit)
    return schema.ChatRoomListResponse(
        items=chat_rooms,
        total=total
    )


@router.put("/rooms/{room_id}", response_model=schema.ChatRoomResponse)
def update_room(
    room_id: int,
    room_data: schema.ChatRoomUpdate,
    current_user: models.User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    채팅방 제목 수정
    - 본인의 채팅방만 수정 가능
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    chat_room = update_chat_room_title(db, room_id, current_user.id, room_data.title)
    if not chat_room:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
    return chat_room


@router.delete("/rooms/{room_id}")
def delete_room(
    room_id: int,
    current_user: models.User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    채팅방 삭제
    - 본인의 채팅방만 삭제 가능
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    success = delete_chat_room(db, room_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="채팅방을 찾을 수 없습니다.")
    return {"message": "채팅방이 삭제되었습니다."}

