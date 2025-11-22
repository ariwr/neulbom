"""
위기 감지 시스템
- 자살, 학대 등 고위험 키워드/맥락 감지
"""

from typing import Dict, Optional
from app.core.config import settings
from app.ai_core.llm_client import llm_client

# 위기 키워드 목록
CRISIS_KEYWORDS = [
    "자살", "죽고 싶", "끝내고 싶", "죽을래", "죽겠",
    "학대", "폭행", "폭력", "구타",
    "절망", "희망 없", "의미 없",
    "계획", "유서", "작별"
]


def detect_crisis(text: str) -> bool:
    """
    위기 감지 시스템
    - 키워드 기반 감지
    - TODO: LLM 기반 맥락 분석 추가
    """
    text_lower = text.lower()
    
    # 키워드 기반 감지
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # TODO: LLM을 사용한 감정 분석 및 맥락 기반 위기 감지
    # sentiment = llm_client.analyze_sentiment(text)
    # if sentiment["score"] < 0.2:  # 매우 부정적
    #     return True
    
    return False


def get_crisis_info() -> Dict:
    """위기 상황 정보 반환"""
    return {
        "phone": settings.CRISIS_HOTLINE,
        "message": "전문가의 도움이 필요해 보여요. 보건복지콜센터(129)로 연락해보세요."
    }


def analyze_crisis_level(text: str) -> Dict:
    """
    위기 수준 분석
    - low: 낮음
    - medium: 중간
    - high: 높음
    """
    is_crisis = detect_crisis(text)
    
    if not is_crisis:
        return {
            "level": "low",
            "is_crisis": False,
            "info": None
        }
    
    # 키워드 개수로 위기 수준 판단
    keyword_count = sum(1 for keyword in CRISIS_KEYWORDS if keyword in text.lower())
    
    if keyword_count >= 3:
        level = "high"
    elif keyword_count >= 2:
        level = "medium"
    else:
        level = "low"
    
    return {
        "level": level,
        "is_crisis": True,
        "info": get_crisis_info()
    }

