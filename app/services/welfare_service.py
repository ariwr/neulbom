"""
복지 정보 서비스
- 사용자 프로필(나이/지역) + RAG 검색 결과 매칭
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import models, schema
from app.models.crud import search_welfares, get_welfare_by_id
from app.ai_core.rag_engine import search_welfare_rag


def search_welfare_with_profile(
    db: Session,
    keyword: Optional[str] = None,
    region: Optional[str] = None,
    age: Optional[int] = None,
    care_target: Optional[str] = None,
    user: Optional[models.User] = None,
    use_rag: bool = True,
    skip: int = 0,
    limit: int = 20
) -> List[models.Welfare]:
    """
    복지 정보 검색 (사용자 프로필 기반)
    - 로그인한 경우 사용자 프로필 정보 활용
    - RAG 검색 또는 키워드 검색
    """
    # 사용자 프로필 정보 활용
    if user:
        if age is None and user.age:
            age = user.age
        if region is None and user.region:
            region = user.region
        if care_target is None and user.care_target:
            care_target = user.care_target
    
    # RAG 검색 또는 키워드 검색
    if use_rag and keyword:
        welfares = search_welfare_rag(
            db=db,
            query=keyword,
            region=region,
            age=age,
            limit=limit
        )
    else:
        welfares = search_welfares(
            db=db,
            keyword=keyword,
            region=region,
            age=age,
            care_target=care_target,
            skip=skip,
            limit=limit
        )
    
    return welfares


def get_welfare_detail(
    db: Session,
    welfare_id: int
) -> Optional[models.Welfare]:
    """복지 정보 상세 조회"""
    return get_welfare_by_id(db, welfare_id)

