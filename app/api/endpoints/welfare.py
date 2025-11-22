from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.models.connection import get_db
from app.models import models, schema
from app.models.crud import get_welfare_by_id, create_bookmark, get_active_welfares
from app.services.auth_service import get_optional_user, require_level
from app.services.welfare_service import search_welfare_with_profile
from app.services.crawler_service import crawl_and_save_welfares

router = APIRouter(prefix="/api/welfare", tags=["welfare"])


@router.get("/search", response_model=List[schema.WelfareItem])
def search_welfare(
    keyword: Optional[str] = Query(None, description="검색 키워드"),
    region: Optional[str] = Query(None, description="지역 필터"),
    age: Optional[int] = Query(None, description="나이 필터"),
    care_target: Optional[str] = Query(None, description="돌봄 대상 필터"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user)
):
    """
    복지 정보 검색
    - Level 1 (비회원) 이상 접근 가능
    - 로그인한 경우 사용자 프로필 기반 필터링 적용
    """
    welfares = search_welfare_with_profile(
        db=db,
        keyword=keyword,
        region=region,
        age=age,
        care_target=care_target,
        user=current_user,
        skip=skip,
        limit=limit
    )
    
    return welfares


@router.post("/{welfare_id}/bookmark")
def bookmark_welfare(
    welfare_id: int,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    복지 정보 북마크 저장
    - Level 2 (일반 회원) 이상 접근 가능
    """
    # 복지 정보 존재 확인
    welfare = get_welfare_by_id(db, welfare_id)
    if not welfare:
        raise HTTPException(status_code=404, detail="Welfare not found")
    
    bookmark = create_bookmark(db, current_user.id, welfare_id)
    return {"message": "Bookmarked successfully", "bookmark_id": bookmark.id}


class CrawlRequest(BaseModel):
    keywords: Optional[List[str]] = None
    max_pages: int = 3
    headless: bool = True  # 헤드리스 모드 사용 여부


@router.post("/crawl", response_model=dict)
def crawl_welfare(
    crawl_request: CrawlRequest = Body(...),
    current_user: models.User = Depends(require_level(3)),  # Level 3 (검증회원) 이상 필요
    db: Session = Depends(get_db)
):
    """
    복지로에서 복지 정보 크롤링 (Selenium 기반)
    - Level 3 (검증회원) 이상 접근 가능
    - 관리자용 엔드포인트
    - Selenium을 사용하여 JavaScript 기반 동적 콘텐츠 크롤링
    """
    result = crawl_and_save_welfares(
        db=db,
        keywords=crawl_request.keywords,
        max_pages=crawl_request.max_pages,
        headless=crawl_request.headless
    )
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error_message', '크롤링 실패'))
    
    return result


@router.get("/active", response_model=List[schema.WelfareItem])
def get_active_welfare_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user)
):
    """
    현재 신청 가능한 복지 정보만 조회 (마감 임박 순)
    - Level 1 (비회원) 이상 접근 가능
    """
    welfares = get_active_welfares(db, skip=skip, limit=limit)
    return welfares

