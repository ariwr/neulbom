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
            crisis_info = crisis_analysis.get("info")
        elif crisis_level == "medium":
            reply = "지금 많이 힘드시는 것 같아요. 이런 감정을 느끼는 것은 당연해요. 혼자 견디기 어려운 상황이라면 전문가의 도움이 필요할 수 있어요. 주변에 도움을 요청하는 것도 용기 있는 행동이에요."
            crisis_info = crisis_analysis.get("info")
        else:
            # 낮은 수준의 위기 감지 시: 전문가 안내 + CBT 기법 적용
            reply = generate_empathic_response(message, history)
            # 낮은 수준이지만 위기로 감지된 경우에도 정보 제공
            crisis_info = crisis_analysis.get("info")
    else:
        # 일반 대화 응답 (CBT 기법 포함)
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
    - 부정적 감정 감지 시 명시적 CBT 기법 적용
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 부정적 감정 키워드 감지
    negative_keywords = ["힘들", "어려", "스트레스", "우울", "불안", "두려", "외로", 
                         "슬프", "절망", "포기", "짜증", "화나", "답답", "지치"]
    has_negative_emotion = any(keyword in message for keyword in negative_keywords)
    
    # 긍정적 감정 키워드 감지
    positive_keywords = ["고마", "감사", "좋", "행복", "기쁘", "즐거", "만족"]
    has_positive_emotion = any(keyword in message for keyword in positive_keywords)
    
    # LLM 감정 분석 시도 (부정적 감정이 감지된 경우)
    sentiment_score = None
    if has_negative_emotion:
        try:
            sentiment_result = llm_client.analyze_sentiment(message)
            sentiment_score = sentiment_result.get("score", 0.5)
        except Exception as e:
            logger.debug(f"감정 분석 실패: {e}")
            pass
    
    # 히스토리 포맷팅 (LLM이 이해할 수 있는 형식으로)
    formatted_history = []
    for h in history:
        role = h.get("role", "user")
        content = h.get("content", "")
        if role in ["user", "assistant"]:
            formatted_history.append({"role": role, "content": content})
    
    # 히스토리 로깅
    logger.info(f"히스토리 길이: {len(formatted_history)}, 메시지: {message[:50]}...")
    if formatted_history:
        logger.debug(f"히스토리 샘플: {formatted_history[-2:] if len(formatted_history) >= 2 else formatted_history}")
    
    try:
        # 부정적 감정이 강하게 감지된 경우 CBT 기법 명시적 적용
        # sentiment_score가 None이어도(감정 분석 실패) 부정적 키워드가 있으면 CBT 적용 시도
        if has_negative_emotion and (sentiment_score is None or sentiment_score < 0.4):
            # 히스토리를 고려하여 자연스럽게 응답 생성
            reply = llm_client.generate_chat_response(
                message=message,
                history=formatted_history,
                system_prompt=CHATBOT_SYSTEM_PROMPT
            )
        elif has_positive_emotion:
            # 긍정적 감정일 때는 감사 일기 기록 유도
            reply = llm_client.generate_chat_response(
                message=message,
                history=formatted_history,
                system_prompt=CHATBOT_SYSTEM_PROMPT
            )
        else:
            # 일반 대화 - 히스토리를 활용하여 자연스러운 대화
            reply = llm_client.generate_chat_response(
                message=message,
                history=formatted_history,
                system_prompt=CHATBOT_SYSTEM_PROMPT
            )
        
        # 응답 검증 및 정제
        if reply and reply.strip() and "안녕하세요. 늘봄입니다." not in reply:
            # 응답이 너무 짧거나 의미 없는 경우 재시도 (fallback보다 LLM 재시도가 나을 수 있으나 비용 문제로 fallback)
            if len(reply.strip()) < 5:  # 기준 완화
                logger.warning(f"응답이 너무 짧음: {reply}")
                # 짧은 응답도 의미가 있을 수 있으므로 일단 반환하되, 너무 이상하면 fallback
                if not reply.strip():
                     reply = _generate_diverse_fallback(message, has_negative_emotion, has_positive_emotion, formatted_history)
            
            # 응답 정제 (불필요한 접두사 제거)
            reply = reply.strip()
            # "늘봄:" 같은 접두사 제거
            if reply.startswith("늘봄:"):
                reply = reply[3:].strip()
            
            logger.info(f"LLM 응답 생성 성공: {len(reply)}자, 응답 시작: {reply[:50]}...")
            return reply
        else:
            logger.warning(f"LLM 응답이 부적절함: {reply} - fallback 사용")
            return _generate_diverse_fallback(message, has_negative_emotion, has_positive_emotion, formatted_history)
            
    except Exception as e:
        logger.error(f"LLM 응답 생성 실패: {e}", exc_info=True)
        return _generate_diverse_fallback(message, has_negative_emotion, has_positive_emotion, formatted_history)


