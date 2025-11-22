"""
채팅 서비스
- 대화 내역 저장
- 위기 감지 결과에 따른 분기 처리
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models import schema
from app.ai_core.llm_client import llm_client
from app.ai_core.prompts import CHATBOT_SYSTEM_PROMPT, CBT_PROMPT
from app.ai_core.safety_guard import detect_crisis, analyze_crisis_level, get_crisis_info


def get_chat_response(
    message: str,
    history: Optional[List[Dict]] = None,
    user_id: Optional[int] = None,
    db: Optional[Session] = None,
    use_llm_detection: bool = True
) -> schema.ChatResponse:
    """
    AI 챗봇 응답 생성
    - 공감형 대화 생성
    - 하이브리드 위기 감지 시스템 활용 (Rule-based + LLM)
    - 위기 수준에 따른 차별화된 응답
    
    Args:
        message: 사용자 메시지
        history: 대화 히스토리
        user_id: 사용자 ID
        db: 데이터베이스 세션
        use_llm_detection: LLM 기반 위기 감지 사용 여부
    """
    if history is None:
        history = []
    
    # 하이브리드 위기 감지 (1차: 키워드, 2차: LLM 감정 분석)
    crisis_analysis = analyze_crisis_level(message, use_llm=use_llm_detection)
    is_crisis = crisis_analysis.get("is_crisis", False)
    crisis_level = crisis_analysis.get("level", "low")
    detection_method = crisis_analysis.get("detection_method")
    
    if is_crisis:
        # 위기 수준에 따른 차별화된 응답
        if crisis_level == "high":
            reply = "지금 정말 힘든 상황이시군요. 혼자 견디기 어려운 상황이라면 즉시 전문가의 도움이 필요해요. 보건복지콜센터(129)로 연락하시거나, 주변에 도움을 요청하는 것도 용기 있는 행동이에요. 당신은 혼자가 아니에요."
        elif crisis_level == "medium":
            reply = "지금 많이 힘드시는 것 같아요. 이런 감정을 느끼는 것은 당연해요. 혼자 견디기 어려운 상황이라면 전문가의 도움이 필요할 수 있어요. 주변에 도움을 요청하는 것도 용기 있는 행동이에요."
        else:
            reply = "지금 힘든 감정을 느끼고 계시는군요. 그런 감정을 공유해주셔서 감사해요. 더 이야기해보실 수 있을까요?"
        
        crisis_info = crisis_analysis.get("info")
    else:
        # 일반 대화 응답
        reply = generate_empathic_response(message, history)
        crisis_info = None
    
    # TODO: 대화 내역 DB 저장
    # if db and user_id:
    #     save_chat_log(db, user_id, message, reply, is_crisis, crisis_level, detection_method)
    
    return schema.ChatResponse(
        reply=reply,
        is_crisis=is_crisis,
        crisis_info=crisis_info
    )


def generate_empathic_response(message: str, history: List[Dict]) -> str:
    """
    공감형 응답 생성
    - LLM API 통합
    - 긍정 심리학 기반 CBT 유도 프롬프트 적용
    """
    # CBT 프롬프트 생성
    prompt = CBT_PROMPT.format(
        message=message,
        history=history
    )
    
    # LLM API 호출
    reply = llm_client.generate_chat_response(
        message=message,
        history=history,
        system_prompt=CHATBOT_SYSTEM_PROMPT
    )
    
    # 임시 응답 (LLM API 미통합 시)
    if reply == "안녕하세요. 늘봄입니다. 어떻게 도와드릴까요?":
        # 간단한 키워드 기반 응답
        if any(word in message for word in ["힘들", "어려", "스트레스"]):
            return "지금 힘든 상황이시군요. 그런 감정을 느끼는 것은 당연해요. 혹시 이 상황에서 작은 변화를 만들어볼 수 있는 부분이 있을까요?"
        elif any(word in message for word in ["고마", "감사", "좋"]):
            return "좋은 감정을 느끼고 계시는군요! 그런 긍정적인 순간들을 기록해보시는 것도 좋을 것 같아요."
        else:
            return "말씀해주셔서 감사해요. 더 자세히 들려주실 수 있나요?"
    
    return reply


def save_chat_log(
    db: Session,
    user_id: int,
    user_message: str,
    bot_reply: str,
    is_crisis: bool
):
    """
    대화 내역 저장
    - TODO: ChatLog 모델 생성 및 저장 로직 구현
    """
    # TODO: ChatLog 모델 생성
    # chat_log = ChatLog(
    #     user_id=user_id,
    #     user_message=user_message,
    #     bot_reply=bot_reply,
    #     is_crisis=is_crisis
    # )
    # db.add(chat_log)
    # db.commit()
    pass

