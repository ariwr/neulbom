"""
배치 summary 생성 서비스
- summary가 없는 기존 복지 정보에 대해 웹 크롤링 + LLM 요약 생성
- RAG 기술을 활용한 자동 요약
"""
from sqlalchemy.orm import Session
from app.models import models
from app.services.web_scraper import scrape_and_summarize
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def generate_summaries_for_missing(
    db: Session,
    limit: Optional[int] = None,
    dry_run: bool = False
) -> dict:
    """
    summary가 없는 복지 정보에 대해 웹 크롤링 + 요약 생성
    
    Args:
        db: 데이터베이스 세션
        limit: 처리할 최대 개수 (None이면 전체)
        dry_run: 실제로 업데이트하지 않고 통계만 확인
    
    Returns:
        처리 결과 통계
    """
    # summary가 없고 source_link가 있는 복지 정보 조회
    query = db.query(models.Welfare).filter(
        (models.Welfare.summary.is_(None) | (models.Welfare.summary == '')),
        models.Welfare.source_link.isnot(None),
        models.Welfare.source_link != ''
    )
    
    if limit:
        query = query.limit(limit)
    
    welfares = query.all()
    
    total = len(welfares)
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    logger.info(f"summary 생성 대상: {total}개 (dry_run={dry_run})")
    
    for i, welfare in enumerate(welfares, 1):
        try:
            logger.info(f"[{i}/{total}] 처리 중: ID={welfare.id}, 제목={welfare.title[:50]}...")
            
            # 웹 크롤링 + 요약 생성
            summary = scrape_and_summarize(welfare.source_link, title=welfare.title)
            
            if summary:
                if not dry_run:
                    welfare.summary = summary
                    db.commit()
                    logger.info(f"✓ summary 생성 성공: ID={welfare.id}")
                else:
                    logger.info(f"✓ summary 생성 성공 (dry_run): ID={welfare.id}")
                success_count += 1
            else:
                logger.warning(f"✗ summary 생성 실패: ID={welfare.id}")
                fail_count += 1
                
        except Exception as e:
            logger.error(f"✗ 처리 중 오류 발생: ID={welfare.id}, 오류: {e}", exc_info=True)
            fail_count += 1
            if not dry_run:
                db.rollback()
    
    if not dry_run:
        logger.info(f"배치 처리 완료: 성공 {success_count}개, 실패 {fail_count}개")
    else:
        logger.info(f"배치 처리 시뮬레이션 완료: 성공 {success_count}개, 실패 {fail_count}개")
    
    return {
        'total': total,
        'success': success_count,
        'failed': fail_count,
        'skipped': skipped_count,
        'dry_run': dry_run
    }


def generate_summaries_for_all(
    db: Session,
    limit: Optional[int] = None,
    force_update: bool = False,
    dry_run: bool = False
) -> dict:
    """
    모든 복지 정보에 대해 summary 생성/업데이트
    
    Args:
        db: 데이터베이스 세션
        limit: 처리할 최대 개수 (None이면 전체)
        force_update: 기존 summary가 있어도 업데이트할지 여부
        dry_run: 실제로 업데이트하지 않고 통계만 확인
    
    Returns:
        처리 결과 통계
    """
    if force_update:
        query = db.query(models.Welfare).filter(
            models.Welfare.source_link.isnot(None),
            models.Welfare.source_link != ''
        )
    else:
        query = db.query(models.Welfare).filter(
            (models.Welfare.summary.is_(None) | (models.Welfare.summary == '')),
            models.Welfare.source_link.isnot(None),
            models.Welfare.source_link != ''
        )
    
    if limit:
        query = query.limit(limit)
    
    welfares = query.all()
    
    total = len(welfares)
    success_count = 0
    fail_count = 0
    
    logger.info(f"summary 생성 대상: {total}개 (force_update={force_update}, dry_run={dry_run})")
    
    for i, welfare in enumerate(welfares, 1):
        try:
            logger.info(f"[{i}/{total}] 처리 중: ID={welfare.id}, 제목={welfare.title[:50]}...")
            
            # 웹 크롤링 + 요약 생성
            summary = scrape_and_summarize(welfare.source_link, title=welfare.title)
            
            if summary:
                if not dry_run:
                    welfare.summary = summary
                    db.commit()
                    logger.info(f"✓ summary 생성 성공: ID={welfare.id}")
                else:
                    logger.info(f"✓ summary 생성 성공 (dry_run): ID={welfare.id}")
                success_count += 1
            else:
                logger.warning(f"✗ summary 생성 실패: ID={welfare.id}")
                fail_count += 1
                
        except Exception as e:
            logger.error(f"✗ 처리 중 오류 발생: ID={welfare.id}, 오류: {e}", exc_info=True)
            fail_count += 1
            if not dry_run:
                db.rollback()
    
    if not dry_run:
        logger.info(f"배치 처리 완료: 성공 {success_count}개, 실패 {fail_count}개")
    else:
        logger.info(f"배치 처리 시뮬레이션 완료: 성공 {success_count}개, 실패 {fail_count}개")
    
    return {
        'total': total,
        'success': success_count,
        'failed': fail_count,
        'dry_run': dry_run
    }