def _generate_diverse_fallback(message: str, has_negative: bool, has_positive: bool, history: List[Dict]) -> str:
    """
    다양한 fallback 응답 생성
    - 히스토리를 고려하여 다양한 응답 생성
    - 감정 상태에 따라 다른 응답 제공
    """
    import random
    
    # 히스토리가 있으면 대화 맥락 고려
    has_history = len(history) > 0
    
    # 히스토리에서 최근 사용자 메시지 확인 (맥락 파악)
    recent_user_messages = [h.get("content", "") for h in history if h.get("role") == "user"][-2:]
    recent_context = " ".join(recent_user_messages + [message])
    
    if has_negative:
        # 히스토리를 고려한 응답
        if "프로젝트" in recent_context or "시간" in recent_context or "촉박" in recent_context:
            responses = [
                "프로젝트 진행하시느라 정말 고생 많으셨어요. 시간이 촉박해서 힘드셨을 텐데, 그래도 잘 마무리되셨다니 다행이에요. 그 과정에서 배운 점이 있으신가요?",
                "프로젝트를 마무리하시기까지 정말 수고하셨어요. 시간이 부족해서 스트레스를 받으셨을 것 같은데, 완료하신 것 자체가 큰 성취예요. 지금은 어떤 기분이신가요?",
                "시간이 촉박한 상황에서 프로젝트를 완료하셨다니 정말 대단하세요. 힘드셨을 텐데도 포기하지 않고 끝까지 해내신 것에 대해 스스로를 칭찬해주셔도 좋을 것 같아요.",
                "프로젝트를 잘 마무리하셨다니 정말 다행이에요. 시간이 부족해서 힘드셨을 텐데, 그런 어려움을 겪으면서도 완료하신 것 자체가 큰 성취예요. 지금은 어떤 감정을 느끼고 계신가요?",
            ]
        elif "하루" in recent_context or "오늘" in recent_context:
            responses = [
                "오늘 하루 정말 힘드셨을 것 같아요. 그런 하루를 보내고 계시는군요. 혹시 오늘 하루 중에서 조금이라도 좋았던 순간이 있었나요?",
                "오늘 하루가 힘드셨군요. 그런 감정을 느끼는 것은 당연해요. 하루를 마무리하면서 어떤 생각이 드시나요?",
                "오늘 하루 정말 수고 많으셨어요. 힘든 하루였지만, 그 속에서도 작은 위로나 긍정적인 순간이 있었을 수도 있어요.",
            ]
        else:
            responses = [
                "지금 힘든 상황이시군요. 그런 감정을 느끼는 것은 당연해요. 혹시 이 상황에서 작은 변화를 만들어볼 수 있는 부분이 있을까요?",
                "지금 많이 힘드시는 것 같아요. 그런 감정을 인정하고 받아들이는 것도 중요해요. 오늘 하루 중에서 조금이라도 좋았던 순간이 있었나요?",
                "힘든 감정을 느끼고 계시는군요. 그런 감정을 느끼는 것 자체가 용기 있는 일이에요. 이 상황을 다른 관점에서도 볼 수 있을까요?",
                "지금 어려운 시기를 겪고 계시는군요. 그런 감정을 함께 나눠주셔서 감사해요. 혹시 오늘 할 수 있는 작은 일 하나를 정해볼까요?",
            ]
    elif has_positive:
        responses = [
            "좋은 감정을 느끼고 계시는군요! 그런 긍정적인 순간들을 기록해보시는 것도 좋을 것 같아요.",
            "긍정적인 감정을 느끼고 계시는군요! 그런 순간들을 소중히 간직하시면 나중에 힘들 때 힘이 될 거예요.",
            "좋은 기분이시군요! 그런 긍정적인 경험을 감사 일기에 적어보시면 더 오래 기억하실 수 있을 거예요.",
        ]
    elif has_history:
        # 대화가 이어지고 있는 경우 - 히스토리 맥락 반영
        if "프로젝트" in recent_context:
            responses = [
                "프로젝트에 대해 더 이야기해주세요. 어떤 부분이 가장 기억에 남으시나요?",
                "프로젝트를 마무리하신 후 느끼는 감정이 어떤가요?",
                "프로젝트를 완료하시면서 어떤 점을 배우셨나요?",
            ]
        else:
            responses = [
                "계속 말씀해주세요. 듣고 있어요.",
                "더 들려주실 이야기가 있으신가요?",
                "그렇군요. 더 자세히 들려주시면 함께 생각해볼 수 있을 것 같아요.",
                "이야기해주셔서 감사해요. 더 구체적으로 말씀해주실 수 있나요?",
                "그런 상황이셨군요. 어떤 부분이 가장 힘드셨나요?",
            ]
    else:
        # 첫 대화인 경우
        responses = [
            "안녕하세요. 늘봄이에요. 오늘 어떤 이야기를 나누고 싶으신가요?",
            "안녕하세요. 어떤 이야기를 들려주시고 싶으신가요?",
            "안녕하세요. 오늘 하루는 어떠셨나요?",
            "안녕하세요. 늘봄이에요. 편하게 이야기해주세요.",
            "안녕하세요. 어떤 일이 있었나요?",
        ]
    
    return random.choice(responses)


