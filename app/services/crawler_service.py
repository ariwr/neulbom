"""
크롤링 서비스
복지로에서 크롤링한 데이터를 DB에 저장하는 서비스
"""
from sqlalchemy.orm import Session
from typing import List, Dict
import logging

from app.crawlers.welfare_crawler import crawl_welfare_services, WelfareCrawler
from app.models import crud, models

logger = logging.getLogger(__name__)


def crawl_and_save_welfares(db: Session, keywords: List[str] = None, max_pages: int = 3, headless: bool = True) -> Dict:
    """
    복지로에서 복지 정보를 크롤링하고 DB에 저장합니다.
    
    Args:
        db: 데이터베이스 세션
        keywords: 크롤링할 키워드 리스트 (None이면 기본 키워드 사용)
        max_pages: 키워드당 최대 페이지 수
        headless: 헤드리스 모드 사용 여부 (기본값: True)
    
    Returns:
        크롤링 결과 통계 딕셔너리
    """
    try:
        crawler = WelfareCrawler(headless=headless)
        
        try:
            if keywords:
                # 사용자 지정 키워드로 크롤링
                all_welfares = []
                for keyword in keywords:
                    welfares = crawler.search_welfare(keyword, page=1)
                    if welfares:
                        all_welfares.extend(welfares)
            else:
                # 기본 키워드로 크롤링
                all_welfares = crawler.crawl_all_keywords(max_pages_per_keyword=max_pages)
        finally:
            # WebDriver 정리
            crawler.close()
        
            # DB에 저장
            saved_count = 0
            skipped_count = 0
            error_count = 0
            
            for welfare_data in all_welfares:
                try:
                    # keyword 필드는 DB에 저장하지 않음 (크롤링 메타데이터)
                    welfare_data.pop('keyword', None)
                    
                    # DB에 저장 또는 업데이트
                    crud.create_or_update_welfare(db, welfare_data)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"복지 정보 저장 실패: {e}")
                    error_count += 1
                    continue
            
            return {
                'total_crawled': len(all_welfares),
                'saved': saved_count,
                'skipped': skipped_count,
                'errors': error_count,
                'success': True
            }
        
    except Exception as e:
        logger.error(f"크롤링 서비스 오류: {e}")
        return {
            'total_crawled': 0,
            'saved': 0,
            'skipped': 0,
            'errors': 0,
            'success': False,
            'error_message': str(e)
        }

