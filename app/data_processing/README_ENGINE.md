# 복지 서비스 추천 엔진 가이드

## 개요

LangChain과 FAISS를 사용한 벡터 유사도 기반 복지 서비스 추천 엔진입니다.

## 주요 기능

1. **벡터 임베딩**: OpenAI Embeddings를 사용하여 데이터를 벡터화
2. **유사도 검색**: 사용자 질문과 유사한 복지 서비스를 검색
3. **상위 결과 반환**: 유사도가 높은 상위 N개 결과 반환
4. **자동 인덱스 구축**: 전처리된 데이터로부터 FAISS 인덱스 자동 생성

## 사용 방법

### 1. 전처리된 데이터 준비

먼저 CSV 파일을 전처리하여 JSON 데이터를 생성해야 합니다:

```bash
python scripts/preprocess_csv.py
```

### 2. 엔진 테스트

```bash
# 기본 테스트 실행
python scripts/test_engine.py

# 또는 직접 실행
python -m app.data_processing.engine
```

### 3. 코드에서 사용

```python
from app.data_processing.engine import WelfareRecommendationEngine

# 엔진 초기화
engine = WelfareRecommendationEngine()

# 검색
results = engine.search("할머니 병원비 때문에 학교 다니기 힘들어", top_k=3)

# 결과 출력
for result in results:
    print(f"서비스명: {result['service_name']}")
    print(f"요약: {result['summary']}")
    print(f"URL: {result['url']}")
    print()
```

## API

### WelfareRecommendationEngine

#### `__init__(data_path=None, embedding_model="text-embedding-3-small", index_path=None)`

엔진을 초기화합니다.

- `data_path`: 전처리된 JSON 파일 경로 (기본값: `data/preprocessed/rag_welfare_data.json`)
- `embedding_model`: OpenAI 임베딩 모델명 (기본값: `text-embedding-3-small`)
- `index_path`: FAISS 인덱스 저장 경로 (기본값: `data/vector_db/welfare_faiss.index`)

#### `search(query, top_k=3, min_score=None) -> List[Dict]`

사용자 질문에 대한 복지 서비스를 검색합니다.

**매개변수:**
- `query`: 사용자 질문 (예: "할머니 병원비 때문에 학교 다니기 힘들어")
- `top_k`: 반환할 상위 결과 수 (기본값: 3)
- `min_score`: 최소 유사도 점수 (L2 거리, 낮을수록 유사, None이면 필터링 안 함)

**반환값:**
검색 결과 리스트. 각 결과는 다음 필드를 포함:
- `rank`: 순위
- `service_name`: 서비스명
- `summary`: 요약 내용
- `url`: 신청 URL
- `target`: 지원 대상
- `organization`: 기관명
- `contact`: 연락처
- `similarity_score`: 유사도 점수 (L2 거리, 낮을수록 유사)

#### `format_results(results) -> str`

검색 결과를 읽기 쉬운 형식으로 포맷팅합니다.

## 예시

### 기본 사용

```python
from app.data_processing.engine import WelfareRecommendationEngine

# 엔진 초기화
engine = WelfareRecommendationEngine()

# 검색
query = "할머니 병원비 때문에 학교 다니기 힘들어"
results = engine.search(query, top_k=3)

# 결과 출력
print(engine.format_results(results))
```

### 커스텀 데이터 경로

```python
engine = WelfareRecommendationEngine(
    data_path="./my_data/rag_welfare_data.json",
    index_path="./my_index/welfare.index"
)
```

### 유사도 필터링

```python
# 유사도 점수가 100 이하인 결과만 반환
results = engine.search(query, top_k=10, min_score=100)
```

## 출력 형식

검색 결과는 다음과 같은 형식으로 반환됩니다:

```
================================================================================
[순위 1] 서비스명
================================================================================
요약: 서비스 요약 내용...
대상: 지원 대상
기관: 기관명
연락처: 연락처 정보
신청 URL: https://...
유사도 점수: 45.1234 (낮을수록 유사)
```

## 인덱스 관리

### 자동 구축
엔진을 처음 초기화할 때 전처리된 데이터로부터 FAISS 인덱스를 자동으로 구축합니다.

### 인덱스 재사용
한 번 구축된 인덱스는 자동으로 저장되며, 다음 실행 시 재사용됩니다.

### 인덱스 재구축
인덱스를 재구축하려면 기존 인덱스 파일을 삭제하세요:

```bash
rm data/vector_db/welfare_faiss.index
rm data/vector_db/welfare_id_mapping.pkl
```

## 성능

- **인덱스 구축**: 데이터 수에 따라 다름 (100개 기준 약 1-2분)
- **검색 속도**: 매우 빠름 (밀리초 단위)
- **메모리 사용**: 인덱스 크기에 비례

## 문제 해결

### "데이터 파일을 찾을 수 없습니다"
- 전처리 스크립트를 먼저 실행하세요: `python scripts/preprocess_csv.py`

### "OpenAI API 키가 설정되지 않았습니다"
- `.env` 파일에 `OPENAI_API_KEY=your_key`를 추가하세요

### "FAISS가 설치되지 않았습니다"
- `pip install faiss-cpu`를 실행하세요

### "LangChain이 설치되지 않았습니다"
- `pip install langchain langchain-openai`를 실행하세요

### 검색 결과가 없음
- 인덱스가 제대로 구축되었는지 확인하세요
- 검색 쿼리를 더 구체적으로 작성해보세요
- `min_score` 값을 조정해보세요

## 다음 단계

1. **API 통합**: FastAPI 엔드포인트에 통합
2. **요약 개선**: LLM을 사용하여 더 나은 요약 생성
3. **필터링**: 지역, 나이 등 추가 필터링 기능
4. **캐싱**: 자주 검색되는 쿼리 결과 캐싱

