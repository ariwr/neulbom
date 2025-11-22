"""
복지로 크롤링 모듈 (Selenium 기반)
가족돌봄청년(영케어러) 관련 복지 서비스를 크롤링합니다.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import logging
import re

from app.crawlers.utils import parse_date_range, check_is_active, determine_status

logger = logging.getLogger(__name__)

# 복지로 크롤링 추천 키워드 리스트
WELFARE_KEYWORDS = [
    # 핵심 대상 및 신조어
    "가족돌봄청년",
    "영케어러",
    "돌봄가족",
    "청소년부모",
    
    # 상황별 지원
    "가사간병",
    "긴급복지",
    "병원동행",
    "재가급여",
    "재가복지",
    "발달재활",
    
    # 청년/심리 특화
    "청년마음건강",
    "청년월세",
    "장학금",
]


class WelfareCrawler:
    """복지로 크롤러 클래스 (Selenium 기반)"""
    
    def __init__(self, base_url: str = "https://www.bokjiro.go.kr", headless: bool = True):
        """
        크롤러 초기화
        
        Args:
            base_url: 복지로 기본 URL
            headless: 헤드리스 모드 사용 여부 (기본값: True)
        """
        self.base_url = base_url
        self.driver = None
        self.headless = headless
        self._init_driver()
    
    def _init_driver(self):
        """Selenium WebDriver 초기화"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--lang=ko-KR')
            
            # 자동으로 ChromeDriver 다운로드 및 설정
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(5)
            
            logger.info("Selenium WebDriver 초기화 완료")
        except Exception as e:
            logger.error(f"WebDriver 초기화 실패: {e}")
            raise
    
    def __enter__(self):
        """Context manager 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()
    
    def close(self):
        """WebDriver 종료"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver 종료 완료")
            except Exception as e:
                logger.warning(f"WebDriver 종료 중 오류: {e}")
    
    def search_welfare(self, keyword: str, page: int = 1, search_type: str = "복지서비스") -> List[Dict]:
        """
        복지로 통합검색에서 키워드로 검색하여 복지 정보 리스트를 가져옵니다.
        
        Args:
            keyword: 검색 키워드
            page: 페이지 번호 (기본값: 1)
            search_type: 검색 타입 ("전체", "복지서비스", "복지정보", "온라인신청")
        
        Returns:
            복지 정보 딕셔너리 리스트
        """
        try:
            # 통합검색 페이지로 이동
            search_url = f"{self.base_url}/ssis-tbu/twatzzza/intgSearch/moveTWZZ01000M.do"
            self.driver.get(search_url)
            
            # 페이지 로드 대기
            time.sleep(2)
            
            # 검색어 입력 필드 찾기 및 입력
            try:
                search_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'][placeholder*='검색어'], input[type='text'][aria-label*='검색어']"))
                )
                search_input.clear()
                search_input.send_keys(keyword)
                logger.info(f"검색어 입력: {keyword}")
            except TimeoutException:
                # 다른 선택자 시도
                try:
                    search_input = self.driver.find_element(By.NAME, "searchKeyword")
                    search_input.clear()
                    search_input.send_keys(keyword)
                except NoSuchElementException:
                    logger.error("검색어 입력 필드를 찾을 수 없습니다")
                    return []
            
            # 검색 버튼 클릭
            try:
                search_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button:contains('검색'), input[type='submit'][value*='검색']"))
                )
                search_button.click()
            except TimeoutException:
                # Enter 키로 검색 시도
                from selenium.webdriver.common.keys import Keys
                search_input.send_keys(Keys.RETURN)
            
            # 검색 결과 로드 대기
            time.sleep(3)
            
            # 복지서비스 탭 클릭 (search_type이 "복지서비스"인 경우)
            if search_type == "복지서비스":
                try:
                    # 탭 찾기 및 클릭
                    tab_selectors = [
                        "button[role='tab']:contains('복지서비스')",
                        "a[role='tab']:contains('복지서비스')",
                        "//button[contains(text(), '복지서비스')]",
                        "//a[contains(text(), '복지서비스')]",
                    ]
                    
                    tab_clicked = False
                    for selector in tab_selectors:
                        try:
                            if selector.startswith("//"):
                                tab = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, selector))
                                )
                            else:
                                # CSS 선택자로는 :contains를 직접 사용할 수 없으므로 XPath 사용
                                tab = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '복지서비스')] | //a[contains(text(), '복지서비스')]"))
                                )
                            tab.click()
                            time.sleep(2)  # 탭 전환 대기
                            tab_clicked = True
                            logger.info("복지서비스 탭 클릭 완료")
                            break
                        except (TimeoutException, NoSuchElementException):
                            continue
                    
                    if not tab_clicked:
                        logger.warning("복지서비스 탭을 찾을 수 없습니다. 전체 결과를 사용합니다.")
                except Exception as e:
                    logger.warning(f"탭 클릭 실패: {e}")
            
            # 검색 결과가 로드될 때까지 대기
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li, div[class*='item'], div[class*='list'], a[href*='ssi']"))
                )
            except TimeoutException:
                logger.warning("검색 결과 로드 대기 시간 초과")
            
            # 추가 대기 (동적 콘텐츠 로딩)
            time.sleep(2)
            
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 검색 결과 파싱
            welfare_items = self._parse_search_results(soup, keyword)
            
            logger.info(f"키워드 '{keyword}' 검색 결과: {len(welfare_items)}개")
            return welfare_items
            
        except Exception as e:
            logger.error(f"복지로 검색 오류 (키워드: {keyword}): {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []
    
    def _parse_search_results(self, soup: BeautifulSoup, keyword: str) -> List[Dict]:
        """
        검색 결과 페이지를 파싱합니다.
        
        Args:
            soup: BeautifulSoup 객체
            keyword: 검색 키워드
        
        Returns:
            복지 정보 리스트
        """
        welfare_items = []
        
        # 검색 결과 항목 찾기 - 다양한 패턴 시도
        result_selectors = [
            # 리스트 아이템
            soup.find_all('li', class_=lambda x: x and any(
                kw in str(x).lower() for kw in ['item', 'list', 'result', 'service']
            ) if x else False),
            # div 아이템
            soup.find_all('div', class_=lambda x: x and any(
                kw in str(x).lower() for kw in ['item', 'list', 'result', 'service']
            ) if x else False),
            # 테이블 행
            soup.find_all('tr', class_=lambda x: x and 'item' in str(x).lower() if x else False),
        ]
        
        # 링크 기반 검색
        links = soup.find_all('a', href=lambda x: x and (
            'ssi' in str(x).lower() or 
            'welfare' in str(x).lower() or 
            'service' in str(x).lower() or
            '.do' in str(x).lower()
        ) if x else False)
        
        # 중복 제거를 위한 set
        processed_links = set()
        
        # 링크에서 복지 정보 추출
        for link in links:
            try:
                href = link.get('href', '')
                if not href or href in processed_links:
                    continue
                
                title = link.get_text(strip=True)
                if not title or len(title) < 5:
                    continue
                
                # 링크 URL 정규화
                if href.startswith('javascript:'):
                    # JavaScript 링크 처리
                    onclick = link.get('onclick', '')
                    url_match = re.search(r"['\"]([^'\"]+\.do[^'\"]*)['\"]", onclick)
                    if url_match:
                        href = url_match.group(1)
                    else:
                        continue
                
                if not href.startswith('http'):
                    href = f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"
                
                processed_links.add(href)
                
                # 복지 정보 생성
                welfare_data = {
                    'title': title,
                    'source_link': href,
                    'keyword': keyword,
                }
                
                # 상세 페이지에서 추가 정보 가져오기
                detail_info = self._fetch_detail_page(href)
                if detail_info:
                    welfare_data.update(detail_info)
                
                # 날짜 파싱
                date_text = welfare_data.get('apply_period', '')
                start_date, end_date, is_always = parse_date_range(date_text)
                status = determine_status(date_text)
                
                welfare_data.update({
                    'apply_start': start_date,
                    'apply_end': end_date,
                    'is_always': is_always,
                    'status': status,
                })
                
                # 만료된 공고 필터링
                if check_is_active(date_text):
                    welfare_items.append(welfare_data)
                else:
                    logger.debug(f"만료된 공고 필터링: {title}")
                    
            except Exception as e:
                logger.debug(f"링크 파싱 실패: {e}")
                continue
        
        # 결과 항목 파싱
        for selector_results in result_selectors:
            for item in selector_results[:50]:  # 최대 50개만
                try:
                    welfare_data = self._parse_welfare_item(item, keyword)
                    if welfare_data and welfare_data.get('source_link') not in processed_links:
                        processed_links.add(welfare_data.get('source_link'))
                        welfare_items.append(welfare_data)
                except Exception as e:
                    logger.debug(f"항목 파싱 실패: {e}")
                    continue
        
        return welfare_items
    
    def _parse_welfare_item(self, item, keyword: str) -> Optional[Dict]:
        """
        개별 복지 항목을 파싱합니다.
        
        Args:
            item: BeautifulSoup 요소
            keyword: 검색 키워드
        
        Returns:
            파싱된 복지 정보 딕셔너리
        """
        try:
            # 제목 추출
            title = None
            link = None
            
            # 패턴 1: a 태그의 텍스트
            link_elem = item.find('a', href=True)
            if link_elem:
                title = link_elem.get_text(strip=True)
                href = link_elem.get('href', '')
                if href:
                    if href.startswith('http'):
                        link = href
                    elif href.startswith('javascript:'):
                        onclick = link_elem.get('onclick', '')
                        url_match = re.search(r"['\"]([^'\"]+\.do[^'\"]*)['\"]", onclick)
                        if url_match:
                            link = f"{self.base_url}{url_match.group(1)}"
                    else:
                        link = f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"
            
            # 패턴 2: 제목이 별도 요소에 있는 경우
            if not title:
                title_elem = item.find(['h3', 'h4', 'h5', 'strong', 'b'], class_=lambda x: x and 'title' in str(x).lower() if x else False) or \
                            item.find('span', class_=lambda x: x and 'title' in str(x).lower() if x else False) or \
                            item.find('div', class_=lambda x: x and 'title' in str(x).lower() if x else False)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if not link:
                        link_in_title = title_elem.find('a', href=True)
                        if link_in_title:
                            href = link_in_title.get('href', '')
                            if href and not href.startswith('javascript:'):
                                link = f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"
            
            # 패턴 3: 텍스트가 충분히 긴 경우
            if not title:
                text = item.get_text(strip=True)
                if len(text) > 10 and len(text) < 200:
                    title = text.split('\n')[0].strip()
            
            if not title or len(title) < 5:
                return None
            
            # 신청기간 추출
            date_text = None
            item_text = item.get_text()
            
            date_patterns = [
                r'신청기간[:\s]*(\d{4}[.-]\d{2}[.-]\d{2}\s*~\s*\d{4}[.-]\d{2}[.-]\d{2})',
                r'접수기간[:\s]*(\d{4}[.-]\d{2}[.-]\d{2}\s*~\s*\d{4}[.-]\d{2}[.-]\d{2})',
                r'(\d{4}[.-]\d{2}[.-]\d{2}\s*~\s*\d{4}[.-]\d{2}[.-]\d{2})',
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, item_text)
                if match:
                    date_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
                    break
            
            # 상세 페이지에서 추가 정보 가져오기
            summary = None
            full_text = None
            region = None
            
            if link:
                detail_info = self._fetch_detail_page(link)
                if detail_info:
                    date_text = detail_info.get('apply_period') or date_text
                    summary = detail_info.get('summary')
                    full_text = detail_info.get('full_text')
                    region = detail_info.get('region')
            
            # 날짜 파싱
            start_date, end_date, is_always = parse_date_range(date_text or "")
            status = determine_status(date_text or "")
            
            # 만료된 공고 필터링
            if not check_is_active(date_text or ""):
                logger.debug(f"만료된 공고 필터링: {title}")
                return None
            
            return {
                'title': title,
                'summary': summary,
                'full_text': full_text,
                'source_link': link,
                'region': region,
                'apply_start': start_date,
                'apply_end': end_date,
                'is_always': is_always,
                'status': status,
                'keyword': keyword,
            }
            
        except Exception as e:
            logger.debug(f"복지 항목 파싱 오류: {e}")
            return None
    
    def _fetch_detail_page(self, url: str) -> Optional[Dict]:
        """
        복지 상세 페이지에서 추가 정보를 가져옵니다.
        
        Args:
            url: 상세 페이지 URL
        
        Returns:
            상세 정보 딕셔너리
        """
        try:
            # 새 탭에서 열기
            original_window = self.driver.current_window_handle
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            
            # 새 탭으로 전환
            self.driver.switch_to.window([w for w in self.driver.window_handles if w != original_window][0])
            
            # 페이지 로드 대기
            time.sleep(2)
            
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            detail_info = {}
            
            # 신청기간 추출
            period_elem = soup.find(string=lambda text: text and ('신청기간' in text or '접수기간' in text))
            if period_elem:
                parent = period_elem.parent
                if parent:
                    period_text = parent.get_text(strip=True)
                    date_match = re.search(r'신청기간[:\s]*([^\n]+)', period_text)
                    if date_match:
                        detail_info['apply_period'] = date_match.group(1).strip()
            
            # 요약 정보 추출
            summary_elem = soup.find('div', class_=lambda x: x and 'summary' in str(x).lower() if x else False) or \
                          soup.find('p', class_=lambda x: x and 'intro' in str(x).lower() if x else False)
            if summary_elem:
                detail_info['summary'] = summary_elem.get_text(strip=True)
            
            # 전체 텍스트 추출
            content_elem = soup.find('div', class_=lambda x: x and 'content' in str(x).lower() if x else False) or \
                          soup.find('div', class_=lambda x: x and 'detail' in str(x).lower() if x else False)
            if content_elem:
                detail_info['full_text'] = content_elem.get_text(strip=True)
            
            # 지역 정보 추출
            region_elem = soup.find(string=lambda text: text and ('지역' in text or '지원대상' in text))
            if region_elem:
                parent = region_elem.parent
                if parent:
                    region_text = parent.get_text(strip=True)
                    detail_info['region'] = region_text
            
            # 원래 탭으로 돌아가기
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
            return detail_info if detail_info else None
            
        except Exception as e:
            logger.warning(f"상세 페이지 가져오기 실패 ({url}): {e}")
            # 탭 전환 실패 시 원래 탭으로 복귀 시도
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(original_window)
            except:
                pass
            return None
    
    def crawl_all_keywords(self, max_pages_per_keyword: int = 3) -> List[Dict]:
        """
        모든 키워드로 복지 정보를 크롤링합니다.
        
        Args:
            max_pages_per_keyword: 키워드당 최대 페이지 수
        
        Returns:
            모든 복지 정보 리스트
        """
        all_welfares = []
        
        for keyword in WELFARE_KEYWORDS:
            logger.info(f"키워드 크롤링 시작: {keyword}")
            
            try:
                welfares = self.search_welfare(keyword, page=1)
                
                if welfares:
                    all_welfares.extend(welfares)
                
                # 서버 부하 방지를 위한 딜레이
                time.sleep(2)
                
                logger.info(f"키워드 '{keyword}' 크롤링 완료: {len([w for w in all_welfares if w.get('keyword') == keyword])}개")
            except Exception as e:
                logger.error(f"키워드 '{keyword}' 크롤링 중 오류: {e}")
                continue
        
        # 중복 제거 (제목 기준)
        seen_titles = set()
        unique_welfares = []
        for welfare in all_welfares:
            title = welfare.get('title', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_welfares.append(welfare)
        
        logger.info(f"전체 크롤링 완료: {len(unique_welfares)}개 (중복 제거 후)")
        return unique_welfares


def crawl_welfare_services(headless: bool = True) -> List[Dict]:
    """
    복지로에서 복지 서비스를 크롤링하는 메인 함수
    
    Args:
        headless: 헤드리스 모드 사용 여부
    
    Returns:
        크롤링된 복지 정보 리스트
    """
    crawler = WelfareCrawler(headless=headless)
    try:
        return crawler.crawl_all_keywords()
    finally:
        crawler.close()
