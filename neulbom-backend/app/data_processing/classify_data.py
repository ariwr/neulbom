"""
LLM 기반 복지 데이터 분류 스크립트
DB에 저장된 복지 정보를 LLM을 통해 SERVICE/NEWS/UNCERTAIN으로 분류합니다.
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.models.connection import get_db
from app.models import models
from app.ai_core.llm_client import llm_client
from app.core.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def mock_llm_call(title: str, content: str) -> str:
    """
    LLM을 호출하여 데이터를 분류합니다.
    
    Args:
        title: 복지 정보 제목
        content: 복지 정보 내용 (summary 또는 full_text)
    
    Returns:
        'SERVICE', 'NEWS', 또는 'UNCERTAIN'
    
    TODO: 실제 LLM API 호출로 교체
    현재는 mock 함수이며, 실제 구현 시 아래 주석 처리된 코드를 사용하세요.
    """
    # 실제 LLM API 호출 (주석 해제하여 사용)
    # try:
    #     prompt = f"""다음 복지 관련 글을 읽고 분류해주세요.
    #
    # 제목: {title}
    # 내용: {content[:1000] if content else "(내용 없음)"}
    #
    # 분류 기준:
    # - 'SERVICE': 실제로 신청 가능한 복지 서비스 (예: 급여, 바우처, 지원금 등)
    # - 'NEWS': 단순 뉴스나 행사 알림, 공지사항 (예: 설명회, 행사 안내, 뉴스 기사)
    # - 'UNCERTAIN': 분류가 애매한 경우
    #
    # 응답은 반드시 'SERVICE', 'NEWS', 'UNCERTAIN' 중 하나만 출력해주세요."""
    #
    #     response = llm_client.generate_chat_response(
    #         message=prompt,
    #         history=[],
    #         system_prompt="당신은 복지 정보를 정확하게 분류하는 전문가입니다.",
    #         provider=settings.DEFAULT_LLM_PROVIDER
    #     )
    #
    #     # 응답에서 분류 결과 추출
    #     response = response.strip().upper()
    #     if 'SERVICE' in response:
    #         return 'SERVICE'
    #     elif 'NEWS' in response:
    #         return 'NEWS'
    #     else:
    #         return 'UNCERTAIN'
    # except Exception as e:
    #     logger.error(f"LLM 호출 실패: {e}")
    #     return 'UNCERTAIN'
    
    # Mock 구현: 간단한 키워드 기반 분류 (실제 LLM 호출 전 테스트용)
    content_lower = (content or "").lower()
    title_lower = title.lower()
    
    # SERVICE 키워드
    service_keywords = ['신청', '지원', '급여', '바우처', '수당', '지원금', '혜택', '서비스', '제공']
    # NEWS 키워드
    news_keywords = ['안내', '공지', '설명회', '행사', '뉴스', '보도', '기사', '알림']
    
    service_score = sum(1 for kw in service_keywords if kw in title_lower or kw in content_lower)
    news_score = sum(1 for kw in news_keywords if kw in title_lower or kw in content_lower)
    
    if service_score > news_score and service_score > 0:
        return 'SERVICE'
    elif news_score > service_score and news_score > 0:
        return 'NEWS'
    else:
        return 'UNCERTAIN'


def classify_welfare_data(db: Session, welfare: models.Welfare) -> Optional[str]:
    """
    단일 복지 데이터를 분류합니다.
    
    Args:
        db: 데이터베이스 세션
        welfare: 분류할 복지 정보 모델
    
    Returns:
        분류 결과 ('SERVICE', 'NEWS', 'UNCERTAIN') 또는 None (오류 시)
    """
    try:
        # 제목과 내용 준비
        title = welfare.title or ""
        content = welfare.summary or welfare.full_text or ""
        
        if not title:
            logger.warning(f"제목이 없는 데이터 (ID: {welfare.id})")
            return None
        
        # LLM으로 분류
        category = mock_llm_call(title, content)
        
        # DB 업데이트
        welfare.category = category
        db.commit()
        db.refresh(welfare)
        
        logger.info(f"분류 완료 (ID: {welfare.id}, 제목: {title[:50]}, 카테고리: {category})")
        return category
        
    except Exception as e:
        logger.error(f"분류 실패 (ID: {welfare.id}): {e}")
        db.rollback()
        return None


def classify_all_unclassified_data(limit: Optional[int] = None, batch_size: int = 10):
    """
    category가 NULL인 모든 복지 데이터를 분류합니다.
    
    Args:
        limit: 분류할 최대 개수 (None이면 전체)
        batch_size: 한 번에 처리할 배치 크기
    """
    db = next(get_db())
    
    try:
        # category가 NULL인 데이터 조회
        query = db.query(models.Welfare).filter(
            models.Welfare.category.is_(None)
        )
        
        if limit:
            query = query.limit(limit)
        
        unclassified_welfares = query.all()
        total_count = len(unclassified_welfares)
        
        if total_count == 0:
            logger.info("분류할 데이터가 없습니다.")
            return
        
        logger.info(f"총 {total_count}개의 미분류 데이터를 분류합니다.")
        
        # 통계
        service_count = 0
        news_count = 0
        uncertain_count = 0
        error_count = 0
        
        # 배치 단위로 처리
        for i in range(0, total_count, batch_size):
            batch = unclassified_welfares[i:i + batch_size]
            logger.info(f"배치 처리 중: {i+1}~{min(i+batch_size, total_count)}/{total_count}")
            
            for welfare in batch:
                category = classify_welfare_data(db, welfare)
                
                if category == 'SERVICE':
                    service_count += 1
                elif category == 'NEWS':
                    news_count += 1
                elif category == 'UNCERTAIN':
                    uncertain_count += 1
                else:
                    error_count += 1
        
        # 결과 출력
        logger.info("=" * 60)
        logger.info("분류 완료!")
        logger.info("=" * 60)
        logger.info(f"총 처리: {total_count}개")
        logger.info(f"  - SERVICE: {service_count}개")
        logger.info(f"  - NEWS: {news_count}개")
        logger.info(f"  - UNCERTAIN: {uncertain_count}개")
        logger.info(f"  - 오류: {error_count}개")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"분류 작업 중 오류: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='복지 데이터 LLM 분류 스크립트')
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='분류할 최대 개수 (기본값: 전체)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='한 번에 처리할 배치 크기 (기본값: 10)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("복지 데이터 LLM 분류 스크립트")
    print("=" * 60)
    print(f"\n설정:")
    print(f"  - 최대 개수: {args.limit or '전체'}")
    print(f"  - 배치 크기: {args.batch_size}")
    print(f"  - LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    print("\n분류 시작...\n")
    
    classify_all_unclassified_data(limit=args.limit, batch_size=args.batch_size)
    
    print("\n작업 완료!")

