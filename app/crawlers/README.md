# 복지로 크롤러 (Selenium 기반)

복지로에서 가족돌봄청년(영케어러) 관련 복지 서비스를 크롤링하는 모듈입니다.

## 주요 기능

1. **Selenium 기반 크롤링**: JavaScript 기반 동적 콘텐츠 크롤링 지원
2. **키워드 기반 크롤링**: 가족돌봄청년 관련 키워드로 복지 서비스 검색
3. **날짜 필터링**: 만료된 공고는 크롤링 시점에 자동 필터링
4. **중복 제거**: 제목 기준으로 중복 항목 제거
5. **DB 저장**: 크롤링한 데이터를 자동으로 DB에 저장
6. **상세 페이지 크롤링**: 검색 결과에서 상세 페이지로 이동하여 추가 정보 수집

## 사용 방법

### API를 통한 크롤링

```bash
POST /api/welfare/crawl
Content-Type: application/json

{
  "keywords": ["가족돌봄청년", "영케어러"],  # 선택사항 (없으면 기본 키워드 사용)
  "max_pages": 3  # 키워드당 최대 페이지 수
}
```

### Python 코드에서 직접 사용

```python
from app.services.crawler_service import crawl_and_save_welfares
from app.models.connection import get_db

db = next(get_db())
result = crawl_and_save_welfares(db, keywords=["가족돌봄청년"], max_pages=3)
print(result)
```

## 크롤링 키워드

기본적으로 다음 키워드들이 사용됩니다:

- **핵심 대상**: 가족돌봄청년, 영케어러, 돌봄가족, 청소년부모
- **상황별 지원**: 가사간병, 긴급복지, 병원동행, 재가급여, 재가복지, 발달재활
- **청년/심리 특화**: 청년마음건강, 청년월세, 장학금

## 기술 스택

- **Selenium**: 브라우저 자동화를 통한 JavaScript 실행 및 동적 콘텐츠 크롤링
- **BeautifulSoup**: HTML 파싱
- **ChromeDriver**: Chrome 브라우저 자동화 (webdriver-manager로 자동 관리)

## 주요 특징

1. **동적 콘텐츠 지원**: JavaScript로 로드되는 검색 결과를 정확히 크롤링
2. **자동 대기**: WebDriverWait를 사용하여 요소가 로드될 때까지 자동 대기
3. **탭 전환**: 복지서비스 탭을 자동으로 클릭하여 검색 결과 필터링
4. **상세 페이지 크롤링**: 새 탭에서 상세 페이지를 열어 추가 정보 수집
5. **헤드리스 모드**: 서버 환경에서도 실행 가능한 헤드리스 모드 지원

## 설치 요구사항

1. **Chrome 브라우저**: 시스템에 Chrome이 설치되어 있어야 합니다
2. **Python 패키지**: `selenium`, `webdriver-manager` (requirements.txt에 포함)

## 사용 방법

### 테스트 스크립트 실행

가장 간단한 방법은 테스트 스크립트를 사용하는 것입니다:

```bash
# 프로젝트 루트 디렉토리에서 실행
cd neulbom-backend

# 단일 키워드 테스트 (브라우저 창 표시)
python -m app.crawlers.test_crawler --mode single

# 단일 키워드 테스트 (헤드리스 모드)
python -m app.crawlers.test_crawler --mode single --headless

# 여러 키워드 테스트
python -m app.crawlers.test_crawler --mode multiple

# 전체 키워드 테스트 (시간이 오래 걸림)
python -m app.crawlers.test_crawler --mode all
```

### Python 코드에서 직접 사용

```python
from app.crawlers.welfare_crawler import WelfareCrawler

# 헤드리스 모드로 크롤러 생성
with WelfareCrawler(headless=True) as crawler:
    # 단일 키워드 검색
    results = crawler.search_welfare("가족돌봄청년")
    
    # 모든 키워드 크롤링
    all_results = crawler.crawl_all_keywords()
```

### API를 통한 크롤링

```bash
# 서버 실행 후
POST /api/welfare/crawl
Content-Type: application/json
Authorization: Bearer {your_token}

{
  "keywords": ["가족돌봄청년", "영케어러"],
  "max_pages": 3,
  "headless": true
}
```

### Python 인터프리터에서 직접 테스트

```bash
# 프로젝트 루트에서
cd neulbom-backend
python

# Python 인터프리터에서
>>> from app.crawlers.welfare_crawler import WelfareCrawler
>>> with WelfareCrawler(headless=False) as crawler:
...     results = crawler.search_welfare("가족돌봄청년")
...     print(f"검색 결과: {len(results)}개")
...     for item in results[:3]:
...         print(f"- {item['title']}")
```

## 주의사항

1. **ChromeDriver 자동 설치**: webdriver-manager가 자동으로 ChromeDriver를 다운로드합니다
2. **메모리 사용**: Selenium은 브라우저를 실행하므로 메모리를 많이 사용합니다
3. **실행 시간**: JavaScript 실행 및 페이지 로딩 대기로 인해 시간이 걸릴 수 있습니다
4. **헤드리스 모드**: 서버 환경에서는 `headless=True`로 설정하는 것을 권장합니다

## 트러블슈팅

### ChromeDriver 오류
- Chrome 브라우저가 최신 버전인지 확인
- webdriver-manager가 자동으로 호환되는 드라이버를 다운로드합니다

### 타임아웃 오류
- 네트워크 상태 확인
- 대기 시간을 늘려야 할 수 있습니다 (코드에서 `time.sleep()` 값 조정)

### 메모리 부족
- 동시에 여러 크롤러를 실행하지 마세요
- 크롤링 후 `crawler.close()`를 호출하여 리소스를 정리하세요

## 파일 구조

- `welfare_crawler.py`: 크롤러 메인 클래스
- `utils.py`: 날짜 파싱 및 유효성 검사 유틸리티 함수

