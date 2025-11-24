"""
커뮤니티 가입 심사 서비스
- AI 기반 자동 승인/거절 로직
"""

import logging
import re
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from app.ai_core.llm_client import llm_client
from app.ai_core.prompts import VERIFICATION_PROMPT
from app.utils.db_utils import safe_rollback, safe_commit

logger = logging.getLogger(__name__)


def verify_with_ai(verification_text: str) -> Dict[str, Any]:
    """
    AI를 사용하여 심사 텍스트 분석 및 승인/거절 결정
    
    Args:
        verification_text: 심사 제출 텍스트
        
    Returns:
        Dict: {
            "approved": bool,  # 승인 여부
            "reason": str,     # 승인/거절 이유
            "confidence": float  # 신뢰도 (0.0 ~ 1.0)
        }
    """
    if not verification_text or len(verification_text.strip()) < 10:
        return {
            "approved": False,
            "reason": "심사 제출 글의 내용이 너무 짧습니다. 구체적으로 작성해주세요.",
            "confidence": 1.0
        }
    
    try:
        # 프롬프트 생성
        prompt = VERIFICATION_PROMPT.format(text=verification_text)
        
        # LLM 호출 (시스템 프롬프트 없이 직접 프롬프트 사용)
        response = llm_client.generate_chat_response(
            message=prompt,
            history=[],
            system_prompt="당신은 커뮤니티 가입 심사를 담당하는 AI입니다. 제출된 글을 분석하여 승인 또는 거절을 결정합니다.",
            provider=None  # 기본 provider 사용
        )
        
        logger.info(f"AI 심사 응답: {response}")
        
        # 응답 파싱
        response_lower = response.lower()
        
        # 승인/거절 판단
        approved = False
        reason = response.strip()
        confidence = 0.7  # 기본 신뢰도
        
        # 승인 키워드 확인
        approval_keywords = ["승인", "approve", "approved", "통과", "합격", "허용"]
        rejection_keywords = ["거부", "reject", "rejected", "거절", "불합격", "거부함"]
        
        has_approval = any(keyword in response_lower for keyword in approval_keywords)
        has_rejection = any(keyword in response_lower for keyword in rejection_keywords)
        
        if has_approval and not has_rejection:
            approved = True
            confidence = 0.8
        elif has_rejection and not has_approval:
            approved = False
            confidence = 0.8
        elif has_approval and has_rejection:
            # 둘 다 있으면 더 강한 키워드 확인
            approval_count = sum(1 for keyword in approval_keywords if keyword in response_lower)
            rejection_count = sum(1 for keyword in rejection_keywords if keyword in response_lower)
            approved = approval_count > rejection_count
            confidence = 0.6
        else:
            # 명확한 키워드가 없으면 텍스트 길이와 내용으로 판단
            # 긍정적 단어가 많으면 승인
            positive_words = ["진심", "성실", "참여", "도움", "지원", "공감", "이해"]
            negative_words = ["부적절", "위험", "불법", "악용", "남용", "사기"]
            
            positive_count = sum(1 for word in positive_words if word in response_lower)
            negative_count = sum(1 for word in negative_words if word in response_lower)
            
            if negative_count > 0:
                approved = False
                confidence = 0.7
                reason = "부적절한 내용이 감지되었습니다."
            elif positive_count >= 2:
                approved = True
                confidence = 0.6
                reason = "진정성 있는 참여 의지가 확인되었습니다."
            else:
                # 애매한 경우 기본적으로 승인 (관대한 정책)
                approved = True
                confidence = 0.5
                reason = "심사 결과 승인되었습니다."
        
        # 최소 길이 체크 (너무 짧으면 거절)
        if len(verification_text.strip()) < 20:
            approved = False
            confidence = 0.9
            reason = "심사 제출 글의 내용이 충분하지 않습니다. 더 구체적으로 작성해주세요."
        
        return {
            "approved": approved,
            "reason": reason,
            "confidence": confidence,
            "raw_response": response
        }
        
    except Exception as e:
        logger.error(f"AI 심사 중 오류 발생: {e}", exc_info=True)
        # 오류 발생 시 기본적으로 승인 (안전한 정책)
        return {
            "approved": True,
            "reason": "AI 심사 시스템 오류로 인해 자동 승인되었습니다.",
            "confidence": 0.3,
            "error": str(e)
        }


def reject_verification(db: Session, user_id: int, reason: str) -> Optional[Any]:
    """
    심사 거절
    
    Args:
        db: 데이터베이스 세션
        user_id: 사용자 ID
        reason: 거절 사유
        
    Returns:
        업데이트된 User 객체 또는 None
    """
    from app.models import models
    
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            return None
        
        db_user.verification_status = "rejected"
        safe_commit(db)
        db.refresh(db_user)
        return db_user
    except Exception as e:
        safe_rollback(db)
        logger.error(f"심사 거절 실패: user_id={user_id}, error={e}", exc_info=True)
        raise

