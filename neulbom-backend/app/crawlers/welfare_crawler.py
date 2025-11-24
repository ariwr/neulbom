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
            headless: 헤드리스 모드 사용 여부 (기본값: True, Chrome 창 없이 실행)
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
                chrome_options.add_argument('--headless=new')  # 새로운 headless 모드
                logger.info("헤드리스 모드로 실행 (Chrome 창 없음)")
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--lang=ko-KR')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 봇 감지 방지
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 자동으로 ChromeDriver 다운로드 및 설정
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(5)
            
            # 봇 감지 방지를 위한 스크립트 실행
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
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
                # WebDriver가 이미 종료되었는지 확인
                try:
                    # 간단한 명령으로 연결 상태 확인
                    self.driver.current_url
                except:
                    # 이미 종료된 경우
                    logger.debug("WebDriver가 이미 종료되었습니다")
                    self.driver = None
                    return
                
                self.driver.quit()
                logger.info("WebDriver 종료 완료")
            except Exception as e:
                logger.debug(f"WebDriver 종료 중 오류 (무시됨): {e}")
            finally:
                self.driver = None
    
    def search_welfare(self, keyword: str, page: int = 1, search_type: str = "복지서비스") -> List[Dict]:
        """
        [최종 수정본] JavaScript 기반 입력 및 클릭 (입력 오류 방지 버전)
        직접 URL 접근 실패로 인해, 검색 페이지에서 JS로 강제 실행합니다.
        """
        try:
            # ---------------------------------------------------------
            # 1. 통합검색 페이지 이동
            # ---------------------------------------------------------
            # 검색 결과 페이지가 아니라 '검색창이 있는 페이지'로 이동합니다.
            if page == 1:
                search_url = f"{self.base_url}/ssis-tbu/twatzzza/intgSearch/moveTWZZ01000M.do"
                logger.info(f"검색 페이지 이동: {search_url}")
                self.driver.get(search_url)
                
                # 검색창 대기
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "searchKeyword"))
                    )
                except:
                    logger.warning("검색창 로딩 지연")
                
                # ---------------------------------------------------------
                # 2. 검색어 입력 (JavaScript 강제 주입)
                # ---------------------------------------------------------
                # Selenium의 send_keys를 쓰지 않고, 브라우저 콘솔에서 치는 것과 똑같이 값을 꽂아넣습니다.
                logger.info(f"키워드 '{keyword}' JS 주입 시도...")
                
                self.driver.execute_script(f"""
                    var input = document.getElementById('searchKeyword');
                    if (input) {{
                        input.value = '{keyword}';
                    }}
                """)
                time.sleep(0.5)
                
                # ---------------------------------------------------------
                # 3. 검색 버튼 클릭 (JavaScript 강제 클릭)
                # ---------------------------------------------------------
                logger.info("검색 버튼 클릭 시도...")
                
                # 복지로의 실제 검색 버튼을 찾아서 클릭합니다.
                # 보통 돋보기 아이콘이나 '검색' 텍스트가 있는 버튼입니다.
                clicked = self.driver.execute_script("""
                    // 1. ID로 시도
                    var btn = document.querySelector('#btnSearch');
                    if (btn) { btn.click(); return true; }
                    
                    // 2. 클래스로 시도 (.btn-search)
                    btn = document.querySelector('.btn-search');
                    if (btn) { btn.click(); return true; }
                    
                    // 3. 텍스트로 시도 ('검색' 글자가 있는 버튼)
                    var btns = document.querySelectorAll('button, a');
                    for (var i=0; i<btns.length; i++) {
                        if (btns[i].innerText.trim() === '검색') {
                            btns[i].click();
                            return true;
                        }
                    }
                    return false;
                """)
                
                if not clicked:
                    logger.warning("JS로 버튼을 못 찾음. Enter 키로 대체 시도.")
                    self.driver.find_element(By.ID, "searchKeyword").send_keys("\n")
                
                # 검색 결과 로딩 대기 (URL이 바뀌거나 결과 영역이 뜰 때까지)
                time.sleep(3)
            
            # ---------------------------------------------------------
            # 4. 페이지 이동 (2페이지 이상일 때)
            # ---------------------------------------------------------
            else:
                if not self._click_next_page():
                    return []
                time.sleep(2)
            
            # ---------------------------------------------------------
            # 5. '복지서비스' 탭 클릭
            # ---------------------------------------------------------
            if page == 1 and search_type == "복지서비스":
                # 탭 클릭 로직 호출
                self._force_click_tab("복지서비스")
                # 탭 전환 로딩 대기
                time.sleep(2)
            
            # ---------------------------------------------------------
            # 6. 결과 파싱
            # ---------------------------------------------------------
            # 로딩 완료 확인
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # '검색결과가 없습니다' 체크
            if "검색결과가 없습니다" in soup.text:
                logger.info("검색 결과 없음")
                return []
            
            welfare_items = self._parse_search_results(soup, keyword)
            logger.info(f"페이지 {page} 결과: {len(welfare_items)}건")
            
            return welfare_items
            
        except Exception as e:
            logger.error(f"검색 로직 수행 중 오류: {e}")
            return []
    
    def _force_click_tab(self, tab_name: str) -> bool:
        """탭 강제 클릭 (JavaScript)"""
        try:
            return self.driver.execute_script(f"""
                var tabs = document.querySelectorAll('a, button, li, span');
                for (var i=0; i<tabs.length; i++) {{
                    var txt = tabs[i].innerText.trim();
                    // '복지서비스'가 포함되어 있고 '정보'는 제외
                    if (txt.includes('{tab_name}') && !txt.includes('정보')) {{
                        // 부모 요소가 탭 리스트인 경우도 고려하여 클릭
                        tabs[i].click();
                        return true;
                    }}
                }}
                return false;
            """)
        except:
            return False
    
    def _parse_search_results(self, soup: BeautifulSoup, keyword: str) -> List[Dict]:
        """관대한 파싱 로직 (복구용)"""
        welfare_items = []
        processed_links = set()
        
        # 본문 영역 찾기
        content_area = soup.find('div', {'id': 'content'}) or soup
        
        # 모든 링크 검사
        potential_links = content_area.find_all('a')
        
        for link in potential_links:
            try:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                
                # 1. 텍스트와 링크 유효성 체크
                if not text or len(text) < 3 or not href or href == '#':
                    continue
                
                # 2. 복지로 상세 페이지 패턴 체크 (.do 포함 여부)
                is_valid = ('.do' in href or 'javascript' in href) and \
                           ('view' in href.lower() or 'wlfareInfo' in href or 'move' in href.lower())
                
                if not is_valid:
                    continue
                
                if href in processed_links:
                    continue
                
                # 3. URL 정규화
                if 'javascript' in href:
                    # onclick에서 URL 추출 시도
                    match = re.search(r"['\"]([^'\"]+\.do[^'\"]*)['\"]", link.get('onclick', ''))
                    if match:
                        href = match.group(1)
                    else:
                        continue
                
                final_url = f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"
                processed_links.add(href)  # 중복 방지
                
                # 4. 상세 페이지 정보 가져오기
                logger.info(f"상세 페이지 수집: {text}")
                detail_info = self._fetch_detail_page(final_url)
                
                item = {
                    'title': text,
                    'source_link': final_url,
                    'keyword': keyword
                }
                if detail_info:
                    item.update(detail_info)
                
                # 날짜 필터링 후 추가
                date_text = item.get('apply_period', '')
                if check_is_active(date_text):
                    welfare_items.append(item)
                
            except Exception as e:
                continue
                
        return welfare_items
    
    def _parse_welfare_item(self, item, keyword: str) -> Optional[Dict]:
        """
        개별 복지 항목을 파싱합니다.
        
        Args:
            item: BeautifulSoup 요소 (tr, div, li 등)
            keyword: 검색 키워드
        
        Returns:
            파싱된 복지 정보 딕셔너리
        """
        try:
            # 제목 추출
            title = None
            link = None
            
            # 패턴 1: a 태그의 텍스트 (우선순위 높음)
            # 복지로는 .do 링크나 moveTWZZ, selectTwatzzza 패턴 사용
            link_elem = item.find('a', href=lambda x: x and (
                '.do' in str(x) or 
                'moveTWZZ' in str(x) or 
                'selectTwatzzza' in str(x) or
                'intgSearch' in str(x)
            ) if x else False)
            
            if not link_elem:
                # 일반 링크도 시도
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
                            # 다른 패턴 시도
                            url_match = re.search(r"(moveTWZZ|selectTwatzzza|intgSearch)[^'\"]*\.do", onclick)
                            if url_match:
                                link = f"{self.base_url}/{url_match.group(0)}"
                    else:
                        link = f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"
            
            # 패턴 2: 제목이 별도 요소에 있는 경우 (cl- 클래스 포함)
            if not title:
                # cl- 클래스를 가진 요소에서 제목 찾기
                cl_title = item.find(['h3', 'h4', 'h5', 'strong', 'b', 'span', 'div'], 
                                    class_=lambda x: x and ('title' in str(x).lower() or 'tit' in str(x).lower() or 'cl-' in str(x)) if x else False)
                if cl_title:
                    title = cl_title.get_text(strip=True)
                    if not link:
                        link_in_title = cl_title.find('a', href=True)
                        if link_in_title:
                            href = link_in_title.get('href', '')
                            if href and not href.startswith('javascript:'):
                                link = f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"
                
                # 일반적인 제목 요소도 시도
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
            
            # 패턴 3: 텍스트가 충분히 긴 경우 (첫 번째 줄을 제목으로)
            if not title:
                text = item.get_text(strip=True)
                # 여러 줄로 나뉘어 있으면 첫 번째 줄 사용
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if lines:
                    # 가장 긴 줄이나 첫 번째 줄을 제목으로
                    title = max(lines, key=len) if lines else lines[0] if lines else None
                    if title and (len(title) < 5 or len(title) > 200):
                        # 길이가 적절하지 않으면 첫 번째 줄 사용
                        title = lines[0] if lines else None
            
            if not title or len(title) < 3:
                logger.debug(f"제목을 찾을 수 없음: {item.name if hasattr(item, 'name') else 'unknown'}")
                return None
            
            # 링크가 없으면 제목만으로는 저장하지 않음 (상세 정보를 가져올 수 없음)
            if not link:
                logger.debug(f"링크를 찾을 수 없음: {title[:50]}")
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
            
            # 만료된 공고 필터링 (날짜 정보가 없으면 일단 포함)
            if date_text:
                if not check_is_active(date_text):
                    logger.debug(f"만료된 공고 필터링: {title} (날짜: {date_text[:30]})")
                    return None
            # 날짜 정보가 없으면 필터링하지 않음
            
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
        original_window = None
        try:
            # 새 탭에서 열기
            original_window = self.driver.current_window_handle
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            
            # 새 탭으로 전환
            time.sleep(0.5)  # 탭 생성 대기 (1초 -> 0.5초)
            new_windows = [w for w in self.driver.window_handles if w != original_window]
            if not new_windows:
                logger.warning(f"새 탭 생성 실패: {url}")
                return None
            
            self.driver.switch_to.window(new_windows[0])
            
            # 페이지 로드 대기 (3초 -> 1.5초로 단축)
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except:
                pass
            time.sleep(1)  # 추가 대기 (3초 -> 1초로 단축)
            
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            detail_info = {}
            
            # 신청기간 추출 (다양한 패턴 시도)
            period_text = None
            period_patterns = [
                soup.find(string=lambda text: text and ('신청기간' in text or '접수기간' in text)),
                soup.find('th', string=lambda text: text and ('신청기간' in text or '접수기간' in text)),
                soup.find('dt', string=lambda text: text and ('신청기간' in text or '접수기간' in text)),
            ]
            
            for period_elem in period_patterns:
                if period_elem:
                    if hasattr(period_elem, 'parent') and period_elem.parent:
                        parent = period_elem.parent
                        # 다음 형제 요소나 부모의 텍스트에서 날짜 찾기
                        period_text = parent.get_text(strip=True)
                        # td, dd 등 다음 요소도 확인
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            period_text = next_sibling.get_text(strip=True)
                        break
                    elif isinstance(period_elem, str):
                        # 문자열인 경우 부모 찾기
                        parent = soup.find(string=lambda t: t == period_elem)
                        if parent and hasattr(parent, 'parent'):
                            period_text = parent.parent.get_text(strip=True)
                            break
            
            if period_text:
                date_match = re.search(r'신청기간[:\s]*([^\n\r]+)', period_text) or \
                           re.search(r'접수기간[:\s]*([^\n\r]+)', period_text) or \
                           re.search(r'(\d{4}[.-]\d{2}[.-]\d{2}\s*[~-]\s*\d{4}[.-]\d{2}[.-]\d{2})', period_text) or \
                           re.search(r'(상시신청|연중)', period_text)
                if date_match:
                    detail_info['apply_period'] = date_match.group(1).strip() if len(date_match.groups()) > 0 else date_match.group(0).strip()
            
            # 요약 정보 추출 (다양한 선택자 시도)
            summary_selectors = [
                soup.find('div', class_=lambda x: x and ('summary' in str(x).lower() or 'intro' in str(x).lower() or 'desc' in str(x).lower()) if x else False),
                soup.find('p', class_=lambda x: x and ('summary' in str(x).lower() or 'intro' in str(x).lower()) if x else False),
                soup.find('div', id=lambda x: x and 'summary' in str(x).lower() if x else False),
                soup.find('div', class_='view_con'),  # 복지로 특정 클래스
                soup.find('div', class_='detail_con'),  # 복지로 특정 클래스
            ]
            
            for summary_elem in summary_selectors:
                if summary_elem:
                    summary_text = summary_elem.get_text(strip=True)
                    if summary_text and len(summary_text) > 20:  # 의미있는 텍스트인지 확인
                        detail_info['summary'] = summary_text[:500]  # 요약은 500자로 제한
                        break
            
            # 전체 텍스트 추출 (더 넓은 범위)
            content_selectors = [
                soup.find('div', class_=lambda x: x and ('content' in str(x).lower() or 'detail' in str(x).lower() or 'view' in str(x).lower()) if x else False),
                soup.find('div', class_='view_con'),
                soup.find('div', class_='detail_con'),
                soup.find('div', id=lambda x: x and ('content' in str(x).lower() or 'detail' in str(x).lower()) if x else False),
                soup.find('article'),
                soup.find('main'),
            ]
            
            for content_elem in content_selectors:
                if content_elem:
                    full_text = content_elem.get_text(strip=True)
                    if full_text and len(full_text) > 50:  # 의미있는 텍스트인지 확인
                        detail_info['full_text'] = full_text
                        break
            
            # 지역 정보 추출
            region_patterns = [
                soup.find(string=lambda text: text and ('지역' in text or '지원지역' in text)),
                soup.find('th', string=lambda text: text and ('지역' in text or '지원지역' in text)),
                soup.find('dt', string=lambda text: text and ('지역' in text or '지원지역' in text)),
            ]
            
            for region_elem in region_patterns:
                if region_elem:
                    if hasattr(region_elem, 'parent') and region_elem.parent:
                        parent = region_elem.parent
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            region_text = next_sibling.get_text(strip=True)
                        else:
                            region_text = parent.get_text(strip=True)
                        if region_text and len(region_text) < 100:  # 지역명은 보통 짧음
                            detail_info['region'] = region_text
                            break
            
            # 원래 탭으로 돌아가기
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
            logger.debug(f"상세 페이지 파싱 완료: apply_period={bool(detail_info.get('apply_period'))}, summary={bool(detail_info.get('summary'))}, full_text={bool(detail_info.get('full_text'))}, region={bool(detail_info.get('region'))}")
            return detail_info if detail_info else None
            
        except Exception as e:
            logger.warning(f"상세 페이지 가져오기 실패 ({url}): {e}")
            import traceback
            logger.debug(traceback.format_exc())
            # 탭 전환 실패 시 원래 탭으로 복귀 시도
            try:
                if original_window and original_window in self.driver.window_handles:
                    self.driver.switch_to.window(original_window)
                # 열려있는 새 탭 닫기
                for handle in self.driver.window_handles:
                    if handle != original_window:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                if original_window and original_window in self.driver.window_handles:
                    self.driver.switch_to.window(original_window)
            except Exception as cleanup_e:
                logger.debug(f"탭 정리 중 오류: {cleanup_e}")
            return None
    
    def _has_next_page(self) -> bool:
        """
        현재 페이지에 다음 페이지가 있는지 확인합니다.
        
        Returns:
            다음 페이지가 있으면 True, 없으면 False
        """
        try:
            # 다음 버튼 찾기
            next_selectors = [
                (By.XPATH, "//a[contains(text(), '다음')]"),
                (By.XPATH, "//button[contains(text(), '다음')]"),
                (By.XPATH, "//a[contains(@class, 'next')]"),
                (By.XPATH, "//button[contains(@class, 'next')]"),
                (By.XPATH, "//*[@aria-label='다음']"),
                (By.CSS_SELECTOR, "a.next, button.next, .pagination .next"),
            ]
            
            for by, selector in next_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                # disabled 속성 확인
                                if element.get_attribute('disabled') or element.get_attribute('aria-disabled') == 'true':
                                    continue
                                # 다음 버튼이 있고 활성화되어 있으면 True
                                return True
                        except:
                            continue
                except:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"다음 페이지 확인 중 오류: {e}")
            return False
    
    def _click_next_page(self) -> bool:
        """
        다음 페이지 버튼을 클릭합니다.
        
        Returns:
            클릭 성공 시 True, 실패 시 False
        """
        try:
            next_selectors = [
                (By.XPATH, "//a[contains(text(), '다음')]"),
                (By.XPATH, "//button[contains(text(), '다음')]"),
                (By.XPATH, "//a[contains(@class, 'next')]"),
                (By.XPATH, "//button[contains(@class, 'next')]"),
                (By.XPATH, "//*[@aria-label='다음']"),
                (By.CSS_SELECTOR, "a.next, button.next, .pagination .next"),
            ]
            
            for by, selector in next_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                if element.get_attribute('disabled') or element.get_attribute('aria-disabled') == 'true':
                                    continue
                                
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(0.3)  # 0.5초 -> 0.3초
                                self.driver.execute_script("arguments[0].click();", element)
                                # 페이지 전환 대기 (3초 -> 1.5초로 단축)
                                try:
                                    WebDriverWait(self.driver, 5).until(
                                        lambda d: d.execute_script("return document.readyState") == "complete"
                                    )
                                except:
                                    pass
                                time.sleep(1)  # 추가 대기 (3초 -> 1초로 단축)
                                return True
                        except:
                            continue
                except:
                    continue
            
            return False
        except Exception as e:
            logger.warning(f"다음 페이지 클릭 실패: {e}")
            return False
    
    def crawl_all_keywords(self, max_pages_per_keyword: Optional[int] = None) -> List[Dict]:
        """
        모든 키워드로 복지 정보를 크롤링합니다.
        
        Args:
            max_pages_per_keyword: 키워드당 최대 페이지 수 (None이면 전체 페이지 크롤링)
        
        Returns:
            모든 복지 정보 리스트
        """
        all_welfares = []
        
        for keyword in WELFARE_KEYWORDS:
            if max_pages_per_keyword is None:
                logger.info(f"키워드 크롤링 시작: {keyword} (전체 페이지 크롤링)")
            else:
                logger.info(f"키워드 크롤링 시작: {keyword} (최대 {max_pages_per_keyword}페이지)")
            
            try:
                keyword_welfares = []
                page = 1
                consecutive_empty_pages = 0
                max_consecutive_empty = 3  # 연속으로 3페이지가 비어있으면 종료
                seen_titles = set()  # 중복 체크를 위한 set (제목 기준)
                
                # 페이지 크롤링 (전체 또는 지정된 페이지 수까지)
                while True:
                    # max_pages_per_keyword가 지정된 경우 제한 확인
                    if max_pages_per_keyword is not None and page > max_pages_per_keyword:
                        logger.info(f"  최대 페이지 수({max_pages_per_keyword})에 도달하여 크롤링 종료")
                        break
                    
                    logger.info(f"  페이지 {page} 크롤링 중...")
                    welfares = self.search_welfare(keyword, page=page)
                    
                    if not welfares:
                        consecutive_empty_pages += 1
                        logger.info(f"  페이지 {page}에 데이터가 없음 (연속 빈 페이지: {consecutive_empty_pages})")
                        
                        # 연속으로 빈 페이지가 많으면 종료
                        if consecutive_empty_pages >= max_consecutive_empty:
                            logger.info(f"  연속 {max_consecutive_empty}페이지가 비어있어 크롤링 종료")
                            break
                    else:
                        # 중복 체크: 같은 제목이 반복되는지 확인
                        new_welfares = []
                        duplicate_count = 0
                        for welfare in welfares:
                            title = welfare.get('title', '')
                            if title and title not in seen_titles:
                                seen_titles.add(title)
                                new_welfares.append(welfare)
                            else:
                                duplicate_count += 1
                        
                        if duplicate_count > 0:
                            logger.info(f"  페이지 {page}에서 중복 항목 {duplicate_count}개 제외 (이미 크롤링된 항목)")
                        
                        # 새로운 항목이 없으면 연속 빈 페이지로 간주
                        if not new_welfares:
                            consecutive_empty_pages += 1
                            logger.info(f"  페이지 {page}에 새로운 데이터가 없음 (모두 중복, 연속 빈 페이지: {consecutive_empty_pages})")
                            
                            if consecutive_empty_pages >= max_consecutive_empty:
                                logger.info(f"  연속 {max_consecutive_empty}페이지에 새로운 데이터가 없어 크롤링 종료")
                                break
                        else:
                            consecutive_empty_pages = 0  # 새로운 데이터가 있으면 카운터 리셋
                            keyword_welfares.extend(new_welfares)
                            logger.info(f"  페이지 {page}에서 {len(new_welfares)}개 새로운 항목 추가 (중복 제외)")
                    
                    # 다음 페이지가 있는지 확인
                    has_next = self._has_next_page()
                    if not has_next:
                        logger.info(f"  다음 페이지가 없어 크롤링 종료")
                        break
                    
                    # 다음 페이지로 이동
                    if not self._click_next_page():
                        logger.info(f"  다음 페이지로 이동 실패. 크롤링 종료")
                        break
                    
                    page += 1
                    
                    # 서버 부하 방지를 위한 딜레이 (2초 -> 1초로 단축)
                    time.sleep(1)
                
                if keyword_welfares:
                    all_welfares.extend(keyword_welfares)
                
                logger.info(f"키워드 '{keyword}' 크롤링 완료: {len(keyword_welfares)}개 (총 {page - 1}페이지 크롤링)")
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
