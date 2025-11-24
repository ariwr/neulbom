from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import logging

from app.models.connection import get_db
from app.models import models, schema
from app.models.crud import (
    get_welfare_by_id, create_bookmark, get_active_welfares, get_user_bookmarks, delete_bookmark,
    create_welfare_view_log, get_user_recent_welfare_views, get_popular_welfares as crud_get_popular_welfares
)
from app.services.auth_service import get_optional_user, require_level
from app.services.welfare_service import search_welfare_with_profile
# 크롤링 기능은 backup_crawling 폴더로 이동됨
# from app.services.crawler_service import crawl_and_save_welfares

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/welfare", tags=["welfare"])


def _clean_welfare_items(welfares: List[models.Welfare]) -> List[schema.WelfareItem]:
    """복지 정보 목록의 summary를 정제하여 WelfareItem 리스트로 변환"""
    result = []
    for welfare in welfares:
        cleaned_summary = schema.clean_welfare_summary(welfare.summary, welfare.full_text)
        welfare_dict = {
            'id': welfare.id,
            'title': welfare.title,
            'summary': cleaned_summary,
            'source_link': welfare.source_link,
            'region': welfare.region,
            'apply_start': welfare.apply_start,
            'apply_end': welfare.apply_end,
            'is_always': welfare.is_always,
            'status': welfare.status,
        }
        result.append(schema.WelfareItem(**welfare_dict))
    return result


def increment_welfare_view_count(db: Session, welfare_id: int, user_id: Optional[int] = None):
    """복지 정보 조회수 증가 (비동기 처리용)"""
    try:
        if user_id:
            # 로그인한 사용자의 경우 열람 기록도 생성
            create_welfare_view_log(db, user_id, welfare_id)
        else:
            # 비회원의 경우 조회수만 증가
            welfare = get_welfare_by_id(db, welfare_id)
            if welfare:
                welfare.view_count = (welfare.view_count or 0) + 1
                db.commit()
    except Exception as e:
        # 조회수 증가 실패는 로그만 남기고 무시
        logger.error(f"조회수 증가 실패: welfare_id={welfare_id}, error={e}")


