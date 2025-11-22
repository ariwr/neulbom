from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.models.connection import get_db
from app.models import schema, models
from app.services.chat_service import get_chat_response
from app.services.auth_service import get_optional_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=schema.ChatResponse)
def send_message(
    message_data: schema.ChatMessage,
    response: Response,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user)
):
    """
    AI 챗봇 메시지 전송
    - Level 1 (비회원) 이상 접근 가능
    """
    # UTF-8 인코딩 명시
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    
    user_id = current_user.id if current_user else None
    chat_response = get_chat_response(
        message=message_data.message,
        history=message_data.history,
        user_id=user_id,
        db=db
    )
    return chat_response

