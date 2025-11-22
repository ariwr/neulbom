"""
복지로 크롤러 테스트 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.crawlers.welfare_crawler import WelfareCrawler
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_single_keyword():
    """단일 키워드로 크롤링 테스트"""
    print("=" * 60)
    print("단일 키워드 크롤링 테스트")
    print("=" * 60)
    
    keyword = "가족돌봄청년"
    print(f"\n키워드: {keyword}")
    print("크롤링 시작...\n")
    
    try:
        with WelfareCrawler(headless=False) as crawler:  # headless=False로 브라우저 확인 가능
            results = crawler.search_welfare(keyword)
            
            print(f"\n검색 결과: {len(results)}개")
            print("-" * 60)
            
            for i, item in enumerate(results[:5], 1):  # 최대 5개만 출력
                print(f"\n[{i}] {item.get('title', 'N/A')}")
                print(f"    링크: {item.get('source_link', 'N/A')}")
                print(f"    신청기간: {item.get('apply_start')} ~ {item.get('apply_end')}")
                print(f"    상시신청: {item.get('is_always', False)}")
                print(f"    상태: {item.get('status', 'N/A')}")
                if item.get('summary'):
                    print(f"    요약: {item.get('summary')[:100]}...")
            
            if len(results) > 5:
                print(f"\n... 외 {len(results) - 5}개 더 있음")
            
            print("\n" + "=" * 60)
            print("테스트 완료!")
            
    except Exception as e:
        logger.error(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_keywords():
    """여러 키워드로 크롤링 테스트"""
    print("=" * 60)
    print("여러 키워드 크롤링 테스트")
    print("=" * 60)
    
    keywords = ["가족돌봄청년", "영케어러"]
    print(f"\n키워드: {', '.join(keywords)}")
    print("크롤링 시작...\n")
    
    try:
        with WelfareCrawler(headless=True) as crawler:  # headless=True로 빠르게
            all_results = []
            for keyword in keywords:
                print(f"키워드 '{keyword}' 크롤링 중...")
                results = crawler.search_welfare(keyword)
                all_results.extend(results)
                print(f"  -> {len(results)}개 발견\n")
            
            print(f"전체 결과: {len(all_results)}개")
            print("-" * 60)
            
            # 중복 제거
            seen_titles = set()
            unique_results = []
            for item in all_results:
                title = item.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_results.append(item)
            
            print(f"중복 제거 후: {len(unique_results)}개")
            print("\n" + "=" * 60)
            print("테스트 완료!")
            
    except Exception as e:
        logger.error(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()


def test_all_keywords():
    """모든 키워드로 크롤링 테스트 (시간이 오래 걸릴 수 있음)"""
    print("=" * 60)
    print("전체 키워드 크롤링 테스트")
    print("=" * 60)
    print("\n⚠️  주의: 이 테스트는 시간이 오래 걸릴 수 있습니다.")
    print("계속하시겠습니까? (y/n): ", end="")
    
    response = input().strip().lower()
    if response != 'y':
        print("테스트 취소됨")
        return
    
    try:
        with WelfareCrawler(headless=True) as crawler:
            results = crawler.crawl_all_keywords(max_pages_per_keyword=1)  # 페이지 1페이지만
            
            print(f"\n전체 크롤링 결과: {len(results)}개")
            print("-" * 60)
            
            # 키워드별 통계
            keyword_stats = {}
            for item in results:
                keyword = item.get('keyword', 'Unknown')
                keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
            
            print("\n키워드별 결과:")
            for keyword, count in sorted(keyword_stats.items()):
                print(f"  {keyword}: {count}개")
            
            print("\n" + "=" * 60)
            print("테스트 완료!")
            
    except Exception as e:
        logger.error(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='복지로 크롤러 테스트')
    parser.add_argument(
        '--mode',
        choices=['single', 'multiple', 'all'],
        default='single',
        help='테스트 모드: single (단일 키워드), multiple (여러 키워드), all (전체 키워드)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='헤드리스 모드로 실행 (브라우저 창 숨김)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("복지로 크롤러 테스트")
    print("=" * 60)
    
    if args.mode == 'single':
        test_single_keyword()
    elif args.mode == 'multiple':
        test_multiple_keywords()
    elif args.mode == 'all':
        test_all_keywords()
    
    print("\n")

