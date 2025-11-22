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
        except Exception:
            pass
    
    # 부정적 감정이 강하게 감지된 경우 CBT 기법 명시적 적용
    if has_negative_emotion and (sentiment_score is None or sentiment_score < 0.4):
        # CBT 프롬프트를 메시지에 포함하여 LLM에 전달
        cbt_enhanced_message = f"""{message}

위 메시지를 읽고, CBT(인지행동치료) 기법을 적용하여 응답해주세요:
1. 먼저 감정을 공감하고 인정하기
2. 감사 일기 작성 유도: "오늘 하루 중에서 조금이라도 좋았던 순간이 있었나요?"
3. 사고 전환 제안: 부정적 해석을 긍정적 관점으로 전환
4. 작은 행동 변화 제안: 실현 가능한 작은 일 하나 제안"""
        
        reply = llm_client.generate_chat_response(
            message=cbt_enhanced_message,
            history=history,
            system_prompt=CHATBOT_SYSTEM_PROMPT
        )
    elif has_positive_emotion:
        # 긍정적 감정일 때는 감사 일기 기록 유도
        gratitude_message = f"""{message}

위 메시지를 읽고, 긍정적인 감정을 격려하고 감사 일기 기록을 유도해주세요."""
        
        reply = llm_client.generate_chat_response(
            message=gratitude_message,
            history=history,
            system_prompt=CHATBOT_SYSTEM_PROMPT
        )
    else:
        # 일반 대화
        reply = llm_client.generate_chat_response(
            message=message,
            history=history,
            system_prompt=CHATBOT_SYSTEM_PROMPT
        )
    
    # 임시 응답 (LLM API 미통합 시 fallback)
    if reply == "안녕하세요. 늘봄입니다. 어떻게 도와드릴까요?" or not reply.strip():
        # 부정적 감정이 있을 때 CBT 기법 적용한 응답
        if has_negative_emotion:
            return """지금 힘든 상황이시군요. 그런 감정을 느끼는 것은 당연해요. 

혹시 오늘 하루 중에서 조금이라도 좋았던 순간이 있었나요? 작은 것이라도 괜찮아요. 그런 순간들을 떠올려보시는 것도 도움이 될 수 있어요.

또한 이 상황을 다른 관점에서도 볼 수 있을까요? 예를 들어, 지금 힘듦을 겪고 계시지만 그 속에서도 배울 수 있는 부분이 있을 수도 있어요.

오늘 할 수 있는 작은 일 하나를 정해보시는 것은 어떨까요? 아주 작은 것이라도 괜찮아요."""
        elif has_positive_emotion:
            return "좋은 감정을 느끼고 계시는군요! 그런 긍정적인 순간들을 기록해보시는 것도 좋을 것 같아요. 감사 일기를 써보시면 나중에 힘들 때 다시 읽어보시면서 힘을 얻으실 수 있을 거예요."
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

