# CSV 데이터 처리 가이드

## 개요

한국사회보장정보원 복지서비스 정보 CSV 파일을 전처리하여 데이터베이스에 저장하고, RAG 시스템을 위한 벡터 임베딩을 생성합니다.

## 파일 구조

- `csv_processor.py`: CSV 파일 전처리 및 DB 저장 로직
- `import_csv.py`: CSV 임포트 및 벡터 인덱스 구축 메인 스크립트

## 사용 방법

### 1. CSV 파일 임포트

```bash
# 방법 1: 직접 실행
cd neulbom-backend
python -m app.data_processing.import_csv "한국사회보장정보원_복지서비스정보_20250722.csv"

# 방법 2: 편의 스크립트 사용
python scripts/import_csv_data.py
```

### 2. 옵션

```bash
# CSV 임포트만 (벡터 임베딩 생성 안 함)
python -m app.data_processing.import_csv "파일경로.csv" --skip-embedding

# 벡터 인덱스만 재구축 (CSV 임포트 안 함)
python -m app.data_processing.import_csv "파일경로.csv" --skip-import

# 배치 크기 조정
python -m app.data_processing.import_csv "파일경로.csv" --batch-size 50
```

## 처리 과정

1. **CSV 파일 로드**
   - 인코딩 자동 감지 (CP949, EUC-KR, UTF-8)
   - 데이터프레임으로 변환

2. **데이터 전처리**
   - 텍스트 정제 (HTML 태그 제거, 공백 정리)
   - 지역 정보 추출
   - 나이 범위 추출
   - 연락처 정보 파싱
   - 날짜 파싱

3. **DB 저장**
   - 중복 체크 (service_id 기반)
   - 기존 데이터 업데이트 또는 새로 생성
   - 배치 커밋으로 성능 최적화

4. **벡터 임베딩 생성**
   - OpenAI Embeddings API 사용
   - FAISS 벡터 인덱스 구축
   - ID 매핑 저장

## CSV 파일 형식

예상 컬럼 구조:
- 서비스ID
- 서비스명
- 서비스URL
- 서비스내용
- 서비스기관
- 연락처
- 담당부서
- 서비스대상
- 기준년도
- 기준일자

## 환경 변수 설정

`.env` 파일에 다음 설정이 필요합니다:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 주의사항

1. **API 비용**: OpenAI Embeddings API 사용 시 비용이 발생할 수 있습니다.
2. **처리 시간**: 대량의 데이터 처리 시 시간이 오래 걸릴 수 있습니다.
3. **인코딩**: CSV 파일이 CP949/EUC-KR 인코딩인 경우 자동으로 감지하여 처리합니다.

## 문제 해결

### 인코딩 오류
- CSV 파일의 인코딩을 확인하세요
- `chardet` 라이브러리를 사용하여 자동 감지됩니다

### 임베딩 생성 실패
- OpenAI API 키가 올바르게 설정되었는지 확인하세요
- API 할당량을 확인하세요

### 벡터 인덱스 오류
- `data/vector_db` 디렉토리가 생성되었는지 확인하세요
- FAISS가 올바르게 설치되었는지 확인하세요 (`pip install faiss-cpu`)

