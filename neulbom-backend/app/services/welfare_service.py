"""
복지 정보 서비스
- 사용자 프로필(나이/지역) + RAG 검색 결과 매칭
- 순수 CRUD 전담 (AI 로직 제거)
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import models, schema
from app.models.crud import search_welfares, get_welfare_by_id
from app.ai_core.rag_engine import search_context
import logging

logger = logging.getLogger(__name__)


def search_welfare_with_profile(
    db: Session,
    keyword: Optional[str] = None,
    region: Optional[str] = None,
    age: Optional[int] = None,
    care_target: Optional[str] = None,
    user: Optional[models.User] = None,
    use_rag: bool = False,  # 기본값을 False로 변경하여 안정성 향상
    skip: int = 0,
    limit: int = 20
) -> List[models.Welfare]:
    """
    복지 정보 검색 (사용자 프로필 기반)
    - 로그인한 경우 사용자 프로필 정보 활용
    - RAG 검색 또는 키워드 검색
    """
    # 사용자 프로필 정보 활용 (검색 시에는 프로필 필터링을 적용하지 않음)
    # 주석: 검색 시 사용자 프로필을 자동으로 필터링하면 검색 결과가 너무 제한될 수 있음
    # if user:
    #     if age is None and user.age:
    #         age = user.age
    #     if region is None and user.region:
    #         region = user.region
    #     if care_target is None and user.care_target:
    #         care_target = user.care_target
    
    # RAG 검색 또는 키워드 검색
    if use_rag and keyword:
        try:
            # RAG 엔진을 통해 관련 문서 ID 검색
            rag_welfare_ids = search_context(query=keyword, limit=limit * 3)
            
            if rag_welfare_ids:
                # DB에서 복지 정보 조회
                welfares = db.query(models.Welfare).filter(
                    models.Welfare.id.in_(rag_welfare_ids)
                ).all()
                
                # 순서 유지 (RAG 검색 결과 순서대로)
                welfare_dict = {w.id: w for w in welfares}
                welfares = [welfare_dict[w_id] for w_id in rag_welfare_ids if w_id in welfare_dict]
                
                # 지역/나이 필터링
                if region:
                    welfares = [w for w in welfares if region in (w.region or "")]
                
                if age:
                    welfares = [
                        w for w in welfares
                        if (w.age_min is None or w.age_min <= age) and
                           (w.age_max is None or w.age_max >= age)
                    ]
                
                # 상위 limit개만 반환
                welfares = welfares[:limit]
            else:
                # RAG 검색 결과가 없으면 키워드 검색으로 폴백
                logger.info(f"RAG 검색 결과 없음, 키워드 검색으로 폴백: {keyword}")
                welfares = search_welfares(
                    db=db,
                    keyword=keyword,
                    region=region,
                    age=age,
                    care_target=care_target,
                    skip=skip,
                    limit=limit
                )
        except Exception as e:
            # RAG 검색 실패 시 키워드 검색으로 폴백
            logger.warning(f"RAG 검색 실패, 키워드 검색으로 폴백: {e}")
            welfares = search_welfares(
                db=db,
                keyword=keyword,
                region=region,
                age=age,
                care_target=care_target,
                skip=skip,
                limit=limit
            )
    else:
        # 키워드 검색 (CRUD 함수 사용)
        logger.info(f"키워드 검색 실행: keyword={keyword}, region={region}, age={age}, care_target={care_target}, skip={skip}, limit={limit}")
        welfares = search_welfares(
            db=db,
            keyword=keyword,
            region=region,
            age=age,
            care_target=care_target,
            skip=skip,
            limit=limit
        )
        logger.info(f"키워드 검색 결과: {len(welfares)}개")
    
    return welfares


def get_welfare_detail(
    db: Session,
    welfare_id: int
) -> Optional[models.Welfare]:
    """복지 정보 상세 조회"""
    return get_welfare_by_id(db, welfare_id)

