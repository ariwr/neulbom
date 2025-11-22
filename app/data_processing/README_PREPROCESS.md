# CSV 전처리 가이드

## 개요

한국사회보장정보원 복지서비스 정보 CSV 파일을 RAG 시스템에 최적화된 형태로 전처리합니다.

## 주요 기능

1. **컬럼 자동 분석**: CSV 파일의 컬럼 구조를 자동으로 분석하고 주요 컬럼을 매핑합니다.
2. **텍스트 병합**: 여러 컬럼의 텍스트를 합쳐서 `search_content` 컬럼을 생성합니다.
3. **청년 필터링**: 옵션으로 청년 관련 키워드가 포함된 데이터만 필터링합니다.
4. **다양한 형식 저장**: CSV, JSON, RAG용 JSON 등 다양한 형식으로 저장합니다.

## 사용 방법

### 기본 사용

```bash
# 방법 1: 편의 스크립트 사용
cd neulbom-backend
python scripts/preprocess_csv.py

# 방법 2: 직접 실행
python -m app.data_processing.preprocess "../한국사회보장정보원_복지서비스정보_20250722.csv"
```

### 옵션

```bash
# 청년 관련 데이터만 필터링
python scripts/preprocess_csv.py --filter-youth

# 필터링 없이 전체 데이터 처리
python scripts/preprocess_csv.py --no-filter

# 커스텀 키워드로 필터링
python scripts/preprocess_csv.py --keywords 청년 학생 장학 생계 의료 돌봄

# 출력 디렉토리 지정
python scripts/preprocess_csv.py --output-dir ./my_output
```

## 출력 파일

전처리 후 다음 파일들이 생성됩니다:

1. **preprocessed_welfare_data.csv**: 전체 전처리된 데이터 (CSV 형식)
2. **preprocessed_welfare_data.json**: 전체 전처리된 데이터 (JSON 형식)
3. **rag_welfare_data.json**: RAG 시스템용 간소화된 JSON
4. **preprocessing_stats.json**: 전처리 통계 정보

### RAG용 JSON 구조

```json
{
  "id": "WLF00000022",
  "title": "서비스명",
  "search_content": "병합된 검색용 텍스트",
  "url": "https://...",
  "target": "지원대상",
  "organization": "기관명",
  "contact": "연락처"
}
```

## 컬럼 매핑

스크립트는 다음 컬럼을 자동으로 찾아서 매핑합니다:

- **서비스ID**: 서비스ID, ID, service_id 등
- **서비스명**: 서비스명, 제목, title, service_name 등
- **서비스목적**: 서비스목적, purpose 등
- **지원대상**: 지원대상, 서비스대상, target 등
- **선정기준**: 선정기준, criteria 등
- **서비스URL**: 서비스URL, URL, link 등
- **서비스내용**: 서비스내용, 내용, content 등
- **서비스기관**: 서비스기관, 기관, organization 등
- **연락처**: 연락처, contact, 전화 등

## search_content 생성

다음 컬럼들의 텍스트를 병합하여 `search_content`를 생성합니다:

1. 서비스명
2. 서비스목적
3. 지원대상
4. 서비스내용
5. 선정기준

이렇게 병합된 텍스트는 RAG 시스템에서 사용자의 자연어 질문과 매칭됩니다.

## 청년 필터링

기본 필터링 키워드:
- 청년, 학생, 장학, 생계, 의료, 돌봄, 가족, 청소년, 대학생
- 취업, 주거, 주택, 생활, 지원, 급여, 수당, 보조금

필터링은 `search_content`에 키워드가 포함된 행만 남깁니다.

## 예시

### 전체 데이터 전처리

```bash
python scripts/preprocess_csv.py --no-filter
```

### 청년 관련 데이터만 전처리

```bash
python scripts/preprocess_csv.py --filter-youth
```

### 커스텀 키워드 필터링

```bash
python scripts/preprocess_csv.py --keywords 가족 돌봄 청년 학생
```

## 결과 확인

전처리 후 생성된 파일을 확인:

```python
import json
import pandas as pd

# JSON 확인
with open('data/preprocessed/rag_welfare_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f"총 {len(data)}개 항목")
    print(data[0])  # 첫 번째 항목 확인

# CSV 확인
df = pd.read_csv('data/preprocessed/preprocessed_welfare_data.csv')
print(df.head())
print(f"\n총 {len(df)}개 행")
print(f"search_content 평균 길이: {df['search_content'].str.len().mean():.1f}자")
```

## 문제 해결

### 인코딩 오류
- CSV 파일의 인코딩이 자동으로 감지됩니다
- CP949, EUC-KR, UTF-8 등을 자동으로 시도합니다

### 컬럼을 찾을 수 없음
- 스크립트는 다양한 컬럼명 변형을 시도합니다
- `preprocessing_stats.json`에서 실제 매핑된 컬럼을 확인할 수 있습니다

### 필터링 결과가 너무 적음
- `--no-filter` 옵션으로 필터링을 비활성화하세요
- 또는 `--keywords`로 더 많은 키워드를 추가하세요

## 다음 단계

전처리된 데이터를 사용하여:

1. **DB에 저장**: `import_csv.py`를 사용하여 DB에 저장
2. **벡터 임베딩 생성**: RAG 엔진을 사용하여 임베딩 생성
3. **검색 테스트**: 자연어 쿼리로 검색 테스트

