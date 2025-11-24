"""
위기 감지 시스템
- 하이브리드 위기 감지 시스템 (Rule-based + LLM)
- 1차: 고위험 키워드 즉시 탐지 (속도)
- 2차: LLM 감정 분석을 통한 은유적/맥락적 위기 상황 판단 (정확도)
"""

from typing import Dict, Optional
import logging
from app.core.config import settings
from app.ai_core.llm_client import llm_client

logger = logging.getLogger(__name__)

# 위기 키워드 목록 (고위험 키워드)
CRISIS_KEYWORDS = [
    "자살", "죽고 싶", "끝내고 싶", "죽을래", "죽겠", "죽고싶",
    "학대", "폭행", "폭력", "구타", "폭행당", "학대당",
    "절망", "희망 없", "의미 없", "의미없", "희망없",
    "계획", "유서", "작별", "이별", "끝내",
    "목매", "교수형", "독약", "약물과다"
]

# 중간 위험 키워드 (감정 분석 트리거)
WARNING_KEYWORDS = [
    "힘들", "어려", "스트레스", "우울", "불안", "두려",
    "외로", "고독", "슬프", "절망", "포기", "포기하",
    "도움", "도와줘", "구해줘", "살기 싫"
]


def detect_crisis(text: str, use_llm: bool = True) -> bool:
    """
    하이브리드 위기 감지 시스템
    
    Args:
        text: 분석할 텍스트
        use_llm: LLM 감정 분석 사용 여부 (기본값: True)
    
    Returns:
        bool: 위기 상황 여부
    
    동작 방식:
        1차: 고위험 키워드 즉시 탐지 (빠른 속도)
        2차: 키워드가 없으면 LLM 감정 분석 수행 (정확도)
    """
    if not text or not text.strip():
        return False
    
    text_lower = text.lower()
    
    # 1차: 고위험 키워드 즉시 탐지 (속도 최적화)
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            logger.warning(f"위기 키워드 감지: '{keyword}' in text")
            return True
    
    # 2차: LLM 감정 분석을 통한 은유적/맥락적 위기 상황 판단
    if use_llm:
        # 중간 위험 키워드가 있거나 텍스트가 충분히 긴 경우에만 LLM 분석 수행
        has_warning_keyword = any(keyword in text_lower for keyword in WARNING_KEYWORDS)
        is_long_text = len(text.strip()) > 20  # 짧은 텍스트는 키워드만으로 판단
        
        if has_warning_keyword or is_long_text:
            try:
                sentiment = llm_client.analyze_sentiment(text)
                sentiment_score = sentiment.get("score", 0.5)
                sentiment_label = sentiment.get("sentiment", "neutral")
                
                logger.info(f"감정 분석 결과: {sentiment_label} (score: {sentiment_score:.2f})")
                
                # 매우 부정적인 감정 (score < 0.25)이면 위기로 판단
                if sentiment_score < 0.25:
                    logger.warning(f"LLM 기반 위기 감지: 감정 점수 {sentiment_score:.2f}")
                    return True
                
                # 부정적 감정이면서 위험 키워드가 포함된 경우
                if sentiment_score < 0.4 and has_warning_keyword:
                    logger.warning(f"하이브리드 위기 감지: 부정적 감정 + 경고 키워드")
                    return True
                    
            except Exception as e:
                logger.error(f"LLM 감정 분석 오류: {e}")
                # LLM 실패 시 경고 키워드가 있으면 위기로 판단 (안전 우선)
                if has_warning_keyword:
                    logger.warning("LLM 실패, 경고 키워드 기반 위기 감지")
                    return True
    
    return False


def get_crisis_info() -> Dict:
    """위기 상황 정보 반환"""
    return {
        "phone": settings.CRISIS_HOTLINE,
        "message": "전문가의 도움이 필요해 보여요. 보건복지콜센터(129)로 연락해보세요."
    }


def analyze_crisis_level(text: str, use_llm: bool = True) -> Dict:
    """
    위기 수준 분석 (하이브리드 방식)
    - low: 낮음
    - medium: 중간
    - high: 높음
    
    Args:
        text: 분석할 텍스트
        use_llm: LLM 감정 분석 사용 여부
    
    Returns:
        Dict: 위기 수준 정보
    """
    if not text or not text.strip():
        return {
            "level": "low",
            "is_crisis": False,
            "info": None,
            "detection_method": None
        }
    
    text_lower = text.lower()
    
    # 1차: 고위험 키워드 개수 확인
    crisis_keyword_count = sum(1 for keyword in CRISIS_KEYWORDS if keyword in text_lower)
    warning_keyword_count = sum(1 for keyword in WARNING_KEYWORDS if keyword in text_lower)
    
    # 고위험 키워드가 있으면 즉시 위기로 판단
    if crisis_keyword_count > 0:
        if crisis_keyword_count >= 3:
            level = "high"
        elif crisis_keyword_count >= 2:
            level = "medium"
        else:
            level = "medium"  # 고위험 키워드 1개도 중간 이상
        
        return {
            "level": level,
            "is_crisis": True,
            "info": get_crisis_info(),
            "detection_method": "keyword",
            "keyword_count": crisis_keyword_count
        }
    
    # 2차: LLM 감정 분석
    if use_llm:
        try:
            sentiment = llm_client.analyze_sentiment(text)
            sentiment_score = sentiment.get("score", 0.5)
            sentiment_label = sentiment.get("sentiment", "neutral")
            
            # 매우 부정적인 감정 분석
            if sentiment_score < 0.25:
                level = "high"
                return {
                    "level": level,
                    "is_crisis": True,
                    "info": get_crisis_info(),
                    "detection_method": "llm",
                    "sentiment_score": sentiment_score,
                    "sentiment_label": sentiment_label
                }
            elif sentiment_score < 0.35:
                level = "medium"
                return {
                    "level": level,
                    "is_crisis": True,
                    "info": get_crisis_info(),
                    "detection_method": "llm",
                    "sentiment_score": sentiment_score,
                    "sentiment_label": sentiment_label
                }
            elif sentiment_score < 0.4 and warning_keyword_count >= 2:
                # 부정적 감정 + 경고 키워드 다수
                level = "medium"
                return {
                    "level": level,
                    "is_crisis": True,
                    "info": get_crisis_info(),
                    "detection_method": "hybrid",
                    "sentiment_score": sentiment_score,
                    "warning_keyword_count": warning_keyword_count
                }
        except Exception as e:
            logger.error(f"LLM 감정 분석 오류: {e}")
            # LLM 실패 시 경고 키워드가 많으면 위기로 판단
            if warning_keyword_count >= 3:
                return {
                    "level": "medium",
                    "is_crisis": True,
                    "info": get_crisis_info(),
                    "detection_method": "keyword_fallback",
                    "warning_keyword_count": warning_keyword_count
                }
    
    # 위기 상황 아님
    return {
        "level": "low",
        "is_crisis": False,
        "info": None,
        "detection_method": None
    }