@router.get("/search", response_model=List[schema.WelfareItem])
def search_welfare(
    keyword: Optional[str] = Query(None, description="검색 키워드"),
    region: Optional[str] = Query(None, description="지역 필터"),
    age: Optional[int] = Query(None, description="나이 필터"),
    care_target: Optional[str] = Query(None, description="돌봄 대상 필터"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    복지 정보 검색
    - Level 1 (비회원) 이상 접근 가능
    - 로그인한 경우 사용자 프로필 기반 필터링 적용
    - 검색 결과의 조회수 증가 (비동기 처리)
    """
    try:
        user_id = current_user.id if current_user else None
        logger.info(f"복지 검색 요청: keyword={keyword}, region={region}, age={age}, care_target={care_target}, skip={skip}, limit={limit}, user_id={user_id}")
        
        welfares = search_welfare_with_profile(
            db=db,
            keyword=keyword,
            region=region,
            age=age,
            care_target=care_target,
            user=None,  # 검색 시 사용자 프로필 필터링 비활성화 (검색 결과 제한 방지)
            skip=skip,
            limit=limit
        )
        
        logger.info(f"검색 결과: {len(welfares)}개 복지 정보 발견")
        
        # 검색 결과의 조회수 증가 (비동기 처리)
        user_id = current_user.id if current_user else None
        for welfare in welfares:
            background_tasks.add_task(increment_welfare_view_count, db, welfare.id, user_id)
        
        # summary 정제 및 생성
        cleaned_items = _clean_welfare_items(welfares)
        logger.info(f"정제 후 결과: {len(cleaned_items)}개")
        return cleaned_items
    except Exception as e:
        logger.error(f"복지 정보 검색 중 오류 발생: keyword={keyword}, error={e}", exc_info=True)
        # 에러가 발생해도 빈 배열 반환 (서버 크래시 방지)
        return []


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
        raise HTTPException(status_code=404, detail="복지 정보를 찾을 수 없습니다.")
    
    # 북마크 생성 (중복 체크는 create_bookmark 내부에서 처리)
    bookmark, is_new = create_bookmark(db, current_user.id, welfare_id)
    
    if is_new:
        return {
            "message": "북마크가 저장되었습니다.",
            "bookmark_id": bookmark.id,
            "already_bookmarked": False
        }
    else:
        return {
            "message": "이미 북마크된 복지 정보입니다.",
            "bookmark_id": bookmark.id,
            "already_bookmarked": True
        }


@router.get("/bookmarks", response_model=schema.BookmarkListResponse)
def get_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    북마크 목록 조회 (모아보기)
    - Level 2 (일반 회원) 이상 접근 가능
    - 삭제된 복지 정보는 자동으로 제외됩니다
    """
    bookmarks, total = get_user_bookmarks(db, current_user.id, skip=skip, limit=limit)
    
    # 북마크의 welfare summary 정제
    cleaned_items = []
    for bookmark in bookmarks:
        if bookmark.welfare:
            cleaned_summary = schema.clean_welfare_summary(bookmark.welfare.summary, bookmark.welfare.full_text)
            welfare_item = schema.WelfareItem(
                id=bookmark.welfare.id,
                title=bookmark.welfare.title,
                summary=cleaned_summary,
                source_link=bookmark.welfare.source_link,
                region=bookmark.welfare.region,
                apply_start=bookmark.welfare.apply_start,
                apply_end=bookmark.welfare.apply_end,
                is_always=bookmark.welfare.is_always,
                status=bookmark.welfare.status,
            )
            cleaned_items.append(schema.BookmarkItem(
                id=bookmark.id,
                welfare_id=bookmark.welfare_id,
                welfare=welfare_item,
                created_at=bookmark.created_at,
            ))
    
    return schema.BookmarkListResponse(
        items=cleaned_items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.delete("/{welfare_id}/bookmark")
def remove_bookmark(
    welfare_id: int,
    current_user: models.User = Depends(require_level(2)),  # Level 2 이상 필요
    db: Session = Depends(get_db)
):
    """
    북마크 삭제
    - Level 2 (일반 회원) 이상 접근 가능
    """
    # 복지 정보 존재 확인 (선택사항이지만 사용자 경험 개선)
    welfare = get_welfare_by_id(db, welfare_id)
    if not welfare:
        raise HTTPException(status_code=404, detail="복지 정보를 찾을 수 없습니다.")
    
    success = delete_bookmark(db, current_user.id, welfare_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="북마크를 찾을 수 없습니다. 이미 삭제되었거나 존재하지 않습니다."
        )
    return {"message": "북마크가 삭제되었습니다."}


# 크롤링 기능은 backup_crawling 폴더로 이동됨
# 필요시 backup_crawling 폴더의 파일을 참고하세요
#
# class CrawlRequest(BaseModel):
#     keywords: Optional[List[str]] = None
#     max_pages: int = 3
#     headless: bool = True  # 헤드리스 모드 사용 여부
#
#
# @router.post("/crawl", response_model=dict)
# def crawl_welfare(
#     crawl_request: CrawlRequest = Body(...),
#     current_user: models.User = Depends(require_level(3)),  # Level 3 (검증회원) 이상 필요
#     db: Session = Depends(get_db)
# ):
#     """
#     복지로에서 복지 정보 크롤링 (Selenium 기반)
#     - Level 3 (검증회원) 이상 접근 가능
#     - 관리자용 엔드포인트
#     - Selenium을 사용하여 JavaScript 기반 동적 콘텐츠 크롤링
#     """
#     result = crawl_and_save_welfares(
#         db=db,
#         keywords=crawl_request.keywords,
#         max_pages=crawl_request.max_pages,
#         headless=crawl_request.headless
#     )
#     
#     if not result.get('success'):
#         raise HTTPException(status_code=500, detail=result.get('error_message', '크롤링 실패'))
#     
#     return result


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
    return _clean_welfare_items(welfares)


@router.get("/recommend/popular", response_model=List[schema.WelfareItem])
def get_popular_welfares(
    limit: int = Query(10, ge=1, le=50, description="반환할 복지 정보 개수"),
    db: Session = Depends(get_db)
):
    """
    인기 복지 정보 조회 (조회수 기준)
    - Level 1 (비회원) 이상 접근 가능
    """
    try:
        welfares = crud_get_popular_welfares(db, limit=limit)
        return _clean_welfare_items(welfares)
    except Exception as e:
        logger.error(f"인기 복지 정보 조회 중 오류 발생: error={e}", exc_info=True)
        # 에러가 발생해도 빈 배열 반환 (서버 크래시 방지)
        return []


@router.get("/recommend/recent", response_model=List[schema.WelfareItem])
def get_recent_welfares(
    limit: int = Query(10, ge=1, le=50, description="반환할 복지 정보 개수"),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user)
):
    """
    최근 본 복지 정보 조회
    - Level 2 (일반 회원) 이상 접근 가능
    - 로그인하지 않은 경우 빈 배열 반환
    """
    try:
        if not current_user or current_user.level < 2:
            return []
        
        view_logs = get_user_recent_welfare_views(db, current_user.id, limit=limit)
        welfares = [log.welfare for log in view_logs if log.welfare]
        return _clean_welfare_items(welfares)
    except Exception as e:
        logger.error(f"최근 본 복지 정보 조회 중 오류 발생: error={e}", exc_info=True)
        # 에러가 발생해도 빈 배열 반환 (서버 크래시 방지)
        return []


@router.get("/{welfare_id}", response_model=schema.WelfareDetail)
def get_welfare_detail(
    welfare_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    복지 정보 상세 조회
    - Level 1 (비회원) 이상 접근 가능
    - 조회수 증가 (비동기 처리)
    """
    welfare = get_welfare_by_id(db, welfare_id)
    if not welfare:
        raise HTTPException(status_code=404, detail="복지 정보를 찾을 수 없습니다.")
    
    # 조회수 증가 (비동기 처리)
    user_id = current_user.id if current_user else None
    background_tasks.add_task(increment_welfare_view_count, db, welfare_id, user_id)
    
    # summary 정제
    cleaned_summary = schema.clean_welfare_summary(welfare.summary, welfare.full_text)
    
    return schema.WelfareDetail(
        id=welfare.id,
        title=welfare.title,
        summary=cleaned_summary,
        full_text=welfare.full_text,
        source_link=welfare.source_link,
        region=welfare.region,
        age_min=welfare.age_min,
        age_max=welfare.age_max,
        care_target=welfare.care_target,
        apply_start=welfare.apply_start,
        apply_end=welfare.apply_end,
        is_always=welfare.is_always,
        status=welfare.status,
        category=welfare.category,
    )

