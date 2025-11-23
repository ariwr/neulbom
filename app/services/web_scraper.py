"""
웹 크롤링 서비스
- URL에서 웹페이지 내용을 크롤링
- RAG 기술을 활용한 자동 요약 생성
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def scrape_website_content(url: str, timeout: int = 10) -> Optional[str]:
    """
    웹사이트에서 텍스트 내용을 크롤링
    
    Args:
        url: 크롤링할 URL
        timeout: 요청 타임아웃 (초)
    
    Returns:
        크롤링한 텍스트 내용 (실패 시 None)
    """
    try:
        # URL 유효성 검사
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            logger.warning(f"유효하지 않은 URL: {url}")
            return None
        
        # User-Agent 설정 (봇 차단 방지)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # 웹페이지 요청
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # 인코딩 확인
        if response.encoding is None:
            response.encoding = 'utf-8'
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 불필요한 태그 제거
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
            tag.decompose()
        
        # 메인 콘텐츠 추출
        # 일반적인 콘텐츠 영역 선택자들
        content_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '#content',
            '#main',
            '.post-content',
            '.entry-content',
            '.article-content',
        ]
        
        content_text = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                content_text = content.get_text(separator='\n', strip=True)
                break
        
        # 메인 콘텐츠를 찾지 못한 경우 body 전체 사용
        if not content_text:
            body = soup.find('body')
            if body:
                content_text = body.get_text(separator='\n', strip=True)
            else:
                content_text = soup.get_text(separator='\n', strip=True)
        
        # 텍스트 정제
        # 연속된 공백/줄바꿈 제거
        content_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', content_text)
        content_text = re.sub(r' +', ' ', content_text)
        content_text = content_text.strip()
        
        # 최소 길이 확인 (너무 짧으면 의미 없는 페이지)
        if len(content_text) < 50:
            logger.warning(f"크롤링한 내용이 너무 짧음: {url} (길이: {len(content_text)})")
            return None
        
        logger.info(f"웹 크롤링 성공: {url} (길이: {len(content_text)}자)")
        return content_text
        
    except requests.exceptions.Timeout:
        logger.warning(f"웹 크롤링 타임아웃: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"웹 크롤링 실패: {url}, 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"웹 크롤링 중 예상치 못한 오류: {url}, 오류: {e}", exc_info=True)
        return None


def scrape_and_summarize(url: str, title: Optional[str] = None) -> Optional[str]:
    """
    웹사이트를 크롤링하고 LLM으로 요약 생성 (RAG 기술 활용)
    
    Args:
        url: 크롤링할 URL
        title: 복지 서비스 제목 (컨텍스트 제공용)
    
    Returns:
        요약된 텍스트 (실패 시 None)
    """
    try:
        # 웹사이트 크롤링
        scraped_content = scrape_website_content(url)
        if not scraped_content:
            return None
        
        # 제목이 있으면 컨텍스트로 추가
        context = f"복지 서비스: {title}\n\n" if title else ""
        full_text = context + scraped_content
        
        # LLM으로 요약 생성
        from app.ai_core.rag_engine import summarize_welfare
        summary = summarize_welfare(full_text, target_level="17세")
        
        if summary and summary.strip():
            logger.info(f"웹 크롤링 및 요약 성공: {url}")
            return summary.strip()
        else:
            logger.warning(f"요약 생성 실패: {url}")
            return None
            
    except Exception as e:
        logger.error(f"웹 크롤링 및 요약 중 오류: {url}, 오류: {e}", exc_info=True)
        return None