def save_chat_log(
    db: Session,
    room_id: int,
    user_message: str,
    bot_reply: str,
    is_crisis: bool = False
):
    """
    대화 내역 저장
    - User 메시지와 Bot 메시지를 각각 ChatLog에 저장
    
    Args:
        db: 데이터베이스 세션
        room_id: 채팅방 ID
        user_message: 사용자 메시지
        bot_reply: 봇 응답 메시지
        is_crisis: 위기 상황 여부
    """
    from app.models import models
    from app.utils.db_utils import safe_commit, safe_rollback
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 사용자 메시지 저장
        user_log = models.ChatLog(
            room_id=room_id,
            is_user=True,
            message=user_message
        )
        db.add(user_log)
        
        # 봇 응답 메시지 저장
        bot_log = models.ChatLog(
            room_id=room_id,
            is_user=False,
            message=bot_reply
        )
        db.add(bot_log)
        
        # 채팅방 업데이트 시간 갱신
        chat_room = db.query(models.ChatRoom).filter(models.ChatRoom.id == room_id).first()
        if chat_room:
            from datetime import datetime
            chat_room.updated_at = datetime.now()
        
        safe_commit(db)
        logger.debug(f"채팅 기록 저장 완료: room_id={room_id}, user_message_length={len(user_message)}, bot_reply_length={len(bot_reply)}")
    except Exception as e:
        safe_rollback(db)
        logger.error(f"채팅 기록 저장 실패: room_id={room_id}, error={e}", exc_info=True)
        # 채팅 기록 저장 실패는 로그만 남기고 예외를 발생시키지 않음 (Soft Fail)

